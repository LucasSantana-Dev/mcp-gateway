"""Metrics API endpoints for AI router observability."""

from __future__ import annotations

from typing import Any

from tool_router.observability.metrics import get_metrics


def get_ai_router_metrics() -> dict[str, Any]:
    """Get AI router metrics for monitoring and observability.

    Returns:
        Dictionary containing AI router metrics including:
        - Selection method counts (AI vs keyword)
        - AI confidence statistics
        - Fallback event counts
        - Error rates
        - Performance metrics
    """
    metrics = get_metrics()

    # Get all AI-related counters
    ai_metrics = {
        "selection_methods": {
            "ai_success": metrics.get_counter("execute_task.ai_selection.success"),
            "ai_low_confidence": metrics.get_counter("execute_task.ai_selection.low_confidence"),
            "ai_error": metrics.get_counter("execute_task.ai_selection.error"),
            "keyword_fallback": metrics.get_counter("execute_task.keyword_selection"),
        },
        "ai_selector_status": {
            "initialized": metrics.get_counter("ai_selector.initialized"),
            "unavailable": metrics.get_counter("ai_selector.unavailable"),
            "init_error": metrics.get_counter("ai_selector.init_error"),
            "disabled": metrics.get_counter("ai_selector.disabled"),
        },
        "performance": {
            "avg_ai_confidence": metrics.get_gauge("execute_task.ai_confidence"),
            "total_executions": (
                metrics.get_counter("execute_task.ai_selection.success")
                + metrics.get_counter("execute_task.keyword_selection")
            ),
        },
    }

    # Calculate derived metrics
    total_selections = (
        ai_metrics["selection_methods"]["ai_success"] + ai_metrics["selection_methods"]["keyword_fallback"]
    )

    if total_selections > 0:
        ai_metrics["statistics"] = {
            "ai_usage_rate": round(ai_metrics["selection_methods"]["ai_success"] / total_selections * 100, 2),
            "fallback_rate": round(ai_metrics["selection_methods"]["keyword_fallback"] / total_selections * 100, 2),
        }
    else:
        ai_metrics["statistics"] = {
            "ai_usage_rate": 0.0,
            "fallback_rate": 0.0,
        }

    return ai_metrics
