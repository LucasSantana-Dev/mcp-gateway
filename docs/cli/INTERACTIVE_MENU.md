# Interactive CLI Menu Guide

The `mcp wizard` command now features an enhanced interactive menu system with arrow-key navigation, detailed server previews, and automatic JWT authentication.

## Prerequisites

### Required Dependencies

- **`gum`** - Interactive CLI tool for menus and prompts
  - macOS: `brew install gum`
  - Linux: See [gum installation guide](https://github.com/charmbracelet/gum#installation)
- **`jq`** - JSON processor for parsing server configurations
  - macOS: `brew install jq`
  - Linux: `apt-get install jq` or `yum install jq`

## Features

### 1. Arrow-Key Navigation

Navigate through available virtual servers using ↑↓ arrow keys instead of typing server names manually.

### 2. Real-Time Preview Pane

See detailed information about each server as you navigate:
- Full server description
- Total number of tools
- Authentication requirements (🔒 indicator)
- Complete list of included tools/gateways
- Tags for categorization

### 3. Automatic JWT Authentication

For servers requiring authentication (marked with 🔒):
- Checks for existing JWT in `.env` file
- Reuses valid tokens automatically
- Generates new tokens when needed
- Prompts for credentials only if missing
- Stores JWT persistently in `.env`

### 4. Visual Indicators

- **Icons**: Each server has a unique icon (⭐, 🔀, ⚛️, etc.)
- **Colors**: Category-based color coding
- **Auth Badge**: 🔒 indicates authentication required
- **Tool Count**: Shows number of tools in brackets

## Usage

### Basic Workflow

```bash
./scripts/mcp wizard
```

1. **IDE Selection**: Choose your IDE (windsurf/cursor)
2. **Server Selection**: Navigate with arrow keys, press Enter to select
3. **Authentication** (if needed): Automatic JWT generation
4. **Configuration**: IDE config generated with JWT included

### Example Session

```text
ℹ Starting IDE setup wizard...

Which IDE would you like to configure? [windsurf/cursor]: windsurf

ℹ Loading virtual servers...

┌─────────────────────────────────────────────────────────────────────┐
│ 📦 Select Virtual Server                                            │
├─────────────────────────────────────────────────────────────────────┤
│ ⭐ default - Core dev + search + browser [9 tools]                  │
│ 🔀 router - AI-powered tool routing [1 tool] 🔒                     │
│ → ⚛️  react-nextjs - React/Next.js Development (Full) [10 tools] 🔒 │
│ ⚡ react-nextjs-minimal - React/Next.js (Minimal) [4 tools] 🔒      │
└─────────────────────────────────────────────────────────────────────┘

Preview (shows on right side):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚛️  React/Next.js Development (Full)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tools: 10
Authentication: Required 🔒
Tags: react, nextjs, frontend, full

Included Tools:
  • tool-router - AI-powered tool routing
  • github - GitHub operations
  • filesystem - File system access
  • memory - Persistent memory
  • git-mcp - Git operations
  • chrome-devtools - Browser DevTools
  • playwright - Browser automation
  • snyk - Security scanning
  • tavily - Web search
  • Context7 - Documentation search
```

### Authentication Scenarios

#### Scenario 1: JWT Already Exists

```text
✓ Using existing JWT from .env
ℹ Generating windsurf configuration for server: react-nextjs
```

#### Scenario 2: JWT Missing, Credentials in .env

```text
⚠ This server requires authentication
ℹ Generating JWT token...
✓ JWT token generated and saved to .env
ℹ Generating windsurf configuration for server: react-nextjs
```

#### Scenario 3: JWT Missing, Credentials Missing

```text
⚠ This server requires authentication
ℹ Admin credentials not found in .env
Enter admin email: admin@example.com
Enter JWT secret key: ********
ℹ Generating JWT token...
✓ JWT token generated and saved to .env
ℹ Generating windsurf configuration for server: react-nextjs
```

## Configuration

### Pre-Configure Credentials

To avoid prompts, add credentials to `.env`:

```bash
PLATFORM_ADMIN_EMAIL=admin@example.com
JWT_SECRET_KEY=your-secret-key-here
```

### JWT Storage

JWT tokens are stored in `.env` as:

```bash
GATEWAY_JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The token is automatically:
- Validated on each use
- Regenerated if invalid
- Included in IDE configuration
- Reused across sessions

## Troubleshooting

### gum Not Found

```
✗ gum is required for interactive menus

Install gum:
  macOS:   brew install gum
  Linux:   See https://github.com/charmbracelet/gum#installation
```

**Solution**: Install gum using your package manager.

### jq Not Found

```
✗ jq is required for parsing server configuration

Install jq:
  macOS:   brew install jq
  Linux:   apt-get install jq / yum install jq
```

**Solution**: Install jq using your package manager.

### JWT Generation Failed

```
✗ Failed to generate JWT
```

**Possible causes**:
1. Gateway container not running: `docker compose ps gateway`
2. Invalid credentials in `.env`
3. Missing `JWT_SECRET_KEY` in `.env`

**Solution**:
- Ensure gateway is running: `make start`
- Verify credentials in `.env`
- Run `make jwt` manually to test

### No Servers Available

```
⚠ No virtual servers configured yet
  Run './scripts/gateway/register.sh' first
```

**Solution**: Register gateways and create virtual servers:
```bash
make register
```

## Technical Details

### Files Modified

- **`scripts/mcp`**: Main CLI with interactive menu logic
- **`scripts/utils/ensure-jwt.sh`**: JWT management helper
- **`Makefile`**: Updated to pass JWT_TOKEN parameter
- **`config/virtual-servers.json`**: Server metadata with `requiresAuth` flags

### JWT Helper Script

Location: `scripts/utils/ensure-jwt.sh`

Functions:
- Checks existing JWT in `.env`
- Validates token format
- Generates new tokens using `get_jwt()` from `lib/gateway.sh`
- Prompts for credentials if missing
- Stores tokens persistently
- Exports for current session

### Preview Script

Dynamically generated temporary script that:
- Parses `config/virtual-servers.json`
- Extracts server metadata
- Formats preview with tool lists
- Updates in real-time as you navigate

## Best Practices

1. **Pre-configure credentials**: Add to `.env` to avoid prompts
2. **Keep JWT fresh**: Tokens expire; regenerate periodically
3. **Use non-auth servers**: For testing, use servers without 🔒
4. **Check preview**: Review tool lists before selecting
5. **Verify config**: Check generated IDE config includes JWT

## See Also

- [MCP CLI Documentation](MCP_CLI.md)
- [IDE Setup Guide](../setup/IDE_SETUP_GUIDE.md)
- [Virtual Servers Configuration](../../config/virtual-servers.json)
