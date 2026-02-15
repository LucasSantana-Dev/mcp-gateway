"""Tests for REST API endpoints."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from tool_router.api.rest import (
    handle_get_server,
    handle_list_servers,
    handle_update_server,
)


@pytest.fixture
def temp_config_file(monkeypatch):
    """Create a temporary virtual-servers.txt file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# Test configuration\n")
        f.write("cursor-default|sequential-thinking,filesystem|true\n")
        f.write("cursor-search|tavily,brave-search|false\n")
        f.write("cursor-browser|playwright,puppeteer\n")
        temp_path = Path(f.name)

    def mock_get_file():
        return temp_path

    monkeypatch.setattr("tool_router.api.lifecycle.get_virtual_servers_file", mock_get_file)

    yield temp_path

    temp_path.unlink(missing_ok=True)
    backup = temp_path.with_suffix(".txt.bak")
    backup.unlink(missing_ok=True)


class TestHandleListServers:
    """Test list servers endpoint handler."""

    def test_list_servers_success(self, temp_config_file):
        """Test successful server listing."""
        result, status = handle_list_servers()

        assert status == 200
        assert "servers" in result
        assert "summary" in result
        assert len(result["servers"]) == 3
        assert result["summary"]["total"] == 3
        assert result["summary"]["enabled"] == 2
        assert result["summary"]["disabled"] == 1

    def test_list_servers_error_handling(self, monkeypatch):
        """Test error handling in list servers."""

        def mock_list_error():
            raise RuntimeError("Test error")

        monkeypatch.setattr("tool_router.api.rest.list_virtual_servers", mock_list_error)

        result, status = handle_list_servers()

        assert status == 500
        assert "error" in result


class TestHandleGetServer:
    """Test get server endpoint handler."""

    def test_get_existing_server(self, temp_config_file):
        """Test getting an existing server."""
        result, status = handle_get_server("cursor-default")

        assert status == 200
        assert result["found"] is True
        assert result["name"] == "cursor-default"
        assert result["enabled"] is True

    def test_get_nonexistent_server(self, temp_config_file):
        """Test getting a nonexistent server."""
        result, status = handle_get_server("nonexistent")

        assert status == 404
        assert result["found"] is False
        assert "error" in result

    def test_get_server_error_handling(self, monkeypatch):
        """Test error handling in get server."""

        def mock_status_error(name):
            raise RuntimeError("Test error")

        monkeypatch.setattr("tool_router.api.rest.get_server_status", mock_status_error)

        result, status = handle_get_server("test")

        assert status == 500
        assert "error" in result


class TestHandleUpdateServer:
    """Test update server endpoint handler."""

    def test_enable_server_success(self, temp_config_file):
        """Test enabling a server."""
        result, status = handle_update_server("cursor-search", {"enabled": True})

        assert status == 200
        assert result["success"] is True
        assert result["enabled"] is True

    def test_disable_server_success(self, temp_config_file):
        """Test disabling a server."""
        result, status = handle_update_server("cursor-default", {"enabled": False})

        assert status == 200
        assert result["success"] is True
        assert result["enabled"] is False

    def test_update_nonexistent_server(self, temp_config_file):
        """Test updating a nonexistent server."""
        result, status = handle_update_server("nonexistent", {"enabled": True})

        assert status == 404
        assert result["success"] is False

    def test_update_missing_enabled_field(self, temp_config_file):
        """Test update with missing enabled field."""
        result, status = handle_update_server("cursor-default", {})

        assert status == 400
        assert "error" in result
        assert "enabled" in result["error"]

    def test_update_invalid_enabled_type(self, temp_config_file):
        """Test update with invalid enabled type."""
        result, status = handle_update_server("cursor-default", {"enabled": "yes"})

        assert status == 400
        assert "error" in result
        assert "boolean" in result["error"]

    def test_update_server_error_handling(self, monkeypatch):
        """Test error handling in update server."""

        def mock_enable_error(name):
            raise RuntimeError("Test error")

        monkeypatch.setattr("tool_router.api.rest.enable_server", mock_enable_error)

        result, status = handle_update_server("test", {"enabled": True})

        assert status == 500
        assert "error" in result
