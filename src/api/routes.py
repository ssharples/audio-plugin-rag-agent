"""
FastAPI routes for the RAG agent API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time

from ..database.models import PluginQuery, PluginChain, RAGResponse
from ..agent.rag_agent import rag_agent
from ..database.vector_store import vector_store

router = APIRouter()


@router.post("/query", response_model=RAGResponse)
async def query_plugin_chains(query: PluginQuery):
    """
    Query for plugin chain recommendations
    """
    try:
        response = await rag_agent.query(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chains", response_model=dict)
async def add_plugin_chain(chain: PluginChain):
    """
    Add a new plugin chain to the database
    """
    try:
        chain_id = await rag_agent.add_plugin_chain(chain)
        return {"id": chain_id, "message": "Plugin chain added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chains/search")
async def search_chains(
    q: str,
    genre: str = None,
    instrument: str = None,
    limit: int = 5
):
    """
    Direct search of plugin chains (without AI agent)
    """
    try:
        results = await vector_store.search_plugin_chains(
            query_text=q,
            limit=limit,
            genre_filter=genre,
            instrument_filter=instrument
        )
        
        formatted_results = []
        for chain, similarity in results:
            formatted_results.append({
                "chain": chain.dict(),
                "similarity_score": similarity
            })
        
        return {
            "results": formatted_results,
            "total": len(formatted_results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        await vector_store.initialize_tables()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Service unavailable: {str(e)}"
        )


@router.post("/initialize")
async def initialize_database():
    """
    Initialize database tables
    """
    try:
        await rag_agent.initialize_database()
        return {"message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
