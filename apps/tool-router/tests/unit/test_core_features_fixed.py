"""Unit tests for core features to improve coverage."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, mock_open
import os

from tool_router.core.features import FeatureFlags, Feature, get_feature_flags, is_feature_enabled, reload_feature_flags


class TestFeatureFlags:
    """Tests for FeatureFlags class."""

    def test_load_with_yaml_and_env(self, mocker) -> None:
        """Test load method with both YAML and environment variables."""
        mock_yaml_content = """
features:
  test_feature:
    enabled: true
    description: "Test feature"
    category: "test"
    env_var: "TEST_FEATURE"
"""

        # Mock YAML loading
        mocker.patch("builtins.open", mock_open(read_data=mock_yaml_content))
        mock_yaml_load = mocker.patch("yaml.safe_load")
        mock_yaml_load.return_value = {
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test feature",
                    "category": "test",
                    "env_var": "TEST_FEATURE"
                }
            }
        }

        # Mock environment variables
        mocker.patch.dict(os.environ, {
            "TEST_FEATURE": "false"
        })

        flags = FeatureFlags.load()

        # Environment variable should override YAML
        assert not flags.is_enabled("test_feature")

    def test_load_from_yaml_method(self, mocker) -> None:
        """Test _load_from_yaml method."""
        mock_yaml_content = """
features:
  test_feature:
    enabled: true
    description: "Test feature"
    category: "test"
