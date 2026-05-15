from __future__ import annotations

from typing import Any, Optional

from linters.pylint_wrapper import PylintWrapper
from rules.security_rules import SecurityRuleEngine


class ReviewerAgent:
    """Agent that reviews generated code for security and quality issues."""

    def __init__(self, threshold: float = 7.0):
        self.pylint = PylintWrapper(threshold=threshold)
        self.security = SecurityRuleEngine()
        self.name = "Reviewer"

    def review(self, code: str, filepath: str = "<string>") -> dict[str, Any]:
        """Run a full review of the provided code."""
        report: dict[str, Any] = {
            "passed": True,
            "score": 10.0,
            "security_issues": [],
            "quality_issues": [],
            "recommendations": [],
        }

        security_issues = self.security.scan(code, filepath)
        report["security_issues"] = security_issues

        try:
            lint_result = self.pylint.run(filepath)
            report["quality_issues"] = lint_result["issues"]
            report["score"] = lint_result["score"]
        except Exception as e:
            report["quality_issues"] = [{"message": f"Lint error: {e}"}]
            report["score"] = 5.0

        for issue in security_issues:
            report["recommendations"].append(
                f"[{issue['severity'].upper()}] {issue['message']} (line {issue['line']})"
            )

        report["passed"] = (
            len(security_issues) == 0 and report["score"] >= self.pylint.threshold
        )

        return report

    def suggest_fixes(self, issues: list[dict[str, Any]]) -> list[str]:
        """Generate fix suggestions from review issues."""
        suggestions = []
        for issue in issues:
            rid = issue.get("rule_id", "")
            if rid == "SEC001":
                suggestions.append(
                    "Move credentials to os.getenv() or a .env file"
                )
            elif rid == "SEC002":
                suggestions.append(
                    "Replace f-string SQL with parameterized query (? placeholder)"
                )
            elif rid == "SEC003":
                suggestions.append("Replace eval/exec with a safe parser")
            elif rid == "QUAL001":
                suggestions.append("Add type annotations to function signature")
            else:
                suggestions.append(issue.get("message", ""))
        return suggestions
