import hashlib
import logging
import time
from contextlib import contextmanager

from mem0.memory.utils import format_entities

try:
    from gremlin_python.driver import client, serializer
except ImportError:
    raise ImportError("gremlin_python is not installed. Please install it using `pip install gremlinpython`")

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    raise ImportError("rank_bm25 is not installed. Please install it using pip install rank-bm25")

from mem0.graphs.tools import (
    DELETE_MEMORY_STRUCT_TOOL_GRAPH,
    DELETE_MEMORY_TOOL_GRAPH,
    EXTRACT_ENTITIES_STRUCT_TOOL,
    EXTRACT_ENTITIES_TOOL,
    RELATIONS_STRUCT_TOOL,
    RELATIONS_TOOL,
)
from mem0.graphs.utils import EXTRACT_RELATIONS_PROMPT, get_delete_messages
from mem0.utils.factory import EmbedderFactory, LlmFactory, VectorStoreFactory

logger = logging.getLogger(__name__)

@contextmanager
def suppress_gremlin_errors():
    """Temporarily suppress gremlinpython error logs"""
    gremlin_logger = logging.getLogger('gremlinpython')
    original_level = gremlin_logger.level
    gremlin_logger.setLevel(logging.CRITICAL)
    try:
        yield
    finally:
        gremlin_logger.setLevel(original_level)


