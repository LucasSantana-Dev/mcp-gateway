"""Server lifecycle management API endpoints."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def get_virtual_servers_file() -> Path:
    """Get path to virtual-servers.txt configuration file."""
    repo_root = Path(__file__).parent.parent.parent
    config_dir = os.environ.get("CONFIG_DIR", repo_root / "config")
    return Path(config_dir) / "virtual-servers.txt"


def parse_server_line(line: str) -> dict[str, Any] | None:
    """Parse a line from virtual-servers.txt.

    Format: Name|gateways|enabled
    Returns dict with name, gateways, enabled or None if invalid.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split("|")
    if len(parts) < 2:
        return None

    name = parts[0].strip()
    gateways = [g.strip() for g in parts[1].split(",")]

    # Parse enabled flag (default true)
    enabled = True
    if len(parts) >= 3:
        enabled_flag = parts[2].strip().lower()
        enabled = enabled_flag != "false"

    return {
        "name": name,
        "gateways": gateways,
        "enabled": enabled,
    }


def list_virtual_servers() -> dict[str, Any]:
    """List all virtual servers with their status.

    Returns:
        Dict with servers list and summary statistics.
    """
    config_file = get_virtual_servers_file()

    if not config_file.exists():
        return {
            "servers": [],
            "summary": {
                "total": 0,
                "enabled": 0,
                "disabled": 0,
            },
            "error": f"Configuration file not found: {config_file}",
        }

    servers = []
    enabled_count = 0
    disabled_count = 0

    with config_file.open() as f:
        for line in f:
            server = parse_server_line(line)
            if server:
                servers.append(server)
                if server["enabled"]:
                    enabled_count += 1
                else:
                    disabled_count += 1

    return {
        "servers": servers,
        "summary": {
            "total": len(servers),
            "enabled": enabled_count,
            "disabled": disabled_count,
        },
    }


def get_server_status(server_name: str) -> dict[str, Any]:
    """Get status of a specific virtual server.

    Args:
        server_name: Name of the server to check.

    Returns:
        Dict with server details or error.
    """
    config_file = get_virtual_servers_file()

    if not config_file.exists():
        return {
            "error": f"Configuration file not found: {config_file}",
        }

    with config_file.open() as f:
        for line in f:
            server = parse_server_line(line)
            if server and server["name"] == server_name:
                return {
                    "name": server["name"],
                    "gateways": server["gateways"],
                    "enabled": server["enabled"],
                    "found": True,
                }

    return {
        "error": f"Server '{server_name}' not found",
        "found": False,
    }


def update_server_status(server_name: str, enabled: bool) -> dict[str, Any]:
    """Enable or disable a virtual server.

    Args:
        server_name: Name of the server to update.
        enabled: True to enable, False to disable.

    Returns:
        Dict with success status and message.
    """
    config_file = get_virtual_servers_file()

    if not config_file.exists():
        return {
            "success": False,
            "error": f"Configuration file not found: {config_file}",
        }

    # Read all lines
    lines = []
    server_found = False

    with config_file.open() as f:
        for line in f:
            original_line = line
            server = parse_server_line(line)

            if server and server["name"] == server_name:
                server_found = True
                # Update the line with new enabled status
                enabled_str = "true" if enabled else "false"
                gateways_str = ",".join(server["gateways"])
                new_line = f"{server['name']}|{gateways_str}|{enabled_str}\n"
                lines.append(new_line)
            else:
                lines.append(original_line)

    if not server_found:
        return {
            "success": False,
            "error": f"Server '{server_name}' not found",
        }

    # Create backup
    backup_file = config_file.with_suffix(".txt.bak")
    config_file.rename(backup_file)

    # Write updated content
    with config_file.open("w") as f:
        f.writelines(lines)

    action = "enabled" if enabled else "disabled"
    return {
        "success": True,
        "message": f"Server '{server_name}' {action}",
        "server_name": server_name,
        "enabled": enabled,
    }


def enable_server(server_name: str) -> dict[str, Any]:
    """Enable a virtual server.

    Args:
        server_name: Name of the server to enable.

    Returns:
        Dict with success status and message.
    """
    return update_server_status(server_name, enabled=True)


def disable_server(server_name: str) -> dict[str, Any]:
    """Disable a virtual server.

    Args:
        server_name: Name of the server to disable.

    Returns:
        Dict with success status and message.
    """
    return update_server_status(server_name, enabled=False)
