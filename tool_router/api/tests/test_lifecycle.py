"""Tests for server lifecycle management API."""

from __future__ import annotations

from pathlib import Path

from tool_router.api.lifecycle import (
    disable_server,
    enable_server,
    get_server_status,
    list_virtual_servers,
    parse_server_line,
)


class TestParseServerLine:
    """Test server line parsing."""

    def test_parse_valid_line_with_enabled_true(self):
        """Test parsing line with enabled=true."""
        result = parse_server_line("cursor-default|filesystem,tavily|true")
        assert result is not None
        assert result["name"] == "cursor-default"
        assert result["gateways"] == ["filesystem", "tavily"]
        assert result["enabled"] is True

    def test_parse_valid_line_with_enabled_false(self):
        """Test parsing line with enabled=false."""
        result = parse_server_line("cursor-search|brave-search|false")
        assert result is not None
        assert result["name"] == "cursor-search"
        assert result["gateways"] == ["brave-search"]
        assert result["enabled"] is False

    def test_parse_valid_line_without_enabled_flag(self):
        """Test parsing line without enabled flag (defaults to true)."""
        result = parse_server_line("cursor-browser|playwright")
        assert result is not None
        assert result["name"] == "cursor-browser"
        assert result["gateways"] == ["playwright"]
        assert result["enabled"] is True

    def test_parse_comment_line(self):
        """Test parsing comment line returns None."""
        result = parse_server_line("# This is a comment")
        assert result is None

    def test_parse_empty_line(self):
        """Test parsing empty line returns None."""
        result = parse_server_line("")
        assert result is None

    def test_parse_invalid_line(self):
        """Test parsing invalid line returns None."""
        result = parse_server_line("invalid")
        assert result is None


class TestListVirtualServers:
    """Test listing virtual servers."""

    def test_list_servers_success(self, temp_config_file):
        """Test successful server listing."""
        result = list_virtual_servers()

        assert "servers" in result
        assert "summary" in result
        assert len(result["servers"]) == 3

        # Check summary
        assert result["summary"]["total"] == 3
        assert result["summary"]["enabled"] == 2  # cursor-default and cursor-browser
        assert result["summary"]["disabled"] == 1  # cursor-search

        # Check server details
        servers = {s["name"]: s for s in result["servers"]}
        assert servers["cursor-default"]["enabled"] is True
        assert servers["cursor-search"]["enabled"] is False
        assert servers["cursor-browser"]["enabled"] is True

    def test_list_servers_file_not_found(self, monkeypatch):
        """Test listing when config file doesn't exist."""

        def mock_get_file():
            return Path("/nonexistent/file.txt")

        monkeypatch.setattr("tool_router.api.lifecycle.get_virtual_servers_file", mock_get_file)

        result = list_virtual_servers()

        assert "error" in result
        assert result["summary"]["total"] == 0


class TestGetServerStatus:
    """Test getting server status."""

    def test_get_status_existing_server(self, temp_config_file):
        """Test getting status of existing server."""
        result = get_server_status("cursor-default")

        assert result["found"] is True
        assert result["name"] == "cursor-default"
        assert result["enabled"] is True
        assert "sequential-thinking" in result["gateways"]

    def test_get_status_nonexistent_server(self, temp_config_file):
        """Test getting status of nonexistent server."""
        result = get_server_status("nonexistent")

        assert result["found"] is False
        assert "error" in result


class TestEnableDisableServer:
    """Test enabling and disabling servers."""

    def test_enable_disabled_server(self, temp_config_file):
        """Test enabling a disabled server."""
        # cursor-search starts disabled
        result = enable_server("cursor-search")

        assert result["success"] is True
        assert result["enabled"] is True
        assert "enabled" in result["message"]

        # Verify the change persisted
        status = get_server_status("cursor-search")
        assert status["enabled"] is True

    def test_disable_enabled_server(self, temp_config_file):
        """Test disabling an enabled server."""
        # cursor-default starts enabled
        result = disable_server("cursor-default")

        assert result["success"] is True
        assert result["enabled"] is False
        assert "disabled" in result["message"]

        # Verify the change persisted
        status = get_server_status("cursor-default")
        assert status["enabled"] is False

    def test_enable_nonexistent_server(self, temp_config_file):
        """Test enabling nonexistent server."""
        result = enable_server("nonexistent")

        assert result["success"] is False
        assert "error" in result

    def test_disable_nonexistent_server(self, temp_config_file):
        """Test disabling nonexistent server."""
        result = disable_server("nonexistent")

        assert result["success"] is False
        assert "error" in result

    def test_backup_created_on_update(self, temp_config_file):
        """Test that backup file is created when updating."""
        backup_file = temp_config_file.with_suffix(".txt.bak")

        # Ensure no backup exists initially
        backup_file.unlink(missing_ok=True)

        # Update a server
        enable_server("cursor-search")

        # Verify backup was created
        assert backup_file.exists()
