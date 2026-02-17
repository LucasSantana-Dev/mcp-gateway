"""Enhanced unit tests for AI selector to improve coverage."""

from __future__ import annotations

import requests
from unittest.mock import Mock, patch

from tool_router.ai.selector import AIToolSelector


class TestAIToolSelectorEnhanced:
    """Enhanced tests for AIToolSelector to improve coverage."""

    def test_init_with_custom_config(self) -> None:
        """Test AIToolSelector initialization with custom configuration."""
        selector = AIToolSelector(
            endpoint="http://custom-ollama:11434",
            model="custom-model",
            timeout_ms=60000
        )

        assert selector.endpoint == "http://custom-ollama:11434"
        assert selector.model == "custom-model"
        assert selector.timeout_seconds == 60.0

    def test_select_tool_with_empty_tools_list(self) -> None:
        """Test select_tool with empty tools list."""
        selector = AIToolSelector()

        result = selector.select_tool(
            task="test query",
            tools=[]
        )

        assert result is None

    def test_select_tool_with_whitespace_task(self) -> None:
        """Test select_tool with whitespace-only task."""
        selector = AIToolSelector()

        result = selector.select_tool(
            task="   ",
            tools=[{"name": "test", "description": "test tool"}]
        )

        assert result is None

    def test_select_tool_with_no_matching_tools(self, mocker) -> None:
        """Test select_tool when no tools match the task."""
        selector = AIToolSelector()

        # Mock the AI response to return no matches
        mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "none"}')
        mocker.patch.object(selector, '_parse_response', return_value=None)

        result = selector.select_tool(
            task="complex task",
            tools=[{"name": "simple", "description": "simple tool"}]
        )

        assert result is None

    def test_select_tool_with_context_variables(self, mocker) -> None:
        """Test select_tool with context variables."""
        selector = AIToolSelector()

        # Mock successful AI selection
        mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "test_tool"}')
        mocker.patch.object(selector, '_parse_response', return_value={"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""})

        result = selector.select_tool(
            task="test task with context",
            tools=[{"name": "test_tool", "description": "test tool"}]
        )

        assert result == {"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""}

    def test_call_ollama_connection_error(self, mocker) -> None:
        """Test _call_ollama with connection error."""
        selector = AIToolSelector()

        # Mock requests to raise connection error
        mocker.patch("requests.post", side_effect=requests.ConnectionError("Connection failed"))

        result = selector._call_ollama("test prompt")

        assert result is None

    def test_call_ollama_timeout_error(self, mocker) -> None:
        """Test _call_ollama with timeout error."""
        selector = AIToolSelector(timeout_ms=1000)  # Very short timeout

        # Mock requests to raise timeout error
        mocker.patch("requests.post", side_effect=requests.Timeout("Request timed out"))

        result = selector._call_ollama("test prompt")

        assert result is None

    def test_call_ollama_invalid_response(self, mocker) -> None:
        """Test _call_ollama with invalid JSON response."""
        selector = AIToolSelector()

        # Mock requests to return invalid JSON
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mocker.patch("requests.post", return_value=mock_response)

        result = selector._call_ollama("test prompt")

        assert result is None

    def test_parse_response_empty_json(self) -> None:
        """Test _parse_response with empty JSON."""
        selector = AIToolSelector()

        result = selector._parse_response("{}", [])

        assert result is None

    def test_parse_response_missing_tool_field(self) -> None:
        """Test _parse_response with missing tool field."""
        selector = AIToolSelector()

        result = selector._parse_response('{"confidence": 0.8}', [])

        assert result is None

    def test_parse_response_invalid_json_structure(self) -> None:
        """Test _parse_response with invalid JSON structure."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": null}', [])

        assert result is None

    def test_parse_response_with_confidence(self) -> None:
        """Test _parse_response with confidence score."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.95}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.95, "reasoning": ""}

    def test_parse_response_with_extra_fields(self) -> None:
        """Test _parse_response with extra fields."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.9, "reasoning": "Good match"}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.9, "reasoning": "Good match"}

    def test_parse_response_with_invalid_confidence(self) -> None:
        """Test _parse_response with invalid confidence value."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": "invalid"}', [{"name": "test_tool"}])

        assert result is None

    def test_parse_response_with_out_of_range_confidence(self) -> None:
        """Test _parse_response with out-of-range confidence."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 2.0}', [{"name": "test_tool"}])

        # Should clamp to 1.0
        assert result == {"tool_name": "test_tool", "confidence": 1.0, "reasoning": ""}

    def test_select_tool_with_long_task(self, mocker) -> None:
        """Test select_tool with very long task."""
        selector = AIToolSelector()

        long_task = "test " * 100  # Very long task

        mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "test_tool"}')
        mocker.patch.object(selector, '_parse_response', return_value={"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""})

        result = selector.select_tool(
            task=long_task,
            tools=[{"name": "test_tool", "description": "test tool"}]
        )

        assert result == {"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""}

    def test_select_tool_with_special_characters(self, mocker) -> None:
        """Test select_tool with special characters in task."""
        selector = AIToolSelector()

        special_task = "test with @#$%^&*() characters"

        mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "test_tool"}')
        mocker.patch.object(selector, '_parse_response', return_value={"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""})

        result = selector.select_tool(
            task=special_task,
            tools=[{"name": "test_tool", "description": "test tool"}]
        )

        assert result == {"tool_name": "test_tool", "confidence": 0.9, "reasoning": ""}

    def test_select_tool_with_malformed_tools_list(self, mocker) -> None:
        """Test select_tool with malformed tools list."""
        selector = AIToolSelector()

        # Tools without required fields
        malformed_tools = [
            {"name": "tool1"},  # Missing description
            {"description": "tool2"},  # Missing name
            {},  # Empty tool dict
        ]

        mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "tool1"}')
        mocker.patch.object(selector, '_parse_response', return_value={"tool_name": "tool1", "confidence": 0.9, "reasoning": ""})

        result = selector.select_tool(
            task="test task",
            tools=malformed_tools
        )

        # Should still work despite malformed tools
        assert result == {"tool_name": "tool1", "confidence": 0.9, "reasoning": ""}

    def test_select_tool_with_none_response(self, mocker) -> None:
        """Test select_tool when _call_ollama returns None."""
        selector = AIToolSelector()

        mocker.patch.object(selector, '_call_ollama', return_value=None)

        result = selector.select_tool(
            task="test task",
            tools=[{"name": "test", "description": "test tool"}]
        )

        assert result is None

    def test_parse_response_with_invalid_json_string(self) -> None:
        """Test _parse_response with invalid JSON string."""
        selector = AIToolSelector()

        result = selector._parse_response("not valid json", [])

        assert result is None

    def test_parse_response_with_tool_not_in_list(self) -> None:
        """Test _parse_response when selected tool is not in the tools list."""
        selector = AIToolSelector()

        tools = [{"name": "tool1", "description": "first tool"}]
        result = selector._parse_response('{"tool_name": "tool2"}', tools)

        assert result is None
