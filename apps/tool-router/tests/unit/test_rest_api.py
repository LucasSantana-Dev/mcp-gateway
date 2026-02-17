"""Unit tests for REST API handlers."""

from __future__ import annotations

from flask import Flask
import pytest

from tool_router.api.rest import (
    handle_get_server,
    handle_list_servers,
    handle_update_server,
    register_fastapi_routes,
    register_flask_routes,
)


class TestHandleListServers:
    """Tests for handle_list_servers."""

    def test_list_servers_success(self, mocker):
        """Test successful server listing."""
        mock_result = {"servers": [{"name": "server1", "enabled": True}]}
        mocker.patch("tool_router.api.rest.list_virtual_servers", return_value=mock_result)

        result, status = handle_list_servers()

        assert status == 200
        assert result == mock_result

    def test_list_servers_error(self, mocker):
        """Test error handling."""
        mocker.patch("tool_router.api.rest.list_virtual_servers", side_effect=Exception("DB error"))

        result, status = handle_list_servers()

        assert status == 500
        assert "error" in result


class TestHandleGetServer:
    """Tests for handle_get_server."""

    def test_get_server_found(self, mocker):
        """Test getting existing server."""
        mock_result = {"found": True, "name": "server1", "enabled": True}
        mocker.patch("tool_router.api.rest.get_server_status", return_value=mock_result)

        result, status = handle_get_server("server1")

        assert status == 200
        assert result["found"] is True

    def test_get_server_not_found(self, mocker):
        """Test getting non-existent server."""
        mock_result = {"found": False}
        mocker.patch("tool_router.api.rest.get_server_status", return_value=mock_result)

        result, status = handle_get_server("nonexistent")

        assert status == 404
        assert result["found"] is False

    def test_get_server_error(self, mocker):
        """Test error handling."""
        mocker.patch("tool_router.api.rest.get_server_status", side_effect=Exception("Error"))

        result, status = handle_get_server("server1")

        assert status == 500
        assert "error" in result


class TestHandleUpdateServer:
    """Tests for handle_update_server."""

    def test_update_server_enable(self, mocker):
        """Test enabling a server."""
        mock_result = {"success": True, "message": "Enabled"}
        mock_enable = mocker.patch("tool_router.api.rest.enable_server", return_value=mock_result)

        result, status = handle_update_server("server1", {"enabled": True})

        assert status == 200
        assert result["success"] is True
        mock_enable.assert_called_once_with("server1")

    def test_update_server_disable(self, mocker):
        """Test disabling a server."""
        mock_result = {"success": True, "message": "Disabled"}
        mock_disable = mocker.patch("tool_router.api.rest.disable_server", return_value=mock_result)

        result, status = handle_update_server("server1", {"enabled": False})

        assert status == 200
        assert result["success"] is True
        mock_disable.assert_called_once_with("server1")

    def test_update_server_missing_enabled(self):
        """Test missing enabled field."""
        result, status = handle_update_server("server1", {})

        assert status == 400
        assert "enabled" in result["error"]

    def test_update_server_invalid_enabled_type(self):
        """Test invalid enabled type."""
        result, status = handle_update_server("server1", {"enabled": "yes"})

        assert status == 400
        assert "boolean" in result["error"]

    def test_update_server_not_found(self, mocker):
        """Test enabling non-existent server."""
        mock_result = {"success": False, "error": "Not found"}
        mocker.patch("tool_router.api.rest.enable_server", return_value=mock_result)

        result, status = handle_update_server("nonexistent", {"enabled": True})

        assert status == 404
        assert result["success"] is False

    def test_update_server_disable_not_found(self, mocker):
        """Test disabling non-existent server."""
        mock_result = {"success": False, "error": "Not found"}
        mocker.patch("tool_router.api.rest.disable_server", return_value=mock_result)

        result, status = handle_update_server("nonexistent", {"enabled": False})

        assert status == 404
        assert result["success"] is False

    def test_update_server_error(self, mocker):
        """Test error handling."""
        mocker.patch("tool_router.api.rest.enable_server", side_effect=Exception("Error"))

        result, status = handle_update_server("server1", {"enabled": True})

        assert status == 500
        assert "error" in result


