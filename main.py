from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

from src.pipeline.orchestrator import Orchestrator
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.core.reviewer import ReviewerAgent
from src.config.settings import AppConfig


def main(argv: Optional[list[str]] = None) -> None:
    """CLI entry point for the Multi-Agent pipeline."""
    argv = argv or sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help"):
        print("Usage: python -m main <requirement_file> [options]")
        print()
        print("Options:")
        print("  --config FILE     Path to config JSON/YAML file")
        print("  --report-dir DIR  Output directory for reports")
        print("  --max-retries N   Max retry attempts per task (default: 2)")
        print("  --json            Output JSON report")
        print("  --requirement R   Inline requirement string")
        print()
        print("Examples:")
        print('  python -m main --requirement "- [ ] Build login API"')
        print('  python -m main requirements.txt --json')
        return

    config_path = _extract_flag(argv, "--config")
    report_dir = _extract_flag(argv, "--report-dir") or "reports"
    max_retries = int(_extract_flag(argv, "--max-retries") or "2")
    output_json = "--json" in argv

    config = AppConfig.load(config_path)
    config.pipeline.report_dir = report_dir
    config.agent.max_retries = max_retries

    requirement = _get_requirement(argv)
    if not requirement:
        print("Error: No requirement provided.", file=sys.stderr)
        sys.exit(1)

    orc = Orchestrator(
        planner=PlannerAgent(),
        executor=ExecutorAgent(),
        reviewer=ReviewerAgent(threshold=config.agent.reviewer_threshold),
        max_retries=config.agent.max_retries,
    )

    result = orc.run(requirement)
    fmt = "json" if output_json else "md"

    from src.report.reporter import ReportGenerator
    reporter = ReportGenerator(output_dir=report_dir)
    report_path = reporter.save(result, fmt=fmt)
    print(f"Report saved: {report_path}")
    print(f"Pipeline status: {result.get('status', 'unknown')}")
    sys.exit(0 if result.get("status") in ("completed", "completed_with_issues") else 1)


def _extract_flag(argv: list[str], flag: str) -> Optional[str]:
    for i, arg in enumerate(argv):
        if arg == flag and i + 1 < len(argv):
            value = argv.pop(i + 1)
            argv.pop(i)
            return value
    return None


def _get_requirement(argv: list[str]) -> Optional[str]:
    if "--requirement" in argv:
        idx = argv.index("--requirement")
        if idx + 1 < len(argv):
            return argv[idx + 1]
    if argv and not argv[0].startswith("--"):
        path = Path(argv[0])
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


if __name__ == "__main__":
    main()
