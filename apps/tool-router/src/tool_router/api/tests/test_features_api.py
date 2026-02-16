"""Integration tests for feature toggle REST API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tool_router.api.features import features_bp
from tool_router.core.features import FeatureFlags


@pytest.fixture
def temp_features_config(tmp_path):
    """Create a temporary features.yaml file for testing."""
    config_file = tmp_path / "features.yaml"
    config_data = {
        "version": "1.0",
        "features": {
            "test_feature_1": {
                "enabled": True,
                "description": "Test feature 1",
                "category": "test",
                "requires_restart": False,
                "env_var": "TEST_FEATURE_1",
            },
            "test_feature_2": {
                "enabled": False,
                "description": "Test feature 2",
                "category": "test",
                "requires_restart": True,
                "env_var": "TEST_FEATURE_2",
            },
            "core_ai_router": {
                "enabled": True,
                "description": "AI Router",
                "category": "core",
                "requires_restart": True,
                "env_var": "FEATURE_CORE_AI_ROUTER",
            },
        },
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    return config_file


@pytest.fixture
def flask_app(temp_features_config, monkeypatch):
    """Create a Flask test app with features blueprint."""
    from flask import Flask

    app = Flask(__name__)
    app.config["TESTING"] = True

    # Create a test FeatureFlags instance
    test_flags = FeatureFlags(config_file=temp_features_config)
    test_flags._load_from_yaml()

    # Patch the get_feature_flags function to return our test instance
    import tool_router.api.features as features_module
    monkeypatch.setattr(features_module, "get_feature_flags", lambda: test_flags)

    app.register_blueprint(features_bp)

    return app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    return flask_app.test_client()


class TestListFeatures:
    """Tests for GET /api/features endpoint."""

    def test_list_all_features(self, client) -> None:
        """Test listing all features."""
        response = client.get("/api/features")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "features" in data
        assert len(data["features"]) == 3
        assert "test_feature_1" in data["features"]
        assert "test_feature_2" in data["features"]
        assert "core_ai_router" in data["features"]

    def test_list_features_by_category(self, client) -> None:
        """Test filtering features by category."""
        response = client.get("/api/features?category=test")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["features"]) == 2
        assert "test_feature_1" in data["features"]
        assert "test_feature_2" in data["features"]
        assert "core_ai_router" not in data["features"]

    def test_list_features_invalid_category(self, client) -> None:
        """Test listing features with non-existent category."""
        response = client.get("/api/features?category=nonexistent")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["features"]) == 0


class TestGetFeature:
    """Tests for GET /api/features/<name> endpoint."""

    def test_get_existing_feature(self, client) -> None:
        """Test getting a specific feature."""
        response = client.get("/api/features/test_feature_1")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["name"] == "test_feature_1"
        assert data["enabled"] is True
        assert data["description"] == "Test feature 1"
        assert data["category"] == "test"
        assert data["requires_restart"] is False

    def test_get_nonexistent_feature(self, client) -> None:
        """Test getting a feature that doesn't exist."""
        response = client.get("/api/features/nonexistent")
        assert response.status_code == 404

        data = json.loads(response.data)
        assert "error" in data
        assert "not found" in data["error"].lower()


