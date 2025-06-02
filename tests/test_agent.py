"""
Tests for the RAG agent
"""
import pytest
import asyncio
from src.agent import rag_agent
from src.database.models import PluginQuery


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test that the agent initializes correctly"""
    await rag_agent.initialize_database()
    assert rag_agent is not None


@pytest.mark.asyncio  
async def test_simple_query():
    """Test a simple query to the agent"""
    response = await rag_agent.run_sync("test query")
    assert response is not None
    assert hasattr(response, 'recommendations')
    assert hasattr(response, 'explanation')
    assert hasattr(response, 'confidence')


if __name__ == "__main__":
    pytest.main([__file__])
