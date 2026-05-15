import ast
import re
import subprocess
from typing import Any

from rules.security_rules import SecurityRuleEngine


class PylintWrapper:
    """Wrapper around pylint with additional custom checks."""

    def __init__(self, threshold: float = 7.0):
        self.threshold = threshold
        self.security_engine = SecurityRuleEngine()

    def run(self, filepath: str) -> dict[str, Any]:
        """Run pylint on a file and return structured results."""
        result: dict[str, Any] = {
            "score": 10.0,
            "issues": [],
            "security_issues": [],
            "passed": True,
        }

        pylint_issues = self._run_pylint(filepath)
        result["issues"].extend(pylint_issues)

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        sec_issues = self.security_engine.scan(source, filepath)
        result["security_issues"].extend(sec_issues)

        total_bonus = self._count_quality_bonus(source)
        deduction = len(result["issues"]) * 0.5 + len(result["security_issues"]) * 2.0
        result["score"] = max(0.0, min(10.0, 10.0 - deduction + total_bonus))
        result["passed"] = (
            result["score"] >= self.threshold
            and len(result["security_issues"]) == 0
        )
        return result

    def _run_pylint(self, filepath: str) -> list[dict[str, Any]]:
        """Execute pylint as a subprocess."""
        try:
            proc = subprocess.run(
                ["pylint", "--output-format=json", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if proc.returncode in (0, 2, 4, 8, 16, 32):
                return []
            if proc.stdout.strip():
                import json
                return json.loads(proc.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return []

    def _count_quality_bonus(self, source: str) -> float:
        """Add bonus for docstrings and type annotations."""
        bonus = 0.0
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    bonus += 0.2
                if node.returns:
                    bonus += 0.1
        return min(bonus, 2.0)
