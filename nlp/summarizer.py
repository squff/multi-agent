from __future__ import annotations

import re
from typing import Optional


def summarize_context(
    context: list[dict[str, str]],
    max_tokens: int = 4096,
    preserve_patterns: Optional[list[str]] = None,
) -> str:
    """Compress a conversation context into a concise summary.

    Args:
        context: List of {"role": ..., "content": ...} messages.
        max_tokens: Target token budget for the summary.
        preserve_patterns: Regex patterns for content that must be kept verbatim.

    Returns:
        Compressed summary string.
    """
    if not context:
        return ""

    patterns = preserve_patterns or [
        r"def \w+\(.*?\)",
        r"class \w+",
        r"(?:func|fn|function)\s+\w+",
        r"^\s*#\s*(?:TODO|FIXME|HACK|XXX)",
    ]

    preserved: list[str] = []
    summaries: list[str] = []

    for msg in context:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")

        for pat in patterns:
            preserved.extend(re.findall(pat, content, re.MULTILINE))

        if len(content) > 200:
            compressed = _compress_message(content)
            summaries.append(f"[{role}] {compressed}")
        else:
            summaries.append(f"[{role}] {content}")

    summary = "; ".join(summaries)
    if len(summary) > max_tokens * 4:
        summary = summary[: max_tokens * 4] + "..."

    preserved_unique = list(dict.fromkeys(preserved))
    if preserved_unique:
        preserved_str = "; ".join(preserved_unique[:50])
        summary = f"{summary}\n\n# Preserved signatures: {preserved_str}"

    return summary


def _compress_message(text: str) -> str:
    """Truncate a long message to its first and last sections."""
    lines = text.split("\n")
    if len(lines) <= 6:
        head = " ".join(lines[:3])
        return head[:300]

    head = " ".join(lines[:3])
    tail = " ".join(lines[-3:])
    compressed = f"{head[:200]} ... ({len(lines)} lines total) ... {tail[:200]}"
    return compressed


def extract_key_variables(text: str) -> dict[str, str]:
    """Extract variable assignments that appear to be important."""
    variables: dict[str, str] = {}
    for match in re.finditer(
        r'(?:self\.)?(\w+)\s*=\s*(?:(\d+\.?\d*)|(\[.*?\])|(\{.*?\})|(\'.*?\')|(".*?"))',
        text,
    ):
        name = match.group(1)
        value = next(g for g in match.groups()[1:] if g is not None)
        if not name.startswith("_"):
            variables[name] = value[:80]
    return variables
