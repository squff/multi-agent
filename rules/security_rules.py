import ast
import json
import re
from pathlib import Path
from typing import Any, Optional


class SecurityRuleEngine:
    """Load and evaluate security rules against source code."""

    def __init__(self, rules_path: Optional[str] = None):
        path = rules_path or Path(__file__).parent.parent / "rules" / "security_rules.json"
        with open(path, "r", encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

    def scan(self, source: str, filepath: str = "<string>") -> list[dict[str, Any]]:
        issues = []
        tree = ast.parse(source)
        lines = source.split("\n")

        for rule in self.rules:
            pattern = rule.get("pattern")
            if not pattern:
                if rule["id"] == "QUAL002":
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            end_lineno = getattr(node, "end_lineno", node.lineno)
                            if end_lineno - node.lineno > 50:
                                issues.append({
                                    "rule_id": rule["id"],
                                    "severity": rule["severity"],
                                    "message": rule["message"],
                                    "line": node.lineno,
                                })
                continue

            for lineno, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        "rule_id": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "line": lineno,
                    })

        return issues
