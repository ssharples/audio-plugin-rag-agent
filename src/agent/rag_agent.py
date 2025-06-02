"""
Main Pydantic AI RAG Agent for Audio Plugin Recommendations
"""
import time
from typing import List, Optional
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field

from ..database.models import PluginQuery, RAGResponse, PluginRecommendation, PluginChain
from ..database.vector_store import vector_store
from ..utils.config import config
from .tools import RAGDependencies, search_plugin_chains_tool, search_knowledge_base_tool


class AudioPluginResponse(BaseModel):
    """Structured response from the audio plugin RAG agent"""
    recommendations: List[dict] = Field(description="List of recommended plugin chains")
    explanation: str = Field(description="Explanation of why these chains were recommended")
    additional_tips: Optional[str] = Field(description="Additional audio engineering tips")
    confidence: float = Field(description="Confidence in recommendations (0-1)", ge=0, le=1)


class AudioPluginRAGAgent:
    """
    Pydantic AI agent specialized for audio plugin chain recommendations
    using RAG from PostgreSQL vector database
    """
    
    def __init__(self, model: str = "openai:gpt-4o"):
        # Initialize the agent with dependencies and output type
        self.agent = Agent[RAGDependencies, AudioPluginResponse](
            model=model,
            deps_type=RAGDependencies,
            output_type=AudioPluginResponse,
            system_prompt=self._get_system_prompt(),
            instrument=True  # Enable Logfire instrumentation
        )
        
        # Register tools
        self._register_tools()
        
        # Initialize dependencies
        self.dependencies = RAGDependencies()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """
        You are an expert audio engineer and plugin specialist with deep knowledge of music production.
        Your role is to recommend optimal plugin chains for specific audio engineering tasks.
        
        Use the search_plugin_chains_tool to find relevant plugin chains from the database.
        Use the search_knowledge_base_tool to find additional audio engineering information.
        
        When making recommendations:
        1. Consider the musical genre and target instrument
        2. Explain the signal flow and why each plugin works in the chain
        3. Provide specific settings recommendations when available
        4. Consider the user's owned plugins if provided
        5. Explain the sonic characteristics each plugin contributes
        6. Suggest alternatives if the exact plugins aren't available
        
        Be practical, educational, and focus on achieving professional results.
        Always explain your reasoning and provide confidence in your recommendations.
        """
    
    def _register_tools(self):
        """Register tools with the agent"""
        
        @self.agent.tool
        async def search_plugin_chains(
            ctx: RunContext[RAGDependencies],
            query: str,
            genre: Optional[str] = None,
            instrument: Optional[str] = None,
            max_results: int = 5
        ) -> List[dict]:
            """Search for audio plugin chains based on the query."""
            return await search_plugin_chains_tool(ctx, query, genre, instrument, max_results)
        
        @self.agent.tool  
        async def search_knowledge_base(
            ctx: RunContext[RAGDependencies],
            query: str,
            max_results: int = 3
        ) -> List[dict]:
            """Search the general knowledge base for audio engineering information."""
            return await search_knowledge_base_tool(ctx, query, max_results)
    
    async def query(self, query: PluginQuery) -> RAGResponse:
        """
        Query the agent for plugin chain recommendations
        
        Args:
            query: PluginQuery containing the user's request
            
        Returns:
            RAGResponse with recommendations and metadata
        """
        start_time = time.time()
        
        # Ensure database tables are initialized
        await vector_store.initialize_tables()
        
        # Create query context
        query_context = f"Query: {query.text}"
        if query.genre:
            query_context += f" | Genre: {query.genre}"
        if query.instrument:
            query_context += f" | Instrument: {query.instrument}"
        if query.owned_plugins:
            query_context += f" | Owned plugins: {', '.join(query.owned_plugins)}"
        
        # Run the agent
        result = await self.agent.run(
            query.text,
            deps=self.dependencies
        )
        
        # Calculate search time
        search_time = (time.time() - start_time) * 1000
        
        # Convert agent response to RAGResponse format
        recommendations = []
        for rec in result.output.recommendations:
            plugin_rec = PluginRecommendation(
                chain=PluginChain(**rec),
                similarity_score=rec.get('similarity_score', 0.0),
                explanation=result.output.explanation,
                confidence=result.output.confidence
            )
            recommendations.append(plugin_rec)
        
        return RAGResponse(
            recommendations=recommendations,
            query_context=query_context,
            total_results=len(recommendations),
            search_time_ms=search_time
        )
    
    async def run_sync(self, query_text: str, **kwargs) -> AudioPluginResponse:
        """
        Synchronous interface for simple queries
        
        Args:
            query_text: Natural language query
            **kwargs: Additional query parameters
            
        Returns:
            AudioPluginResponse from the agent
        """
        query = PluginQuery(text=query_text, **kwargs)
        
        # Ensure database tables are initialized
        await vector_store.initialize_tables()
        
        result = await self.agent.run(
            query.text,
            deps=self.dependencies
        )
        
        return result.output
    
    async def add_plugin_chain(self, chain: PluginChain) -> int:
        """Add a new plugin chain to the database"""
        await vector_store.initialize_tables()
        return await vector_store.add_plugin_chain(chain)
    
    async def initialize_database(self):
        """Initialize database tables"""
        await vector_store.initialize_tables()


# Global agent instance
rag_agent = AudioPluginRAGAgent()
