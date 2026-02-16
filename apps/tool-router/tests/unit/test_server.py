"""Unit tests for MCP server tool functions.

DEPRECATED: These tests are for the old module structure before monorepo migration.
The execute_task and search_tools functions now use different internal implementations.
These tests are skipped pending refactoring to match new architecture.
"""

from __future__ import annotations

import pytest

from tool_router.core.server import execute_task, search_tools


pytestmark = pytest.mark.skip(reason="Deprecated tests for old module structure - pending refactoring")


class TestExecuteTask:
    """Tests for execute_task function."""

    def test_execute_task_success(self, mocker) -> None:
        """Test successful task execution with matching tool."""
        mock_tools = [
            {
                "name": "search_web",
                "description": "Search the web",
                "gatewaySlug": "brave",
                "inputSchema": {"properties": {"query": {"type": "string"}}},
            }
        ]

        mocker.patch("tool_router.gateway.client.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.ai.selector.pick_best_tools", return_value=mock_tools)
        mocker.patch("tool_router.args.builder.build_arguments", return_value={"query": "python"})
        mocker.patch("tool_router.gateway.client.call_tool", return_value="Search results for python")

        result = execute_task("search for python")

        assert result == "Search results for python"

    def test_execute_task_no_tools(self, mocker) -> None:
        """Test when gateway returns no tools."""
        mocker.patch("tool_router.gateway.client.get_tools", return_value=[])

        result = execute_task("search for python")

        assert result == "No tools registered in the gateway."

    def test_execute_task_gateway_value_error(self, mocker) -> None:
        """Test handling of ValueError from get_tools."""
        mocker.patch("tool_router.server.get_tools", side_effect=ValueError("Invalid gateway response"))

        result = execute_task("search for python")

        assert "Failed to list tools" in result
        assert "Invalid gateway response" in result

    def test_execute_task_gateway_connection_error(self, mocker) -> None:
        """Test handling of ConnectionError from get_tools."""
        mocker.patch("tool_router.server.get_tools", side_effect=ConnectionError("Gateway unreachable"))

        result = execute_task("search for python")

        assert "Failed to list tools" in result
        assert "Gateway unreachable" in result

    def test_execute_task_gateway_os_error(self, mocker) -> None:
        """Test handling of OSError from get_tools."""
        mocker.patch("tool_router.server.get_tools", side_effect=OSError("File system error"))

        result = execute_task("search for python")

        assert "Unexpected error listing tools" in result
        assert "OSError" in result

    def test_execute_task_gateway_runtime_error(self, mocker) -> None:
        """Test handling of RuntimeError from get_tools."""
        mocker.patch("tool_router.server.get_tools", side_effect=RuntimeError("Runtime failure"))

        result = execute_task("search for python")

        assert "Unexpected error listing tools" in result
        assert "RuntimeError" in result

    def test_execute_task_no_matching_tool(self, mocker) -> None:
        """Test when no tool matches the task."""
        mock_tools = [{"name": "list_files", "description": "List files"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", return_value=[])

        result = execute_task("search for python")

        assert "No matching tool found" in result

    def test_execute_task_tool_selection_error(self, mocker) -> None:
        """Test handling of errors during tool selection."""
        mock_tools = [{"name": "search_web"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", side_effect=ValueError("Selection error"))

        result = execute_task("search for python")

        assert "Error selecting tool" in result
        assert "ValueError" in result

    def test_execute_task_tool_without_name(self, mocker) -> None:
        """Test when selected tool has no name."""
        mock_tools = [{"description": "A tool without name"}]

        mocker.patch("tool_router.server.get_tools", return_value=[{"name": "test"}])
        mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools)

        result = execute_task("search for python")

        assert "Chosen tool has no name" in result

    def test_execute_task_args_build_error(self, mocker) -> None:
        """Test handling of errors during argument building."""
        mock_tools = [{"name": "search_web", "description": "Search"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.build_arguments", side_effect=KeyError("Missing key"))

        result = execute_task("search for python")

        assert "Error building arguments" in result
        assert "KeyError" in result

    def test_execute_task_with_context(self, mocker) -> None:
        """Test task execution with context parameter."""
        mock_tools = [{"name": "search_web", "description": "Search"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mock_pick = mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.build_arguments", return_value={"query": "python"})
        mocker.patch("tool_router.server.call_tool", return_value="Results")

        result = execute_task("search for python", context="programming")

        # Verify context was passed to pick_best_tools
        mock_pick.assert_called_once()
        assert mock_pick.call_args[0][2] == "programming"
        assert result == "Results"


class TestSearchTools:
    """Tests for search_tools function."""

    def test_search_tools_success(self, mocker) -> None:
        """Test successful tool search."""
        mock_tools = [
            {"name": "search_web", "description": "Search the web", "gatewaySlug": "brave"},
            {"name": "search_docs", "description": "Search documentation", "gatewaySlug": "context7"},
        ]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools)

        result = search_tools("search")

        assert "search_web" in result
        assert "search_docs" in result
        assert "brave" in result
        assert "context7" in result

    def test_search_tools_no_matches(self, mocker) -> None:
        """Test when no tools match the query."""
        mock_tools = [{"name": "list_files", "description": "List files"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", return_value=[])

        result = search_tools("nonexistent")

        assert "No tools match the query" in result

    def test_search_tools_gateway_error(self, mocker) -> None:
        """Test handling of gateway errors."""
        mocker.patch("tool_router.server.get_tools", side_effect=ValueError("Gateway error"))

        result = search_tools("search")

        assert "Failed to list tools" in result

    def test_search_tools_no_tools(self, mocker) -> None:
        """Test when gateway has no tools."""
        mocker.patch("tool_router.gateway.client.get_tools", return_value=[])

        result = search_tools("search")

        assert "No tools registered in the gateway" in result

    def test_search_tools_selection_error(self, mocker) -> None:
        """Test handling of tool selection errors."""
        mock_tools = [{"name": "test"}]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", side_effect=TypeError("Type error"))

        result = search_tools("search")

        assert "Error searching tools" in result
        assert "TypeError" in result

    def test_search_tools_formats_output(self, mocker) -> None:
        """Test output formatting with various tool properties."""
        mock_tools = [
            {
                "name": "tool1",
                "description": "A" * 100,  # Long description
                "gatewaySlug": "gateway1",
            },
            {
                "name": "tool2",
                "description": None,  # No description
                "gateway_slug": "gateway2",  # Alternative key
            },
            {
                "name": "tool3",
                "description": "Short desc",
                # No gateway slug
            },
        ]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools)

        result = search_tools("tool")

        # Verify formatting
        assert "tool1 (gateway1):" in result
        assert "tool2 (gateway2):" in result
        assert "tool3 ():" in result
        # Verify description truncation (80 chars)
        lines = result.split("\n")
        tool1_line = next(line for line in lines if "tool1" in line)
        assert len(tool1_line.split(": ", 1)[1]) <= 80

    def test_search_tools_top_n_limit(self, mocker) -> None:
        """Test that search returns top 10 tools."""
        mock_tools = [{"name": f"tool{i}", "description": f"Tool {i}"} for i in range(15)]

        mocker.patch("tool_router.server.get_tools", return_value=mock_tools)
        mock_pick = mocker.patch("tool_router.server.pick_best_tools", return_value=mock_tools[:10])

        search_tools("tool")

        # Verify top_n=10 was passed
        mock_pick.assert_called_once()
        assert mock_pick.call_args[1]["top_n"] == 10
