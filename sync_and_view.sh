#!/bin/bash
# EVOL Sync and View Script
# Syncs GitHub projects and opens Grafana

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
INCLUDE_DISASM=false
OPEN_GRAFANA=true
DEVICE_DUMP=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --disasm)
            INCLUDE_DISASM=true
            shift
            ;;
        --no-grafana)
            OPEN_GRAFANA=false
            shift
            ;;
        --device)
            DEVICE_DUMP="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] owner/repo [owner/repo2 ...]"
            echo ""
            echo "Options:"
            echo "  --disasm        Include binary disassembly"
            echo "  --no-grafana    Don't open Grafana after sync"
            echo "  --device FILE   Import device telemetry dump"
            echo "  -h, --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 capybara-works/EVOL"
            echo "  $0 --disasm owner/repo1 owner/repo2"
            echo "  $0 --device test.dump owner/repo"
            exit 0
            ;;
        *)
            PROJECTS+=("$1")
            shift
            ;;
    esac
done

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file not found. Run ./quickstart.sh first."
    exit 1
fi

# Source environment
export $(cat .env | grep -v '^#' | xargs)

# Check GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠${NC} GITHUB_TOKEN not set in .env"
    exit 1
fi

echo "================================"
echo "  EVOL Sync & View"
echo "================================"
echo ""

# Import device dump if specified
if [ -n "$DEVICE_DUMP" ]; then
    echo -e "${BLUE}→${NC} Importing device dump: $DEVICE_DUMP"
    python -m evol.collector.sync --import-device "$DEVICE_DUMP"
    echo -e "${GREEN}✓${NC} Device dump imported"
    echo ""
fi

# Sync projects
if [ ${#PROJECTS[@]} -eq 0 ]; then
    echo "No projects specified. Use --help for usage."
    exit 1
fi

for project in "${PROJECTS[@]}"; do
    echo -e "${BLUE}→${NC} Syncing: $project"
    
    CMD="python -m evol.collector.sync --project $project"
    
    if [ "$INCLUDE_DISASM" = true ]; then
        CMD="$CMD --include-disasm"
        echo "  (with disassembly)"
    fi
    
    eval $CMD
    echo -e "${GREEN}✓${NC} Synced: $project"
    echo ""
done

# Show sync summary
echo "================================"
echo "  Sync Complete!"
echo "================================"
echo ""

# Count records
if command -v sqlite3 &> /dev/null; then
    TOTAL_RUNS=$(sqlite3 evol.db "SELECT COUNT(*) FROM runs;" 2>/dev/null || echo "?")
    TOTAL_ARTIFACTS=$(sqlite3 evol.db "SELECT COUNT(*) FROM artifacts;" 2>/dev/null || echo "?")
    
    echo "Database statistics:"
    echo "  Total runs: $TOTAL_RUNS"
    echo "  Total artifacts: $TOTAL_ARTIFACTS"
    echo ""
fi

# Open Grafana
if [ "$OPEN_GRAFANA" = true ]; then
    # Check if Grafana is running
    if docker ps | grep -q evol-grafana; then
        echo "Opening Grafana..."
        
        # Try to open browser (macOS/Linux)
        if command -v open &> /dev/null; then
            open http://localhost:3000
        elif command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:3000
        else
            echo "Please open: ${GREEN}http://localhost:3000${NC}"
        fi
    else
        echo -e "${YELLOW}⚠${NC} Grafana is not running. Start with:"
        echo "  docker-compose up -d"
    fi
fi

echo ""
echo "View data:"
echo "  • Grafana: ${GREEN}http://localhost:3000${NC}"
echo "  • API Docs: ${GREEN}http://localhost:8000/docs${NC} (run: uvicorn evol.api.main:app)"
echo ""
