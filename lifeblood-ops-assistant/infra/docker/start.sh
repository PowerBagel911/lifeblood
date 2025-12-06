#!/bin/bash
# Docker Quick Start Script for Linux/Mac

echo "🐳 Lifeblood Ops Assistant - Docker Quick Start"
echo ""

# Check if .env exists
if [ ! -f "../../.env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from template..."
    cp ../../env.template ../../.env
    echo ""
    echo "✏️  Please edit .env and add your GEMINI_API_KEY:"
    echo "   nano ../../.env"
    echo ""
    echo "Then run this script again."
    exit 0
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.\+" ../../.env; then
    echo "⚠️  GEMINI_API_KEY not set in .env file!"
    echo "Please edit .env and add your API key, then run this script again."
    exit 1
fi

echo "✅ Environment configuration found"
echo ""

# Ask user which mode
echo "Select deployment mode:"
echo "1. Production (optimized builds, nginx)"
echo "2. Development (hot-reload, debug logging)"
echo ""
read -p "Enter choice (1 or 2): " mode

if [ "$mode" = "2" ]; then
    echo ""
    echo "🚀 Starting in DEVELOPMENT mode..."
    echo ""
    docker compose -f compose.dev.yaml up --build
else
    echo ""
    echo "🚀 Starting in PRODUCTION mode..."
    echo ""
    echo "Building images..."
    docker compose up --build -d
    
    echo ""
    echo "Waiting for services to be healthy..."
    sleep 10
    
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Service Status:"
    docker compose ps
    
    echo ""
    echo "🌐 Access Points:"
    echo "   Web UI:   http://localhost:3000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "📝 Next Steps:"
    echo "   1. Ingest documents:"
    echo "      curl -X POST http://localhost:8000/ingest"
    echo ""
    echo "   2. View logs:"
    echo "      docker compose logs -f"
    echo ""
    echo "   3. Stop services:"
    echo "      docker compose down"
fi
