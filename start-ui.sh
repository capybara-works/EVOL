#!/bin/bash
# Start EVOL WebUI

set -e

echo "================================"
echo "  EVOL WebUI Starting..."
echo "================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "Run ./quickstart.sh first, or create .env manually"
    exit 1
fi

# Check if database exists
if [ ! -f "evol.db" ]; then
    echo "⚠️  Database not found"
    echo "Run 'alembic upgrade head' to initialize database"
    exit 1
fi

echo "Starting WebUI on http://localhost:8080"
echo ""
echo "📊 Dashboard: http://localhost:8080"
echo "📖 API Docs:  http://localhost:8000/docs (run separately)"
echo "📈 Grafana:   http://localhost:3000 (docker-compose up -d)"
echo ""

uvicorn evol.ui.app:app --host 0.0.0.0 --port 8080 --reload
