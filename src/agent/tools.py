"""
RAG tools for the Pydantic AI agent
"""
from typing import List, Optional, Tuple
from pydantic_ai import RunContext
from ..database.models import PluginQuery, PluginChain, PluginRecommendation, DocumentChunk
from ..database.vector_store import vector_store


class RAGDependencies:
    """Dependencies for the RAG agent"""
    
    def __init__(self):
        self.vector_store = vector_store


async def search_plugin_chains_tool(
    ctx: RunContext[RAGDependencies],
    query: str,
    genre: Optional[str] = None,
    instrument: Optional[str] = None,
    max_results: int = 5
) -> List[dict]:
    """
    Search for audio plugin chains based on the query.
    
    Args:
        query: Natural language description of desired sound/chain
        genre: Musical genre filter (optional)
        instrument: Target instrument filter (optional)
        max_results: Maximum number of results to return
    
    Returns:
        List of plugin chains with similarity scores
    """
    results = await ctx.deps.vector_store.search_plugin_chains(
        query_text=query,
        limit=max_results,
        genre_filter=genre,
        instrument_filter=instrument
    )
    
    # Convert to dict format for the LLM
    formatted_results = []
    for chain, similarity in results:
        formatted_results.append({
            "name": chain.name,
            "description": chain.description,
            "plugins": [
                {
                    "name": plugin.name,
                    "manufacturer": plugin.manufacturer,
                    "category": plugin.category,
                    "order": plugin.order,
                    "settings": plugin.settings
                }
                for plugin in chain.plugins
            ],
            "genre": chain.genre,
            "instrument": chain.instrument,
            "tags": chain.tags,
            "rating": chain.rating,
            "similarity_score": similarity
        })
    
    return formatted_results


async def search_knowledge_base_tool(
    ctx: RunContext[RAGDependencies],
    query: str,
    max_results: int = 3
) -> List[dict]:
    """
    Search the general knowledge base for audio engineering information.
    
    Args:
        query: Search query for audio engineering knowledge
        max_results: Maximum number of document chunks to return
    
    Returns:
        List of relevant document chunks
    """
    results = await ctx.deps.vector_store.search_documents(
        query_text=query,
        limit=max_results
    )
    
    # Convert to dict format for the LLM
    formatted_results = []
    for chunk, similarity in results:
        formatted_results.append({
            "content": chunk.content,
            "source": chunk.source,
            "similarity_score": similarity,
            "metadata": chunk.metadata
        })
    
    return formatted_results
