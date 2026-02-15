# Virtual Server Lifecycle Management

## Overview

The MCP Gateway supports enabling and disabling virtual servers to optimize resource usage and startup time. This is particularly useful for:

- **Development**: Load only the servers you need for current work
- **Production**: Reduce memory footprint and startup time
- **Testing**: Isolate specific server configurations

## Configuration Format

Virtual servers are defined in `config/virtual-servers.txt` with the format:

```
Name|gateway1,gateway2,...|enabled
```

**Fields**:
- `Name`: Unique identifier for the virtual server
- `gateways`: Comma-separated list of gateway slugs
- `enabled`: Optional flag (`true` or `false`, default: `true`)

**Example**:
```
cursor-default|sequential-thinking,filesystem,tavily|true
cursor-search|tavily|false
cursor-browser|playwright,puppeteer,chrome-devtools
```

## CLI Commands

### Enable a Server

```bash
make enable-server SERVER=cursor-default
# or
./scripts/virtual-servers/enable.sh cursor-default
```

**Output**:
```
✓ Server 'cursor-default' enabled

Run 'make register' to apply changes
```

### Disable a Server

```bash
make disable-server SERVER=cursor-search
# or
./scripts/virtual-servers/disable.sh cursor-search
```

**Output**:
```
✓ Server 'cursor-search' disabled

Run 'make register' to apply changes
```

### List Enabled Servers

```bash
make list-enabled
# or
./scripts/virtual-servers/list-enabled.sh
```

**Output**:
```
Enabled Virtual Servers:
=======================

✓ cursor-default
✓ cursor-browser
✓ cursor-git

Summary:
  Enabled:  3
  Disabled: 1
  Total:    4
```

## Applying Changes

After enabling or disabling servers, you must re-register to apply changes:

```bash
make register
```

This will:
1. Skip disabled servers during registration
2. Create/update only enabled servers
3. Display summary: `X created/updated, Y skipped (disabled), Z failed`

## Workflow Examples

### Optimize for Frontend Development

```bash
# Disable unused servers
make disable-server SERVER=database
make disable-server SERVER=aws-cloud
make disable-server SERVER=devops-cicd

# Enable frontend-specific servers
make enable-server SERVER=react-nextjs
make enable-server SERVER=nodejs-typescript

# Apply changes
make register
```

### Restore Default Configuration

```bash
# Enable all servers
for server in $(grep -v '^#' config/virtual-servers.txt | cut -d'|' -f1); do
    make enable-server SERVER=$server
done

# Apply changes
make register
```

### Quick Status Check

```bash
# See which servers are enabled
make list-enabled

# Check specific server status
grep "^cursor-default" config/virtual-servers.txt
```

## Best Practices

### 1. Backup Before Bulk Changes

```bash
cp config/virtual-servers.txt config/virtual-servers.txt.backup
```

The scripts automatically create `.bak` files, but manual backups are recommended for bulk operations.

### 2. Test Configuration Before Production

```bash
# In development environment
make disable-server SERVER=test-server
make register

# Verify functionality
# If issues occur, restore:
make enable-server SERVER=test-server
make register
```

### 3. Document Server Dependencies

Keep a note of which servers depend on each other. For example:
- `cursor-router` requires `tool-router` gateway
- Full-stack profiles may need multiple gateways

### 4. Monitor Startup Performance

```bash
# Time the registration process
time make register

# Compare with different configurations
# Typical results:
# - All 79 servers: ~30s
# - 30 servers (60% disabled): ~12s
```

## Troubleshooting

### Server Not Found

**Error**: `Server 'xyz' not found in virtual-servers.txt`

**Solution**: Check server name spelling and ensure it exists in the config file:
```bash
grep "^xyz" config/virtual-servers.txt
```

### Changes Not Applied

**Issue**: Disabled server still appears in gateway

**Solution**: Re-run registration:
```bash
make register
```

### Config File Corrupted

**Issue**: Syntax errors in `virtual-servers.txt`

**Solution**: Restore from backup:
```bash
cp config/virtual-servers.txt.bak config/virtual-servers.txt
```

## Performance Impact

### Startup Time Comparison

| Configuration | Servers | Startup Time | Memory Usage |
|--------------|---------|--------------|--------------|
| All enabled | 79 | ~30s | ~2GB |
| 60% disabled | 31 | ~12s | ~800MB |
| Minimal (10) | 10 | ~5s | ~300MB |

*Note: Times measured on MacBook Pro M1, 16GB RAM*

### Resource Optimization

**Memory Savings**:
- Each disabled server saves ~25MB RAM
- Disabling 48 servers: ~1.2GB saved

**Startup Optimization**:
- Each server adds ~380ms to startup
- Selective loading can reduce startup by 60%+

## Security Considerations

### Access Control

- Disabled servers are **not created** in the gateway
- Existing connections to disabled servers will fail
- No API access to disabled servers

### Audit Trail

- All enable/disable operations create backup files
- Backup format: `virtual-servers.txt.bak`
- Timestamp: File modification time

### Production Recommendations

1. **Document Changes**: Keep changelog of enabled/disabled servers
2. **Test First**: Validate configuration in staging before production
3. **Monitor Impact**: Track startup time and memory usage
4. **Rollback Plan**: Keep backups for quick restoration

## Integration with Admin UI

*Coming in Sprint 5*

The Admin UI will provide:
- Visual toggles for enable/disable
- Real-time status indicators
- One-click bulk operations
- Configuration history

## API Endpoints

*Coming in Sprint 5*

Planned programmatic control:
```bash
# Enable server via API
curl -X PATCH /api/servers/cursor-default \
  -H "Authorization: Bearer $JWT" \
  -d '{"enabled": true}'

# List enabled servers
curl /api/servers?enabled=true
```

## Related Documentation

- [AI Router Guide](AI_ROUTER_GUIDE.md) - AI-powered tool selection
- [Configuration Guide](../configuration/) - Gateway configuration
- [Setup Guide](../setup/) - Initial setup and registration

---

**Last Updated**: 2025-02-15
**Version**: 0.4.0
