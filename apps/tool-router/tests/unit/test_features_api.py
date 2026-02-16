"""Unit tests for feature toggle API endpoints."""

from __future__ import annotations

import pytest
from flask import Flask

from tool_router.api.features import features_bp
from tool_router.core.features import Feature, FeatureFlags


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(features_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_feature_flags(mocker):
    """Mock feature flags for testing."""
    mock_flags = mocker.Mock(spec=FeatureFlags)
    mock_flags.features = {
        "ai_routing": Feature(
            name="ai_routing",
            enabled=True,
            description="AI-powered tool selection",
            category="ai",
            requires_restart=False,
            env_var="ENABLE_AI_ROUTING",
            backward_compat=None,
        ),
        "metrics": Feature(
            name="metrics",
            enabled=False,
            description="Metrics collection",
            category="observability",
            requires_restart=True,
            env_var="ENABLE_METRICS",
            backward_compat=None,
        ),
    }
    mock_flags.to_dict.return_value = {
        "ai_routing": {
            "name": "ai_routing",
            "enabled": True,
            "description": "AI-powered tool selection",
            "category": "ai",
            "requires_restart": False,
            "env_var": "ENABLE_AI_ROUTING",
            "backward_compat": None,
        },
        "metrics": {
            "name": "metrics",
            "enabled": False,
            "description": "Metrics collection",
            "category": "observability",
            "requires_restart": True,
            "env_var": "ENABLE_METRICS",
            "backward_compat": None,
        },
    }
    return mock_flags


class TestListFeatures:
    """Tests for GET /api/features endpoint."""

    def test_list_features_success(self, client, mocker, mock_feature_flags):
        """Test successful feature listing."""
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.get("/api/features")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "features" in data
        assert "ai" in data["features"]
        assert "observability" in data["features"]
        assert "ai_routing" in data["features"]["ai"]
        assert "metrics" in data["features"]["observability"]

    def test_list_features_error(self, client, mocker):
        """Test error handling when listing features."""
        mocker.patch(
            "tool_router.api.features.get_feature_flags",
            side_effect=Exception("Config error"),
        )

        response = client.get("/api/features")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "Config error" in data["error"]


class TestGetFeature:
    """Tests for GET /api/features/<name> endpoint."""

    def test_get_feature_success(self, client, mocker, mock_feature_flags):
        """Test successful feature retrieval."""
        mock_feature_flags.get_feature.return_value = mock_feature_flags.features["ai_routing"]
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.get("/api/features/ai_routing")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["feature"]["name"] == "ai_routing"
        assert data["feature"]["enabled"] is True
        assert data["feature"]["category"] == "ai"

    def test_get_feature_not_found(self, client, mocker, mock_feature_flags):
        """Test getting non-existent feature."""
        mock_feature_flags.get_feature.return_value = None
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.get("/api/features/nonexistent")
        assert response.status_code == 404

        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()

    def test_get_feature_error(self, client, mocker):
        """Test error handling when getting feature."""
        mocker.patch(
            "tool_router.api.features.get_feature_flags",
            side_effect=Exception("Database error"),
        )

        response = client.get("/api/features/ai_routing")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "Database error" in data["error"]


class TestToggleFeature:
    """Tests for PATCH /api/features/<name> endpoint."""

    def test_toggle_feature_enable(self, client, mocker, mock_feature_flags):
        """Test enabling a feature."""
        mock_feature_flags.get_feature.return_value = mock_feature_flags.features["metrics"]
        mock_feature_flags.update_feature.return_value = True
        mock_feature_flags.save_to_yaml.return_value = True
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.patch("/api/features/metrics", json={"enabled": True})
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "updated successfully" in data["message"]
        mock_feature_flags.update_feature.assert_called_once_with("metrics", True)

    def test_toggle_feature_disable(self, client, mocker, mock_feature_flags):
        """Test disabling a feature."""
        mock_feature_flags.get_feature.return_value = mock_feature_flags.features["ai_routing"]
        mock_feature_flags.update_feature.return_value = True
        mock_feature_flags.save_to_yaml.return_value = True
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.patch("/api/features/ai_routing", json={"enabled": False})
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        mock_feature_flags.update_feature.assert_called_once_with("ai_routing", False)

    def test_toggle_feature_missing_enabled(self, client, mocker, mock_feature_flags):
        """Test toggle without enabled field."""
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.patch("/api/features/ai_routing", json={})
        assert response.status_code == 400

        data = response.get_json()
        assert data["success"] is False
        assert "enabled" in data["error"].lower()

    def test_toggle_feature_update_failed(self, client, mocker, mock_feature_flags):
        """Test when feature update fails."""
        mock_feature_flags.get_feature.return_value = None
        mocker.patch("tool_router.api.features.get_feature_flags", return_value=mock_feature_flags)

        response = client.patch("/api/features/nonexistent", json={"enabled": True})
        assert response.status_code == 404

        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()

    def test_toggle_feature_error(self, client, mocker):
        """Test error handling during toggle."""
        mocker.patch(
            "tool_router.api.features.get_feature_flags",
            side_effect=Exception("Update error"),
        )

        response = client.patch("/api/features/ai_routing", json={"enabled": True})
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "Update error" in data["error"]


class TestReloadFeatures:
    """Tests for POST /api/features/reload endpoint."""

    def test_reload_features_success(self, client, mocker, mock_feature_flags):
        """Test successful feature reload."""
        mocker.patch("tool_router.api.features.reload_feature_flags", return_value=mock_feature_flags)

        response = client.post("/api/features/reload")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "reloaded successfully" in data["message"]

    def test_reload_features_error(self, client, mocker):
        """Test error handling during reload."""
        mocker.patch(
            "tool_router.api.features.reload_feature_flags",
            side_effect=Exception("File not found"),
        )

        response = client.post("/api/features/reload")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "File not found" in data["error"]
