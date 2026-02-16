"""Unit tests for feature toggle system."""

import yaml

from tool_router.core.features import Feature, FeatureFlags


class TestFeature:
    """Test Feature dataclass."""

    def test_feature_creation(self):
        """Test creating a Feature instance."""
        feature = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test",
            requires_restart=False,
            env_var="TEST_FEATURE",
        )
        assert feature.name == "test_feature"
        assert feature.enabled is True
        assert feature.description == "Test feature"
        assert feature.category == "test"
        assert feature.requires_restart is False
        assert feature.env_var == "TEST_FEATURE"


class TestFeatureFlags:
    """Test FeatureFlags class."""

    def test_load_from_yaml(self, tmp_path):
        """Test loading feature flags from YAML file."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test feature",
                    "category": "test",
                    "requires_restart": False,
                    "env_var": "TEST_FEATURE",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        assert "test_feature" in flags.features
        assert flags.features["test_feature"].enabled is True
        assert flags.features["test_feature"].description == "Test feature"

    def test_load_from_environment(self, tmp_path, monkeypatch):
        """Test environment variable overrides."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": False,
                    "description": "Test feature",
                    "category": "test",
                    "env_var": "TEST_FEATURE",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        # Override with environment variable
        monkeypatch.setenv("TEST_FEATURE", "true")
        flags._load_from_environment()

        assert flags.features["test_feature"].enabled is True

    def test_backward_compatibility(self, tmp_path, monkeypatch):
        """Test backward compatibility with old env var names."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "core_ai_router": {
                    "enabled": False,
                    "description": "AI Router",
                    "category": "core",
                    "env_var": "FEATURE_CORE_AI_ROUTER",
                    "backward_compat": "ROUTER_AI_ENABLED",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        # Use old env var name
        monkeypatch.setenv("ROUTER_AI_ENABLED", "true")
        flags._load_from_environment()

        assert flags.features["core_ai_router"].enabled is True

    def test_is_enabled(self, tmp_path):
        """Test is_enabled method."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "enabled_feature": {
                    "enabled": True,
                    "description": "Enabled",
                    "category": "test",
                },
                "disabled_feature": {
                    "enabled": False,
                    "description": "Disabled",
                    "category": "test",
                },
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        assert flags.is_enabled("enabled_feature") is True
        assert flags.is_enabled("disabled_feature") is False
        assert flags.is_enabled("nonexistent_feature") is False

    def test_get_feature(self, tmp_path):
        """Test get_feature method."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test",
                    "category": "test",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        feature = flags.get_feature("test_feature")
        assert feature is not None
        assert feature.name == "test_feature"

        nonexistent = flags.get_feature("nonexistent")
        assert nonexistent is None

    def test_get_features_by_category(self, tmp_path):
        """Test get_features_by_category method."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "core_feature": {
                    "enabled": True,
                    "description": "Core",
                    "category": "core",
                },
                "api_feature": {
                    "enabled": True,
                    "description": "API",
                    "category": "api",
                },
                "another_core": {
                    "enabled": False,
                    "description": "Another Core",
                    "category": "core",
                },
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        core_features = flags.get_features_by_category("core")
        assert len(core_features) == 2
        assert "core_feature" in core_features
        assert "another_core" in core_features

        api_features = flags.get_features_by_category("api")
        assert len(api_features) == 1
        assert "api_feature" in api_features

    def test_update_feature(self, tmp_path):
        """Test update_feature method."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test",
                    "category": "test",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        assert flags.is_enabled("test_feature") is True

        success = flags.update_feature("test_feature", False)
        assert success is True
        assert flags.is_enabled("test_feature") is False

        # Try updating nonexistent feature
        success = flags.update_feature("nonexistent", True)
        assert success is False

    def test_save_to_yaml(self, tmp_path):
        """Test save_to_yaml method."""
        config_file = tmp_path / "features.yaml"
        flags = FeatureFlags(config_file=config_file)

        # Add a feature manually
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test",
            requires_restart=False,
            env_var="TEST_FEATURE",
        )

        # Save to YAML
        success = flags.save_to_yaml()
        assert success is True
        assert config_file.exists()

        # Load and verify
        with open(config_file) as f:
            saved_data = yaml.safe_load(f)

        assert "features" in saved_data
        assert "test_feature" in saved_data["features"]
        assert saved_data["features"]["test_feature"]["enabled"] is True

    def test_to_dict(self, tmp_path):
        """Test to_dict method."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test",
                    "category": "test",
                    "requires_restart": False,
                    "env_var": "TEST_FEATURE",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        result = flags.to_dict()
        assert "test_feature" in result
        assert result["test_feature"]["enabled"] is True
        assert result["test_feature"]["description"] == "Test"
        assert result["test_feature"]["category"] == "test"

    def test_missing_config_file(self, tmp_path):
        """Test behavior when config file doesn't exist."""
        config_file = tmp_path / "nonexistent.yaml"
        flags = FeatureFlags(config_file=config_file)
        flags._load_from_yaml()

        # Should not crash, just have no features
        assert len(flags.features) == 0

    def test_env_var_precedence(self, tmp_path, monkeypatch):
        """Test that environment variables take precedence over YAML."""
        config_file = tmp_path / "features.yaml"
        config_data = {
            "version": "1.0",
            "features": {
                "test_feature": {
                    "enabled": False,
                    "description": "Test",
                    "category": "test",
                    "env_var": "TEST_FEATURE",
                }
            },
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Set env var to true
        monkeypatch.setenv("TEST_FEATURE", "true")

        flags = FeatureFlags.load()
        flags.config_file = config_file
        flags._load_from_yaml()
        flags._load_from_environment()

        # Env var should override YAML
        assert flags.is_enabled("test_feature") is True