"""

        mock_file_exists = mocker.patch("tool_router.core.features.Path.exists", return_value=True)
        mocker.patch("builtins.open", mock_open(read_data=mock_yaml_content))
        mock_yaml_load = mocker.patch("yaml.safe_load")
        mock_yaml_load.return_value = {
            "features": {
                "test_feature": {
                    "enabled": True,
                    "description": "Test feature",
                    "category": "test"
                }
            }
        }

        flags = FeatureFlags()
        flags._load_from_yaml()

        assert flags.is_enabled("test_feature")
        feature = flags.get_feature("test_feature")
        assert feature.enabled is True
        assert feature.description == "Test feature"
        assert feature.category == "test"

    def test_load_from_yaml_file_not_found(self, mocker) -> None:
        """Test _load_from_yaml when YAML file doesn't exist."""
        mocker.patch("tool_router.core.features.Path.exists", return_value=False)

        flags = FeatureFlags()
        flags._load_from_yaml()  # Should not raise exception

        # Should have empty features
        assert len(flags.get_all_features()) == 0

    def test_load_from_yaml_invalid_yaml(self, mocker) -> None:
        """Test _load_from_yaml with invalid YAML content."""
        mocker.patch("tool_router.core.features.Path.exists", return_value=True)
        mocker.patch("builtins.open", mock_open(read_data="invalid: yaml: content:"))
        mock_yaml_load = mocker.patch("yaml.safe_load")
        mock_yaml_load.side_effect = Exception("Invalid YAML")

        flags = FeatureFlags()
        flags._load_from_yaml()  # Should not raise exception

        # Should have empty features
        assert len(flags.get_all_features()) == 0

    def test_load_from_yaml_no_features_section(self, mocker) -> None:
        """Test _load_from_yaml when YAML has no features section."""
        mock_yaml_content = """
other_config:
  some_value: true
"""

        mocker.patch("tool_router.core.features.Path.exists", return_value=True)
        mocker.patch("builtins.open", mock_open(read_data=mock_yaml_content))
        mock_yaml_load = mocker.patch("yaml.safe_load")
        mock_yaml_load.return_value = {"other_config": {"some_value": True}}

        flags = FeatureFlags()
        flags._load_from_yaml()

        # Should have empty features
        assert len(flags.get_all_features()) == 0

    def test_load_from_environment_method(self, mocker) -> None:
        """Test _load_from_environment method."""
        # First add a feature to test with
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test",
            env_var="TEST_FEATURE"
        )

        mocker.patch.dict(os.environ, {
            "TEST_FEATURE": "false"
        })

        flags._load_from_environment()

        assert not flags.is_enabled("test_feature")

    def test_load_from_environment_backward_compat(self, mocker) -> None:
        """Test _load_from_environment with backward compatibility."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test",
            backward_compat="OLD_TEST_FEATURE"
        )

        mocker.patch.dict(os.environ, {
            "OLD_TEST_FEATURE": "false"
        })

        flags._load_from_environment()

        assert not flags.is_enabled("test_feature")

    def test_is_enabled_with_existing_feature(self) -> None:
        """Test is_enabled with an existing feature."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )

        assert flags.is_enabled("test_feature") is True

    def test_is_enabled_with_nonexistent_feature(self) -> None:
        """Test is_enabled with a nonexistent feature."""
        flags = FeatureFlags()

        assert flags.is_enabled("nonexistent") is False

    def test_get_feature_with_existing_feature(self) -> None:
        """Test get_feature with an existing feature."""
        flags = FeatureFlags()
        test_feature = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )
        flags.features["test_feature"] = test_feature

        result = flags.get_feature("test_feature")

        assert result is test_feature
        assert result.name == "test_feature"
        assert result.enabled is True

    def test_get_feature_with_nonexistent_feature(self) -> None:
        """Test get_feature with a nonexistent feature."""
        flags = FeatureFlags()

        result = flags.get_feature("nonexistent")

        assert result is None

    def test_get_all_features(self) -> None:
        """Test get_all_features method."""
        flags = FeatureFlags()
        flags.features["feature1"] = Feature(
            name="feature1",
            enabled=True,
            description="Feature 1",
            category="cat1"
        )
        flags.features["feature2"] = Feature(
            name="feature2",
            enabled=False,
            description="Feature 2",
            category="cat2"
        )

        result = flags.get_all_features()

        assert len(result) == 2
        assert "feature1" in result
        assert "feature2" in result
        # Should be a copy, not the original
        assert result is not flags.features

    def test_get_features_by_category(self) -> None:
        """Test get_features_by_category method."""
        flags = FeatureFlags()
        flags.features["feature1"] = Feature(
            name="feature1",
            enabled=True,
            description="Feature 1",
            category="cat1"
        )
        flags.features["feature2"] = Feature(
            name="feature2",
            enabled=False,
            description="Feature 2",
            category="cat1"
        )
        flags.features["feature3"] = Feature(
            name="feature3",
            enabled=True,
            description="Feature 3",
            category="cat2"
        )

        result = flags.get_features_by_category("cat1")

        assert len(result) == 2
        assert "feature1" in result
        assert "feature2" in result
        assert "feature3" not in result

    def test_update_feature_existing(self) -> None:
        """Test update_feature with existing feature."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )

        result = flags.update_feature("test_feature", False)

        assert result is True
        assert flags.is_enabled("test_feature") is False

    def test_update_feature_nonexistent(self) -> None:
        """Test update_feature with nonexistent feature."""
        flags = FeatureFlags()

        result = flags.update_feature("nonexistent", True)

        assert result is False

    def test_save_to_yaml_success(self, mocker) -> None:
        """Test save_to_yaml with successful save."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )

        mock_file_open = mocker.patch("builtins.open", mock_open())
        mock_yaml_dump = mocker.patch("yaml.dump")
        mock_mkdir = mocker.patch("tool_router.core.features.Path.mkdir")

        result = flags.save_to_yaml()

        assert result is True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_open.assert_called_once()
        mock_yaml_dump.assert_called_once()

    def test_save_to_yaml_failure(self, mocker) -> None:
        """Test save_to_yaml with save failure."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )

        mock_file_open = mocker.patch("builtins.open", mock_open())
        mock_yaml_dump = mocker.patch("yaml.dump", side_effect=Exception("Save failed"))
        mock_mkdir = mocker.patch("tool_router.core.features.Path.mkdir")

        result = flags.save_to_yaml()

        assert result is False

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        flags = FeatureFlags()
        flags.features["test_feature"] = Feature(
            name="test_feature",
            enabled=True,
            description="Test feature",
            category="test"
        )

        result = flags.to_dict()

        assert isinstance(result, dict)
        assert "test_feature" in result
        assert result["test_feature"]["enabled"] is True
        assert result["test_feature"]["description"] == "Test feature"
        assert result["test_feature"]["category"] == "test"


class TestFeatureFlagsModule:
    """Tests for module-level functions."""

    def test_get_feature_flags(self, mocker) -> None:
        """Test get_feature_flags function."""
        mock_flags = Mock(spec=FeatureFlags)
        mocker.patch("tool_router.core.features._feature_flags", mock_flags)

        result = get_feature_flags()

        assert result is mock_flags

    def test_is_feature_enabled(self, mocker) -> None:
        """Test is_feature_enabled convenience function."""
        mock_flags = Mock(spec=FeatureFlags)
        mock_flags.is_enabled.return_value = True
        mocker.patch("tool_router.core.features._feature_flags", mock_flags)

        result = is_feature_enabled("test_feature")

        assert result is True
        mock_flags.is_enabled.assert_called_once_with("test_feature")

    def test_reload_feature_flags(self, mocker) -> None:
        """Test reload_feature_flags function."""
        mock_flags = Mock(spec=FeatureFlags)
        mock_load = mocker.patch.object(FeatureFlags, "load", return_value=mock_flags)
        mocker.patch("tool_router.core.features._feature_flags", mock_flags)

        result = reload_feature_flags()

        assert result is mock_flags
        mock_load.assert_called_once()
