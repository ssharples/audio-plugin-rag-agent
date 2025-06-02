# Audio Plugin RAG Agent

A sophisticated Pydantic AI agent for audio engineering plugin chain recommendations using RAG (Retrieval Augmented Generation) with Supabase PostgreSQL and pgvector.

## 🎯 Features

- **Pydantic AI Agent**: Type-safe AI agent with structured responses
- **Supabase Integration**: Uses existing `documents` and `document_metadata` tables
- **Vector Search**: Semantic search using pgvector for plugin recommendations
- **FastAPI REST API**: Production-ready API endpoints
- **Docker Ready**: Containerized for easy deployment with Coolify
- **Audio Engineering Focused**: Specialized for plugin chain recommendations

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/ssharples/audio-plugin-rag-agent.git
cd audio-plugin-rag-agent
cp .env.example .env
# Edit .env with your configuration
```

### 2. Environment Configuration

Edit your `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://aflxjobceqjpjftxwewp.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFmbHhqb2JjZXFqcGpmdHh3ZXdwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE5MzgxNDMsImV4cCI6MjA0NzUxNDE0M30.nWVRnDthpXBiQXmfD53hfbxJUeEPFapdYptaQJsJU6M
DATABASE_URL=postgresql://postgres:[YOUR_SUPABASE_PASSWORD]@db.aflxjobceqjpjftxwewp.supabase.co:5432/postgres
```

### 3. Install and Run

```bash
pip install -r requirements.txt
python demo.py --demo  # Run demo
python demo.py --server  # Start API server
```

## 🔌 API Endpoints

**Base URL:** `https://pluginagent.alluristdesign.dev/api/v1`

### Core Endpoints

- `POST /query` - Get AI-powered plugin chain recommendations
- `POST /chains` - Add new plugin chains
- `GET /chains/search` - Direct search without AI
- `GET /health` - Health check
- `GET /docs` - API documentation

### Example Request

```bash
curl -X POST "https://pluginagent.alluristdesign.dev/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I need a warm vintage vocal chain for indie rock",
    "genre": "indie rock",
    "instrument": "vocals",
    "max_results": 3
  }'
```

## 🐳 Deployment

### Coolify Deployment

1. **Repository**: `https://github.com/ssharples/audio-plugin-rag-agent`
2. **Domain**: `pluginagent.alluristdesign.dev`
3. **Environment Variables**: Copy from `.env.example` and add your keys

### Docker

```bash
docker-compose up -d
```

## 📚 Frontend Integration

See `FRONTEND_DOCS.md` for complete integration guide including:
- TypeScript types and interfaces
- React, Vue, and vanilla JS examples
- Error handling patterns
- Performance optimization tips

## 🧠 How It Works

1. **Query Processing**: Natural language query from user
2. **Embedding Generation**: OpenAI converts to vector embedding
3. **Vector Search**: pgvector finds similar content in Supabase
4. **Knowledge Retrieval**: RAG system retrieves relevant documents
5. **AI Response**: Pydantic AI generates structured recommendations

## 📊 Database Schema

Uses your existing Supabase tables:
- `documents` - Content with vector embeddings
- `document_metadata` - Document metadata and sources
- `plugin_chains` - Plugin chain data (created by agent)

## 🔧 Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Start development server
python demo.py --server
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the audio engineering community using Pydantic AI and Supabase.
