"""REST API endpoints for feature toggle management.

Provides HTTP endpoints for the web admin UI to manage feature flags:
- GET /api/features - List all features
- GET /api/features/{name} - Get specific feature
- PATCH /api/features/{name} - Toggle feature
- POST /api/features/reload - Reload from YAML
"""

from typing import Any

from flask import Blueprint, jsonify, request

from tool_router.core.features import get_feature_flags, reload_feature_flags


features_bp = Blueprint("features", __name__)


@features_bp.route("/api/features", methods=["GET"])
def list_features() -> tuple[dict[str, Any], int]:
    """List all feature flags with their current state.

    Returns:
        JSON response with all features grouped by category
    """
    try:
        flags = get_feature_flags()
        features_dict = flags.to_dict()

        # Group by category for better UI organization
        grouped: dict[str, dict[str, Any]] = {}
        for name, feature in features_dict.items():
            category = feature["category"]
            if category not in grouped:
                grouped[category] = {}
            grouped[category][name] = feature

        return jsonify({"success": True, "features": grouped}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@features_bp.route("/api/features/<feature_name>", methods=["GET"])
def get_feature(feature_name: str) -> tuple[dict[str, Any], int]:
    """Get details of a specific feature flag.

    Args:
        feature_name: Name of the feature

    Returns:
        JSON response with feature details
    """
    try:
        flags = get_feature_flags()
        feature = flags.get_feature(feature_name)

        if not feature:
            return jsonify({"success": False, "error": "Feature not found"}), 404

        return (
            jsonify(
                {
                    "success": True,
                    "feature": {
                        "name": feature.name,
                        "enabled": feature.enabled,
                        "description": feature.description,
                        "category": feature.category,
                        "requires_restart": feature.requires_restart,
                        "env_var": feature.env_var,
                        "backward_compat": feature.backward_compat,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@features_bp.route("/api/features/<feature_name>", methods=["PATCH"])
def update_feature(feature_name: str) -> tuple[dict[str, Any], int]:
    """Toggle a feature flag on or off.

    Args:
        feature_name: Name of the feature

    Request Body:
        {"enabled": true/false}

    Returns:
        JSON response with updated feature state
    """
    try:
        data = request.get_json()
        if not data or "enabled" not in data:
            return (
                jsonify({"success": False, "error": "Missing 'enabled' field"}),
                400,
            )

        enabled = data["enabled"]
        if not isinstance(enabled, bool):
            return (
                jsonify({"success": False, "error": "'enabled' must be a boolean"}),
                400,
            )

        flags = get_feature_flags()
        feature = flags.get_feature(feature_name)

        if not feature:
            return jsonify({"success": False, "error": "Feature not found"}), 404

        # Update feature state
        success = flags.update_feature(feature_name, enabled)
        if not success:
            return (
                jsonify({"success": False, "error": "Failed to update feature"}),
                500,
            )

        # Save to YAML
        save_success = flags.save_to_yaml()
        if not save_success:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Feature updated but failed to save to YAML",
                    }
                ),
                500,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Feature '{feature_name}' updated successfully",
                    "feature": {
                        "name": feature.name,
                        "enabled": feature.enabled,
                        "requires_restart": feature.requires_restart,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@features_bp.route("/api/features/reload", methods=["POST"])
def reload_features() -> tuple[dict[str, Any], int]:
    """Reload feature flags from YAML configuration.

    Returns:
        JSON response with reload status
    """
    try:
        flags = reload_feature_flags()
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Feature flags reloaded successfully",
                    "feature_count": len(flags.features),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@features_bp.route("/api/features/categories", methods=["GET"])
def list_categories() -> tuple[dict[str, Any], int]:
    """List all feature categories with counts.

    Returns:
        JSON response with category information
    """
    try:
        flags = get_feature_flags()
        categories: dict[str, int] = {}

        for feature in flags.features.values():
            category = feature.category
            categories[category] = categories.get(category, 0) + 1

        return jsonify({"success": True, "categories": categories}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
