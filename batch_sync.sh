#!/bin/bash
# EVOL Batch Sync Script
# Syncs multiple repositories from repos.txt

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if repos.txt exists
if [ ! -f "repos.txt" ]; then
    echo "Error: repos.txt not found"
    echo "Create it from the example:"
    echo "  cp repos.txt.example repos.txt"
    exit 1
fi

# Parse options
INCLUDE_DISASM=false
if [ "$1" = "--disasm" ]; then
    INCLUDE_DISASM=true
fi

echo "================================"
echo "  EVOL Batch Sync"
echo "================================"
echo ""

# Count repositories
TOTAL=$(grep -v '^#' repos.txt | grep -v '^$' | wc -l | tr -d ' ')
echo "Found $TOTAL repositories to sync"
echo ""

CURRENT=0
FAILED=()

# Sync each repository
while IFS= read -r repo; do
    # Skip comments and empty lines
    [[ "$repo" =~ ^#.*$ ]] && continue
    [[ -z "$repo" ]] && continue
    
    CURRENT=$((CURRENT + 1))
    echo -e "${BLUE}[$CURRENT/$TOTAL]${NC} Syncing: $repo"
    
    CMD="python -m evol.collector.sync --project $repo"
    if [ "$INCLUDE_DISASM" = true ]; then
        CMD="$CMD --include-disasm"
    fi
    
    if eval $CMD 2>&1; then
        echo -e "${GREEN}✓${NC} Success: $repo"
    else
        echo -e "\033[0;31m✗${NC} Failed: $repo"
        FAILED+=("$repo")
    fi
    echo ""
done < repos.txt

# Summary
echo "================================"
echo "  Batch Sync Complete"
echo "================================"
echo ""
echo "Synced: $((CURRENT - ${#FAILED[@]}))/$TOTAL"

if [ ${#FAILED[@]} -gt 0 ]; then
    echo ""
    echo "Failed repositories:"
    for repo in "${FAILED[@]}"; do
        echo "  • $repo"
    done
fi
echo ""