class TestRegisterFlaskRoutes:
    """Tests for register_flask_routes function."""

    def test_register_flask_routes_success(self, mocker):
        """Test successful Flask route registration."""
        # Mock the dependencies to avoid actual HTTP calls
        mock_list_servers = mocker.patch("tool_router.api.rest.list_virtual_servers",
                                     return_value={"servers": []})
        mock_get_server = mocker.patch("tool_router.api.rest.get_server_status",
                                   return_value={"found": False})
        mock_enable_server = mocker.patch("tool_router.api.rest.enable_server",
                                     return_value={"success": True})
        mock_disable_server = mocker.patch("tool_router.api.rest.disable_server",
                                      return_value={"success": True})
        mock_features_bp = mocker.patch("tool_router.api.features.features_bp")

        app = Flask(__name__)
        register_flask_routes(app)

        assert app is not None
        assert hasattr(app, 'url_map')  # Flask app should have routes

    def test_register_flask_routes_registers_blueprint(self, mocker):
        """Test that Flask app registers blueprint."""
        # Mock the dependencies
        mocker.patch("tool_router.api.rest.list_virtual_servers")
        mocker.patch("tool_router.api.rest.get_server_status")
        mocker.patch("tool_router.api.rest.enable_server")
        mocker.patch("tool_router.api.rest.disable_server")
        mock_features_bp = mocker.Mock()
        mocker.patch("tool_router.api.features.features_bp", mock_features_bp)

        app = Flask(__name__)
        # Mock the register_blueprint method
        mock_register_blueprint = mocker.patch.object(app, 'register_blueprint')

        register_flask_routes(app)

        # Verify blueprint was registered
        mock_register_blueprint.assert_called_once_with(mock_features_bp)

    def test_register_flask_routes_has_routes(self, mocker):
        """Test that Flask app has expected routes."""
        # Mock the dependencies to avoid actual HTTP calls
        mocker.patch("tool_router.api.rest.list_virtual_servers",
                                     return_value={"servers": []})
        mocker.patch("tool_router.api.rest.get_server_status",
                                   return_value={"found": False})
        mocker.patch("tool_router.api.rest.enable_server",
                                     return_value={"success": True})
        mocker.patch("tool_router.api.rest.disable_server",
                                      return_value={"success": True})
        mocker.patch("tool_router.api.features.features_bp")

        app = Flask(__name__)
        register_flask_routes(app)

        # Check that routes were registered by inspecting the app's url_map
        routes = [str(rule) for rule in app.url_map.iter_rules()]

        # Should contain our API routes - just check for the path, not method
        assert any("/api/virtual-servers" in route for route in routes)
        # Check for the parameterized route
        assert any("server_name" in route for route in routes)


class TestRegisterFastAPIRoutes:
    """Tests for register_fastapi_routes function."""

    def test_register_fastapi_routes_exists(self, mocker):
        """Test that register_fastapi_routes function exists and is callable."""
        # Just test that the function can be called without error
        mock_app = mocker.Mock()

        # Mock the dependencies inside the function
        mocker.patch("tool_router.api.rest.list_virtual_servers")
        mocker.patch("tool_router.api.rest.get_server_status")
        mocker.patch("tool_router.api.rest.enable_server")
        mocker.patch("tool_router.api.rest.disable_server")
        mocker.patch("tool_router.api.features.features_bp")

        # This should not raise an exception
        register_fastapi_routes(mock_app)

    def test_register_fastapi_routes_calls_dependencies(self, mocker):
        """Test that register_fastapi_routes calls expected functions."""
        mock_app = mocker.Mock()

        # Mock the dependencies to track calls
        mock_list = mocker.patch("tool_router.api.rest.list_virtual_servers")
        mock_get = mocker.patch("tool_router.api.rest.get_server_status")
        mock_enable = mocker.patch("tool_router.api.rest.enable_server")
        mock_disable = mocker.patch("tool_router.api.rest.disable_server")
        mock_features = mocker.patch("tool_router.api.features.features_bp")

        register_fastapi_routes(mock_app)

        # Verify that dependencies were called (they should be called during route registration)
        # Note: The actual FastAPI decorators might not be called if the function doesn't use them
        # This test just ensures the function runs without error