class MemoryGraph:
    def __init__(self, config):
        self.config = config
        self.graph = client.Client(
            url=config.graph_store.config.url,
            traversal_source=config.graph_store.config.traversal_source,
            username=config.graph_store.config.username,
            password=config.graph_store.config.password,
            message_serializer=config.graph_store.config.message_serializer
            if config.graph_store.config.message_serializer else serializer.GraphBinarySerializersV1(),
        )

        self.llm_provider = "openai_structured"
        if self.config.llm.provider:
            self.llm_provider = self.config.llm.provider
        if self.config.graph_store.llm:
            self.llm_provider = self.config.graph_store.llm.provider
        self.llm = LlmFactory.create(self.llm_provider, self.config.llm.config)

        self.node_label = "__Entity__" if self.config.graph_store.config.base_label else ""
        
        # Check if vector search is enabled
        self.enable_vector_search = getattr(self.config.graph_store.config, 'enable_vector_search', False)
        
        # Initialize vector store and embedding model for external vector indexing only if enabled
        if self.enable_vector_search:
            self.embedding_model = EmbedderFactory.create(
                self.config.embedder.provider, self.config.embedder.config, self.config.vector_store.config
            )
            
            # Initialize vector store for entity embeddings
            vector_store_config = self.config.vector_store.config.model_dump() if hasattr(self.config.vector_store.config, 'model_dump') else self.config.vector_store.config
            vector_store_config['collection_name'] = "graph_entities"
            
            self.vector_store = VectorStoreFactory.create(
                self.config.vector_store.provider, vector_store_config
            )
            
            self.similarity_threshold = 0.7
        else:
            self.embedding_model = None
            self.vector_store = None
            self.similarity_threshold = None

    def add(self, data, filters):
        """
        Adds data to the graph.

        Args:
            data (str): The data to add to the graph.
            filters (dict): A dictionary containing filters to be applied during the addition.
        """
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        entity_type_map = self._retrieve_nodes_from_data(data, filters)
        to_be_added = self._establish_nodes_relations_from_data(data, filters, entity_type_map)
        search_output = self._search_graph_db(node_list=list(entity_type_map.keys()), filters=filters)
        to_be_deleted = self._get_delete_entities_from_search_output(search_output, data, filters)
        deleted_entities = self._delete_entities(to_be_deleted, filters)
        added_entities = self._add_entities(to_be_added, filters, entity_type_map)

        return {"deleted_entities": deleted_entities, "added_entities": added_entities}

    def search(self, query, filters, limit=100):
        """
        Search for memories and related graph data.

        Args:
            query (str): Query to search for.
            filters (dict): A dictionary containing filters to be applied during the search.
            limit (int): The maximum number of nodes and relationships to retrieve. Defaults to 100.

        Returns:
            dict: A dictionary containing:
                - "contexts": List of search results from the base data store.
                - "entities": List of related graph data based on the query.
        """
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        entity_type_map = self._retrieve_nodes_from_data(query, filters)
        search_output = self._search_graph_db(node_list=list(entity_type_map.keys()), filters=filters)

        if not search_output:
            return []

        search_outputs_sequence = [
            [item["source"], item["relationship"], item["destination"]] for item in search_output
        ]
        bm25 = BM25Okapi(search_outputs_sequence)

        tokenized_query = query.split(" ")
        reranked_results = bm25.get_top_n(tokenized_query, search_outputs_sequence, n=5)

        search_results = []
        for item in reranked_results:
            search_results.append({"source": item[0], "relationship": item[1], "destination": item[2]})

        return search_results

    def delete_all(self, filters):
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")

        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Delete from Gremlin graph
        query = f"g.V().hasLabel('{self.node_label}').has('user_id', '{user_id}')"
        if agent_id:
            query += f".has('agent_id', '{agent_id}')"
        query += ".sideEffect(__.bothE().drop()).drop()"
        self.graph.submit(query).all().result()
        
        # Clean up vector store entries
        if self.enable_vector_search:
            try:
                self._cleanup_vector_store(filters)
            except Exception as e:
                logger.warning(f"Failed to cleanup vector store for user {user_id}: {e}")

    def _cleanup_vector_store(self, filters):
        """Clean up vector store entries for deleted entities."""
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Build filter for vector store
        vector_filters = {"user_id": user_id, "node_type": "entity"}
        if agent_id:
            vector_filters["agent_id"] = agent_id
            
        try:
            # Search for all entities matching the filters
            search_results = self.vector_store.search(
                query="*",  # Match all
                vectors=[],
                limit=10000,  # Large limit to get all entities
                filters=vector_filters
            )
            
            # Delete each matching entity from vector store
            for result in search_results:
                if result.id:
                    try:
                        self.vector_store.delete(result.id)
                    except Exception as e:
                        logger.warning(f"Failed to delete vector {result.id}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to cleanup vector store: {e}")

    def get_all(self, filters, limit=100):
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        query = (
            f"g.V().hasLabel(node_label)"
            f".has('user_id', user_id)"
        )
        if agent_id:
            query += f".has('agent_id', agent_id)"
        query += (
            f".outE()"
            f".where(inV().has('user_id', user_id)"
        )
        if agent_id:
            query += f".has('agent_id', agent_id)"
        query += (
            f")"
            f".project('source', 'relationship', 'target')"
            f".by(outV().values('name'))"
            f".by(label)"
            f".by(inV().values('name'))"
            f".limit(limit)"
        )
        params = {
            'node_label': self.node_label,
            'user_id': user_id,
            'limit': limit
        }
        if agent_id:
            params['agent_id'] = agent_id

        results = self.graph.submit(query, params).all().result()
        final_results = [
            {
                "source": result["source"],
                "relationship": result["relationship"],
                "target": result["target"]
            }
            for result in results
        ]
        return final_results

    def _retrieve_nodes_from_data(self, data, filters):
        """Extracts all the entities mentioned in the query."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        _tools = [EXTRACT_ENTITIES_TOOL]
        if self.llm_provider in ["azure_openai_structured", "openai_structured"]:
            _tools = [EXTRACT_ENTITIES_STRUCT_TOOL]
        search_results = self.llm.generate_response(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a smart assistant who understands entities and their types in a given text. "
                               f"If user message contains self reference such as 'I', 'me', 'my' etc. "
                               f"then use {filters['user_id']} as the source entity. Extract all the entities from"
                               f" the text. ***DO NOT*** answer the question itself if the given text is a question.",
                },
                {"role": "user", "content": data},
            ],
            tools=_tools,
        )

        entity_type_map = {}

        try:
            for tool_call in search_results["tool_calls"]:
                if tool_call["name"] != "extract_entities":
                    continue
                for item in tool_call["arguments"]["entities"]:
                    entity_type_map[item["entity"]] = item["entity_type"]
        except Exception as e:
            logger.exception(
                f"Error in search tool: {e}, llm_provider={self.llm_provider}, search_results={search_results}"
            )

        entity_type_map = {k.lower().replace(" ", "_"): v.lower().replace(" ", "_") for k, v in entity_type_map.items()}
        logger.debug(f"Entity type map: {entity_type_map}\n search_results={search_results}")
        return entity_type_map

    def _establish_nodes_relations_from_data(self, data, filters, entity_type_map):
        """
        Establish relations among the extracted nodes.
        return List[Dict] stored `source` `destination` `relationship`
        """
        # Compose user identification string for prompt
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        user_identity = f"user:{filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f",agent:{filters['agent_id']}"

        if self.config.graph_store.custom_prompt:
            system_content = EXTRACT_RELATIONS_PROMPT.replace("USER_ID", user_identity)
            # Add the custom prompt line if configured
            system_content = system_content.replace(
                "CUSTOM_PROMPT", f"4. {self.config.graph_store.custom_prompt}"
            )
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": data},
            ]
        else:
            system_content = EXTRACT_RELATIONS_PROMPT.replace("USER_ID", user_identity)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"List of entities: {list(entity_type_map.keys())}. \n\nText: {data}"},
            ]

        _tools = [RELATIONS_TOOL]
        if self.llm_provider in ["azure_openai_structured", "openai_structured"]:
            _tools = [RELATIONS_STRUCT_TOOL]

        extracted_entities = self.llm.generate_response(
            messages=messages,
            tools=_tools,
        )

        entities = []
        if extracted_entities["tool_calls"]:
            entities = extracted_entities["tool_calls"][0]["arguments"]["entities"]

        entities = self._remove_spaces_from_entities(entities)
        logger.debug(f"Extracted entities: {entities}")
        return entities

    def _search_graph_db(self, node_list, filters, limit=100):
        """Search similar nodes using vector similarity and retrieve their relations."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        # If vector search is disabled, fall back to traditional graph search
        if not self.enable_vector_search:
            return self._search_graph_db_traditional(node_list, filters, limit)
        
        result_relations = []
        
        # Use vector search for each node to find similar entities
        for node in node_list:
            try:
                # Generate embedding for the node
                node_embedding = self.embedding_model.embed(node)
                
                # Search for similar entities in vector store
                vector_filters = {"user_id": filters["user_id"], "node_type": "entity"}
                if filters.get("agent_id"):
                    vector_filters["agent_id"] = filters["agent_id"]
                
                search_results = self.vector_store.search(
                    query="",  # Using vectors directly
                    vectors=node_embedding,
                    limit=limit,
                    filters=vector_filters
                )
                
                # For each similar entity found, get its relationships from Gremlin
                for result in search_results:
                    if result.score >= self.similarity_threshold:
                        entity_name = result.payload.get("entity_name")
                        if entity_name:
                            # Query Gremlin for relationships involving this entity
                            relations = self._get_entity_relations(entity_name, filters, limit)
                            result_relations.extend(relations)
                            
            except Exception as e:
                logger.warning(f"Vector search failed for node '{node}': {e}")
                continue
        
        return result_relations
    
    def _search_graph_db_traditional(self, node_list, filters, limit=100):
        """Traditional graph search without vector similarity."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        result_relations = []
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Search for exact matches and relationships for each node
        for node in node_list:
            try:
                # Build query to find nodes with exact name match
                query = f"g.V().hasLabel(nodeLabel).has('name', nodeName).has('user_id', user_id)"
                if agent_id:
                    query += ".has('agent_id', agent_id)"
                
                query_params = {
                    'nodeLabel': self.node_label,
                    'nodeName': node,
                    'user_id': user_id
                }
                if agent_id:
                    query_params['agent_id'] = agent_id
                
                # Execute query to find matching nodes
                matching_nodes = self.graph.submit(query, query_params).all().result()
                
                # For each matching node, get its relationships
                for graph_node in matching_nodes:
                    node_id = graph_node.id if hasattr(graph_node, 'id') else str(graph_node)
                    relations = self._get_entity_relations_by_id(node_id, filters, limit)
                    result_relations.extend(relations)
                    
            except Exception as e:
                logger.warning(f"Traditional graph search failed for node '{node}': {e}")
                continue
        
        return result_relations
    
    def _get_entity_relations_by_id(self, node_id, filters, limit=100):
        """Get all relationships for a specific entity by node ID from Gremlin graph."""
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Query for outgoing relationships
        outgoing_query = f"g.V(nodeId).has('user_id', user_id)"
        if agent_id:
            outgoing_query += ".has('agent_id', agent_id)"
        outgoing_query += (
            ".as('source')"
            ".outE().as('relation')"
            ".inV().has('user_id', user_id)"
        )
        if agent_id:
            outgoing_query += ".has('agent_id', agent_id)"
        outgoing_query += (
            ".as('destination')"
            ".select('source', 'relation', 'destination')"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".by(project('label', 'id').by(label).by(id))"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".limit(limit)"
        )
        
        # Query for incoming relationships  
        incoming_query = f"g.V(nodeId).has('user_id', user_id)"
        if agent_id:
            incoming_query += ".has('agent_id', agent_id)"
        incoming_query += (
            ".as('destination')"
            ".inE().as('relation')"
            ".outV().has('user_id', user_id)"
        )
        if agent_id:
            incoming_query += ".has('agent_id', agent_id)"
        incoming_query += (
            ".as('source')"
            ".select('source', 'relation', 'destination')"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".by(project('label', 'id').by(label).by(id))"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".limit(limit)"
        )
        
        query_params = {
            'nodeId': node_id,
            'user_id': user_id,
            'limit': limit
        }
        if agent_id:
            query_params['agent_id'] = agent_id
        
        try:
            outgoing_results = self.graph.submit(outgoing_query, query_params).all().result()
            incoming_results = self.graph.submit(incoming_query, query_params).all().result()
            
            all_results = []
            all_results.extend(outgoing_results)
            all_results.extend(incoming_results)
            
            # Process and deduplicate results
            unique_results = set()
            processed_relations = []
            
            for r in all_results:
                source = r['source']
                relation = r['relation']
                destination = r['destination']
                
                result_tuple = (
                    source.get('name'),
                    source.get('id'),
                    relation.get('label'),
                    relation.get('id'),
                    destination.get('name'),
                    destination.get('id')
                )
                
                if result_tuple not in unique_results:
                    unique_results.add(result_tuple)
                    processed_relations.append({
                        'source': result_tuple[0],
                        'source_id': result_tuple[1],
                        'relationship': result_tuple[2],
                        'relation_id': result_tuple[3],
                        'destination': result_tuple[4],
                        'destination_id': result_tuple[5]
                    })
            
            return processed_relations
            
        except Exception as e:
            logger.error(f"Failed to get relations for node ID '{node_id}': {e}")
            return []
    
    def _get_entity_relations(self, entity_name, filters, limit=100):
        """Get all relationships for a specific entity from Gremlin graph."""
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        base_query = f"g.V().hasLabel(nodeLabel).has('name', entityName).has('user_id', user_id)"
        if agent_id:
            base_query += ".has('agent_id', agent_id)"
        
        # Query for outgoing relationships
        outgoing_query = (
            f"{base_query}"
            ".as('source')"
            ".outE().as('relation')"
            ".inV().has('user_id', user_id)"
        )
        if agent_id:
            outgoing_query += ".has('agent_id', agent_id)"
        outgoing_query += (
            ".as('destination')"
            ".select('source', 'relation', 'destination')"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".by(project('label', 'id').by(label).by(id))"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".limit(limit)"
        )
        
        # Query for incoming relationships  
        incoming_query = (
            f"{base_query}"
            ".as('destination')"
            ".inE().as('relation')"
            ".outV().has('user_id', user_id)"
        )
        if agent_id:
            incoming_query += ".has('agent_id', agent_id)"
        incoming_query += (
            ".as('source')"
            ".select('source', 'relation', 'destination')"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".by(project('label', 'id').by(label).by(id))"
            ".by(project('id', 'name').by(id).by(values('name')))"
            ".limit(limit)"
        )
        
        query_params = {
            'nodeLabel': self.node_label,
            'entityName': entity_name,
            'user_id': user_id,
            'limit': limit
        }
        if agent_id:
            query_params['agent_id'] = agent_id
        
        try:
            outgoing_results = self.graph.submit(outgoing_query, query_params).all().result()
            incoming_results = self.graph.submit(incoming_query, query_params).all().result()
            
            all_results = []
            all_results.extend(outgoing_results)
            all_results.extend(incoming_results)
            
            # Process and deduplicate results
            unique_results = set()
            processed_relations = []
            
            for r in all_results:
                source = r['source']
                relation = r['relation']
                destination = r['destination']
                
                result_tuple = (
                    source.get('name'),
                    source.get('id'),
                    relation.get('label'),
                    relation.get('id'),
                    destination.get('name'),
                    destination.get('id')
                )
                
                if result_tuple not in unique_results:
                    unique_results.add(result_tuple)
                    processed_relations.append({
                        'source': result_tuple[0],
                        'source_id': result_tuple[1],
                        'relationship': result_tuple[2],
                        'relation_id': result_tuple[3],
                        'destination': result_tuple[4],
                        'destination_id': result_tuple[5]
                    })
            
            return processed_relations
            
        except Exception as e:
            logger.error(f"Failed to get relations for entity '{entity_name}': {e}")
            return []

    def _get_delete_entities_from_search_output(self, search_output, data, filters):
        """Get the entities to be deleted from the search output."""
        search_output_string = format_entities(search_output)

        # Compose user identification string for prompt
        user_identity = f"user_id: {filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f", agent_id: {filters['agent_id']}"

        system_prompt, user_prompt = get_delete_messages(search_output_string, data, user_identity)

        _tools = [DELETE_MEMORY_TOOL_GRAPH]
        if self.llm_provider in ["azure_openai_structured", "openai_structured"]:
            _tools = [
                DELETE_MEMORY_STRUCT_TOOL_GRAPH,
            ]

        memory_updates = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tools=_tools,
        )

        to_be_deleted = []
        for item in memory_updates.get("tool_calls", []):
            if item.get("name") == "delete_graph_memory":
                to_be_deleted.append(item.get("arguments"))
        # Clean entities formatting
        to_be_deleted = self._remove_spaces_from_entities(to_be_deleted)
        logger.debug(f"Deleted relationships: {to_be_deleted}")
        return to_be_deleted

    def _delete_entities(self, to_be_deleted, filters):
        """Delete the entities from the graph."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        results = []

        for item in to_be_deleted:
            source = item["source"]
            destination = item["destination"]
            relationship = item["relationship"]

            params = {
                'node_label': self.node_label,
                'source_name': source,
                'dest_name': destination,
                'user_id': user_id,
                'relationship': relationship
            }
            if agent_id:
                params['agent_id'] = agent_id

            check_relation_query = (
                f"g.V().hasLabel(node_label)"
                f".has('name', source_name)"
                f".has('user_id', user_id)"
            )
            if agent_id:
                check_relation_query += f".has('agent_id', agent_id)"
            check_relation_query += (
                f".outE(relationship)"
                f".where(inV().has('name', dest_name)"
                f".has('user_id', user_id)"
            )
            if agent_id:
                check_relation_query += f".has('agent_id', agent_id)"
            check_relation_query += (
                f")"
                f".project('source', 'target', 'relationship')"
                f".by(outV().values('name'))"
                f".by(inV().values('name'))"
                f".by(label())"
            )

            result = self.graph.submit(check_relation_query, params).all().result()

            # only when you find it that you can delete the edge and vertex.
            if result:
                results.extend(result)
                delete_edge_query = (
                    f"g.V().hasLabel(node_label)"
                    f".has('name', source_name)"
                    f".has('user_id', user_id)"
                )
                if agent_id:
                    delete_edge_query += f".has('agent_id', agent_id)"
                delete_edge_query += (
                    f".outE(relationship)"
                    f".where(inV().has('name', dest_name)"
                    f".has('user_id', user_id)"
                )
                if agent_id:
                    delete_edge_query += f".has('agent_id', agent_id)"
                delete_edge_query += f").drop()"
                self.graph.submit(delete_edge_query, params).all().result()

                source_query = (
                    f"g.V().has('name', source_name).has('user_id', user_id)"
                    f".choose(__.not(bothE()),"
                    f"__.drop(),"
                    f"__.property('mentions', __.values('mentions').math('_ - 1')))"
                )

                dest_query = (
                    f"g.V().has('name', dest_name).has('user_id', user_id)"
                    f".choose(__.not(bothE()),"
                    f"__.drop(),"
                    f"__.property('mentions', __.values('mentions').math('_ - 1')))"
                )

                self.graph.submit_async(source_query, params).result()
                self.graph.submit_async(dest_query, params).result()
                
                # Delete corresponding embeddings from vector store (only if enabled)
                if self.enable_vector_search:
                    self._delete_entity_embedding(source, filters)
                    self._delete_entity_embedding(destination, filters)
                    self._refresh_vector_store()
                
        return results

    def _add_entities(self, to_be_added, filters, entity_type_map):
        """Add the new entities to the graph. Merge the nodes if they already exist."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id", None)
        results = []

        for item in to_be_added:
            # entities
            source = item["source"]
            destination = item["destination"]
            relationship = item["relationship"]

            # types
            source_type = entity_type_map.get(source)
            source_type = self.node_label if self.node_label else source_type
            destination_type = entity_type_map.get(destination)
            destination_type = self.node_label if self.node_label else destination_type

            # If vector search is enabled, generate embeddings and search for similar nodes
            if self.enable_vector_search:
                # Generate embeddings
                source_embedding = self.embedding_model.embed(source)
                dest_embedding = self.embedding_model.embed(destination)

                # Search for existing similar nodes using vector similarity
                source_node_search_result = self._search_source_node(source_embedding, filters, threshold=0.9)
                destination_node_search_result = self._search_destination_node(dest_embedding, filters, threshold=0.9)
            else:
                # When vector search is disabled, skip similarity search
                source_embedding = None
                dest_embedding = None
                source_node_search_result = []
                destination_node_search_result = []

            # Prepare agent_id for node creation
            agent_id_property = f".property('agent_id', '{agent_id}')" if agent_id else ''

            # Handle different scenarios based on search results
            if not destination_node_search_result and source_node_search_result:
                # Source exists, create destination
                source_id = source_node_search_result[0]["elementId(source_candidate)"]
                dest_id = f"{hashlib.md5((destination + user_id).encode()).hexdigest()}"
                
                # First try to create the destination vertex
                try:
                    create_dest_query = f"""
                    g.addV('{destination_type}')
                        .property(id, '{dest_id}')
                        .property('name', '{destination}')
                        .property('user_id', '{user_id}')
                        .property('created', {self._current_timestamp()})
                        {agent_id_property}
                        .property('mentions', 1)
                    """
                    with suppress_gremlin_errors():
                        result = self.graph.submit(create_dest_query)
                        # Force evaluation of the result
                        result.all().result()
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg or "GraphDB id exists" in error_msg:
                        # Vertex already exists, just update mentions
                        update_query = f"g.V('{dest_id}').property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))"
                        self.graph.submit(update_query).all().result()
                    else:
                        logger.error(f"Error creating destination vertex: {error_msg}")
                        raise e
                
                # Update source mentions and create edge
                query = f"""
                g.V('{source_id}').as('source')
                .property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))
                .V('{dest_id}').as('dest')
                .select('source')
                .coalesce(
                    __.outE('{relationship}').where(inV().as('dest')),
                    addE('{relationship}')
                        .to('dest')
                        .property('created', {self._current_timestamp()})
                )
                .project('source', 'destination')
                .by(outV().values('name'))
                .by(inV().values('name'))
                """

            elif destination_node_search_result and not source_node_search_result:
                # Destination exists, create source
                dest_id = destination_node_search_result[0]["elementId(destination_candidate)"]
                source_id = f"{hashlib.md5((source + user_id).encode()).hexdigest()}"
                
                # First try to create the source vertex
                try:
                    create_source_query = f"""
                    g.addV('{source_type}')
                        .property(id, '{source_id}')
                        .property('name', '{source}')
                        .property('user_id', '{user_id}')
                        .property('created', {self._current_timestamp()})
                        {agent_id_property}
                        .property('mentions', 1)
                    """
                    with suppress_gremlin_errors():
                        result = self.graph.submit(create_source_query)
                        # Force evaluation of the result
                        result.all().result()
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg or "GraphDB id exists" in error_msg:
                        # Vertex already exists, just update mentions
                        update_query = f"g.V('{source_id}').property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))"
                        self.graph.submit(update_query).all().result()
                    else:
                        logger.error(f"Error creating source vertex: {error_msg}")
                        raise e
                
                # Update destination mentions and create edge
                query = f"""
                g.V('{dest_id}').as('dest')
                .property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))
                .V('{source_id}').as('source')
                .select('source')
                .coalesce(
                    __.outE('{relationship}').where(inV().as('dest')),
                    addE('{relationship}')
                        .to('dest')
                        .property('created', {self._current_timestamp()})
                )
                .project('source', 'destination')
                .by(outV().values('name'))
                .by(inV().values('name'))
                """

            elif source_node_search_result and destination_node_search_result:
                # Both nodes exist, just create relationship
                source_id = source_node_search_result[0]["elementId(source_candidate)"]
                dest_id = destination_node_search_result[0]["elementId(destination_candidate)"]
                
                query = f"""
                g.V('{source_id}').as('source')
                .property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))
                .V('{dest_id}').as('dest')
                .property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))
                .select('source')
                .coalesce(
                    __.outE('{relationship}').where(inV().as('dest')),
                    addE('{relationship}')
                        .to('dest')
                        .property('created', {self._current_timestamp()})
                )
                .project('source', 'destination')
                .by(outV().values('name'))
                .by(inV().values('name'))
                """

            else:
                # Neither node exists, create both
                source_id = f"{hashlib.md5((source + user_id).encode()).hexdigest()}"
                dest_id = f"{hashlib.md5((destination + user_id).encode()).hexdigest()}"
                
                # Try to create source vertex
                try:
                    create_source_query = f"""
                    g.addV('{source_type}')
                        .property(id, '{source_id}')
                        .property('name', '{source}')
                        .property('user_id', '{user_id}')
                        .property('created', {self._current_timestamp()})
                        {agent_id_property}
                        .property('mentions', 1)
                    """
                    with suppress_gremlin_errors():
                        result = self.graph.submit(create_source_query)
                        # Force evaluation of the result
                        result.all().result()
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg or "GraphDB id exists" in error_msg:
                        # Vertex already exists, just update mentions
                        update_query = f"g.V('{source_id}').property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))"
                        self.graph.submit(update_query).all().result()
                    else:
                        logger.error(f"Error creating source vertex: {error_msg}")
                        raise e
                
                # Try to create destination vertex
                try:
                    create_dest_query = f"""
                    g.addV('{destination_type}')
                        .property(id, '{dest_id}')
                        .property('name', '{destination}')
                        .property('user_id', '{user_id}')
                        .property('created', {self._current_timestamp()})
                        {agent_id_property}
                        .property('mentions', 1)
                    """
                    with suppress_gremlin_errors():
                        result = self.graph.submit(create_dest_query)
                        # Force evaluation of the result
                        result.all().result()
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg or "GraphDB id exists" in error_msg:
                        # Vertex already exists, just update mentions
                        update_query = f"g.V('{dest_id}').property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))"
                        self.graph.submit(update_query).all().result()
                    else:
                        logger.error(f"Error creating destination vertex: {error_msg}")
                        raise e
                
                # Create edge
                query = f"""
                g.V('{source_id}').as('source')
                .V('{dest_id}').as('dest')
                .select('source')
                .coalesce(
                    __.outE('{relationship}').where(inV().as('dest')),
                    addE('{relationship}')
                        .to('dest')
                        .property('created', {self._current_timestamp()})
                )
                .project('source', 'destination')
                .by(outV().values('name'))
                .by(inV().values('name'))
                """

            # Execute the graph query
            try:
                result = self.graph.submit(query).all().result()
                if result:
                    results.append({
                        "source": result[0]['source'],
                        "relationship": relationship,
                        "target": result[0]['destination']
                    })
                    
                    # Store embeddings in vector store after successful graph operations (only if enabled)
                    if self.enable_vector_search:
                        self._store_entity_embedding(source, source_id, source_embedding, filters, source_type)
                        self._store_entity_embedding(destination, dest_id, dest_embedding, filters, destination_type)
                        self._refresh_vector_store()
            except Exception as e:
                logger.error(f"Failed to execute graph query for {source}-{relationship}-{destination}: {e}")
                continue

        return results

    def _store_entity_embedding(self, entity_name, gremlin_node_id, embedding, filters, entity_type):
        """Store entity embedding in vector store with metadata linking to Gremlin node."""
        try:
            # Check if this entity embedding already exists to avoid duplicates
            vector_id = f"entity_{gremlin_node_id}"
            
            # Try to find if this vector already exists
            try:
                existing_vector = self.vector_store.get(vector_id)
                if existing_vector:
                    logger.debug(f"Entity embedding for '{entity_name}' already exists, skipping storage")
                    return
            except:
                # If get method fails or doesn't exist, proceed with insertion
                pass
            
            # Prepare metadata for vector store
            metadata = {
                "entity_name": entity_name,
                "gremlin_node_id": gremlin_node_id,
                "user_id": filters["user_id"],
                "node_type": "entity",
                "entity_type": entity_type,
                "created": self._current_timestamp()
            }
            
            # Add agent_id if present
            if filters.get("agent_id"):
                metadata["agent_id"] = filters["agent_id"]
            
            # Store in vector database
            self.vector_store.insert(
                vectors=[embedding],
                payloads=[metadata],
                ids=[vector_id]
            )
            logger.debug(f"Stored embedding for entity '{entity_name}' with vector ID '{vector_id}'")
            
        except Exception as e:
            logger.warning(f"Failed to store embedding for entity '{entity_name}': {e}")

    def _delete_entity_embedding(self, entity_name, filters):
        """Delete entity embedding from vector store."""
        try:
            # Build filter for vector store search
            vector_filters = {
                "entity_name": entity_name,
                "user_id": filters["user_id"],
                "node_type": "entity"
            }
            if filters.get("agent_id"):
                vector_filters["agent_id"] = filters["agent_id"]
            
            # Search for the entity in vector store
            search_results = self.vector_store.search(
                query="",  # Using filters only
                vectors=[],
                limit=10,  # Should be unique, but allow for some flexibility
                filters=vector_filters
            )
            
            # Delete matching entities from vector store
            for result in search_results:
                if result.id:
                    try:
                        self.vector_store.delete(result.id)
                        logger.debug(f"Deleted embedding for entity '{entity_name}' with vector ID '{result.id}'")
                    except Exception as e:
                        logger.warning(f"Failed to delete vector {result.id}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to delete embedding for entity '{entity_name}': {e}")

    def _refresh_vector_store(self):
        if self.enable_vector_search and hasattr(self.vector_store, 'refresh') and callable(self.vector_store.refresh):
            self.vector_store.refresh()

    def _remove_spaces_from_entities(self, entity_list):
        for item in entity_list:
            item["source"] = item["source"].lower().replace(" ", "_")
            item["relationship"] = item["relationship"].lower().replace(" ", "_")
            item["destination"] = item["destination"].lower().replace(" ", "_")
        return entity_list

    def _search_source_node(self, source_embedding, filters, threshold=0.9):
        """Search for source nodes using vector store similarity."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        try:
            # Build filter for vector store search
            vector_filters = {
                "user_id": filters["user_id"],
                "node_type": "entity"
            }
            if filters.get("agent_id"):
                vector_filters["agent_id"] = filters["agent_id"]
            
            # Search for similar entities in vector store
            search_results = self.vector_store.search(
                query="",  # Using vectors directly
                vectors=source_embedding,
                limit=5,  # Get top 5 candidates
                filters=vector_filters
            )
            
            # Find best match above threshold
            for result in search_results:
                if result.score >= threshold:
                    gremlin_node_id = result.payload.get("gremlin_node_id")
                    if gremlin_node_id:
                        return [{"elementId(source_candidate)": gremlin_node_id}]
            
            return []
            
        except Exception as e:
            logger.warning(f"Vector search failed for source node: {e}")
            return []

    def _search_destination_node(self, destination_embedding, filters, threshold=0.9):
        """Search for destination nodes using vector store similarity."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        try:
            # Build filter for vector store search
            vector_filters = {
                "user_id": filters["user_id"],
                "node_type": "entity"
            }
            if filters.get("agent_id"):
                vector_filters["agent_id"] = filters["agent_id"]
            
            # Search for similar entities in vector store
            search_results = self.vector_store.search(
                query="",  # Using vectors directly
                vectors=destination_embedding,
                limit=5,  # Get top 5 candidates
                filters=vector_filters
            )
            
            # Find best match above threshold
            for result in search_results:
                if result.score >= threshold:
                    gremlin_node_id = result.payload.get("gremlin_node_id")
                    if gremlin_node_id:
                        return [{"elementId(destination_candidate)": gremlin_node_id}]
            
            return []
            
        except Exception as e:
            logger.warning(f"Vector search failed for destination node: {e}")
            return []

    def _current_timestamp(self):
        return int(time.time())

    def drop_all_entities(self):
        self.graph.submit('g.E().drop()').all().result()
        self.graph.submit('g.V().drop()').all().result()
        if self.enable_vector_search:
            self.vector_store.reset()

