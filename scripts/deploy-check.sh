#!/bin/bash

# Pre-deployment validation script
# This script checks that servers are ready for FastMCP Cloud deployment

echo "🚀 FastMCP Cloud Pre-Deployment Check"
echo "======================================"
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

# Copy shared utilities first
echo "📦 Updating shared utilities..."
"$SCRIPT_DIR/copy-shared.sh"
echo ""

echo "🔍 Checking server structure..."

# Server directories
SERVERS=("elevenlabs-agents" "elevenlabs-knowledge")

for server in "${SERVERS[@]}"; do
    echo ""
    echo "Checking $server:"
    SERVER_DIR="$ROOT_DIR/$server"
    
    # 1. Check directory exists
    if [ ! -d "$SERVER_DIR" ]; then
        echo -e "${RED}  ❌ Server directory not found${NC}"
        ALL_PASSED=false
        continue
    fi
    echo -e "${GREEN}  ✅ Directory exists${NC}"
    
    # 2. Check server.py exists
    if [ ! -f "$SERVER_DIR/src/server.py" ]; then
        echo -e "${RED}  ❌ server.py not found${NC}"
        ALL_PASSED=false
        continue
    fi
    echo -e "${GREEN}  ✅ server.py exists${NC}"
    
    # 3. Check requirements.txt exists
    if [ ! -f "$SERVER_DIR/requirements.txt" ]; then
        echo -e "${RED}  ❌ requirements.txt not found${NC}"
        ALL_PASSED=false
        continue
    fi
    echo -e "${GREEN}  ✅ requirements.txt exists${NC}"
    
    # 4. Check shared code was copied
    if [ ! -d "$SERVER_DIR/src/shared" ]; then
        echo -e "${RED}  ❌ shared/ directory not copied${NC}"
        ALL_PASSED=false
        continue
    fi
    echo -e "${GREEN}  ✅ shared/ directory present${NC}"
    
    # 5. Check for local package references in requirements.txt
    if grep -q "^-e\|file://\|\.\./" "$SERVER_DIR/requirements.txt"; then
        echo -e "${RED}  ❌ requirements.txt contains local references${NC}"
        ALL_PASSED=false
    else
        echo -e "${GREEN}  ✅ requirements.txt contains only PyPI packages${NC}"
    fi
    
    # 6. Check for module-level server object
    if grep -q "^mcp = FastMCP\|^server = FastMCP\|^app = FastMCP" "$SERVER_DIR/src/server.py"; then
        echo -e "${GREEN}  ✅ Module-level server object found${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Could not verify module-level server object${NC}"
        echo "     Please manually verify 'mcp', 'server', or 'app' is at module level"
    fi
done

echo ""
echo "🔐 Checking environment configuration..."

# Check for .env.example
if [ -f "$ROOT_DIR/.env.example" ]; then
    echo -e "${GREEN}  ✅ .env.example found${NC}"
else
    echo -e "${YELLOW}  ⚠️  .env.example not found${NC}"
fi

# Check if .env exists (but don't check contents for security)
if [ -f "$ROOT_DIR/.env" ]; then
    echo -e "${GREEN}  ✅ .env file exists (contents not checked)${NC}"
else
    echo -e "${YELLOW}  ⚠️  .env file not found - remember to set ELEVENLABS_API_KEY${NC}"
fi

echo ""
echo "📋 Summary"
echo "=========="

if [ "$ALL_PASSED" = true ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "Ready for deployment. Next steps:"
    echo "1. Ensure ELEVENLABS_API_KEY is set in .env"
    echo "2. Push to GitHub: git push origin main"
    echo "3. Deploy to FastMCP Cloud following DEPLOYMENT.md"
    exit 0
else
    echo -e "${RED}❌ Some checks failed${NC}"
    echo ""
    echo "Please fix the issues above before deployment."
    echo "See DEPLOYMENT.md for troubleshooting."
    exit 1
fi