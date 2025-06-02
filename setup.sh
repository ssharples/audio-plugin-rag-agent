#!/bin/bash

# Setup script for Pydantic AI RAG Agent

echo "🎵 Setting up Pydantic AI RAG Agent for Audio Plugin Recommendations"
echo "=================================================================="

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [[ $(echo "$python_version >= 3.11" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.11+ required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration:"
    echo "   - Add your OPENAI_API_KEY"
    echo "   - Configure DATABASE_URL for your PostgreSQL instance"
fi

# Check PostgreSQL connection
echo "🔍 Checking PostgreSQL setup..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
    echo "📝 Make sure to:"
    echo "   1. Install pgvector extension: CREATE EXTENSION vector;"
    echo "   2. Update DATABASE_URL in .env file"
else
    echo "⚠️  PostgreSQL client not found. Install it with:"
    echo "   - macOS: brew install postgresql"
    echo "   - Ubuntu: sudo apt-get install postgresql-client"
    echo "   - Or use Docker: docker run --name pgvector-container -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d pgvector/pgvector:pg16"
fi

echo ""
echo "🚀 Setup complete! Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start PostgreSQL with pgvector extension"
echo "3. Run demo: python demo.py --demo"
echo "4. Start API server: python demo.py --server"
echo ""
echo "📚 Documentation: README.md"
echo "🔗 API docs (when running): http://localhost:8000/docs"
