"""Additional unit tests for AI selector to cover remaining missing lines."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from tool_router.ai.selector import AIToolSelector


class TestAIToolSelectorAdditional:
    """Additional tests for AIToolSelector to improve coverage."""

    def test_select_tool_with_too_many_tools(self, mocker) -> None:
        """Test select_tool with more than 100 tools triggers warning and limiting."""
        selector = AIToolSelector()

        # Create 150 tools
        tools = [{"name": f"tool_{i}", "description": f"Tool {i}"} for i in range(150)]

        mock_call_ollama = mocker.patch.object(selector, '_call_ollama', return_value='{"tool_name": "tool_50"}')
        mock_parse_response = mocker.patch.object(selector, '_parse_response', return_value={"tool_name": "tool_50", "confidence": 0.9, "reasoning": ""})

        with patch("tool_router.ai.selector.logger") as mock_logger:
            result = selector.select_tool("test task", tools)

        # Should have logged warning about too many tools
        mock_logger.warning.assert_called_once_with("Too many tools (150) for AI selection, limiting to first 100")

        # Should have limited tools to first 100
        mock_call_ollama.assert_called_once()
        call_args = mock_call_ollama.call_args[0]
        prompt = call_args[0]

        # Verify prompt contains only first 100 tools
        assert "tool_0" in prompt
        assert "tool_99" in prompt
        assert "tool_100" not in prompt
        assert "tool_149" not in prompt

        assert result == {"tool_name": "tool_50", "confidence": 0.9, "reasoning": ""}

    def test_select_tool_requests_exception_logging(self, mocker) -> None:
        """Test select_tool logs warning on requests.RequestException."""
        selector = AIToolSelector()

        mocker.patch.object(selector, '_call_ollama', side_effect=Exception("Network error"))

        with patch("tool_router.ai.selector.logger") as mock_logger:
            result = selector.select_tool("test task", [{"name": "test", "description": "test"}])

        assert result is None
        mock_logger.warning.assert_called_once_with("AI selection request failed: Network error")

    def test_select_tool_unexpected_exception_logging(self, mocker) -> None:
        """Test select_tool logs exception on unexpected errors."""
        selector = AIToolSelector()

        mocker.patch.object(selector, '_call_ollama', side_effect=ValueError("Unexpected error"))

        with patch("tool_router.ai.selector.logger") as mock_logger:
            result = selector.select_tool("test task", [{"name": "test", "description": "test"}])

        assert result is None
        mock_logger.exception.assert_called_once_with("Unexpected error in AI selection: Unexpected error")

    def test_parse_response_with_tool_name_none(self) -> None:
        """Test _parse_response when tool_name is None."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": null, "confidence": 0.8}', [])

        assert result is None

    def test_parse_response_with_confidence_none(self) -> None:
        """Test _parse_response when confidence is None."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": null}', [{"name": "test_tool"}])

        assert result is None

    def test_parse_response_with_missing_reasoning(self) -> None:
        """Test _parse_response when reasoning field is missing."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.8}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.8, "reasoning": ""}

    def test_parse_response_with_empty_reasoning(self) -> None:
        """Test _parse_response when reasoning field is empty string."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.8, "reasoning": ""}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.8, "reasoning": ""}

    def test_parse_response_with_reasoning_field(self) -> None:
        """Test _parse_response when reasoning field is present."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.8, "reasoning": "Good match"}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.8, "reasoning": "Good match"}

    def test_parse_response_confidence_clamping_high(self) -> None:
        """Test _parse_response clamps confidence values above 1.0."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 1.5}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 1.0, "reasoning": ""}

    def test_parse_response_confidence_clamping_low(self) -> None:
        """Test _parse_response clamps confidence values below 0.0."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": -0.5}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.0, "reasoning": ""}

    def test_parse_response_with_additional_fields(self) -> None:
        """Test _parse_response preserves additional fields."""
        selector = AIToolSelector()

        result = selector._parse_response('{"tool_name": "test_tool", "confidence": 0.8, "reasoning": "test", "extra": "field", "number": 123}', [{"name": "test_tool"}])

        assert result == {"tool_name": "test_tool", "confidence": 0.8, "reasoning": "test", "extra": "field", "number": 123}

    def test_select_tool_with_empty_tools_list(self) -> None:
        """Test select_tool with empty tools list."""
        selector = AIToolSelector()

        result = selector.select_tool("test task", [])

        assert result is None

    def test_select_tool_with_none_task(self) -> None:
        """Test select_tool with None task."""
        selector = AIToolSelector()

        result = selector.select_tool(None, [{"name": "test", "description": "test"}])

        assert result is None

    def test_select_tool_with_empty_string_task(self) -> None:
        """Test select_tool with empty string task."""
        selector = AIToolSelector()

        result = selector.select_tool("", [{"name": "test", "description": "test"}])

        assert result is None
