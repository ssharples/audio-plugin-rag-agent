"""
FastAPI server for the RAG agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .routes import router
from ..database.vector_store import vector_store
from ..utils.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting up RAG Agent API...")
    try:
        await vector_store.initialize_tables()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down RAG Agent API...")
    try:
        await vector_store.db.close_pool()
        print("Database connections closed")
    except Exception as e:
        print(f"Error closing database connections: {e}")


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Audio Plugin RAG Agent API",
        description="Pydantic AI agent for audio plugin chain recommendations using RAG",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {
            "message": "Audio Plugin RAG Agent API",
            "version": "1.0.0",
            "docs": "/docs"
        }
    
    return app


app = create_app()


def main():
    """Run the server"""
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
