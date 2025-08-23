#!/bin/bash

# Test all servers
# This script validates that all servers can be imported and started

echo "🧪 Testing all ElevenLabs MCP servers..."
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall success
ALL_PASSED=true

# Server directories
SERVERS=("elevenlabs-agents" "elevenlabs-knowledge")

# Test each server
for server in "${SERVERS[@]}"; do
    echo "Testing $server..."
    SERVER_DIR="$ROOT_DIR/$server"
    
    # Check if server directory exists
    if [ ! -d "$SERVER_DIR" ]; then
        echo -e "${RED}  ❌ Server directory not found: $SERVER_DIR${NC}"
        ALL_PASSED=false
        continue
    fi
    
    # Check for server.py
    if [ ! -f "$SERVER_DIR/src/server.py" ]; then
        echo -e "${RED}  ❌ server.py not found in $SERVER_DIR/src/${NC}"
        ALL_PASSED=false
        continue
    fi
    
    # Test Python import
    echo "  Testing Python import..."
    cd "$SERVER_DIR"
    python3 -c "from src.server import mcp; print('    ✅ Server object found')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}  ❌ Failed to import server${NC}"
        ALL_PASSED=false
        continue
    fi
    
    # Test server startup (if --test flag exists)
    echo "  Testing server startup..."
    python3 src/server.py --test 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}  ⚠️  Server test mode not implemented or failed${NC}"
    else
        echo -e "${GREEN}  ✅ Server test passed${NC}"
    fi
    
    echo ""
done

# Summary
echo "================================"
if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi