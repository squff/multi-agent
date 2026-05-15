from __future__ import annotations

from typing import Any, Optional

from nlp.summarizer import summarize_context, extract_key_variables


class ContextManager:
    """Manages and compresses conversation context to fit within token limits."""

    def __init__(self, max_tokens: int = 4096):
        self.max_tokens = max_tokens
        self.context: list[dict[str, str]] = []
        self.summary: Optional[str] = None

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the context."""
        self.context.append({"role": role, "content": content})
        if self._estimate_tokens() > self.max_tokens:
            self.compress()

    def get_context(self) -> list[dict[str, str]]:
        """Return the current (possibly compressed) context."""
        if self.summary:
            return [{"role": "system", "content": self.summary}]
        return self.context

    def compress(self) -> str:
        """Compress the full context into a summary, preserving key signatures."""
        preserved = extract_key_variables(
            "\n".join(m["content"] for m in self.context)
        )

        self.summary = summarize_context(
            self.context,
            max_tokens=self.max_tokens,
            preserve_patterns=[
                r"def \w+\(.*?\)",
                r"class \w+",
                *[rf"\b{k}\b" for k in preserved],
            ],
        )

        self.context = []
        return self.summary

    def reset(self) -> None:
        """Clear all context and summary."""
        self.context = []
        self.summary = None

    def _estimate_tokens(self) -> int:
        """Approximate token count."""
        total = sum(len(m.get("content", "")) for m in self.context)
        return total // 4
