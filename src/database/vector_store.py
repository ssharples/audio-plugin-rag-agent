"""
Vector store operations using pgvector
"""
import asyncpg
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from .connection import db
from .models import DocumentChunk, PluginChain, PluginRecommendation
from ..utils.embeddings import embedding_service


class VectorStore:
    """Vector store using PostgreSQL with pgvector"""
    
    def __init__(self):
        self.db = db
        self.embedding_service = embedding_service
    
    async def initialize_tables(self):
        """Create tables if they don't exist"""
        async with self.db.get_connection() as conn:
            # Create vector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create plugin chains table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS plugin_chains (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    plugins JSONB,
                    genre VARCHAR(100),
                    instrument VARCHAR(100),
                    tags TEXT[],
                    rating FLOAT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    created_by VARCHAR(100),
                    embedding vector(1536)
                );
            """)
            
            # Create document chunks table for general RAG content
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(1536),
                    metadata JSONB,
                    source VARCHAR(500),
                    chunk_index INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Create indices for vector similarity search
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS plugin_chains_embedding_idx 
                ON plugin_chains USING hnsw (embedding vector_cosine_ops);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
                ON document_chunks USING hnsw (embedding vector_cosine_ops);
            """)
    
    async def add_plugin_chain(self, chain: PluginChain) -> int:
        """Add a plugin chain to the vector store"""
        # Generate embedding from chain description and metadata
        chain_text = f"{chain.name} {chain.description} {' '.join(chain.tags)}"
        if chain.genre:
            chain_text += f" {chain.genre}"
        if chain.instrument:
            chain_text += f" {chain.instrument}"
        
        embedding = await self.embedding_service.generate_embedding(chain_text)
        
        async with self.db.get_connection() as conn:
            row = await conn.fetchrow("""
                INSERT INTO plugin_chains 
                (name, description, plugins, genre, instrument, tags, rating, created_by, embedding)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """, 
                chain.name,
                chain.description,
                [plugin.dict() for plugin in chain.plugins],
                chain.genre,
                chain.instrument,
                chain.tags,
                chain.rating,
                chain.created_by,
                embedding
            )
            return row['id']
    
    async def search_plugin_chains(
        self, 
        query_text: str, 
        limit: int = 5,
        genre_filter: Optional[str] = None,
        instrument_filter: Optional[str] = None
    ) -> List[Tuple[PluginChain, float]]:
        """Search for plugin chains by similarity"""
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        
        # Build SQL query with optional filters
        where_conditions = []
        params = [query_embedding, limit]
        param_count = 2
        
        if genre_filter:
            param_count += 1
            where_conditions.append(f"genre ILIKE ${param_count}")
            params.append(f"%{genre_filter}%")
        
        if instrument_filter:
            param_count += 1
            where_conditions.append(f"instrument ILIKE ${param_count}")
            params.append(f"%{instrument_filter}%")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query = f"""
            SELECT *, 1 - (embedding <=> $1) as similarity
            FROM plugin_chains
            {where_clause}
            ORDER BY embedding <=> $1
            LIMIT $2
        """
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            
            results = []
            for row in rows:
                chain = PluginChain(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    plugins=[Plugin(**plugin) for plugin in row['plugins']],
                    genre=row['genre'],
                    instrument=row['instrument'],
                    tags=row['tags'] or [],
                    rating=row['rating'],
                    created_at=row['created_at'],
                    created_by=row['created_by']
                )
                similarity = float(row['similarity'])
                results.append((chain, similarity))
            
            return results
    
    async def add_document_chunk(self, chunk: DocumentChunk) -> int:
        """Add a document chunk to the vector store"""
        embedding = await self.embedding_service.generate_embedding(chunk.content)
        
        async with self.db.get_connection() as conn:
            row = await conn.fetchrow("""
                INSERT INTO document_chunks 
                (content, embedding, metadata, source, chunk_index)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
            """,
                chunk.content,
                embedding,
                chunk.metadata,
                chunk.source,
                chunk.chunk_index
            )
            return row['id']
    
    async def search_documents(self, query_text: str, limit: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for document chunks by similarity"""
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        
        query = """
            SELECT *, 1 - (embedding <=> $1) as similarity
            FROM document_chunks
            ORDER BY embedding <=> $1
            LIMIT $2
        """
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query, query_embedding, limit)
            
            results = []
            for row in rows:
                chunk = DocumentChunk(
                    id=row['id'],
                    content=row['content'],
                    embedding=list(row['embedding']),
                    metadata=row['metadata'],
                    source=row['source'],
                    chunk_index=row['chunk_index'],
                    created_at=row['created_at']
                )
                similarity = float(row['similarity'])
                results.append((chunk, similarity))
            
            return results


# Global vector store instance
vector_store = VectorStore()
