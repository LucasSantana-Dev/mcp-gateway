"""Unit tests for configuration management."""

from __future__ import annotations

import pytest

from tool_router.core.config import AIRouterConfig, GatewayConfig, ToolRouterConfig


class TestGatewayConfig:
    """Tests for GatewayConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = GatewayConfig(url="http://test:4444", jwt="token")

        assert config.url == "http://test:4444"
        assert config.jwt == "token"
        assert config.timeout_ms == 120000
        assert config.max_retries == 3
        assert config.retry_delay_ms == 2000

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = GatewayConfig(
            url="http://custom:8080",
            jwt="custom-token",
            timeout_ms=5000,
            max_retries=5,
            retry_delay_ms=1000,
        )

        assert config.url == "http://custom:8080"
        assert config.jwt == "custom-token"
        assert config.timeout_ms == 5000
        assert config.max_retries == 5
        assert config.retry_delay_ms == 1000

    def test_from_env_success(self, monkeypatch) -> None:
        """Test loading configuration from environment variables."""
        monkeypatch.setenv("GATEWAY_URL", "http://env-gateway:4444")
        monkeypatch.setenv("GATEWAY_JWT", "env-token")
        monkeypatch.setenv("GATEWAY_TIMEOUT_MS", "30000")
        monkeypatch.setenv("GATEWAY_MAX_RETRIES", "5")
        monkeypatch.setenv("GATEWAY_RETRY_DELAY_MS", "1500")

        config = GatewayConfig.load_from_environment()

        assert config.url == "http://env-gateway:4444"
        assert config.jwt == "env-token"
        assert config.timeout_ms == 30000
        assert config.max_retries == 5
        assert config.retry_delay_ms == 1500

    def test_from_env_missing_jwt(self, monkeypatch) -> None:
        """Test that missing JWT raises ValueError."""
        monkeypatch.delenv("GATEWAY_JWT", raising=False)

        with pytest.raises(ValueError, match="GATEWAY_JWT environment variable"):
            GatewayConfig.load_from_environment()

    def test_from_env_defaults(self, monkeypatch) -> None:
        """Test default values when env vars not set."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.delenv("GATEWAY_URL", raising=False)
        monkeypatch.delenv("GATEWAY_TIMEOUT_MS", raising=False)
        monkeypatch.delenv("GATEWAY_MAX_RETRIES", raising=False)
        monkeypatch.delenv("GATEWAY_RETRY_DELAY_MS", raising=False)

        config = GatewayConfig.load_from_environment()

        assert config.url == "http://gateway:4444"
        assert config.timeout_ms == 120000
        assert config.max_retries == 3
        assert config.retry_delay_ms == 2000

    def test_url_trailing_slash_stripped(self, monkeypatch) -> None:
        """Test that trailing slashes are removed from URL."""
        monkeypatch.setenv("GATEWAY_URL", "http://gateway:4444/")
        monkeypatch.setenv("GATEWAY_JWT", "token")

        config = GatewayConfig.load_from_environment()

        assert config.url == "http://gateway:4444"
        assert not config.url.endswith("/")


class TestToolRouterConfig:
    """Tests for ToolRouterConfig dataclass."""

    def test_default_values(self, monkeypatch) -> None:
        """Test default configuration values."""
        monkeypatch.setenv("GATEWAY_JWT", "token")

        config = ToolRouterConfig.load_from_environment()

        assert config.max_tools_search == 10
        assert config.default_top_n == 1
        assert isinstance(config.gateway, GatewayConfig)

    def test_custom_values(self, monkeypatch) -> None:
        """Test custom configuration values."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("MAX_TOOLS_SEARCH", "20")
        monkeypatch.setenv("DEFAULT_TOP_N", "3")

        config = ToolRouterConfig.load_from_environment()

        assert config.max_tools_search == 20
        assert config.default_top_n == 3

    def test_gateway_config_integration(self, monkeypatch) -> None:
        """Test that ToolRouterConfig properly loads GatewayConfig."""
        monkeypatch.setenv("GATEWAY_URL", "http://test:4444")
        monkeypatch.setenv("GATEWAY_JWT", "test-token")
        monkeypatch.setenv("GATEWAY_TIMEOUT_MS", "10000")

        config = ToolRouterConfig.load_from_environment()

        assert config.gateway.url == "http://test:4444"
        assert config.gateway.jwt == "test-token"
        assert config.gateway.timeout_ms == 10000

    def test_from_env_propagates_gateway_error(self, monkeypatch) -> None:
        """Test that GatewayConfig errors propagate correctly."""
        monkeypatch.delenv("GATEWAY_JWT", raising=False)

        with pytest.raises(ValueError, match="GATEWAY_JWT"):
            ToolRouterConfig.load_from_environment()

    def test_direct_instantiation(self) -> None:
        """Test direct instantiation with GatewayConfig."""
        from tool_router.core.config import AIRouterConfig

        gateway_config = GatewayConfig(url="http://test:4444", jwt="token")
        ai_config = AIRouterConfig(
            enabled=False,
            provider="ollama",
            model="llama3.2:3b",
            endpoint="http://ollama:11434",
            timeout_ms=5000,
            weight=0.7,
            min_confidence=0.3,
        )
        config = ToolRouterConfig(gateway=gateway_config, ai=ai_config, max_tools_search=15, default_top_n=2)

        assert config.gateway == gateway_config
        assert config.max_tools_search == 15
        assert config.default_top_n == 2


class TestGatewayConfigValidation:
    """Test GatewayConfig validation and error handling."""

    def test_invalid_timeout_ms(self, monkeypatch):
        """Test invalid timeout_ms value."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("GATEWAY_TIMEOUT_MS", "invalid")
        with pytest.raises(ValueError, match="GATEWAY_TIMEOUT_MS must be a valid integer"):
            GatewayConfig.load_from_environment()

    def test_invalid_max_retries(self, monkeypatch):
        """Test invalid max_retries value."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("GATEWAY_MAX_RETRIES", "not_a_number")
        with pytest.raises(ValueError, match="GATEWAY_MAX_RETRIES must be a valid integer"):
            GatewayConfig.load_from_environment()

    def test_invalid_retry_delay_ms(self, monkeypatch):
        """Test invalid retry_delay_ms value."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("GATEWAY_RETRY_DELAY_MS", "abc")
        with pytest.raises(ValueError, match="GATEWAY_RETRY_DELAY_MS must be a valid integer"):
            GatewayConfig.load_from_environment()


