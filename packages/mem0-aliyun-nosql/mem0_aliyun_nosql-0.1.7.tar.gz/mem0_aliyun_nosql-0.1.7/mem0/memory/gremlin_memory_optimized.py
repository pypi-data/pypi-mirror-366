import hashlib
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple

from mem0.memory.utils import format_entities

try:
    from gremlin_python.driver import client, serializer
    from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
    from gremlin_python.process.graph_traversal import __
    from gremlin_python.process.anonymous_traversal import traversal
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


class OptimizedMemoryGraph:
    """Optimized version of MemoryGraph with performance improvements."""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize Gremlin client with connection pooling
        self.graph = client.Client(
            url=config.graph_store.config.url,
            traversal_source=config.graph_store.config.traversal_source,
            username=config.graph_store.config.username,
            password=config.graph_store.config.password,
            message_serializer=config.graph_store.config.message_serializer
            if config.graph_store.config.message_serializer else serializer.GraphBinarySerializersV1(),
            pool_size=getattr(config.graph_store.config, 'pool_size', 10),  # Connection pool
            max_workers=getattr(config.graph_store.config, 'max_workers', 5)
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
        
        # Initialize vector store and embedding model
        if self.enable_vector_search:
            self.embedding_model = EmbedderFactory.create(
                self.config.embedder.provider, self.config.embedder.config, self.config.vector_store.config
            )
            
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
        
        # Performance optimization: caches and thread pool
        self._embedding_cache = {}  # Cache for embeddings
        self._entity_cache = {}     # Cache for entity lookups
        self._llm_cache = {}        # Cache for LLM responses
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._batch_refresh_pending = False  # For lazy vector store refresh
        
        # Combined tool for entity and relation extraction
        self.COMBINED_EXTRACTION_TOOL = {
            "type": "function",
            "function": {
                "name": "extract_entities_and_relations",
                "description": "Extract all entities and their relationships from the text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "entity": {"type": "string"},
                                    "entity_type": {"type": "string"}
                                },
                                "required": ["entity", "entity_type"]
                            }
                        },
                        "relations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source": {"type": "string"},
                                    "relationship": {"type": "string"},
                                    "destination": {"type": "string"}
                                },
                                "required": ["source", "relationship", "destination"]
                            }
                        }
                    },
                    "required": ["entities", "relations"]
                }
            }
        }

    def add(self, data, filters):
        """Optimized add method with combined operations."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        # Combined entity and relation extraction (1 LLM call instead of 2)
        entity_type_map, relations = self._extract_entities_and_relations_combined(data, filters)
        
        # Batch search for existing nodes
        search_output = self._batch_search_graph_db(list(entity_type_map.keys()), filters)
        
        # Determine deletions
        to_be_deleted = self._get_delete_entities_from_search_output(search_output, data, filters)
        
        # Execute deletions and additions in parallel
        deleted_entities, added_entities = self._execute_graph_updates_parallel(
            to_be_deleted, relations, filters, entity_type_map
        )
        
        # Lazy refresh vector store
        self._schedule_vector_refresh()
        
        return {"deleted_entities": deleted_entities, "added_entities": added_entities}

    def search(self, query, filters, limit=100):
        """Optimized search with batched operations."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        # Extract entities from query
        entity_type_map = self._retrieve_nodes_from_data(query, filters)
        
        # Batch search with caching
        search_output = self._batch_search_graph_db(list(entity_type_map.keys()), filters, limit)
        
        if not search_output:
            return []
        
        # Rerank results
        search_outputs_sequence = [
            [item["source"], item["relationship"], item["destination"]] for item in search_output
        ]
        bm25 = BM25Okapi(search_outputs_sequence)
        
        tokenized_query = query.split(" ")
        reranked_results = bm25.get_top_n(tokenized_query, search_outputs_sequence, n=min(limit, 5))
        
        return [
            {"source": item[0], "relationship": item[1], "destination": item[2]}
            for item in reranked_results
        ]

    def _extract_entities_and_relations_combined(self, data: str, filters: dict) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
        """Extract entities and relations in a single LLM call."""
        # Check cache first
        cache_key = hashlib.md5(f"{data}:{filters.get('user_id')}".encode()).hexdigest()
        if cache_key in self._llm_cache:
            cached_result = self._llm_cache[cache_key]
            return cached_result["entities"], cached_result["relations"]
        
        user_identity = f"user:{filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f",agent:{filters['agent_id']}"
        
        system_prompt = f"""You are a smart assistant who extracts entities and relationships from text.
If user message contains self reference such as 'I', 'me', 'my' etc., use {user_identity} as the source entity.

Instructions:
1. Extract ALL entities mentioned in the text with their types.
2. Extract ALL relationships between the entities.
3. Use clear, descriptive relationship names in active voice.
4. If custom prompt is provided, follow it as well.
{f"4. {self.config.graph_store.custom_prompt}" if hasattr(self.config.graph_store, 'custom_prompt') and self.config.graph_store.custom_prompt else ""}"""

        tools = [self.COMBINED_EXTRACTION_TOOL]
        
        try:
            response = self.llm.generate_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": data}
                ],
                tools=tools
            )
            
            entity_type_map = {}
            relations = []
            
            for tool_call in response.get("tool_calls", []):
                if tool_call["name"] == "extract_entities_and_relations":
                    args = tool_call["arguments"]
                    
                    # Process entities
                    for entity in args.get("entities", []):
                        entity_name = entity["entity"].lower().replace(" ", "_")
                        entity_type = entity["entity_type"].lower().replace(" ", "_")
                        entity_type_map[entity_name] = entity_type
                    
                    # Process relations
                    relations = self._remove_spaces_from_entities(args.get("relations", []))
            
            # Cache the result
            self._llm_cache[cache_key] = {"entities": entity_type_map, "relations": relations}
            
            return entity_type_map, relations
            
        except Exception as e:
            logger.error(f"Combined extraction failed: {e}")
            # Fallback to separate extraction
            entity_type_map = self._retrieve_nodes_from_data(data, filters)
            relations = self._establish_nodes_relations_from_data(data, filters, entity_type_map)
            return entity_type_map, relations

    def _batch_search_graph_db(self, node_list: List[str], filters: dict, limit: int = 100) -> List[Dict]:
        """Batch search for multiple nodes in a single query."""
        if not node_list:
            return []
        
        # Check cache for already searched nodes
        cache_key = f"{':'.join(sorted(node_list))}:{filters['user_id']}"
        if cache_key in self._entity_cache:
            return self._entity_cache[cache_key]
        
        result_relations = []
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Batch query for all nodes at once
        try:
            # Build a query that searches for all nodes in one go
            query = f"""
            g.V().hasLabel(nodeLabel)
                 .has('user_id', user_id)
                 {f".has('agent_id', agent_id)" if agent_id else ""}
                 .has('name', within(nodeNames))
                 .as('node')
                 .project('node_id', 'node_name', 'outgoing', 'incoming')
                 .by(id)
                 .by(values('name'))
                 .by(
                    outE().as('out_rel')
                    .inV().has('user_id', user_id)
                    {f".has('agent_id', agent_id)" if agent_id else ""}
                    .as('out_dest')
                    .select('out_rel', 'out_dest')
                    .by(project('label', 'id').by(label).by(id))
                    .by(project('id', 'name').by(id).by(values('name')))
                    .fold()
                 )
                 .by(
                    inE().as('in_rel')
                    .outV().has('user_id', user_id)
                    {f".has('agent_id', agent_id)" if agent_id else ""}
                    .as('in_src')
                    .select('in_rel', 'in_src')
                    .by(project('label', 'id').by(label).by(id))
                    .by(project('id', 'name').by(id).by(values('name')))
                    .fold()
                 )
            """
            
            params = {
                'nodeLabel': self.node_label,
                'nodeNames': node_list,
                'user_id': user_id
            }
            if agent_id:
                params['agent_id'] = agent_id
            
            results = self.graph.submit(query, params).all().result()
            
            # Process results
            for result in results:
                node_name = result['node_name']
                
                # Process outgoing relationships
                for out_rel in result.get('outgoing', []):
                    result_relations.append({
                        'source': node_name,
                        'relationship': out_rel['out_rel']['label'],
                        'destination': out_rel['out_dest']['name']
                    })
                
                # Process incoming relationships
                for in_rel in result.get('incoming', []):
                    result_relations.append({
                        'source': in_rel['in_src']['name'],
                        'relationship': in_rel['in_rel']['label'],
                        'destination': node_name
                    })
            
            # Cache the results
            self._entity_cache[cache_key] = result_relations
            
            return result_relations
            
        except Exception as e:
            logger.error(f"Batch search failed: {e}")
            # Fallback to individual searches
            return self._search_graph_db_traditional(node_list, filters, limit)

    def _execute_graph_updates_parallel(self, to_be_deleted: List[Dict], to_be_added: List[Dict], 
                                       filters: dict, entity_type_map: Dict[str, str]) -> Tuple[List, List]:
        """Execute deletions and additions in parallel."""
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit deletion task
            delete_future = executor.submit(self._delete_entities, to_be_deleted, filters)
            
            # Submit addition task
            add_future = executor.submit(self._add_entities_batch, to_be_added, filters, entity_type_map)
            
            # Wait for both to complete
            deleted_entities = delete_future.result()
            added_entities = add_future.result()
        
        return deleted_entities, added_entities

    def _add_entities_batch(self, to_be_added: List[Dict], filters: dict, entity_type_map: Dict[str, str]) -> List[Dict]:
        """Batch add multiple entities and relationships."""
        if not to_be_added:
            return []
        
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        results = []
        
        # Group additions by operation type for batching
        new_entities = set()
        new_relationships = []
        
        for item in to_be_added:
            source = item["source"]
            destination = item["destination"]
            relationship = item["relationship"]
            
            new_entities.add(source)
            new_entities.add(destination)
            new_relationships.append((source, relationship, destination))
        
        try:
            # Batch create all entities first
            if new_entities:
                entity_creation_query = "g"
                entity_id_map = {}
                
                for entity in new_entities:
                    entity_id = hashlib.md5((entity + user_id).encode()).hexdigest()
                    entity_id_map[entity] = entity_id
                    entity_type = entity_type_map.get(entity, self.node_label)
                    
                    entity_creation_query += f"""
                    .coalesce(
                        V('{entity_id}'),
                        addV('{entity_type}')
                            .property(id, '{entity_id}')
                            .property('name', '{entity}')
                            .property('user_id', '{user_id}')
                            .property('created', {self._current_timestamp()})
                            {f".property('agent_id', '{agent_id}')" if agent_id else ""}
                    )
                    .property('mentions', coalesce(values('mentions'), constant(0)).math('_ + 1'))
                    .as('{entity}')
                    """
                
                # Execute batch entity creation
                self.graph.submit(entity_creation_query).all().result()
                
                # Generate embeddings in batch if vector search is enabled
                if self.enable_vector_search:
                    self._batch_store_embeddings(new_entities, entity_id_map, filters, entity_type_map)
            
            # Batch create relationships
            if new_relationships:
                for source, relationship, destination in new_relationships:
                    source_id = entity_id_map.get(source, hashlib.md5((source + user_id).encode()).hexdigest())
                    dest_id = entity_id_map.get(destination, hashlib.md5((destination + user_id).encode()).hexdigest())
                    
                    rel_query = f"""
                    g.V('{source_id}').as('src')
                     .V('{dest_id}').as('dst')
                     .coalesce(
                         select('src').outE('{relationship}').where(inV().as('dst')),
                         select('src').addE('{relationship}').to('dst')
                                     .property('created', {self._current_timestamp()})
                     )
                     .project('source', 'destination')
                     .by(outV().values('name'))
                     .by(inV().values('name'))
                    """
                    
                    result = self.graph.submit(rel_query).all().result()
                    if result:
                        results.append({
                            "source": source,
                            "relationship": relationship,
                            "target": destination
                        })
            
        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            # Fallback to individual additions
            return self._add_entities(to_be_added, filters, entity_type_map)
        
        return results

    def _batch_store_embeddings(self, entities: set, entity_id_map: Dict[str, str], 
                                filters: dict, entity_type_map: Dict[str, str]):
        """Batch store embeddings for multiple entities."""
        if not self.enable_vector_search:
            return
        
        try:
            # Generate embeddings for all entities in batch
            entity_list = list(entities)
            embeddings = []
            
            # Check cache and generate only missing embeddings
            entities_to_embed = []
            cached_embeddings = {}
            
            for entity in entity_list:
                cache_key = f"emb:{entity}"
                if cache_key in self._embedding_cache:
                    cached_embeddings[entity] = self._embedding_cache[cache_key]
                else:
                    entities_to_embed.append(entity)
            
            # Generate embeddings for uncached entities
            if entities_to_embed:
                if hasattr(self.embedding_model, 'embed_batch'):
                    # Use batch embedding if available
                    new_embeddings = self.embedding_model.embed_batch(entities_to_embed)
                else:
                    # Fallback to individual embedding
                    new_embeddings = [self.embedding_model.embed(entity) for entity in entities_to_embed]
                
                # Cache new embeddings
                for entity, embedding in zip(entities_to_embed, new_embeddings):
                    cache_key = f"emb:{entity}"
                    self._embedding_cache[cache_key] = embedding
                    cached_embeddings[entity] = embedding
            
            # Prepare batch insert for vector store
            vectors = []
            payloads = []
            ids = []
            
            for entity in entity_list:
                entity_id = entity_id_map[entity]
                vector_id = f"entity_{entity_id}"
                
                # Skip if already exists
                try:
                    if hasattr(self.vector_store, 'exists') and self.vector_store.exists(vector_id):
                        continue
                except:
                    pass
                
                vectors.append(cached_embeddings[entity])
                payloads.append({
                    "entity_name": entity,
                    "gremlin_node_id": entity_id,
                    "user_id": filters["user_id"],
                    "node_type": "entity",
                    "entity_type": entity_type_map.get(entity, "unknown"),
                    "created": self._current_timestamp(),
                    **({'agent_id': filters['agent_id']} if filters.get('agent_id') else {})
                })
                ids.append(vector_id)
            
            # Batch insert into vector store
            if vectors:
                self.vector_store.insert(vectors=vectors, payloads=payloads, ids=ids)
                logger.debug(f"Batch stored {len(vectors)} embeddings")
                
        except Exception as e:
            logger.error(f"Batch embedding storage failed: {e}")

    def _schedule_vector_refresh(self):
        """Schedule a lazy refresh of the vector store."""
        if self.enable_vector_search and not self._batch_refresh_pending:
            self._batch_refresh_pending = True
            # Schedule refresh after a short delay using threading
            import threading
            timer = threading.Timer(0.5, self._delayed_vector_refresh_sync)
            timer.start()

    def _delayed_vector_refresh_sync(self):
        """Perform delayed vector store refresh synchronously."""
        if self._batch_refresh_pending:
            self._refresh_vector_store()
            self._batch_refresh_pending = False

    def _current_timestamp(self):
        return int(time.time())

    def _refresh_vector_store(self):
        if self.enable_vector_search and hasattr(self.vector_store, 'refresh') and callable(self.vector_store.refresh):
            self.vector_store.refresh()

    def _remove_spaces_from_entities(self, entity_list):
        for item in entity_list:
            item["source"] = item["source"].lower().replace(" ", "_")
            item["relationship"] = item["relationship"].lower().replace(" ", "_")
            item["destination"] = item["destination"].lower().replace(" ", "_")
        return entity_list

    # Keep original methods for compatibility but optimize them
    def _retrieve_nodes_from_data(self, data, filters):
        """Backwards compatible method that uses the optimized extraction."""
        entity_type_map, _ = self._extract_entities_and_relations_combined(data, filters)
        return entity_type_map

    def _establish_nodes_relations_from_data(self, data, filters, entity_type_map):
        """Backwards compatible method that uses the optimized extraction."""
        _, relations = self._extract_entities_and_relations_combined(data, filters)
        return relations

    def _search_graph_db_traditional(self, node_list, filters, limit=100):
        """Fallback traditional search method."""
        # Use the batch search instead
        return self._batch_search_graph_db(node_list, filters, limit)

    def _delete_entities(self, to_be_deleted, filters):
        """Delete entities with proper cleanup."""
        if not to_be_deleted:
            return []
        
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        results = []
        
        try:
            # Batch delete relationships
            for item in to_be_deleted:
                source = item["source"]
                destination = item["destination"]
                relationship = item["relationship"]
                
                # Check and delete relationship
                delete_query = f"""
                g.V().hasLabel(nodeLabel)
                     .has('name', source)
                     .has('user_id', user_id)
                     {f".has('agent_id', agent_id)" if agent_id else ""}
                     .outE(relationship)
                     .where(inV().has('name', destination)
                                 .has('user_id', user_id)
                                 {f".has('agent_id', agent_id)" if agent_id else ""})
                     .sideEffect(drop())
                     .project('source', 'target', 'relationship')
                     .by(outV().values('name'))
                     .by(inV().values('name'))
                     .by(constant(relationship))
                """
                
                params = {
                    'nodeLabel': self.node_label,
                    'source': source,
                    'destination': destination,
                    'relationship': relationship,
                    'user_id': user_id
                }
                if agent_id:
                    params['agent_id'] = agent_id
                
                result = self.graph.submit(delete_query, params).all().result()
                if result:
                    results.extend(result)
                    
                    # Clean up orphaned nodes
                    cleanup_query = f"""
                    g.V().hasLabel(nodeLabel)
                         .has('user_id', user_id)
                         {f".has('agent_id', agent_id)" if agent_id else ""}
                         .has('name', within([source, destination]))
                         .where(not(bothE()))
                         .drop()
                    """
                    
                    self.graph.submit(cleanup_query, params)
                    
                    # Clean up vector embeddings if enabled
                    if self.enable_vector_search:
                        self._delete_entity_embedding(source, filters)
                        self._delete_entity_embedding(destination, filters)
            
        except Exception as e:
            logger.error(f"Batch delete failed: {e}")
        
        return results

    def _add_entities(self, to_be_added, filters, entity_type_map):
        """Fallback to original add method for compatibility."""
        # Use the batch method
        return self._add_entities_batch(to_be_added, filters, entity_type_map)

    def _get_delete_entities_from_search_output(self, search_output, data, filters):
        """Determine entities to delete based on search output."""
        if not search_output:
            return []
        
        search_output_string = format_entities(search_output)
        
        # Check cache
        cache_key = hashlib.md5(f"del:{search_output_string}:{data}".encode()).hexdigest()
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]
        
        user_identity = f"user_id: {filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f", agent_id: {filters['agent_id']}"
        
        system_prompt, user_prompt = get_delete_messages(search_output_string, data, user_identity)
        
        _tools = [DELETE_MEMORY_TOOL_GRAPH]
        if self.llm_provider in ["azure_openai_structured", "openai_structured"]:
            _tools = [DELETE_MEMORY_STRUCT_TOOL_GRAPH]
        
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
        
        to_be_deleted = self._remove_spaces_from_entities(to_be_deleted)
        
        # Cache result
        self._llm_cache[cache_key] = to_be_deleted
        
        return to_be_deleted

    def _delete_entity_embedding(self, entity_name, filters):
        """Delete entity embedding from vector store."""
        if not self.enable_vector_search:
            return
        
        try:
            # Remove from cache
            cache_key = f"emb:{entity_name}"
            if cache_key in self._embedding_cache:
                del self._embedding_cache[cache_key]
            
            # Search and delete from vector store
            vector_filters = {
                "entity_name": entity_name,
                "user_id": filters["user_id"],
                "node_type": "entity"
            }
            if filters.get("agent_id"):
                vector_filters["agent_id"] = filters["agent_id"]
            
            search_results = self.vector_store.search(
                query="",
                vectors=[],
                limit=10,
                filters=vector_filters
            )
            
            for result in search_results:
                if result.id:
                    try:
                        self.vector_store.delete(result.id)
                        logger.debug(f"Deleted embedding for entity '{entity_name}'")
                    except Exception as e:
                        logger.warning(f"Failed to delete vector {result.id}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to delete embedding for entity '{entity_name}': {e}")

    def delete_all(self, filters):
        """Delete all entities for a user with optimized cleanup."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Clear caches
        self._entity_cache.clear()
        self._llm_cache.clear()
        self._embedding_cache.clear()
        
        # Delete from Gremlin graph
        query = f"g.V().hasLabel('{self.node_label}').has('user_id', '{user_id}')"
        if agent_id:
            query += f".has('agent_id', '{agent_id}')"
        query += ".sideEffect(__.bothE().drop()).drop()"
        self.graph.submit(query)
        
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
        
        vector_filters = {"user_id": user_id, "node_type": "entity"}
        if agent_id:
            vector_filters["agent_id"] = agent_id
        
        try:
            # Batch delete all matching entities
            if hasattr(self.vector_store, 'delete_by_filter'):
                self.vector_store.delete_by_filter(vector_filters)
            else:
                # Fallback to search and delete
                search_results = self.vector_store.search(
                    query="*",
                    vectors=[],
                    limit=10000,
                    filters=vector_filters
                )
                
                ids_to_delete = [r.id for r in search_results if r.id]
                if ids_to_delete and hasattr(self.vector_store, 'delete_batch'):
                    self.vector_store.delete_batch(ids_to_delete)
                else:
                    for vector_id in ids_to_delete:
                        try:
                            self.vector_store.delete(vector_id)
                        except Exception as e:
                            logger.warning(f"Failed to delete vector {vector_id}: {e}")
                            
        except Exception as e:
            logger.warning(f"Failed to cleanup vector store: {e}")

    def get_all(self, filters, limit=100):
        """Get all relationships with optimized query."""
        if filters is None or "user_id" not in filters:
            raise ValueError("filters can't be None and it must contain 'user_id'")
        
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id")
        
        # Optimized query that gets all relationships in one go
        query = f"""
        g.V().hasLabel(nodeLabel)
             .has('user_id', user_id)
             {f".has('agent_id', agent_id)" if agent_id else ""}
             .outE()
             .where(inV().has('user_id', user_id)
                        {f".has('agent_id', agent_id)" if agent_id else ""})
             .project('source', 'relationship', 'target')
             .by(outV().values('name'))
             .by(label)
             .by(inV().values('name'))
             .limit(limit)
        """
        
        params = {
            'nodeLabel': self.node_label,
            'user_id': user_id,
            'limit': limit
        }
        if agent_id:
            params['agent_id'] = agent_id
        
        results = self.graph.submit(query, params).all().result()
        
        return [
            {
                "source": result["source"],
                "relationship": result["relationship"],
                "target": result["target"]
            }
            for result in results
        ]

    def drop_all_entities(self):
        """Drop all entities and clear caches."""
        self.graph.submit('g.E().drop()').all().result()
        self.graph.submit('g.V().drop()').all().result()
        
        # Clear all caches
        self._entity_cache.clear()
        self._llm_cache.clear()
        self._embedding_cache.clear()
        
        if self.enable_vector_search:
            self.vector_store.reset()

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_thread_pool'):
            self._thread_pool.shutdown(wait=False)