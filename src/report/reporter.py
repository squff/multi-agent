from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class ReportGenerator:
    """Generates structured reports from pipeline execution results."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(self, result: dict[str, Any]) -> str:
        status_emoji = {
            "completed": "✅",
            "completed_with_issues": "⚠️",
            "failed": "❌",
            "running": "🔄",
        }.get(result.get("status", "unknown"), "❓")

        lines = [
            f"# Pipeline Report: {status_emoji} {result.get('status', 'unknown')}",
            "",
            f"- **Requirement:** {result.get('requirement', 'N/A')[:100]}",
            f"- **Started:** {result.get('started_at', 'N/A')}",
            f"- **Completed:** {result.get('completed_at', 'N/A')}",
            "",
        ]

        artifacts = result.get("artifacts", [])
        if artifacts:
            lines.append(f"## Generated Artifacts ({len(artifacts)})")
            lines.append("")
            for art in artifacts:
                code = art.get("code", "")
                lines.append(f"### {art['task_id']}: {art.get('description', 'N/A')}")
                lines.append("")
                lines.append("```python")
                lines.append(code if len(code) < 500 else code[:500] + "\n...")
                lines.append("```")
                lines.append("")

        reports = result.get("review_reports", [])
        if reports:
            lines.append("## Review Reports")
            lines.append("")
            total_issues = sum(len(r.get("security_issues", [])) + len(r.get("quality_issues", [])) for r in reports)
            lines.append(f"**Total issues found:** {total_issues}")
            lines.append("")
            for r in reports:
                lines.append(f"### {r.get('task_id', 'unknown')} — Score: {r.get('score', 'N/A')}")
                for sec in r.get("security_issues", []):
                    lines.append(f"- 🔴 `{sec['rule_id']}` {sec['message']} (line {sec['line']})")
                for qual in r.get("quality_issues", [])[:5]:
                    lines.append(f"- 🟡 {qual.get('message', qual)}")
                lines.append("")

        errors = result.get("errors", [])
        if errors:
            lines.append("## Errors")
            lines.append("")
            for err in errors:
                lines.append(f"- ❌ {err}")

        return "\n".join(lines)

    def generate_json(self, result: dict[str, Any]) -> str:
        safe = dict(result)
        safe["report_generated_at"] = datetime.now().isoformat()
        return json.dumps(safe, ensure_ascii=False, indent=2)

    def save(self, result: dict[str, Any], fmt: str = "md") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = ".md" if fmt == "md" else ".json"
        filename = f"pipeline_report_{timestamp}{ext}"
        filepath = self.output_dir / filename

        content = self.generate_markdown(result) if fmt == "md" else self.generate_json(result)
        filepath.write_text(content, encoding="utf-8")
        return str(filepath)
