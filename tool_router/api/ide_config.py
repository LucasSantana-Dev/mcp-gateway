"""IDE configuration generator API.

Generates MCP configuration snippets for Windsurf and Cursor IDEs.
"""

from __future__ import annotations

from typing import Literal


def generate_ide_config(
    ide: Literal["windsurf", "cursor"],
    server_name: str,
    server_uuid: str,
    gateway_url: str = "http://localhost:4444",
    jwt_token: str | None = None,
) -> dict[str, dict]:
    """Generate IDE-specific MCP configuration.

    Args:
        ide: Target IDE (windsurf or cursor)
        server_name: Name for the MCP server entry
        server_uuid: UUID of the virtual server
        gateway_url: Gateway base URL
        jwt_token: Optional JWT token for authenticated access

    Returns:
        Dictionary with mcpServers configuration for the IDE

    Raises:
        ValueError: If ide is not 'windsurf' or 'cursor', or if server_name,
                    server_uuid, or gateway_url are empty strings, or if
                    jwt_token is an empty string (must be None or non-empty).

    Example:
        >>> config = generate_ide_config("windsurf", "my-server", "abc-123")
        >>> print(config["mcpServers"]["my-server"]["command"])
        'npx'
    """
    # Validate inputs
    if ide not in ("windsurf", "cursor"):
        raise ValueError(f"ide must be 'windsurf' or 'cursor', got: {ide}")
    if not server_name:
        raise ValueError("server_name must be a non-empty string")
    if not server_uuid:
        raise ValueError("server_uuid must be a non-empty string")
    if not gateway_url:
        raise ValueError("gateway_url must be a non-empty string")
    if jwt_token is not None and not jwt_token:
        raise ValueError("jwt_token must be None or a non-empty string")

    mcp_url = f"{gateway_url}/servers/{server_uuid}/mcp"
    return _generate_mcp_config(server_name, mcp_url, jwt_token)


def _generate_mcp_config(
    server_name: str,
    mcp_url: str,
    jwt_token: str | None,
) -> dict[str, dict]:
    """Generate MCP configuration for Windsurf and Cursor.

    Both IDEs use the same standard MCP JSON format with npx client.

    Args:
        server_name: Name for the MCP server entry
        mcp_url: Full MCP endpoint URL
        jwt_token: Optional JWT token for authenticated access

    Returns:
        Dictionary with mcpServers configuration
    """
    args = ["-y", "@mcp-gateway/client", f"--url={mcp_url}"]
    if jwt_token:
        args.append(f"--token={jwt_token}")

    return {
        "mcpServers": {
            server_name: {
                "command": "npx",
                "args": args,
                "env": {},
            }
        }
    }


def get_ide_config_paths() -> dict[str, str]:
    """Get default config file paths for supported IDEs.

    Returns:
        Dictionary mapping IDE name to config file path
    """
    return {
        "windsurf": ".windsurf/mcp.json",
        "cursor": "~/.cursor/mcp.json",
    }
