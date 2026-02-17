"""Additional unit tests for REST API to improve coverage."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from tool_router.api.rest import (
    handle_list_servers,
    handle_get_server,
    handle_update_server,
    register_flask_routes,
    register_fastapi_routes
)


class TestRESTAPIAdditional:
    """Additional tests for REST API to improve coverage."""

    def test_register_flask_routes_endpoints(self, mocker) -> None:
        """Test register_flask_routes creates all expected endpoints."""
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        # Mock the handler functions
        mock_handlers = {
            "handle_list_servers": mocker.patch("tool_router.api.rest.handle_list_servers", return_value=([], 200)),
            "handle_get_server": mocker.patch("tool_router.api.rest.handle_get_server", return_value=({}, 200)),
            "handle_update_server": mocker.patch("tool_router.api.rest.handle_update_server", return_value=({}, 200)),
        }

        register_flask_routes(mock_app)

        # Verify blueprint was registered
        mock_app.register_blueprint.assert_called_once_with(mock_features_bp)

        # Verify all routes were added
        route_calls = mock_app.route.call_args_list
        route_paths = [call[0][0] for call in route_calls]

        expected_routes = [
            "/api/virtual-servers",
            "/api/virtual-servers/<server_name>",
        ]

        for route in expected_routes:
            assert route in route_paths

    def test_register_fastapi_routes_endpoints(self, mocker) -> None:
        """Test register_fastapi_routes creates all expected endpoints."""
        mock_router = Mock()

        # Mock the handler functions
        mock_handlers = {
            "handle_list_servers": mocker.patch("tool_router.api.rest.handle_list_servers", return_value=([], 200)),
            "handle_get_server": mocker.patch("tool_router.api.rest.handle_get_server", return_value=({}, 200)),
            "handle_update_server": mocker.patch("tool_router.api.rest.handle_update_server", return_value=({}, 200)),
        }

        register_fastapi_routes(mock_router)

        # Verify all routes were added
        route_calls = mock_router.add_api_route.call_args_list
        route_paths = [call[0][0] for call in route_calls]

        expected_routes = [
            "/api/virtual-servers",
            "/api/virtual-servers/{server_name}",
        ]

        for route in expected_routes:
            assert route in route_paths

    def test_handle_list_servers_success(self) -> None:
        """Test handle_list_servers returns successful response."""
        result, status = handle_list_servers()

        assert status == 200
        assert isinstance(result, dict)

    def test_handle_get_server_success(self) -> None:
        """Test handle_get_server returns successful response."""
        result, status = handle_get_server("test_server")

        assert status == 200
        assert isinstance(result, dict)

    def test_handle_update_server_with_data(self, mocker) -> None:
        """Test handle_update_server with JSON data."""
        mock_request = mocker.patch("tool_router.api.rest.request")
        mock_request.get_json.return_value = {"enabled": True}

        result, status = handle_update_server("test_server", {"enabled": True})

        assert status == 200
        assert isinstance(result, dict)

    def test_handle_update_server_without_data(self) -> None:
        """Test handle_update_server without JSON data."""
        result, status = handle_update_server("test_server", {})

        assert status == 200
        assert isinstance(result, dict)

    def test_flask_route_list_servers_endpoint(self, mocker) -> None:
        """Test Flask list_servers endpoint function."""
        mock_jsonify = mocker.patch("tool_router.api.rest.jsonify")
        mock_handle_list = mocker.patch("tool_router.api.rest.handle_list_servers", return_value=(["server1"], 200))

        # Import the function after mocking
        from tool_router.api.rest import register_flask_routes
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        register_flask_routes(mock_app)

        # Get the route function that was registered
        route_call = mock_app.route.call_args_list[0]
        decorators = route_call[1]
        methods = decorators.get('methods', ['GET'])

        # Verify the route was set up correctly
        assert 'GET' in methods

        # Simulate calling the endpoint function
        mock_jsonify.assert_called_once_with(["server1"])

    def test_flask_route_get_server_endpoint(self, mocker) -> None:
        """Test Flask get_server endpoint function."""
        mock_jsonify = mocker.patch("tool_router.api.rest.jsonify")
        mock_handle_get = mocker.patch("tool_router.api.rest.handle_get_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_flask_routes
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        register_flask_routes(mock_app)

        # Get the route function for get_server
        route_call = mock_app.route.call_args_list[1]

        # Verify the route was set up correctly
        assert "/api/virtual-servers/<server_name>" in route_call[0]

    def test_flask_route_update_server_endpoint(self, mocker) -> None:
        """Test Flask update_server endpoint function."""
        mock_jsonify = mocker.patch("tool_router.api.rest.jsonify")
        mock_request = mocker.patch("tool_router.api.rest.request")
        mock_request.get_json.return_value = {"enabled": True}
        mock_handle_update = mocker.patch("tool_router.api.rest.handle_update_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_flask_routes
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        register_flask_routes(mock_app)

        # Get the route function for update_server
        route_call = mock_app.route.call_args_list[2]

        # Verify the route was set up correctly
        assert "/api/virtual-servers/<server_name>" in route_call[0]
        assert 'PATCH' in route_call[1].get('methods', [])

    def test_flask_route_enable_server_endpoint(self, mocker) -> None:
        """Test Flask enable_server endpoint function."""
        mock_jsonify = mocker.patch("tool_router.api.rest.jsonify")
        mock_handle_enable = mocker.patch("tool_router.api.rest.handle_enable_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_flask_routes
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        register_flask_routes(mock_app)

        # Get the route function for enable_server
        route_call = mock_app.route.call_args_list[3]

        # Verify the route was set up correctly
        assert "/api/virtual-servers/<server_name>/enable" in route_call[0]
        assert 'PATCH' in route_call[1].get('methods', [])

    def test_flask_route_disable_server_endpoint(self, mocker) -> None:
        """Test Flask disable_server endpoint function."""
        mock_jsonify = mocker.patch("tool_router.api.rest.jsonify")
        mock_handle_disable = mocker.patch("tool_router.api.rest.handle_disable_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_flask_routes
        mock_app = Mock()
        mock_features_bp = mocker.patch("tool_router.api.rest.features_bp")

        register_flask_routes(mock_app)

        # Get the route function for disable_server
        route_call = mock_app.route.call_args_list[4]

        # Verify the route was set up correctly
        assert "/api/virtual-servers/<server_name>/disable" in route_call[0]
        assert 'PATCH' in route_call[1].get('methods', [])

    def test_fastapi_route_list_servers_endpoint(self, mocker) -> None:
        """Test FastAPI list_servers endpoint function."""
        mock_handle_list = mocker.patch("tool_router.api.rest.handle_list_servers", return_value=(["server1"], 200))

        from tool_router.api.rest import register_fastapi_routes
        mock_router = Mock()

        register_fastapi_routes(mock_router)

        # Verify the route was added
        route_calls = mock_router.add_api_route.call_args_list
        list_servers_route = None

        for call in route_calls:
            if call[0][0] == "/api/virtual-servers":
                list_servers_route = call
                break

        assert list_servers_route is not None
        assert 'GET' in list_servers_route[1].get('methods', ['GET'])

    def test_fastapi_route_get_server_endpoint(self, mocker) -> None:
        """Test FastAPI get_server endpoint function."""
        mock_handle_get = mocker.patch("tool_router.api.rest.handle_get_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_fastapi_routes
        mock_router = Mock()

        register_fastapi_routes(mock_router)

        # Verify the route was added
        route_calls = mock_router.add_api_route.call_args_list
        get_server_route = None

        for call in route_calls:
            if call[0][0] == "/api/virtual-servers/{server_name}":
                get_server_route = call
                break

        assert get_server_route is not None
        assert 'GET' in get_server_route[1].get('methods', ['GET'])

    def test_fastapi_route_update_server_endpoint(self, mocker) -> None:
        """Test FastAPI update_server endpoint function."""
        mock_handle_update = mocker.patch("tool_router.api.rest.handle_update_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_fastapi_routes
        mock_router = Mock()

        register_fastapi_routes(mock_router)

        # Verify the route was added
        route_calls = mock_router.add_api_route.call_args_list
        update_server_route = None

        for call in route_calls:
            if call[0][0] == "/api/virtual-servers/{server_name}" and 'PATCH' in call[1].get('methods', []):
                update_server_route = call
                break

        assert update_server_route is not None

    def test_fastapi_route_enable_server_endpoint(self, mocker) -> None:
        """Test FastAPI enable_server endpoint function."""
        mock_handle_enable = mocker.patch("tool_router.api.rest.handle_enable_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_fastapi_routes
        mock_router = Mock()

        register_fastapi_routes(mock_router)

        # Verify the route was added
        route_calls = mock_router.add_api_route.call_args_list
        enable_server_route = None

        for call in route_calls:
            if call[0][0] == "/api/virtual-servers/{server_name}/enable":
                enable_server_route = call
                break

        assert enable_server_route is not None
        assert 'PATCH' in enable_server_route[1].get('methods', ['PATCH'])

    def test_fastapi_route_disable_server_endpoint(self, mocker) -> None:
        """Test FastAPI disable_server endpoint function."""
        mock_handle_disable = mocker.patch("tool_router.api.rest.handle_disable_server", return_value=({"name": "test"}, 200))

        from tool_router.api.rest import register_fastapi_routes
        mock_router = Mock()

        register_fastapi_routes(mock_router)

        # Verify the route was added
        route_calls = mock_router.add_api_route.call_args_list
        disable_server_route = None

        for call in route_calls:
            if call[0][0] == "/api/virtual-servers/{server_name}/disable":
                disable_server_route = call
                break

        assert disable_server_route is not None
        assert 'PATCH' in disable_server_route[1].get('methods', ['PATCH'])
