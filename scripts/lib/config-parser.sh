#!/usr/bin/env bash
# Configuration Parser Library
# Supports both legacy .txt and new YAML formats

parse_gateways_config() {
    local config_dir="${1:-config}"
    local env="${2:-development}"

    # Try YAML first (new format)
    local yaml_file="${config_dir}/${env}/gateways.yaml"
    if [[ -f "$yaml_file" ]] && command -v yq &>/dev/null; then
        echo "# Parsing gateways from YAML: $yaml_file" >&2
        yq eval '.local_gateways[] | select(.enabled == true) | .name + "|" + .url + "|" + .transport' "$yaml_file" 2>/dev/null
        yq eval '.remote_gateways[] | select(.enabled == true) | .name + "|" + .url + "|" + .transport' "$yaml_file" 2>/dev/null
        return 0
    fi

    # Fallback to .txt (legacy format)
    local txt_file="${config_dir}/gateways.txt"
    if [[ -f "$txt_file" ]]; then
        echo "# Parsing gateways from TXT: $txt_file" >&2
        grep -v '^[[:space:]]*#' "$txt_file" | grep -v '^[[:space:]]*$'
        return 0
    fi

    echo "# No gateways config found" >&2
    return 1
}

parse_prompts_config() {
    local config_dir="${1:-config}"
    local env="${2:-development}"

    # Try YAML first (new format)
    local yaml_file="${config_dir}/${env}/prompts.yaml"
    if [[ -f "$yaml_file" ]] && command -v yq &>/dev/null; then
        echo "# Parsing prompts from YAML: $yaml_file" >&2
        yq eval '.prompts[] | .name + "|" + .description + "|" + (.template | sub("\n", "\\n"))' "$yaml_file" 2>/dev/null
        return 0
    fi

    # Fallback to .txt (legacy format)
    local txt_file="${config_dir}/prompts.txt"
    if [[ -f "$txt_file" ]]; then
        echo "# Parsing prompts from TXT: $txt_file" >&2
        grep -v '^[[:space:]]*#' "$txt_file" | grep -v '^[[:space:]]*$'
        return 0
    fi

    echo "# No prompts config found" >&2
    return 1
}

parse_resources_config() {
    local config_dir="${1:-config}"
    local env="${2:-development}"

    # Try YAML first (new format)
    local yaml_file="${config_dir}/${env}/resources.yaml"
    if [[ -f "$yaml_file" ]] && command -v yq &>/dev/null; then
        echo "# Parsing resources from YAML: $yaml_file" >&2
        yq eval '.resources[] | select(.enabled == true) | .name + "|" + .uri + "|" + .description + "|" + .mime_type' "$yaml_file" 2>/dev/null
        return 0
    fi

    # Fallback to .txt (legacy format)
    local txt_file="${config_dir}/resources.txt"
    if [[ -f "$txt_file" ]]; then
        echo "# Parsing resources from TXT: $txt_file" >&2
        grep -v '^[[:space:]]*#' "$txt_file" | grep -v '^[[:space:]]*$'
        return 0
    fi

    echo "# No resources config found" >&2
    return 1
}

# Check if yq is available
check_yaml_support() {
    if command -v yq &>/dev/null; then
        return 0
    else
        echo "# Warning: yq not found. Install with: brew install yq (macOS) or snap install yq (Linux)" >&2
        echo "# Falling back to .txt format" >&2
        return 1
    fi
}
