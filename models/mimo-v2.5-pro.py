"""MiMo-V2.5-Pro model interface.

Provides a thin wrapper for invoking the MiMo-V2.5-Pro model
for long-context code generation and reasoning tasks.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MiMoConfig:
    api_base: str = os.getenv("MIMO_API_BASE", "https://api.mimo-platform.dev/v1")
    api_key: str = os.getenv("MIMO_API_KEY", "")
    model: str = "mimo-v2.5-pro"
    max_tokens: int = 32768
    temperature: float = 0.3
    top_p: float = 0.95
    max_context_length: int = 1_000_000


@dataclass
class MiMoMessage:
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass
class MiMoResponse:
    text: str
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = "stop"


class MiMoV2_5Pro:
    """Client for the MiMo-V2.5-Pro model API."""

    def __init__(self, config: Optional[MiMoConfig] = None):
        self.config = config or MiMoConfig()

    def generate(
        self,
        messages: list[MiMoMessage],
        stream: bool = False,
    ) -> MiMoResponse:
        """Send a completion request to the MiMo model."""
        if not self.config.api_key:
            return self._fallback_generate(messages)

        payload = {
            "model": self.config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": stream,
        }

        try:
            import requests
            resp = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            return MiMoResponse(
                text=choice["message"]["content"],
                usage=data.get("usage", {}),
                finish_reason=choice.get("finish_reason", "stop"),
            )
        except Exception as exc:
            return MiMoResponse(
                text=f"# MiMo API call failed: {exc}\n# Falling back to local mode.",
                usage={},
                finish_reason="error",
            )

    def _fallback_generate(self, messages: list[MiMoMessage]) -> MiMoResponse:
        """Local fallback when no API key is configured."""
        last = messages[-1].content if messages else ""
        return MiMoResponse(
            text=f"# [MiMo Fallback] Received {len(messages)} messages.\n"
                 f"# Last message ({len(last)} chars): {last[:200]}...\n"
                 f"# Configure MIMO_API_KEY for remote inference.",
            usage={"prompt_tokens": 0, "completion_tokens": 0},
            finish_reason="stop",
        )

    def count_tokens(self, text: str) -> int:
        """Rough token count estimate."""
        return len(text) // 4 + 1
