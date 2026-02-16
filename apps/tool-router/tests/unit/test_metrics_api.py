"""Unit tests for metrics API."""

from __future__ import annotations

from tool_router.api.metrics import get_ai_router_metrics


class TestGetAIRouterMetrics:
    """Tests for get_ai_router_metrics."""

    def test_metrics_with_data(self, mocker):
        """Test metrics with actual data."""
        mock_metrics = mocker.Mock()
        mock_metrics.get_counter.side_effect = lambda key: {
            "execute_task.ai_selection.success": 80,
            "execute_task.ai_selection.low_confidence": 5,
            "execute_task.ai_selection.error": 2,
            "execute_task.keyword_selection": 20,
            "ai_selector.initialized": 1,
            "ai_selector.unavailable": 0,
            "ai_selector.init_error": 0,
            "ai_selector.disabled": 0,
        }.get(key, 0)
        mock_metrics.get_gauge.return_value = 0.85

        mocker.patch("tool_router.api.metrics.get_metrics", return_value=mock_metrics)

        result = get_ai_router_metrics()

        assert result["selection_methods"]["ai_success"] == 80
        assert result["selection_methods"]["keyword_fallback"] == 20
        assert result["performance"]["avg_ai_confidence"] == 0.85
        assert result["statistics"]["ai_usage_rate"] == 80.0
        assert result["statistics"]["fallback_rate"] == 20.0

    def test_metrics_no_selections(self, mocker):
        """Test metrics when no selections have been made."""
        mock_metrics = mocker.Mock()
        mock_metrics.get_counter.return_value = 0
        mock_metrics.get_gauge.return_value = 0.0

        mocker.patch("tool_router.api.metrics.get_metrics", return_value=mock_metrics)

        result = get_ai_router_metrics()

        assert result["statistics"]["ai_usage_rate"] == 0.0
        assert result["statistics"]["fallback_rate"] == 0.0

    def test_metrics_all_ai(self, mocker):
        """Test metrics when all selections use AI."""
        mock_metrics = mocker.Mock()
        mock_metrics.get_counter.side_effect = lambda key: {
            "execute_task.ai_selection.success": 100,
            "execute_task.keyword_selection": 0,
        }.get(key, 0)
        mock_metrics.get_gauge.return_value = 0.92

        mocker.patch("tool_router.api.metrics.get_metrics", return_value=mock_metrics)

        result = get_ai_router_metrics()

        assert result["statistics"]["ai_usage_rate"] == 100.0
        assert result["statistics"]["fallback_rate"] == 0.0

    def test_metrics_all_keyword(self, mocker):
        """Test metrics when all selections use keyword matching."""
        mock_metrics = mocker.Mock()
        mock_metrics.get_counter.side_effect = lambda key: {
            "execute_task.ai_selection.success": 0,
            "execute_task.keyword_selection": 50,
        }.get(key, 0)
        mock_metrics.get_gauge.return_value = 0.0

        mocker.patch("tool_router.api.metrics.get_metrics", return_value=mock_metrics)

        result = get_ai_router_metrics()

        assert result["statistics"]["ai_usage_rate"] == 0.0
        assert result["statistics"]["fallback_rate"] == 100.0
