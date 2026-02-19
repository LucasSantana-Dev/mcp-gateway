"""MCP Tools for Specialist Training Infrastructure.

This module provides MCP server tools for managing specialist AI training,
including training pipeline management, knowledge base operations, and evaluation.
"""

from __future__ import annotations

from .training_manager import (
    TrainingManagerTool,
    TRAINING_MANAGER_SCHEMA,
    training_manager_handler
)
from .knowledge_base_tool import (
    KnowledgeBaseTool,
    KNOWLEDGE_BASE_SCHEMA,
    knowledge_base_handler
)
from .evaluation_tool import (
    EvaluationTool,
    EVALUATION_SCHEMA,
    evaluation_handler
)
from .server_integration import (
    SpecialistTrainingMCPServer,
    get_server_instance,
    register_tools_with_mcp_server
)

__all__ = [
    # Training Manager
    "TrainingManagerTool",
    "TRAINING_MANAGER_SCHEMA",
    "training_manager_handler",

    # Knowledge Base
    "KnowledgeBaseTool",
    "KNOWLEDGE_BASE_SCHEMA",
    "knowledge_base_handler",

    # Evaluation
    "EvaluationTool",
    "EVALUATION_SCHEMA",
    "evaluation_handler",

    # Server Integration
    "SpecialistTrainingMCPServer",
    "get_server_instance",
    "register_tools_with_mcp_server"
]