class TestAIRouterConfigValidation:
    """Test AIRouterConfig validation and error handling."""

    def test_invalid_timeout_ms(self, monkeypatch):
        """Test invalid timeout_ms value."""
        monkeypatch.setenv("ROUTER_AI_TIMEOUT_MS", "invalid")
        with pytest.raises(ValueError, match="ROUTER_AI_TIMEOUT_MS must be a valid integer"):
            AIRouterConfig.load_from_environment()

    def test_invalid_weight(self, monkeypatch):
        """Test invalid weight value."""
        monkeypatch.setenv("ROUTER_AI_WEIGHT", "not_float")
        with pytest.raises(ValueError, match="ROUTER_AI_WEIGHT must be a valid float"):
            AIRouterConfig.load_from_environment()

    def test_invalid_min_confidence(self, monkeypatch):
        """Test invalid min_confidence value."""
        monkeypatch.setenv("ROUTER_AI_MIN_CONFIDENCE", "abc")
        with pytest.raises(ValueError, match="ROUTER_AI_MIN_CONFIDENCE must be a valid float"):
            AIRouterConfig.load_from_environment()

    def test_weight_out_of_range_high(self, monkeypatch):
        """Test weight value above 1.0."""
        monkeypatch.setenv("ROUTER_AI_WEIGHT", "1.5")
        with pytest.raises(ValueError, match="ROUTER_AI_WEIGHT must be between 0.0 and 1.0"):
            AIRouterConfig.load_from_environment()

    def test_weight_out_of_range_low(self, monkeypatch):
        """Test weight value below 0.0."""
        monkeypatch.setenv("ROUTER_AI_WEIGHT", "-0.5")
        with pytest.raises(ValueError, match="ROUTER_AI_WEIGHT must be between 0.0 and 1.0"):
            AIRouterConfig.load_from_environment()

    def test_min_confidence_out_of_range_high(self, monkeypatch):
        """Test min_confidence value above 1.0."""
        monkeypatch.setenv("ROUTER_AI_MIN_CONFIDENCE", "2.0")
        with pytest.raises(ValueError, match="ROUTER_AI_MIN_CONFIDENCE must be between 0.0 and 1.0"):
            AIRouterConfig.load_from_environment()

    def test_min_confidence_out_of_range_low(self, monkeypatch):
        """Test min_confidence value below 0.0."""
        monkeypatch.setenv("ROUTER_AI_MIN_CONFIDENCE", "-1.0")
        with pytest.raises(ValueError, match="ROUTER_AI_MIN_CONFIDENCE must be between 0.0 and 1.0"):
            AIRouterConfig.load_from_environment()

    def test_complete_env_loading(self, monkeypatch):
        """Test loading all AI router environment variables."""
        monkeypatch.setenv("ROUTER_AI_ENABLED", "true")
        monkeypatch.setenv("ROUTER_AI_PROVIDER", "openai")
        monkeypatch.setenv("ROUTER_AI_MODEL", "gpt-4")
        monkeypatch.setenv("ROUTER_AI_ENDPOINT", "http://api.openai.com")
        monkeypatch.setenv("ROUTER_AI_TIMEOUT_MS", "10000")
        monkeypatch.setenv("ROUTER_AI_WEIGHT", "0.8")
        monkeypatch.setenv("ROUTER_AI_MIN_CONFIDENCE", "0.5")

        config = AIRouterConfig.load_from_environment()
        assert config.enabled is True
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.endpoint == "http://api.openai.com"
        assert config.timeout_ms == 10000
        assert config.weight == 0.8
        assert config.min_confidence == 0.5

    def test_disabled_via_env(self, monkeypatch):
        """Test disabling AI router via environment."""
        monkeypatch.setenv("ROUTER_AI_ENABLED", "false")
        config = AIRouterConfig.load_from_environment()
        assert config.enabled is False

    def test_endpoint_trailing_slash_stripped(self, monkeypatch):
        """Test that trailing slashes are removed from endpoint."""
        monkeypatch.setenv("ROUTER_AI_ENDPOINT", "http://ollama:11434/")
        config = AIRouterConfig.load_from_environment()
        assert config.endpoint == "http://ollama:11434"
        assert not config.endpoint.endswith("/")


class TestToolRouterConfigValidation:
    """Test ToolRouterConfig validation and error handling."""

    def test_invalid_max_tools_search(self, monkeypatch):
        """Test invalid max_tools_search value."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("MAX_TOOLS_SEARCH", "invalid")
        with pytest.raises(ValueError, match="MAX_TOOLS_SEARCH must be a valid integer"):
            ToolRouterConfig.load_from_environment()

    def test_invalid_default_top_n(self, monkeypatch):
        """Test invalid default_top_n value."""
        monkeypatch.setenv("GATEWAY_JWT", "token")
        monkeypatch.setenv("DEFAULT_TOP_N", "not_number")
        with pytest.raises(ValueError, match="DEFAULT_TOP_N must be a valid integer"):
            ToolRouterConfig.load_from_environment()
