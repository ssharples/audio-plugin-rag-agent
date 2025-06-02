"""
Pydantic models for the RAG system
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Plugin(BaseModel):
    """Individual plugin in a chain"""
    name: str = Field(description="Plugin name")
    manufacturer: str = Field(description="Plugin manufacturer")
    category: str = Field(description="Plugin category (EQ, compressor, reverb, etc.)")
    order: int = Field(description="Order in the chain (1-based)")
    settings: Optional[str] = Field(default=None, description="Recommended settings")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Parameter values")


class PluginChain(BaseModel):
    """Complete plugin chain"""
    id: Optional[int] = Field(default=None, description="Database ID")
    name: str = Field(description="Chain name")
    description: str = Field(description="Chain description")
    plugins: List[Plugin] = Field(description="List of plugins in order")
    genre: Optional[str] = Field(default=None, description="Musical genre")
    instrument: Optional[str] = Field(default=None, description="Target instrument")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    rating: Optional[float] = Field(default=None, description="Community rating")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    created_by: Optional[str] = Field(default=None, description="Creator username")


class PluginQuery(BaseModel):
    """Query for plugin chain recommendations"""
    text: str = Field(description="Natural language query")
    genre: Optional[str] = Field(default=None, description="Musical genre filter")
    instrument: Optional[str] = Field(default=None, description="Instrument filter")
    owned_plugins: List[str] = Field(default=[], description="List of owned plugins")
    max_results: int = Field(default=5, description="Maximum number of results")


class PluginRecommendation(BaseModel):
    """Plugin chain recommendation result"""
    chain: PluginChain = Field(description="Recommended plugin chain")
    similarity_score: float = Field(description="Similarity score (0-1)")
    explanation: str = Field(description="Why this chain was recommended")
    confidence: float = Field(description="Confidence in recommendation (0-1)")


class RAGResponse(BaseModel):
    """Response from the RAG agent"""
    recommendations: List[PluginRecommendation] = Field(description="List of recommendations")
    query_context: str = Field(description="Processed query context")
    total_results: int = Field(description="Total number of results found")
    search_time_ms: float = Field(description="Search time in milliseconds")


class DocumentChunk(BaseModel):
    """Vector database document chunk"""
    id: Optional[int] = Field(default=None, description="Database ID")
    content: str = Field(description="Text content")
    embedding: List[float] = Field(description="Vector embedding")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    source: str = Field(description="Source document/URL")
    chunk_index: int = Field(description="Index within source document")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
