"""
Embedding generation utilities
"""
import numpy as np
from typing import List, Optional
from openai import AsyncOpenAI
from .config import config


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or config.openai_api_key)
        self.model = config.embedding.model
        self.dimensions = config.embedding.dimensions
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )
        return [item.embedding for item in response.data]
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        a_np = np.array(a)
        b_np = np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


# Global embedding service instance
embedding_service = EmbeddingService()
