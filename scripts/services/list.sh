#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
source "$SCRIPT_DIR/lib/bootstrap.sh"
load_env || { log_err "Copy .env.example to .env and set PLATFORM_ADMIN_EMAIL, JWT_SECRET_KEY."; exit 1; }
source "$SCRIPT_DIR/lib/gateway.sh"

GATEWAY_URL="${GATEWAY_URL:-http://localhost:${PORT:-4444}}"
normalize_gateway_url || true
JWT=$(get_jwt) || { log_err "Failed to generate JWT. Is the gateway running? Try: docker compose ps gateway"; exit 1; }

log_section "Service Status"
log_step "Fetching service status from $GATEWAY_URL..."

resp=$(curl -s -w "\n%{http_code}" --connect-timeout 5 --max-time 15 \
  -H "Authorization: Bearer $JWT" \
  "${GATEWAY_URL}/services" 2>&1) || true

code=$(parse_http_code "$resp")
body=$(parse_http_body "$resp")

if [[ "$code" != "200" ]]; then
    log_err "Failed to fetch services (HTTP $code)"
    if [[ -n "$body" ]]; then
        echo "$body" | head -10
    fi
    exit 1
fi

if ! command -v jq &>/dev/null; then
    log_ok "Services loaded (install jq for table format)."
    echo "$body"
    exit 0
fi

services_json=$(echo "$body" | jq -c '.services? // []' 2>/dev/null)
count=$(echo "$services_json" | jq 'length' 2>/dev/null)
log_ok "Found $count service(s)."
log_line

if [[ "$count" -eq 0 ]]; then
    log_info "No services configured."
    exit 0
fi

printf "%-25s %-12s %-12s %s\n" "SERVICE" "STATUS" "ENABLED" "CONTAINER"
printf "%-25s %-12s %-12s %s\n" "-------------------------" "------------" "------------" "----------"

while IFS= read -r line; do
    name=$(echo "$line" | jq -r '.name // empty')
    status=$(echo "$line" | jq -r '.status // "unknown"')
    enabled=$(echo "$line" | jq -r '.enabled // true')
    container_id=$(echo "$line" | jq -r '.container_id // "N/A"')

    if [[ "$enabled" == "true" ]]; then
        enabled_fmt="\u2713 Yes"
    else
        enabled_fmt="\u2717 No"
    fi

    if [[ "$container_id" != "N/A" && ${#container_id} -gt 12 ]]; then
        container_id="${container_id:0:12}..."
    fi

    printf "%-25s %-12s %-12s %s\n" "$name" "$status" "$enabled_fmt" "$container_id"
done < <(echo "$services_json" | jq -c '.[]')

log_line
log_info "Use 'make enable-server SERVICE=name' or 'make disable-server SERVICE=name' to toggle services."
