# Configuration Format Migration Guide

## Overview

The MCP Gateway configuration files have been migrated from simple `.txt` format to structured **YAML** format for better validation, maintainability, and extensibility.

## Migration Date

**February 15, 2026**

## What Changed

### File Locations

**Before**:
```
config/
├── gateways.txt
├── prompts.txt
└── resources.txt
```

**After**:
```
config/
├── development/
│   ├── gateways.yaml
│   ├── prompts.yaml
│   └── resources.yaml
├── production/
│   ├── gateways.yaml
│   ├── prompts.yaml
│   └── resources.yaml
└── test/
    ├── gateways.yaml
    ├── prompts.yaml
    └── resources.yaml
```

### Format Changes

#### 1. Gateways Configuration

**Old Format** (`gateways.txt`):
```
# Comment
sequential-thinking|http://sequential-thinking:8013/sse|SSE
Context7|https://mcp.context7.com/mcp|STREAMABLEHTTP
```

**New Format** (`gateways.yaml`):
```yaml
local_gateways:
  - name: sequential-thinking
    url: http://sequential-thinking:8013/sse
    transport: SSE
    enabled: true
    description: Sequential thinking and reasoning capabilities

remote_gateways:
  - name: Context7
    url: https://mcp.context7.com/mcp
    transport: STREAMABLEHTTP
    enabled: true
    description: Context7 documentation
    auth_required: true
    notes: Requires API key in Admin UI
```

**Benefits**:
- ✅ Clear separation of local vs remote gateways
- ✅ Enable/disable gateways without deleting entries
- ✅ Rich metadata (description, notes, auth requirements)
- ✅ Better validation and error messages
- ✅ Easier to programmatically modify

#### 2. Prompts Configuration

**Old Format** (`prompts.txt`):
```
task-breakdown|Break a goal into steps|Goal: {{goal}}\n\nBreak into steps...
```

**New Format** (`prompts.yaml`):
```yaml
prompts:
  - name: task-breakdown
    description: Break a goal into ordered steps with deliverables
    template: |
      Goal: {{goal}}

      Break into ordered steps. For each step: short title, deliverable, and any dependencies.
    arguments:
      - name: goal
        description: The goal or objective to break down
        required: true
        type: string
    category: planning
    tags:
      - task-management
      - planning
```

**Benefits**:
- ✅ Multi-line templates without escape sequences
- ✅ Explicit argument definitions with types
- ✅ Categorization and tagging
- ✅ Better readability

#### 3. Resources Configuration

**Old Format** (`resources.txt`):
```
context-forge-docs|https://ibm.github.io/mcp-context-forge/|Context Forge documentation|text/html
```

**New Format** (`resources.yaml`):
```yaml
resources:
  - name: context-forge-docs
    uri: https://ibm.github.io/mcp-context-forge/
    description: Context Forge documentation
    mime_type: text/html
    category: documentation
    tags:
      - mcp
      - context-forge
      - ibm
    enabled: true
```

**Benefits**:
- ✅ Enable/disable resources
- ✅ Categorization and tagging
- ✅ Better organization

## Backward Compatibility

The system supports **both formats** simultaneously:

1. **YAML files take precedence** if `yq` is installed
2. **Falls back to .txt files** if YAML not found or `yq` not available
3. **No breaking changes** - existing `.txt` files continue to work

### Installation Requirements

To use YAML format, install `yq`:

```bash
# macOS
brew install yq

# Linux (snap)
snap install yq

# Linux (binary)
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
```

## Environment-Specific Configurations

YAML format enables environment-specific configs:

```bash
# Development (default)
config/development/gateways.yaml

# Production
config/production/gateways.yaml

# Testing
config/test/gateways.yaml
```

Set environment via:
```bash
export CONFIG_ENV=production
# or
CONFIG_ENV=production ./scripts/gateway/register.sh
```

## Migration Steps

### Automatic Migration

The YAML files have been pre-generated in `config/development/` with:
- All existing gateways, prompts, and resources
- Enhanced metadata and descriptions
- Proper categorization

### Manual Migration (if needed)

1. **Copy your customizations** from `.txt` files
2. **Edit YAML files** in `config/development/`
3. **Test**: `./scripts/gateway/register.sh`
4. **Verify**: Check Admin UI for registered items

### Validation

Validate YAML syntax:
```bash
yq eval config/development/gateways.yaml
yq eval config/development/prompts.yaml
yq eval config/development/resources.yaml
```

## New Features

### 1. Enable/Disable Without Deletion

```yaml
local_gateways:
  - name: git-mcp
    url: http://git-mcp:8028/sse
    transport: SSE
    enabled: false  # Temporarily disabled
    notes: Connection reset errors
```

### 2. Rich Metadata

```yaml
- name: Context7
  url: https://mcp.context7.com/mcp
  transport: STREAMABLEHTTP
  enabled: true
  description: Context7 documentation and code examples
  auth_required: true
  notes: Requires API key in Admin UI (Passthrough Headers)
  category: documentation
  tags:
    - documentation
    - context
```

### 3. Argument Validation

```yaml
prompts:
  - name: code-review
    arguments:
      - name: code
        description: The code to review
        required: true
        type: string
```

### 4. Categorization

```yaml
resources:
  - name: pytest-docs
    category: documentation
    tags:
      - python
      - testing
      - pytest
```

## Schema Validation (Future)

JSON Schema for validation:

```bash
# Validate against schema
yq eval config/development/gateways.yaml | \
  ajv validate -s config/schemas/gateways.schema.json
```

## Troubleshooting

### Issue: "yq: command not found"

**Solution**: Install `yq` or continue using `.txt` files

### Issue: YAML syntax error

**Solution**: Validate with `yq eval <file>`

### Issue: Gateways not registering

**Solution**:
1. Check `enabled: true` in YAML
2. Verify `REGISTER_GATEWAYS=true` in `.env`
3. Check logs: `docker compose logs gateway`

## Best Practices

1. **Use YAML for new configs** - Better structure and validation
2. **Keep .txt as backup** - During transition period
3. **Environment-specific configs** - Separate dev/prod/test
4. **Document custom gateways** - Use `description` and `notes` fields
5. **Use tags** - For better organization and search
6. **Validate before commit** - Run `yq eval` on YAML files

## Examples

### Adding a New Gateway

```yaml
local_gateways:
  - name: my-custom-gateway
    url: http://my-gateway:9000/sse
    transport: SSE
    enabled: true
    description: My custom MCP gateway
    notes: |
      Additional setup instructions:
      1. Configure API key
      2. Set environment variables
    tags:
      - custom
      - experimental
```

### Adding a New Prompt

```yaml
prompts:
  - name: security-audit
    description: Audit code for security vulnerabilities
    template: |
      Audit the following code for security issues:

      {{code}}

      Focus on:
      - SQL injection
      - XSS vulnerabilities
      - Authentication issues
    arguments:
      - name: code
        description: Code to audit
        required: true
        type: string
    category: security
    tags:
      - security
      - audit
      - code-quality
```

## References

- **YAML Spec**: https://yaml.org/spec/
- **yq Documentation**: https://mikefarah.gitbook.io/yq/
- **MCP Gateway Docs**: `docs/architecture/OVERVIEW.md`
- **Registration Script**: `scripts/gateway/register.sh`

---

**Migration Status**: ✅ Complete
**Backward Compatible**: ✅ Yes
**Breaking Changes**: ❌ None
