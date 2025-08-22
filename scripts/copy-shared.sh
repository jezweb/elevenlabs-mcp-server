#!/bin/bash

# Copy shared utilities to all servers
# This is required for FastMCP Cloud deployment since we can't use local packages

echo "📦 Copying shared utilities to all servers..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Source shared directory
SHARED_DIR="$ROOT_DIR/shared"

# Server directories
SERVERS=("elevenlabs-agents" "elevenlabs-knowledge")

# Check if shared directory exists
if [ ! -d "$SHARED_DIR" ]; then
    echo "❌ Error: shared directory not found at $SHARED_DIR"
    exit 1
fi

# Copy to each server
for server in "${SERVERS[@]}"; do
    SERVER_DIR="$ROOT_DIR/$server"
    
    # Create server src directory if it doesn't exist
    mkdir -p "$SERVER_DIR/src"
    
    # Remove old shared directory if it exists
    if [ -d "$SERVER_DIR/src/shared" ]; then
        echo "  Removing old shared directory from $server..."
        rm -rf "$SERVER_DIR/src/shared"
    fi
    
    # Copy shared directory
    echo "  Copying shared to $server/src/shared..."
    cp -r "$SHARED_DIR" "$SERVER_DIR/src/shared"
    
    echo "  ✅ $server updated"
done

echo "✨ All servers updated with latest shared utilities!"
echo ""
echo "Note: Remember to run this script before:"
echo "  - Testing locally"
echo "  - Committing changes"
echo "  - Deploying to FastMCP Cloud"