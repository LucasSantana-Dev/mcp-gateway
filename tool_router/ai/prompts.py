"""Prompt templates for AI tool selection."""

from __future__ import annotations


class PromptTemplates:
    """Prompt templates for AI tool selection."""

    TOOL_SELECTION_TEMPLATE = """You are a tool selection assistant. Given a task and list of available tools, select the best tool.

Task: {task}

Available tools:
{tool_list}

Respond with JSON:
{{
  "tool_name": "<exact tool name from the list>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}}"""

    @staticmethod
    def create_tool_selection_prompt(task: str, tool_list: str) -> str:
        """Create a tool selection prompt.

        Args:
            task: The task description
            tool_list: Formatted list of available tools

        Returns:
            Complete prompt string
        """
        return PromptTemplates.TOOL_SELECTION_TEMPLATE.format(
            task=task,
            tool_list=tool_list
        )
