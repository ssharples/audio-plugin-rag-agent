#!/usr/bin/env python3
"""
Complete setup and demo script for the Pydantic AI RAG Agent
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent import rag_agent
from src.database.models import PluginQuery, PluginChain, Plugin
from src.api.server import main as start_server


async def setup_demo():
    """Set up demo data and run example queries"""
    
    print("🎵 Pydantic AI RAG Agent for Audio Plugin Recommendations")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Please set it in .env file")
        print("   Copy .env.example to .env and add your OpenAI API key")
        return
    
    if not os.getenv("DATABASE_URL"):
        print("⚠️  Warning: DATABASE_URL not set. Please set it in .env file")
        print("   Make sure PostgreSQL with pgvector is running")
        return
    
    print("1. Initializing database...")
    try:
        await rag_agent.initialize_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return
    
    print("\n2. Adding sample plugin chains...")
    await add_sample_data()
    
    print("\n3. Running example queries...")
    await run_examples()
    
    print("\n🚀 Demo completed! You can now:")
    print("   - Run the API server: python -m src.api.server")
    print("   - Visit http://localhost:8000/docs for API documentation")
    print("   - Use the examples in the examples/ directory")


async def add_sample_data():
    """Add sample plugin chains"""
    
    sample_chains = [
        PluginChain(
            name="Classic Vocal Chain",
            description="Professional vocal processing for pop and rock music",
            plugins=[
                Plugin(name="DeEsser", manufacturer="FabFilter", category="deesser", order=1, 
                      settings="Threshold: -20dB, Frequency: 6kHz"),
                Plugin(name="CLA-2A", manufacturer="Waves", category="compressor", order=2,
                      settings="Limit mode, slow attack/release"),
                Plugin(name="API 550A", manufacturer="Waves", category="EQ", order=3,
                      settings="High shelf +2dB at 10kHz, slight low cut"),
                Plugin(name="H-Reverb", manufacturer="Waves", category="reverb", order=4,
                      settings="Hall preset, 15% wet, pre-delay 40ms")
            ],
            genre="pop", instrument="vocals", tags=["professional", "polished", "radio-ready"],
            rating=4.7, created_by="ProEngineer"
        ),
        
        PluginChain(
            name="Analog Drum Bus",
            description="Warm analog-style drum bus processing with SSL glue",
            plugins=[
                Plugin(name="SSL G-Master Bus", manufacturer="SSL", category="compressor", order=1,
                      settings="4:1 ratio, slow attack, auto release, 2-3dB reduction"),
                Plugin(name="Pultec EQP-1A", manufacturer="UAD", category="EQ", order=2,
                      settings="Low boost at 100Hz, high boost at 10kHz"),
                Plugin(name="Studer A800", manufacturer="UAD", category="tape", order=3,
                      settings="15 IPS, +3 input level")
            ],
            genre="rock", instrument="drums", tags=["analog", "warm", "glue", "vintage"],
            rating=4.9, created_by="VintageSound"
        ),
        
        PluginChain(
            name="Modern Bass Chain",
            description="Clean and punchy bass processing for electronic music",
            plugins=[
                Plugin(name="Pro-C 2", manufacturer="FabFilter", category="compressor", order=1,
                      settings="Clean preset, 4:1 ratio, medium attack"),
                Plugin(name="Pro-Q 3", manufacturer="FabFilter", category="EQ", order=2,
                      settings="High-pass at 40Hz, presence boost at 1kHz"),
                Plugin(name="Pro-MB", manufacturer="FabFilter", category="multiband", order=3,
                      settings="Gentle multiband compression, 3 bands")
            ],
            genre="electronic", instrument="bass", tags=["clean", "modern", "punchy"],
            rating=4.6, created_by="EDMPro"
        )
    ]
    
    for chain in sample_chains:
        try:
            chain_id = await rag_agent.add_plugin_chain(chain)
            print(f"✅ Added: {chain.name} (ID: {chain_id})")
        except Exception as e:
            print(f"⚠️  Chain '{chain.name}' may already exist: {e}")


async def run_examples():
    """Run example queries to demonstrate the agent"""
    
    examples = [
        {
            "description": "Vintage vocal processing",
            "query": "I need a warm vintage vocal chain for indie rock with analog character"
        },
        {
            "description": "Modern electronic bass",
            "query": "Clean and punchy bass processing for electronic dance music"
        },
        {
            "description": "Drum bus compression",
            "query": "Professional drum bus chain with SSL-style glue compression"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i}: {example['description']} ---")
        print(f"Query: {example['query']}")
        
        try:
            response = await rag_agent.run_sync(example['query'])
            
            print(f"Found {len(response.recommendations)} recommendations")
            print(f"Confidence: {response.confidence:.2f}")
            print(f"Explanation: {response.explanation[:100]}...")
            
            if response.recommendations:
                top_rec = response.recommendations[0]
                print(f"Top recommendation: {getattr(top_rec, 'name', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pydantic AI RAG Agent Demo")
    parser.add_argument("--server", action="store_true", help="Start the API server")
    parser.add_argument("--demo", action="store_true", help="Run the demo setup")
    
    args = parser.parse_args()
    
    if args.server:
        print("Starting API server...")
        start_server()
    elif args.demo:
        asyncio.run(setup_demo())
    else:
        print("Pydantic AI RAG Agent")
        print("Usage:")
        print("  python demo.py --demo    # Run demo setup")
        print("  python demo.py --server  # Start API server")


if __name__ == "__main__":
    main()
