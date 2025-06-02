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
    host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "db.aflxjobceqjpjftxwewp.supabase.co"))
    port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    name: str = Field(default_factory=lambda: os.getenv("DB_NAME", "postgres"))
    user: str = Field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    url: Optional[str] = Field(default_factory=lambda: os.getenv("DATABASE_URL"))
    
    # Supabase specific config
    supabase_url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", "https://aflxjobceqjpjftxwewp.supabase.co"))
    supabase_anon_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmbHhqb2JjZXFqcGpmdHh3ZXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE5MzgxNDMsImV4cCI6MjA0NzUxNDE0M30.nWVRnDthpXBiQXmfD53hfbxJUeEPFapdYptaQJsJU6M"))

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
