import logging
import mysql.connector
import threading
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MySQLManager:
    def __init__(self, db_url: str):
        """
        Initialize MySQL manager with database URL
        Args:
            db_url: mysql://user:password@host:port/database
        """
        # Parse database URL
        self._parse_url(db_url)
        self.connection = None
        self._lock = threading.Lock()
        self._connect()
        self._create_history_table()

    def _parse_url(self, db_url: str) -> None:
        """Parse database URL and set connection parameters"""
        try:
            parsed = urlparse(db_url)

            # Parse authentication info
            if '@' in parsed.netloc:
                userpass = parsed.netloc.split('@')[0]
                hostport = parsed.netloc.split('@')[1]
            else:
                userpass = ''
                hostport = parsed.netloc
            
            if ':' in userpass:
                self.user = userpass.split(':')[0]
                self.password = userpass.split(':')[1]
            else:
                self.user = userpass
                self.password = ''

            # Parse host and port
            if ':' in hostport:
                self.host = hostport.split(':')[0]
                self.port = int(hostport.split(':')[1])
            else:
                self.host = hostport
                self.port = 3306

            # Get database name
            self.database = parsed.path.lstrip('/')

            if not all([self.host, self.user, self.database]):
                raise ValueError("Missing required connection parameters")

        except Exception as e:
            raise ValueError(f"Invalid database URL format: {e}")

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            # Create the database if it doesn't exist
            logger.info(f"Successfully connected to MySQL database {self.database}")
        except mysql.connector.Error as err:
            logger.error(f"Failed to connect to MySQL: {err}")
            raise

    def _create_history_table(self) -> None:
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id           VARCHAR(256),
                        memory_id    VARCHAR(256),
                        old_memory   VARCHAR,
                        new_memory   VARCHAR,
                        event        VARCHAR(255),
                        created_at   VARCHAR(255),
                        updated_at   VARCHAR(255),
                        is_deleted   BOOLEAN,
                        actor_id     VARCHAR(255),
                        role         VARCHAR(255),
                        PRIMARY KEY (id)
                    )
                """
                )
                self.connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Failed to create history table: {err}")
                self.connection.rollback()
                raise

    def add_history(
            self,
            memory_id: str,
            old_memory: Optional[str],
            new_memory: Optional[str],
            event: str,
            *,
            created_at: Optional[str] = None,
            updated_at: Optional[str] = None,
            is_deleted: int = 0,
            actor_id: Optional[str] = None,
            role: Optional[str] = None,
    ) -> None:
        with self._lock:
            try:
                cursor = self.connection.cursor()
                query = """
                    INSERT INTO history (
                        id, memory_id, old_memory, new_memory, event,
                        created_at, updated_at, is_deleted, actor_id, role
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    str(uuid.uuid4()),
                    memory_id,
                    old_memory,
                    new_memory,
                    event,
                    created_at,
                    updated_at,
                    bool(is_deleted),
                    actor_id,
                    role,
                )
                cursor.execute(query, values)
                self.connection.commit()
            except mysql.connector.Error as err:
                logger.error(f"Failed to add history record: {err}")
                self.connection.rollback()
                raise

    def get_history(self, memory_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            try:
                cursor = self.connection.cursor(dictionary=True)
                query = """
                    SELECT id, memory_id, old_memory, new_memory, event,
                           created_at, updated_at, is_deleted, actor_id, role
                    FROM history
                    WHERE memory_id = %s
                    ORDER BY created_at ASC, updated_at ASC
                """
                cursor.execute(query, (memory_id,))
                rows = cursor.fetchall()
                for row in rows:
                    row["is_deleted"] = bool(row["is_deleted"])
                return rows
            except mysql.connector.Error as err:
                logger.error(f"Failed to get history: {err}")
                return []

    def reset(self) -> None:
        """Drop and recreate the history table."""
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute("DROP TABLE IF EXISTS history")
                self.connection.commit()
                self._create_history_table()
            except mysql.connector.Error as err:
                logger.error(f"Failed to reset history table: {err}")
                self.connection.rollback()
                raise

    def close(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
