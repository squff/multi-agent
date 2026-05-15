from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from schemas.task_schema import TaskList, TaskStatus
from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.core.reviewer import ReviewerAgent
from src.utils.context_manager import ContextManager
from src.bus.message_bus import MessageBus, Message, MessageType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestrator")


class Orchestrator:
    """Coordinates the Planner - Executor - Reviewer pipeline with event-driven messaging."""

    def __init__(
        self,
        planner: Optional[PlannerAgent] = None,
        executor: Optional[ExecutorAgent] = None,
        reviewer: Optional[ReviewerAgent] = None,
        context_manager: Optional[ContextManager] = None,
        bus: Optional[MessageBus] = None,
        max_retries: int = 2,
    ):
        self.planner = planner or PlannerAgent()
        self.executor = executor or ExecutorAgent()
        self.reviewer = reviewer or ReviewerAgent()
        self.context = context_manager or ContextManager()
        self.bus = bus or MessageBus()
        self.max_retries = max_retries

    def run(self, requirement: str, config: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute the full pipeline from requirement to delivered code."""
        config = config or {}
        result: dict[str, Any] = {
            "requirement": requirement,
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "task_list": None,
            "artifacts": [],
            "review_reports": [],
            "errors": [],
            "metrics": {},
        }

        logger.info("Starting pipeline for requirement: %s", requirement[:80])
        self.bus.publish(Message(MessageType.PIPELINE_STARTED, "orchestrator",
                                 {"requirement": requirement[:200]}))

        try:
            task_list = self._phase_planning(requirement)
            result["task_list"] = task_list.to_json()

            artifacts = self._phase_execution(task_list, config)
            result["artifacts"] = artifacts

            reports = self._phase_review(artifacts)
            result["review_reports"] = reports

            total_issues = sum(
                len(r.get("security_issues", [])) + len(r.get("quality_issues", []))
                for r in reports
            )
            result["metrics"] = {
                "total_tasks": len(task_list.tasks),
                "completed_artifacts": len(artifacts),
                "total_issues": total_issues,
                "security_issues": sum(len(r.get("security_issues", [])) for r in reports),
            }

            if all(r.get("passed") for r in reports):
                result["status"] = "completed"
            else:
                result["status"] = "completed_with_issues"

            result["completed_at"] = datetime.now().isoformat()
            self.bus.publish(Message(MessageType.PIPELINE_COMPLETED, "orchestrator", {
                "status": result["status"], "metrics": result["metrics"],
            }))
            return result

        except Exception as e:
            logger.exception("Pipeline failed")
            result["status"] = "failed"
            result["errors"].append(str(e))
            result["completed_at"] = datetime.now().isoformat()
            self.bus.publish(Message(MessageType.PIPELINE_FAILED, "orchestrator",
                                     {"error": str(e)}))
            return result

    def _phase_planning(self, requirement: str) -> TaskList:
        """Phase 1: Decompose the requirement into tasks."""
        logger.info("Phase 1: Planning")
        self.context.add_message("user", requirement)
        task_list = self.planner.plan(requirement)
        self.context.add_message("assistant", f"Planned {len(task_list.tasks)} tasks")
        self.bus.publish(Message(MessageType.TASK_DELEGATED, "planner",
                                 {"task_count": len(task_list.tasks)}))
        return task_list

    def _phase_execution(self, task_list: TaskList, config: dict) -> list[dict[str, Any]]:
        """Phase 2: Execute each task to generate code."""
        logger.info("Phase 2: Execution")
        artifacts = []

        for task in task_list.tasks:
            for attempt in range(self.max_retries + 1):
                logger.info("  Executing task %s (attempt %d)", task.id, attempt + 1)
                executed = self.executor.execute(task)

                if executed.status == TaskStatus.COMPLETED:
                    artifacts.append({
                        "task_id": task.id,
                        "description": task.description,
                        "code": executed.output,
                    })
                    self.bus.publish(Message(MessageType.TASK_COMPLETED, "executor",
                                             {"task_id": task.id}))
                    break
                else:
                    logger.warning("  Task %s failed: %s", task.id, executed.error)
                    self.bus.publish(Message(MessageType.TASK_FAILED, "executor",
                                             {"task_id": task.id, "error": executed.error}))
                    if attempt < self.max_retries:
                        self._rollback(task_list, task)

        return artifacts

    def _phase_review(self, artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Phase 3: Review all generated code."""
        logger.info("Phase 3: Review")
        reports = []

        for artifact in artifacts:
            code = artifact.get("code", "")
            if not code:
                continue
            report = self.reviewer.review(code, f"artifact_{artifact['task_id']}.py")
            report["task_id"] = artifact["task_id"]
            reports.append(report)
            self.bus.publish(Message(MessageType.REVIEW_COMPLETED, "reviewer", {
                "task_id": artifact["task_id"],
                "passed": report["passed"],
                "issues": len(report.get("security_issues", [])) + len(report.get("quality_issues", [])),
            }))

        return reports

    def _rollback(self, task_list: TaskList, failed_task: Any) -> None:
        """Roll back state before retrying a failed task."""
        logger.info("  Rolling back task %s for retry", failed_task.id)
        failed_task.status = TaskStatus.PENDING
        failed_task.error = None
        failed_task.output = None
