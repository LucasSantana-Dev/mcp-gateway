#!/usr/bin/env bash
# Generate IDE configuration for MCP Gateway
# Usage: ./generate-config.sh --ide=windsurf --server=cursor-router [--token=JWT]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
IDE=""
SERVER_NAME=""
GATEWAY_URL="${GATEWAY_URL:-http://localhost:4444}"
JWT_TOKEN="${JWT_TOKEN:-}"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --ide=*)
            IDE="${arg#*=}"
            shift
            ;;
        --server=*)
            SERVER_NAME="${arg#*=}"
            shift
            ;;
        --url=*)
            GATEWAY_URL="${arg#*=}"
            shift
            ;;
        --token=*)
            JWT_TOKEN="${arg#*=}"
            shift
            ;;
        --help)
            echo "Usage: $0 --ide=<windsurf|cursor> --server=<server-name> [--url=<gateway-url>] [--token=<jwt>]"
            echo ""
            echo "Options:"
            echo "  --ide        Target IDE (windsurf or cursor)"
            echo "  --server     Virtual server name"
            echo "  --url        Gateway URL (default: http://localhost:4444)"
            echo "  --token      JWT token for authenticated access (optional)"
            echo ""
            echo "Environment Variables:"
            echo "  GATEWAY_URL  Gateway base URL"
            echo "  JWT_TOKEN    JWT authentication token"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$IDE" ]]; then
    echo "Error: --ide is required"
    echo "Use --help for usage information"
    exit 1
fi

if [[ -z "$SERVER_NAME" ]]; then
    echo "Error: --server is required"
    echo "Use --help for usage information"
    exit 1
fi

# Validate IDE
if [[ "$IDE" != "windsurf" && "$IDE" != "cursor" ]]; then
    echo "Error: --ide must be 'windsurf' or 'cursor'"
    exit 1
fi

# Fetch server UUID from gateway API
echo "Fetching server UUID for '$SERVER_NAME'..." >&2

# Try to get server info from gateway
SERVER_UUID=""
if command -v curl &> /dev/null; then
    # Use curl to fetch server list
    RESPONSE=$(curl -s "${GATEWAY_URL}/api/virtual-servers" 2>/dev/null || echo "")

    if [[ -n "$RESPONSE" ]]; then
        # Try jq first for robust JSON parsing
        if command -v jq &> /dev/null; then
            SERVER_UUID=$(echo "$RESPONSE" | jq --arg SERVER_NAME "$SERVER_NAME" -r '.[] | select(.name==$SERVER_NAME) | .uuid' 2>/dev/null || echo "")
        else
            # Fall back to Python for JSON parsing
            SERVER_UUID=$(python3 -c "
import json
import sys
try:
    data = json.loads(sys.stdin.read())
    for item in data:
        if item.get('name') == sys.argv[1]:
            print(item.get('uuid', ''))
            break
except Exception:
    pass
" "${SERVER_NAME}" <<< "$RESPONSE" 2>/dev/null || echo "")
        fi
    fi
fi

# If we couldn't fetch UUID, use server name as fallback
if [[ -z "$SERVER_UUID" ]]; then
    echo "Warning: Could not fetch server UUID from gateway. Using server name as UUID." >&2
    SERVER_UUID="$SERVER_NAME"
fi

echo "Generating $IDE configuration for server: $SERVER_NAME (UUID: $SERVER_UUID)" >&2

# Generate configuration using Python with environment variables to avoid injection
export IDE SERVER_NAME SERVER_UUID GATEWAY_URL JWT_TOKEN PROJECT_ROOT
python3 -c "
import json
import os
import sys

project_root = os.environ.get('PROJECT_ROOT', '')
sys.path.insert(0, project_root)

from tool_router.api.ide_config import generate_ide_config

ide = os.environ.get('IDE', '')
server_name = os.environ.get('SERVER_NAME', '')
server_uuid = os.environ.get('SERVER_UUID', '')
gateway_url = os.environ.get('GATEWAY_URL', '')
jwt_token = os.environ.get('JWT_TOKEN', '')

# Convert empty JWT_TOKEN to None
jwt_token = jwt_token if jwt_token else None

config = generate_ide_config(
    ide=ide,
    server_name=server_name,
    server_uuid=server_uuid,
    gateway_url=gateway_url,
    jwt_token=jwt_token,
)

print(json.dumps(config, indent=2))
"

echo "" >&2
echo "Configuration generated successfully!" >&2
echo "Copy the JSON above to your IDE's mcp.json file." >&2
