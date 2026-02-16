# Feature Toggle System

The MCP Gateway includes a centralized feature toggle system for fine-grained control over functionality.

## Overview

The feature toggle system provides:
- **17 fine-grained feature flags** organized by category
- **YAML configuration** with environment variable overrides
- **REST API** for runtime management
- **Web UI** for visual management at `/admin/features`
- **Backward compatibility** with existing environment variables

## Feature Categories

### Core Features (4)
- `FEATURE_CORE_AI_ROUTER` - AI-powered tool selection using Ollama
- `FEATURE_CORE_HYBRID_SCORING` - AI + keyword hybrid scoring
- `FEATURE_CORE_TOOL_SEARCH` - Search tools MCP endpoint
- `FEATURE_CORE_EXECUTE_TASK` - Execute task MCP endpoint

### API Features (5)
- `FEATURE_API_HEALTH` - Health check endpoints
- `FEATURE_API_METRICS` - Metrics and observability endpoints
- `FEATURE_API_LIFECYCLE` - Virtual server lifecycle management
- `FEATURE_API_IDE_CONFIG` - IDE configuration generator
- `FEATURE_API_FEATURES` - Feature toggle management API

### Tool Features (4)
- `FEATURE_TOOL_LIST_SERVERS` - List virtual servers MCP tool
- `FEATURE_TOOL_GET_SERVER_STATUS` - Get server status MCP tool
- `FEATURE_TOOL_ENABLE_SERVER` - Enable server MCP tool
- `FEATURE_TOOL_DISABLE_SERVER` - Disable server MCP tool

### UI Features (4)
- `FEATURE_UI_WEB_ADMIN` - Next.js web admin interface
- `FEATURE_UI_FEATURE_TOGGLES` - Feature toggle management page
- `FEATURE_UI_SERVER_MANAGEMENT` - Virtual server management page
- `FEATURE_UI_GATEWAY_MONITORING` - Gateway status monitoring page

## Configuration

### YAML Configuration

Primary configuration file: `config/features.yaml`

```yaml
version: "1.0"
features:
  core_ai_router:
    enabled: true
    description: "AI-powered tool selection using Ollama"
    category: "core"
    requires_restart: true
    env_var: "FEATURE_CORE_AI_ROUTER"
    backward_compat: "ROUTER_AI_ENABLED"
```

### Environment Variables

All features can be controlled via environment variables:

```bash
# Core Features
FEATURE_CORE_AI_ROUTER=true
FEATURE_CORE_HYBRID_SCORING=true
FEATURE_CORE_TOOL_SEARCH=true
FEATURE_CORE_EXECUTE_TASK=true

# API Features
FEATURE_API_HEALTH=true
FEATURE_API_METRICS=true
FEATURE_API_LIFECYCLE=true
FEATURE_API_IDE_CONFIG=true
FEATURE_API_FEATURES=true

# Tool Features
FEATURE_TOOL_LIST_SERVERS=true
FEATURE_TOOL_GET_SERVER_STATUS=true
FEATURE_TOOL_ENABLE_SERVER=true
FEATURE_TOOL_DISABLE_SERVER=true

# UI Features
FEATURE_UI_WEB_ADMIN=true
FEATURE_UI_FEATURE_TOGGLES=true
FEATURE_UI_SERVER_MANAGEMENT=true
FEATURE_UI_GATEWAY_MONITORING=true
```

### Precedence

Environment variables take precedence over YAML configuration:

1. **Environment Variables** (highest priority)
2. **YAML Configuration**
3. **Default Values** (all features enabled by default)

## Usage

### Python Code

```python
from tool_router.core.features import is_feature_enabled, get_feature_flags

# Check if a feature is enabled
if is_feature_enabled("core_ai_router"):
    # Use AI-powered tool selection
    pass

# Get all feature flags
flags = get_feature_flags()
all_features = flags.get_all_features()

# Get features by category
core_features = flags.get_features_by_category("core")
```

### REST API

See [FEATURES_API.md](api/FEATURES_API.md) for complete API documentation.

```bash
# List all features
curl http://localhost:8030/api/features

# Get specific feature
curl http://localhost:8030/api/features/core_ai_router

# Toggle feature
curl -X PATCH http://localhost:8030/api/features/core_ai_router \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Reload from YAML
curl -X POST http://localhost:8030/api/features/reload
```

### Web UI

Access the web admin interface at `http://localhost:4444/admin/features` to:
- View all 17 feature flags grouped by category
- Toggle features on/off with visual switches
- See which features require restart
- Reload configuration from YAML

## Backward Compatibility

The system maintains backward compatibility with existing environment variables:

- `ROUTER_AI_ENABLED` → `FEATURE_CORE_AI_ROUTER`

Both variables work, with the new naming convention taking precedence if both are set.

## Best Practices

1. **Use environment variables** for deployment-specific overrides
2. **Use YAML configuration** for default feature states
3. **Document feature dependencies** if features depend on each other
4. **Test feature combinations** to ensure no breaking interactions
5. **Monitor feature usage** via metrics endpoints

## Troubleshooting

### Feature not taking effect

1. Check environment variable spelling (case-sensitive)
2. Verify YAML syntax is valid
3. Check if feature requires restart (`requires_restart: true`)
4. Reload configuration: `curl -X POST http://localhost:8030/api/features/reload`

### Configuration file not found

The system gracefully handles missing `config/features.yaml` by using defaults. All features default to `enabled: true` for backward compatibility.

### Environment variable not working

Ensure the variable is:
- Set before starting the application
- Using correct format: `true`, `1`, or `yes` (case-insensitive)
- Not overridden by a later configuration load

## Development

### Adding New Features

1. Add feature to `config/features.yaml`
2. Add environment variable to `.env.example`
3. Update this documentation
4. Add feature check in code where needed
5. Add tests for the new feature flag

### Testing

Run the feature toggle test suite:

```bash
pytest tool_router/core/tests/test_features.py -v
```

## References

- [Features API Documentation](api/FEATURES_API.md)
- [Web Admin Guide](WEB_ADMIN_GUIDE.md)
- [Configuration Guide](../README.md#configuration)