class TestUpdateFeature:
    """Tests for PATCH /api/features/<name> endpoint."""

    def test_update_feature_enable(self, client) -> None:
        """Test enabling a disabled feature."""
        response = client.patch(
            "/api/features/test_feature_2",
            data=json.dumps({"enabled": True}),
            content_type="application/json",
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["feature"]["enabled"] is True

    def test_update_feature_disable(self, client) -> None:
        """Test disabling an enabled feature."""
        response = client.patch(
            "/api/features/test_feature_1",
            data=json.dumps({"enabled": False}),
            content_type="application/json",
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["feature"]["enabled"] is False

    def test_update_nonexistent_feature(self, client) -> None:
        """Test updating a feature that doesn't exist."""
        response = client.patch(
            "/api/features/nonexistent",
            data=json.dumps({"enabled": True}),
            content_type="application/json",
        )
        assert response.status_code == 404

        data = json.loads(response.data)
        assert "error" in data

    def test_update_feature_missing_enabled_field(self, client) -> None:
        """Test updating without providing enabled field."""
        response = client.patch(
            "/api/features/test_feature_1",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data
        assert "enabled" in data["error"].lower()

    def test_update_feature_invalid_json(self, client) -> None:
        """Test updating with invalid JSON."""
        response = client.patch(
            "/api/features/test_feature_1",
            data="invalid json",
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data

    def test_update_feature_invalid_enabled_type(self, client) -> None:
        """Test updating with non-boolean enabled value."""
        response = client.patch(
            "/api/features/test_feature_1",
            data=json.dumps({"enabled": "not a boolean"}),
            content_type="application/json",
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data


class TestReloadFeatures:
    """Tests for POST /api/features/reload endpoint."""

    def test_reload_features_success(self, client, temp_features_config) -> None:
        """Test reloading features from YAML."""
        # Modify the YAML file
        config_data = {
            "version": "1.0",
            "features": {
                "new_feature": {
                    "enabled": True,
                    "description": "New feature",
                    "category": "test",
                }
            },
        }
        with open(temp_features_config, "w") as f:
            yaml.dump(config_data, f)

        response = client.post("/api/features/reload")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert "reloaded" in data["message"].lower()

    def test_reload_features_missing_file(self, client) -> None:
        """Test reloading when config file doesn't exist."""
        import tool_router.api.features as features_module
        original_config = features_module.flags.config_file
        features_module.flags.config_file = Path("/nonexistent/features.yaml")

        response = client.post("/api/features/reload")

        # Should still succeed but with empty features
        assert response.status_code == 200

        # Restore original config
        features_module.flags.config_file = original_config


class TestListCategories:
    """Tests for GET /api/features/categories endpoint."""

    def test_list_categories(self, client) -> None:
        """Test listing all feature categories."""
        response = client.get("/api/features/categories")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "categories" in data
        assert "test" in data["categories"]
        assert "core" in data["categories"]
        assert len(data["categories"]) == 2

    def test_categories_with_counts(self, client) -> None:
        """Test that categories include feature counts."""
        response = client.get("/api/features/categories")
        assert response.status_code == 200

        data = json.loads(response.data)
        categories = data["categories"]

        # Test category has 2 features
        assert categories["test"] == 2
        # Core category has 1 feature
        assert categories["core"] == 1


class TestFeatureIntegration:
    """Integration tests for feature toggle workflows."""

    def test_full_feature_lifecycle(self, client) -> None:
        """Test complete feature lifecycle: list, get, update, reload."""
        # 1. List all features
        response = client.get("/api/features")
        assert response.status_code == 200
        json.loads(response.data)["features"]

        # 2. Get specific feature
        response = client.get("/api/features/test_feature_1")
        assert response.status_code == 200
        feature = json.loads(response.data)
        assert feature["enabled"] is True

        # 3. Disable the feature
        response = client.patch(
            "/api/features/test_feature_1",
            data=json.dumps({"enabled": False}),
            content_type="application/json",
        )
        assert response.status_code == 200

        # 4. Verify it's disabled
        response = client.get("/api/features/test_feature_1")
        assert response.status_code == 200
        feature = json.loads(response.data)
        assert feature["enabled"] is False

        # 5. Reload features
        response = client.post("/api/features/reload")
        assert response.status_code == 200

    def test_category_filtering_workflow(self, client) -> None:
        """Test filtering features by category."""
        # Get all categories
        response = client.get("/api/features/categories")
        assert response.status_code == 200
        categories = json.loads(response.data)["categories"]

        # For each category, get features
        for category in categories:
            response = client.get(f"/api/features?category={category}")
            assert response.status_code == 200
            features = json.loads(response.data)["features"]

            # Verify all features belong to the category
            for _feature_name, feature_data in features.items():
                assert feature_data["category"] == category
