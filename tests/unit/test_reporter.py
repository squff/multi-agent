from __future__ import annotations

import tempfile
from pathlib import Path

from src.report.reporter import ReportGenerator


class TestReportGenerator:
    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.reporter = ReportGenerator(output_dir=self.tmpdir)

    def test_generate_markdown(self) -> None:
        result = {
            "status": "completed",
            "requirement": "Build a login API",
            "started_at": "2025-01-01T00:00:00",
            "completed_at": "2025-01-01T00:01:00",
            "artifacts": [
                {"task_id": "t1", "description": "Create login endpoint", "code": "def login(): pass"}
            ],
            "review_reports": [
                {"task_id": "t1", "passed": True, "score": 9.5, "security_issues": [], "quality_issues": []}
            ],
            "errors": [],
        }
        md = self.reporter.generate_markdown(result)
        assert "Pipeline Report" in md
        assert "completed" in md
        assert "Build a login API" in md
        assert "def login(): pass" in md

    def test_generate_markdown_failed(self) -> None:
        result = {
            "status": "failed",
            "requirement": "Broken task",
            "started_at": "",
            "errors": ["Something went wrong"],
            "artifacts": [],
            "review_reports": [],
        }
        md = self.reporter.generate_markdown(result)
        assert "Something went wrong" in md

    def test_generate_json(self) -> None:
        result = {"status": "completed", "artifacts": [], "review_reports": [], "errors": []}
        js = self.reporter.generate_json(result)
        assert '"status": "completed"' in js
        assert "report_generated_at" in js

    def test_save_markdown(self) -> None:
        result = {"status": "completed", "artifacts": [], "review_reports": [], "errors": []}
        path = self.reporter.save(result, fmt="md")
        assert Path(path).exists()
        content = Path(path).read_text(encoding="utf-8")
        assert "Pipeline Report" in content

    def test_save_json(self) -> None:
        result = {"status": "completed", "artifacts": [], "review_reports": [], "errors": []}
        path = self.reporter.save(result, fmt="json")
        assert Path(path).exists()
        content = Path(path).read_text(encoding="utf-8")
        assert "completed" in content
