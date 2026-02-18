"""AI-powered tool selection using Ollama."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class OllamaSelector:
    """AI-powered tool selector using Ollama LLM."""

    def __init__(self, endpoint: str, model: str, timeout: int = 2000) -> None:
        """Initialize the Ollama selector.

        Args:
            endpoint: Ollama API endpoint (e.g., http://localhost:11434)
            model: Model name (e.g., llama3.2:3b)
            timeout: Timeout in milliseconds
        """
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.timeout_ms = timeout
        self.timeout_s = timeout / 1000.0

    def select_tool(self, task: str, tools: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Select the best tool for a given task using AI.

        Args:
            task: The task description
            tools: List of available tools with name and description

        Returns:
            Dictionary with tool_name, confidence, and reasoning, or None if failed
        """
        try:
            # Prepare tool list for the prompt
            tool_list = "\n".join(
                f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
                for tool in tools
            )

            # Create the prompt
            prompt = self._create_prompt(task, tool_list)

            # Call Ollama API
            response = self._call_ollama(prompt)
            if not response:
                return None

            # Parse the response
            result = self._parse_response(response)
            return result

        except Exception as e:
            logger.warning(f"AI selector failed: {e}")
            return None

    def _create_prompt(self, task: str, tool_list: str) -> str:
        """Create the prompt for Ollama."""
        return f"""You are a tool selection assistant. Given a task and list of available tools, select the best tool.

Task: {task}

Available tools:
{tool_list}

Respond with JSON:
{{
  "tool_name": "<exact tool name from the list>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}}"""

    def _call_ollama(self, prompt: str) -> str | None:
        """Call the Ollama API."""
        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for consistent results
                            "max_tokens": 150,   # Keep responses short
                        }
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()

        except httpx.TimeoutException:
            logger.warning(f"Ollama request timed out after {self.timeout_ms}ms")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"Ollama HTTP error: {e}")
            return None
        except Exception as e:
            logger.warning(f"Ollama request failed: {e}")
            return None

    def _parse_response(self, response: str) -> dict[str, Any] | None:
        """Parse the JSON response from Ollama."""
        try:
            # Extract JSON from the response (in case there's extra text)
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in Ollama response")
                return None

            json_str = response[start_idx:end_idx]
            result = json.loads(json_str)

            # Validate required fields
            if not all(key in result for key in ["tool_name", "confidence", "reasoning"]):
                logger.warning("Missing required fields in AI response")
                return None

            # Validate confidence range
            confidence = result["confidence"]
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                logger.warning(f"Invalid confidence value: {confidence}")
                return None

            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error parsing AI response: {e}")
            return None
