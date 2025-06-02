"""
AsyncPG database connection management
"""
import asyncpg
from typing import Optional, Any, List, Dict
from contextlib import asynccontextmanager
import json
from ..utils.config import config


class DatabaseConnection:
    """Manages PostgreSQL connections with pgvector support"""
    
    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url or config.database.connection_url
        self._pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self, min_size: int = 5, max_size: int = 20) -> asyncpg.Pool:
        """Create connection pool"""
        self._pool = await asyncpg.create_pool(
            self.connection_url,
            min_size=min_size,
            max_size=max_size,
            init=self._init_connection
        )
        return self._pool
    
    async def _init_connection(self, connection: asyncpg.Connection):
        """Initialize connection with pgvector support"""
        # Register vector type for pgvector
        await connection.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Register custom types if needed
        await connection.set_type_codec(
            'json',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )
    
    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        if not self._pool:
            await self.create_pool()
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query and return results"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_one(self, query: str, *args) -> Any:
        """Execute a query and return first result"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_command(self, query: str, *args) -> str:
        """Execute a command (INSERT, UPDATE, DELETE)"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)


# Global database connection instance
db = DatabaseConnection()
