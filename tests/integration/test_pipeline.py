from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.core.reviewer import ReviewerAgent
from src.pipeline.orchestrator import Orchestrator
from src.utils.context_manager import ContextManager
from tests.mocks.stub_model import StubModel

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(name: str) -> str:
    path = FIXTURES_DIR / "sample_requirements.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[name]


class TestPipelineIntegration:
    """End-to-end integration tests for the Multi-Agent pipeline."""

    def test_planner_decomposes_simple_requirement(self):
        planner = PlannerAgent()
        req = load_fixture("simple_requirement")
        task_list = planner.plan(req)
        assert len(task_list.tasks) == 4, f"Expected 4 tasks, got {len(task_list.tasks)}"
        priorities = [t.priority.value for t in task_list.tasks]
        assert "high" in priorities, "Expected at least one high-priority task"

    def test_planner_decomposes_nested_requirement(self):
        planner = PlannerAgent()
        req = load_fixture("complex_requirement")
        task_list = planner.plan(req)
        top_level = [t for t in task_list.tasks if t.parent_id is None]
        assert len(top_level) == 4, f"Expected 4 top-level tasks, got {len(top_level)}"
        has_nested = any(len(t.subtasks) > 0 for t in task_list.tasks)
        assert has_nested, "Expected at least one task with subtasks"

    def test_executor_generates_valid_code(self):
        from schemas.task_schema import Task, Priority
        stub = StubModel(responses={
            "Python": "def authenticate(token: str) -> dict:\n    \"\"\"Verify a JWT token and return user data.\"\"\"\n    return {\"user_id\": 1}\n",
        })
        executor = ExecutorAgent(model=stub)
        task_data = load_fixture("code_generation_task")
        task = Task(
            id=task_data["id"],
            description=task_data["description"],
            priority=Priority(task_data["priority"]),
        )
        result = executor.execute(task)
        assert result.status.value == "completed", f"Execution failed: {result.error}"
        assert result.output is not None, "Expected code output"
        assert "def " in result.output, "Expected function definition in output"

    def test_executor_with_stub_model(self):
        from schemas.task_schema import Task, Priority
        stub = StubModel(responses={"JWT": "def verify_jwt(token: str) -> dict: pass"})
        executor = ExecutorAgent(model=stub)
        task = Task(id="t1", description="Implement JWT verification", priority=Priority.HIGH)
        result = executor.execute(task)
        assert result.status.value == "completed"

    def test_reviewer_detects_security_issues(self):
        reviewer = ReviewerAgent()
        code = load_fixture("code_with_security_issues")
        report = reviewer.review(code)
        assert len(report["security_issues"]) > 0, "Expected security issues to be detected"
        issue_types = {i["rule_id"] for i in report["security_issues"]}
        assert "SEC001" in issue_types, "Expected hardcoded API key detection"
        assert "SEC002" in issue_types, "Expected SQL injection detection"

    def test_reviewer_passes_clean_code(self):
        reviewer = ReviewerAgent()
        code = """from __future__ import annotations

def greet(name: str) -> str:
    \"\"\"Return a greeting for the given name.\"\"\"
    return f"Hello, {name}!"
"""
        report = reviewer.review(code)
        assert report["passed"], "Expected clean code to pass review"

    def test_context_manager_compression(self):
        cm = ContextManager(max_tokens=100)
        for i in range(20):
            cm.add_message("user", f"This is message number {i} with some padding content to fill context.")
        compressed = cm.compress()
        assert compressed is not None, "Expected a compressed summary"
        assert len(compressed) > 0, "Expected non-empty summary"

    def test_orchestrator_full_pipeline_with_stub(self):
        stub = StubModel()
        planner = PlannerAgent(model=stub)
        executor = ExecutorAgent(model=stub)
        reviewer = ReviewerAgent()
        orc = Orchestrator(
            planner=planner,
            executor=executor,
            reviewer=reviewer,
            max_retries=1,
        )
        req = load_fixture("simple_requirement")
        result = orc.run(req)
        assert result["status"] in ("completed", "completed_with_issues"), f"Pipeline failed: {result['errors']}"
        assert result["task_list"] is not None, "Expected task list in result"
        assert len(result["artifacts"]) > 0, "Expected at least one code artifact"
        assert len(result["review_reports"]) > 0, "Expected review reports"

    def test_orchestrator_handles_empty_requirement(self):
        orc = Orchestrator(PlannerAgent(), ExecutorAgent(), ReviewerAgent())
        result = orc.run("")
        assert result["status"] in ("completed", "failed")

    def test_reviewer_suggest_fixes(self):
        reviewer = ReviewerAgent()
        issues = [
            {"rule_id": "SEC001", "severity": "critical", "message": "Hardcoded API key", "line": 5},
            {"rule_id": "SEC002", "severity": "critical", "message": "SQL injection risk", "line": 10},
        ]
        suggestions = reviewer.suggest_fixes(issues)
        assert len(suggestions) == 2
        assert "os.getenv" in suggestions[0]
        assert "parameterized" in suggestions[1]

    def test_context_manager_preserves_signatures(self):
        cm = ContextManager(max_tokens=500)
        cm.add_message("user", "def process_data(input_path: str) -> dict:")
        cm.add_message("assistant", "class DataProcessor:")
        for i in range(30):
            cm.add_message("user", f"Additional context line {i}" * 20)
        compressed = cm.compress()
        assert "process_data" in compressed or "DataProcessor" in compressed, (
            "Key signatures should be preserved in compression"
        )
