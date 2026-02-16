from __future__ import annotations

from tool_router.scoring import pick_best_tools, score_tool


def test_score_tool_empty_task_returns_zero() -> None:
    tool = {"name": "search", "description": "Search the web"}
    assert score_tool("", "", tool) == 0


def test_score_tool_matching_name_scores_positive() -> None:
    tool = {"name": "search", "description": "Search the web"}
    assert score_tool("search the web", "", tool) > 0


def test_score_tool_matching_description_scores_positive() -> None:
    tool = {"name": "foo", "description": "search the web for things"}
    assert score_tool("search for things", "", tool) > 0


def test_score_tool_no_match_returns_zero() -> None:
    tool = {"name": "fetch", "description": "Fetch a URL"}
    assert score_tool("calculate sum", "", tool) == 0


def test_score_tool_uses_context_tokens() -> None:
    tool = {"name": "search", "description": "Search"}
    assert score_tool("do it", "search docs", tool) > 0


def test_pick_best_tools_empty_list_returns_empty() -> None:
    assert pick_best_tools([], "search", "") == []


def test_pick_best_tools_returns_best_match() -> None:
    tools = [
        {"name": "fetch", "description": "Fetch URL"},
        {"name": "search", "description": "Search the web"},
        {"name": "time", "description": "Get time"},
    ]
    best = pick_best_tools(tools, "search the web", "", top_n=1)
    assert len(best) == 1
    assert best[0]["name"] == "search"


def test_pick_best_tools_respects_top_n() -> None:
    tools = [
        {"name": "search", "description": "Search"},
        {"name": "web search", "description": "Search web"},
        {"name": "fetch", "description": "Fetch"},
    ]
    best = pick_best_tools(tools, "search web", "", top_n=2)
    assert len(best) == 2


def test_pick_best_tools_no_match_returns_empty() -> None:
    tools = [{"name": "fetch", "description": "Fetch URL"}]
    assert pick_best_tools(tools, "calculate", "", top_n=1) == []


# Additional tests for comprehensive coverage via public API


def test_score_tool_case_insensitive() -> None:
    """Test that scoring is case insensitive."""
    tool = {"name": "SearchWeb", "description": "Search the WEB"}
    assert score_tool("search web", "", tool) > 0
    assert score_tool("SEARCH WEB", "", tool) > 0


def test_score_tool_special_characters() -> None:
    """Test scoring handles special characters."""
    tool = {"name": "file-system", "description": "File_System operations"}
    assert score_tool("file system", "", tool) > 0


def test_score_tool_partial_word_matching() -> None:
    """Test partial word matching in tool names."""
    tool = {"name": "filesystem", "description": "Operations"}
    # "file" should partially match "filesystem"
    assert score_tool("file", "", tool) > 0


def test_score_tool_empty_inputs() -> None:
    """Test scoring with various empty inputs."""
    tool = {"name": "test", "description": "test tool"}
    assert score_tool("", "", tool) == 0
    assert score_tool("task", "", {"name": "", "description": ""}) >= 0


def test_score_tool_synonym_matching() -> None:
    """Test that synonyms increase scores."""
    tool = {"name": "find_files", "description": "Locate files"}
    # "search" is a synonym of "find"
    score_with_synonym = score_tool("search files", "", tool)
    score_without = score_tool("random task", "", tool)
    assert score_with_synonym > score_without


def test_score_tool_gateway_slug_matching() -> None:
    """Test that gateway slug contributes to score."""
    tool = {
        "name": "tool1",
        "description": "A tool",
        "gatewaySlug": "brave-search",
    }
    assert score_tool("brave search", "", tool) > 0


def test_score_tool_missing_fields() -> None:
    """Test scoring with missing optional fields."""
    tool = {"name": "test"}  # No description or gateway
    assert score_tool("test", "", tool) > 0

    tool2 = {"description": "test tool"}  # No name
    assert score_tool("test", "", tool2) >= 0


def test_score_tool_name_weight_higher() -> None:
    """Test that name matches score higher than description matches."""
    tool1 = {"name": "search_web", "description": "Other stuff"}
    tool2 = {"name": "other", "description": "search web"}
    score1 = score_tool("search web", "", tool1)
    score2 = score_tool("search web", "", tool2)
    assert score1 > score2


def test_pick_best_tools_zero_scores_filtered() -> None:
    """Test that tools with zero scores are filtered out."""
    tools = [
        {"name": "search", "description": "Search"},
        {"name": "unrelated", "description": "Completely different"},
    ]
    best = pick_best_tools(tools, "search", "", top_n=10)
    # Should only return the matching tool, not the unrelated one
    assert len(best) == 1
    assert best[0]["name"] == "search"


def test_pick_best_tools_sorting() -> None:
    """Test that tools are sorted by score."""
    tools = [
        {"name": "fetch", "description": "Fetch URL"},
        {"name": "search_web", "description": "Search the web"},
        {"name": "web_search", "description": "Web search tool"},
    ]
    best = pick_best_tools(tools, "web search", "", top_n=3)
    # Verify exact ordering - web_search should rank highest (exact match in name)
    assert best[0]["name"] == "web_search"
    assert best[1]["name"] == "search_web"
