#!/usr/bin/env bash
# Ensure JWT token exists for authenticated servers
# Usage: ensure_jwt <server_name> <requires_auth>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Source bootstrap for logging functions
source "$SCRIPT_DIR/../lib/bootstrap.sh"
source "$SCRIPT_DIR/../lib/gateway.sh"

ensure_jwt() {
    # shellcheck disable=SC2034  # server_name parameter reserved for future use
    local server_name="$1"
    local requires_auth="$2"

    # Skip if auth not required
    if [[ "$requires_auth" != "true" ]]; then
        return 0
    fi

    # Check existing JWT in .env
    if [[ -f "$PROJECT_ROOT/.env" ]]; then
        source "$PROJECT_ROOT/.env" 2>/dev/null || true
    fi

    if [[ -n "${GATEWAY_JWT:-}" ]]; then
        # Validate token format (basic check)
        if [[ "$GATEWAY_JWT" =~ ^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$ ]]; then
            info "Using existing JWT from .env"
            export GATEWAY_JWT
            return 0
        fi
    fi

    # Need to generate JWT
    warn "This server requires authentication"
    echo ""

    # Check for credentials in .env
    if [[ -z "${PLATFORM_ADMIN_EMAIL:-}" ]] || [[ -z "${JWT_SECRET_KEY:-}" ]]; then
        info "Admin credentials not found in .env"
        read -rp "Enter admin email: " PLATFORM_ADMIN_EMAIL
        read -rsp "Enter JWT secret key: " JWT_SECRET_KEY
        echo ""
        export PLATFORM_ADMIN_EMAIL JWT_SECRET_KEY
    fi

    # Generate JWT using existing infrastructure
    info "Generating JWT token..."
    local jwt_token
    jwt_token=$(get_jwt) || {
        error "Failed to generate JWT"
        return 1
    }

    # Store in .env
    if ! grep -q "^GATEWAY_JWT=" "$PROJECT_ROOT/.env" 2>/dev/null; then
        echo "GATEWAY_JWT=$jwt_token" >> "$PROJECT_ROOT/.env"
    else
        # Use portable sed syntax
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^GATEWAY_JWT=.*|GATEWAY_JWT=$jwt_token|" "$PROJECT_ROOT/.env"
        else
            sed -i "s|^GATEWAY_JWT=.*|GATEWAY_JWT=$jwt_token|" "$PROJECT_ROOT/.env"
        fi
    fi

    success "JWT token generated and saved to .env"
    export GATEWAY_JWT="$jwt_token"
    return 0
}

# If called directly, run the function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    ensure_jwt "${1:-}" "${2:-}"
fi
