"""
Configuration management for the RAG agent
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration"""
    host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "plugin_rag_db"))
    user: str = Field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    url: Optional[str] = Field(default_factory=lambda: os.getenv("DATABASE_URL"))

    @property
    def connection_url(self) -> str:
        """Get the database connection URL"""
        if self.url:
            return self.url
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class EmbeddingConfig(BaseModel):
    """Embedding model configuration"""
    model: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    dimensions: int = Field(default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSIONS", "1536")))


class Config(BaseModel):
    """Main application configuration"""
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    
    model_config = {"env_file": ".env"}


# Global config instance
config = Config()
