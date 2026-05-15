from __future__ import annotations

from typing import Any, Optional

from models.mimo-v2.5-pro import MiMoResponse


class StubModel:
    """A lightweight mock model for testing without API dependencies."""

    def __init__(self, responses: Optional[dict[str, str]] = None):
        self.responses = responses or {}

    def generate(
        self,
        messages: list[Any],
        stream: bool = False,
    ) -> MiMoResponse:
        """Return a canned or template response."""
        last_content = messages[-1].content if messages else ""

        for trigger, response in self.responses.items():
            if trigger.lower() in last_content.lower():
                return MiMoResponse(text=response, usage={"prompt_tokens": 10, "completion_tokens": 20})

        return MiMoResponse(
            text=f"def stub_function():\n    \"\"\"Stub generated for: {last_content[:50]}...\"\"\"\n    pass\n",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
        )

    def count_tokens(self, text: str) -> int:
        return len(text) // 4 + 1
