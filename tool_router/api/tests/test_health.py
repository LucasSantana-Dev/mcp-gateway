"""Tests for health check API endpoints."""

from __future__ import annotations

from unittest.mock import Mock

from tool_router.api.health import get_ai_router_health
from tool_router.core.config import AIRouterConfig, GatewayConfig, ToolRouterConfig


class TestHealthAPI:
    """Test health check API endpoints."""

    def test_get_ai_router_health_enabled_available(self):
        """Test health check with AI enabled and Ollama available."""
        config = ToolRouterConfig(
            gateway=GatewayConfig(url="http://localhost:4444"),
            ai=AIRouterConfig(
                enabled=True,
                provider="ollama",
                model="llama3.2:3b",
                endpoint="http://ollama:11434",
                timeout_ms=5000,
                weight=0.7,
                min_confidence=0.3,
            ),
        )

        mock_selector = Mock()
        mock_selector.is_available.return_value = True

        result = get_ai_router_health(config, mock_selector)

        assert result["status"] == "healthy"
        assert result["ai_enabled"] is True
        assert result["ollama_available"] is True
        assert len(result["issues"]) == 0
        assert result["configuration"]["model"] == "llama3.2:3b"

    def test_get_ai_router_health_enabled_unavailable(self):
        """Test health check with AI enabled but Ollama unavailable."""
        config = ToolRouterConfig(
            gateway=GatewayConfig(url="http://localhost:4444"),
            ai=AIRouterConfig(
                enabled=True,
                provider="ollama",
                model="llama3.2:3b",
                endpoint="http://ollama:11434",
                timeout_ms=5000,
                weight=0.7,
                min_confidence=0.3,
            ),
        )

        mock_selector = Mock()
        mock_selector.is_available.return_value = False

        result = get_ai_router_health(config, mock_selector)

        assert result["status"] == "degraded"
        assert result["ai_enabled"] is True
        assert result["ollama_available"] is False
        assert len(result["issues"]) == 1
        assert "not available" in result["issues"][0]

    def test_get_ai_router_health_disabled(self):
        """Test health check with AI disabled."""
        config = ToolRouterConfig(
            gateway=GatewayConfig(url="http://localhost:4444"),
            ai=AIRouterConfig(
                enabled=False,
                provider="ollama",
                model="llama3.2:3b",
                endpoint="http://ollama:11434",
                timeout_ms=5000,
                weight=0.7,
                min_confidence=0.3,
            ),
        )

        result = get_ai_router_health(config, None)

        assert result["status"] == "healthy"
        assert result["ai_enabled"] is False
        assert result["ollama_available"] is None
        assert len(result["issues"]) == 1
        assert "disabled" in result["issues"][0]

    def test_get_ai_router_health_no_selector_provided(self):
        """Test health check creates temporary selector when none provided."""
        config = ToolRouterConfig(
            gateway=GatewayConfig(url="http://localhost:4444"),
            ai=AIRouterConfig(
                enabled=True,
                provider="ollama",
                model="llama3.2:3b",
                endpoint="http://ollama:11434",
                timeout_ms=5000,
                weight=0.7,
                min_confidence=0.3,
            ),
        )

        # Should create temporary selector and check availability
        result = get_ai_router_health(config, None)

        assert "status" in result
        assert "ollama_available" in result
