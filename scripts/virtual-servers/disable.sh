#!/usr/bin/env bash
# Disable a virtual server by updating virtual-servers.txt
# Usage: ./disable.sh <server-name>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="${CONFIG_DIR:-$REPO_ROOT/config}"
VIRTUAL_SERVERS_FILE="$CONFIG_DIR/virtual-servers.txt"

# Check arguments
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <server-name>" >&2
    echo "" >&2
    echo "Example: $0 cursor-default" >&2
    exit 1
fi

SERVER_NAME="$1"

# Check if file exists
if [[ ! -f "$VIRTUAL_SERVERS_FILE" ]]; then
    echo "Error: $VIRTUAL_SERVERS_FILE not found" >&2
    exit 1
fi

# Check if server exists
if ! grep -q "^${SERVER_NAME}|" "$VIRTUAL_SERVERS_FILE" && ! grep -q "^${SERVER_NAME} " "$VIRTUAL_SERVERS_FILE"; then
    echo "Error: Server '$SERVER_NAME' not found in $VIRTUAL_SERVERS_FILE" >&2
    exit 1
fi

# Create backup
cp "$VIRTUAL_SERVERS_FILE" "${VIRTUAL_SERVERS_FILE}.bak"

# Disable the server by:
# 1. If line has |true at end, change to |false
# 2. If line has |false at end, leave as is (already disabled)
# 3. If line has no enabled flag, add |false
# 4. Skip comment lines
temp_file=$(mktemp)
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
        echo "$line"
        continue
    fi

    # Check if this is the target server
    if [[ "$line" =~ ^${SERVER_NAME}\| ]] || [[ "$line" =~ ^${SERVER_NAME}[[:space:]] ]]; then
        # Parse the line
        IFS='|' read -r name gateways enabled_flag <<< "$line"

        # Set enabled to false
        if [[ -z "$enabled_flag" ]]; then
            # No enabled flag, add it as false
            echo "${name}|${gateways}|false"
        elif [[ "$enabled_flag" == "true" ]]; then
            # Change true to false
            echo "${name}|${gateways}|false"
        else
            # Already false or other value, keep as is
            echo "$line"
        fi
    else
        echo "$line"
    fi
done < "$VIRTUAL_SERVERS_FILE" > "$temp_file"

# Replace original file
mv "$temp_file" "$VIRTUAL_SERVERS_FILE"

echo "✓ Server '$SERVER_NAME' disabled"
echo ""
echo "Run 'make register' to apply changes"
