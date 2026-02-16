from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from tool_router.gateway.client import call_tool, get_tools


def test_get_tools_raises_when_gateway_jwt_unset() -> None:
    with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="GATEWAY_JWT"):
        get_tools()


def test_get_tools_returns_list_from_list_response() -> None:
    data = [{"name": "t1", "description": "d1"}]
    resp = MagicMock()
    resp.read.return_value = json.dumps(data).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = get_tools()
    assert result == data


def test_get_tools_returns_tools_from_wrapped_response() -> None:
    data = {"tools": [{"name": "t1"}]}
    resp = MagicMock()
    resp.read.return_value = json.dumps(data).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = get_tools()
    assert result == [{"name": "t1"}]


def test_get_tools_returns_empty_for_unknown_shape() -> None:
    resp = MagicMock()
    resp.read.return_value = b"{}"
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = get_tools()
    assert result == []


def test_call_tool_raises_when_gateway_jwt_unset() -> None:
    with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError, match="GATEWAY_JWT"):
        call_tool("foo", {})


def test_call_tool_returns_error_message_on_jsonrpc_error() -> None:
    out = {"jsonrpc": "2.0", "id": 1, "error": {"message": "Tool not found"}}
    resp = MagicMock()
    resp.read.return_value = json.dumps(out).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = call_tool("bad_tool", {})
    assert "Gateway error" in result
    assert "Tool not found" in result


def test_call_tool_returns_text_content() -> None:
    out = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"content": [{"type": "text", "text": "Hello"}]},
    }
    resp = MagicMock()
    resp.read.return_value = json.dumps(out).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = call_tool("greet", {})
    assert result == "Hello"


def test_get_tools_timeout_exhaustion() -> None:
    """Test that timeout errors are retried and eventually fail."""
    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timeout")):
            with pytest.raises(ValueError, match="timeout"):
                get_tools()


def test_get_tools_json_decode_error() -> None:
    """Test handling of invalid JSON response."""
    resp = MagicMock()
    resp.read.return_value = b"not json"
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            with pytest.raises(ValueError, match="Invalid JSON"):
                get_tools()


def test_get_tools_http_500_retries() -> None:
    """Test that 500 errors trigger retries."""
    from urllib.error import HTTPError

    error = HTTPError("http://test", 500, "Server Error", {}, None)
    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", side_effect=error):
            with pytest.raises(ValueError, match="server error"):
                get_tools()


def test_get_tools_http_400_no_retry() -> None:
    """Test that 4xx errors don't retry."""
    from urllib.error import HTTPError

    error = HTTPError("http://test", 400, "Bad Request", {}, None)
    error.read = MagicMock(return_value=b"Bad request")
    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", side_effect=error):
            with pytest.raises(ValueError, match="HTTP error 400"):
                get_tools()


def test_get_tools_network_error_retries() -> None:
    """Test that network errors trigger retries."""
    from urllib.error import URLError

    error = URLError("Connection refused")
    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", side_effect=error):
            with pytest.raises(ValueError, match="Network error"):
                get_tools()


def test_call_tool_with_dict_response() -> None:
    """Test call_tool with dict response format."""
    out = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"content": [{"type": "text", "text": "Result"}]},
    }
    resp = MagicMock()
    resp.read.return_value = json.dumps(out).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = call_tool("test", {})
    assert result == "Result"


def test_call_tool_empty_content() -> None:
    """Test call_tool with empty content array."""
    out = {"jsonrpc": "2.0", "id": 1, "result": {"content": []}}
    resp = MagicMock()
    resp.read.return_value = json.dumps(out).encode()
    resp.__enter__ = MagicMock(return_value=resp)
    resp.__exit__ = MagicMock(return_value=None)

    with patch.dict("os.environ", {"GATEWAY_JWT": "token", "GATEWAY_URL": "http://localhost:4444"}):
        with patch("urllib.request.urlopen", return_value=resp):
            result = call_tool("test", {})
    # Empty content returns the JSON string representation
    assert '"content": []' in result
