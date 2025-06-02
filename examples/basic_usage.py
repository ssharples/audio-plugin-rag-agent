"""
Basic usage example for the Audio Plugin RAG Agent
"""
import asyncio
import os
from src.agent import rag_agent
from src.database.models import PluginQuery, PluginChain, Plugin


async def main():
    """Example usage of the RAG agent"""
    
    # Initialize the database
    await rag_agent.initialize_database()
    
    # Add some sample plugin chains
    await add_sample_chains()
    
    # Example 1: Simple query
    print("=" * 50)
    print("Example 1: Simple vocal chain query")
    print("=" * 50)
    
    response = await rag_agent.run_sync(
        "I need a warm vintage vocal chain for indie rock"
    )
    
    print(f"Recommendations: {len(response.recommendations)}")
    print(f"Explanation: {response.explanation}")
    print(f"Confidence: {response.confidence}")
    
    # Example 2: Structured query with filters
    print("\n" + "=" * 50)
    print("Example 2: Structured query with filters")
    print("=" * 50)
    
    query = PluginQuery(
        text="punchy drum bus compression",
        genre="rock",
        instrument="drums",
        owned_plugins=["SSL G-Master Bus Compressor", "FabFilter Pro-Q 3"],
        max_results=3
    )
    
    rag_response = await rag_agent.query(query)
    
    print(f"Query context: {rag_response.query_context}")
    print(f"Total results: {rag_response.total_results}")
    print(f"Search time: {rag_response.search_time_ms:.2f}ms")
    
    for i, rec in enumerate(rag_response.recommendations, 1):
        print(f"\nRecommendation {i}:")
        print(f"  Chain: {rec.chain.name}")
        print(f"  Similarity: {rec.similarity_score:.3f}")
        print(f"  Plugins: {len(rec.chain.plugins)} plugins")


async def add_sample_chains():
    """Add some sample plugin chains to the database"""
    
    # Vintage Vocal Chain
    vintage_vocal = PluginChain(
        name="Vintage Vocal Chain",
        description="Warm analog-style vocal processing for indie and alternative rock",
        plugins=[
            Plugin(
                name="CLA-2A",
                manufacturer="Waves", 
                category="compressor",
                order=1,
                settings="2:1 ratio, slow attack, moderate release"
            ),
            Plugin(
                name="Pultec EQP-1A",
                manufacturer="Universal Audio",
                category="EQ",
                order=2, 
                settings="Gentle high boost at 10kHz, slight low boost at 100Hz"
            ),
            Plugin(
                name="1176 Compressor",
                manufacturer="Universal Audio",
                category="compressor", 
                order=3,
                settings="4:1 ratio, fast attack for peak control"
            )
        ],
        genre="indie rock",
        instrument="vocals",
        tags=["vintage", "warm", "analog", "classic"],
        rating=4.8
    )
    
    # Modern Drum Bus
    drum_bus = PluginChain(
        name="Modern Drum Bus", 
        description="Punchy and controlled drum bus processing for rock and pop",
        plugins=[
            Plugin(
                name="SSL G-Master Bus Compressor",
                manufacturer="Solid State Logic",
                category="compressor",
                order=1,
                settings="4:1 ratio, slow attack, auto release, 2-3dB reduction"
            ),
            Plugin(
                name="Pro-Q 3",
                manufacturer="FabFilter",
                category="EQ", 
                order=2,
                settings="High-pass at 60Hz, slight presence boost at 2-4kHz"
            )
        ],
        genre="rock",
        instrument="drums", 
        tags=["punchy", "modern", "controlled", "glue"],
        rating=4.9
    )
    
    # Add chains to database
    try:
        await rag_agent.add_plugin_chain(vintage_vocal)
        await rag_agent.add_plugin_chain(drum_bus)
        print("Sample plugin chains added successfully!")
    except Exception as e:
        print(f"Note: Sample chains may already exist: {e}")


if __name__ == "__main__":
    asyncio.run(main())
