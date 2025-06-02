"""
Load sample data into the RAG database
"""
import asyncio
from src.database.models import PluginChain, Plugin, DocumentChunk
from src.database.vector_store import vector_store


async def load_plugin_chains():
    """Load sample plugin chains"""
    
    chains = [
        PluginChain(
            name="Classic SSL Console Chain",
            description="SSL console emulation for professional mixing",
            plugins=[
                Plugin(name="SSL 4000 E Channel", manufacturer="Waves", category="channel strip", order=1),
                Plugin(name="SSL G-Master Bus Compressor", manufacturer="SSL", category="compressor", order=2)
            ],
            genre="any", instrument="mix bus", tags=["ssl", "console", "professional"]
        ),
        PluginChain(
            name="Analog Mastering Chain", 
            description="Vintage mastering chain for warm, musical results",
            plugins=[
                Plugin(name="Pultec EQP-1A", manufacturer="Universal Audio", category="EQ", order=1),
                Plugin(name="Fairchild 670", manufacturer="Universal Audio", category="compressor", order=2),
                Plugin(name="Studer A800", manufacturer="Universal Audio", category="tape", order=3)
            ],
            genre="any", instrument="master", tags=["mastering", "vintage", "warm"]
        )
    ]
    
    for chain in chains:
        await vector_store.add_plugin_chain(chain)
    
    print(f"Loaded {len(chains)} plugin chains")


async def load_knowledge_base():
    """Load sample audio engineering knowledge"""
    
    chunks = [
        DocumentChunk(
            content="Compression reduces the dynamic range of audio by attenuating loud signals above a threshold. Key parameters include ratio, attack, release, and threshold.",
            metadata={"topic": "compression", "type": "definition"},
            source="Audio Engineering Handbook",
            chunk_index=1
        ),
        DocumentChunk(
            content="EQ (equalization) adjusts the balance of frequency components. High-pass filters remove low-end rumble, while shelving EQs boost or cut frequency ranges.",
            metadata={"topic": "EQ", "type": "definition"}, 
            source="Mixing Fundamentals",
            chunk_index=1
        )
    ]
    
    for chunk in chunks:
        await vector_store.add_document_chunk(chunk)
    
    print(f"Loaded {len(chunks)} knowledge base chunks")


async def main():
    """Load all sample data"""
    print("Initializing database...")
    await vector_store.initialize_tables()
    
    print("Loading plugin chains...")
    await load_plugin_chains()
    
    print("Loading knowledge base...")
    await load_knowledge_base()
    
    print("Sample data loaded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
