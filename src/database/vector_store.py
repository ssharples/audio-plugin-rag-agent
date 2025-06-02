"""
Vector store operations using pgvector with existing Supabase tables
"""
import asyncpg
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
from .connection import db
from .models import DocumentChunk, PluginChain, PluginRecommendation, Plugin
from ..utils.embeddings import embedding_service


class SupabaseVectorStore:
    """Vector store using existing Supabase documents and document_metadata tables"""
    
    def __init__(self):
        self.db = db
        self.embedding_service = embedding_service
    
    async def initialize_tables(self):
        """Check if tables exist and create plugin-related ones if needed"""
        async with self.db.get_connection() as conn:
            # Check if documents table exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'documents'
                );
            """)
            
            if not exists:
                raise Exception("Documents table not found in Supabase database")
            
            # Create plugin chains table if it doesn't exist
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
            
            # Create indices for vector similarity search if they don't exist
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS plugin_chains_embedding_idx 
                ON plugin_chains USING hnsw (embedding vector_cosine_ops);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS documents_embedding_idx 
                ON documents USING hnsw (embedding vector_cosine_ops);
            """)
    
    async def search_documents(self, query_text: str, limit: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for document chunks by similarity using existing documents table"""
        query_embedding = await self.embedding_service.generate_embedding(query_text)
        
        query = """
            SELECT d.id, d.content, d.metadata, d.embedding, 
                   dm.title, dm.url, 
                   1 - (d.embedding <=> $1) as similarity
            FROM documents d
            LEFT JOIN document_metadata dm ON d.metadata->>'source' = dm.id
            WHERE d.embedding IS NOT NULL
            ORDER BY d.embedding <=> $1
            LIMIT $2
        """
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query, query_embedding, limit)
            
            results = []
            for row in rows:
                # Extract metadata with fallbacks
                metadata = dict(row['metadata']) if row['metadata'] else {}
                source = metadata.get('source', row.get('url', 'Unknown'))
                
                chunk = DocumentChunk(
                    id=row['id'],
                    content=row['content'],
                    embedding=list(row['embedding']) if row['embedding'] else [],
                    metadata=metadata,
                    source=source,
                    chunk_index=metadata.get('chunk_index', 0),
                    created_at=None  # Not stored in your current schema
                )
                similarity = float(row['similarity'])
                results.append((chunk, similarity))
            
            return results
    
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
    
    async def add_document(self, content: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None) -> int:
        """Add a document to the existing documents table"""
        if embedding is None:
            embedding = await self.embedding_service.generate_embedding(content)
        
        async with self.db.get_connection() as conn:
            row = await conn.fetchrow("""
                INSERT INTO documents (content, metadata, embedding)
                VALUES ($1, $2, $3)
                RETURNING id
            """, content, metadata, embedding)
            return row['id']


# Global vector store instance
vector_store = SupabaseVectorStore()
