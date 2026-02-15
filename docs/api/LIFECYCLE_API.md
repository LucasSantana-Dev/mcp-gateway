# Server Lifecycle Management API

## Overview

The Server Lifecycle Management API provides REST endpoints for managing virtual servers in the MCP Gateway. These endpoints allow you to list, query, enable, and disable virtual servers programmatically.

## Base URL

```
http://localhost:4444/api
```

For production deployments, replace with your gateway URL.

## Authentication

Currently, the API endpoints are accessible without authentication when running locally. For production deployments, ensure proper authentication is configured.

## Endpoints

### List All Virtual Servers

Get a list of all virtual servers with their status.

**Endpoint:** `GET /api/virtual-servers`

**Response:**
```json
{
  "servers": [
    {
      "name": "cursor-default",
      "gateways": ["sequential-thinking", "filesystem", "tavily"],
      "enabled": true
    },
    {
      "name": "cursor-search",
      "gateways": ["tavily", "brave-search"],
      "enabled": false
    }
  ],
  "summary": {
    "total": 2,
    "enabled": 1,
    "disabled": 1
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:4444/api/virtual-servers
```

---

### Get Server Status

Get details about a specific virtual server.

**Endpoint:** `GET /api/virtual-servers/{server_name}`

**Parameters:**
- `server_name` (path) - Name of the server

**Response (Success):**
```json
{
  "name": "cursor-default",
  "gateways": ["sequential-thinking", "filesystem"],
  "enabled": true,
  "found": true
}
```

**Response (Not Found):**
```json
{
  "error": "Server 'nonexistent' not found",
  "found": false
}
```

**Status Codes:**
- `200 OK` - Server found
- `404 Not Found` - Server not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:4444/api/virtual-servers/cursor-default
```

---

### Update Server Status

Enable or disable a virtual server.

**Endpoint:** `PATCH /api/virtual-servers/{server_name}`

**Parameters:**
- `server_name` (path) - Name of the server

**Request Body:**
```json
{
  "enabled": true
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Server 'cursor-default' enabled",
  "server_name": "cursor-default",
  "enabled": true
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "error": "Server 'nonexistent' not found"
}
```

**Response (Bad Request):**
```json
{
  "error": "Missing 'enabled' field in request body"
}
```

**Status Codes:**
- `200 OK` - Update successful
- `400 Bad Request` - Invalid request body
- `404 Not Found` - Server not found
- `500 Internal Server Error` - Server error

**Examples:**

Enable a server:
```bash
curl -X PATCH http://localhost:4444/api/virtual-servers/cursor-search \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

Disable a server:
```bash
curl -X PATCH http://localhost:4444/api/virtual-servers/cursor-default \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

---

## Integration Examples

### JavaScript/TypeScript (React)

```typescript
// List all servers
async function listServers() {
  const response = await fetch('http://localhost:4444/api/virtual-servers');
  const data = await response.json();
  return data;
}

// Get server status
async function getServerStatus(serverName: string) {
  const response = await fetch(
    `http://localhost:4444/api/virtual-servers/${serverName}`
  );
  const data = await response.json();
  return data;
}

// Enable/disable server
async function updateServer(serverName: string, enabled: boolean) {
  const response = await fetch(
    `http://localhost:4444/api/virtual-servers/${serverName}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ enabled }),
    }
  );
  const data = await response.json();
  return data;
}

// React component example
function ServerToggle({ serverName, initialEnabled }) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [loading, setLoading] = useState(false);

  const handleToggle = async () => {
    setLoading(true);
    try {
      const result = await updateServer(serverName, !enabled);
      if (result.success) {
        setEnabled(!enabled);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button onClick={handleToggle} disabled={loading}>
      {enabled ? 'Disable' : 'Enable'} {serverName}
    </button>
  );
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:4444/api"

# List all servers
def list_servers():
    response = requests.get(f"{BASE_URL}/virtual-servers")
    return response.json()

# Get server status
def get_server_status(server_name):
    response = requests.get(f"{BASE_URL}/virtual-servers/{server_name}")
    return response.json()

# Enable server
def enable_server(server_name):
    response = requests.patch(
        f"{BASE_URL}/virtual-servers/{server_name}",
        json={"enabled": True}
    )
    return response.json()

# Disable server
def disable_server(server_name):
    response = requests.patch(
        f"{BASE_URL}/virtual-servers/{server_name}",
        json={"enabled": False}
    )
    return response.json()
```

### cURL

```bash
# List all servers
curl http://localhost:4444/api/virtual-servers

# Get server status
curl http://localhost:4444/api/virtual-servers/cursor-default

# Enable server
curl -X PATCH http://localhost:4444/api/virtual-servers/cursor-search \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Disable server
curl -X PATCH http://localhost:4444/api/virtual-servers/cursor-default \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

---

## Error Handling

All endpoints return JSON responses with appropriate HTTP status codes.

**Common Error Response Format:**
```json
{
  "error": "Error message describing what went wrong"
}
```

**Error Codes:**
- `400 Bad Request` - Invalid request parameters or body
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Unexpected server error

---

## MCP Tools

In addition to REST endpoints, the same functionality is available as MCP tools for IDE integration:

- `list_servers_tool()` - List all servers
- `get_server_status_tool(server_name)` - Get server status
- `enable_server_tool(server_name)` - Enable a server
- `disable_server_tool(server_name)` - Disable a server

These tools are automatically available when connecting to the tool-router MCP server.

---

## Notes

- Changes to server status are persisted to `config/virtual-servers.txt`
- Automatic backups are created before modifications (`.txt.bak`)
- After enabling/disabling servers, run `make register` to apply changes
- Disabled servers are not created during registration

---

**Last Updated:** 2026-02-15
**API Version:** 1.0.0
