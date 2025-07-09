import psycopg2
from psycopg2 import pool
from typing import Dict, Any
import logging
from contextlib import contextmanager
from .exceptions import ConnectionError

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, max_connections: int = 10):
        self.pools: Dict[str, pool.SimpleConnectionPool] = {}
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        self.max_connections = max_connections
    
    def connect(self, name: str, host: str, port: int, database: str, username: str, password: str):
        try:
            conn_pool = pool.SimpleConnectionPool(
                1, self.max_connections,
                host=host, port=port, database=database, 
                user=username, password=password
            )
            self.pools[name] = conn_pool
            self.connection_info[name] = {"host": host, "database": database}
            logger.info(f"Connected to {database} as {name}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(f"Failed to connect: {e}")
    
    @contextmanager
    def get_connection(self, name: str):
        if name not in self.pools:
            raise ConnectionError(f"Connection {name} not found")
        conn = None
        try:
            conn = self.pools[name].getconn()
            yield conn
        finally:
            if conn:
                self.pools[name].putconn(conn)
    
    def disconnect(self, name: str):
        if name in self.pools:
            self.pools[name].closeall()
            del self.pools[name]
            del self.connection_info[name]
            logger.info(f"Disconnected {name}")
    
    def list_connections(self):
        return self.connection_info.copy()
    
    def is_connected(self, name: str) -> bool:
        if name not in self.pools:
            return False
        try:
            with self.get_connection(name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except:
            return False