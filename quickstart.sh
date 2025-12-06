#!/bin/bash
# EVOL Quick Start Script
# This script automates the initial setup process

set -e  # Exit on error

echo "================================"
echo "  EVOL Quick Start v1.0"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found: Python $PYTHON_VERSION"

# Check if running in project directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the EVOL project directory"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
if command -v poetry &> /dev/null; then
    echo "  Using Poetry..."
    poetry install
else
    echo "  Using pip..."
    pip install -e .
fi
echo -e "${GREEN}✓${NC} Dependencies installed"

# Setup .env file
echo ""
if [ -f ".env" ]; then
    echo ".env file already exists, skipping..."
else
    echo "Setting up environment variables..."
    read -p "Enter your GitHub Personal Access Token: " github_token
    
    cat > .env << EOF
# EVOL Environment Configuration
DATABASE_URL=sqlite:///./evol.db
GITHUB_TOKEN=${github_token}
EOF
    echo -e "${GREEN}✓${NC} .env file created"
fi

# Initialize database
echo ""
echo "Initializing database..."
alembic upgrade head
echo -e "${GREEN}✓${NC} Database initialized"

# Check Docker
echo ""
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "Starting Grafana..."
    docker-compose up -d
    echo -e "${GREEN}✓${NC} Grafana started"
    GRAFANA_URL="http://localhost:3000"
else
    echo -e "${YELLOW}⚠${NC} Docker not found. Skipping Grafana setup."
    echo "  Install Docker to use Grafana visualization"
    GRAFANA_URL=""
fi

# Show next steps
echo ""
echo "================================"
echo "  Setup Complete! 🎉"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Sync your first project:"
echo "   ${GREEN}./sync_and_view.sh owner/repo${NC}"
echo ""
if [ -n "$GRAFANA_URL" ]; then
    echo "2. View data in Grafana:"
    echo "   ${GREEN}${GRAFANA_URL}${NC}"
    echo "   (Default login: admin/admin)"
    echo ""
fi
echo "3. Or use the API:"
echo "   ${GREEN}uvicorn evol.api.main:app${NC}"
echo "   Then open: http://localhost:8000/docs"
echo ""
echo "For more details, see OPERATIONS_GUIDE.md"
echo ""
