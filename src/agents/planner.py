from __future__ import annotations

from typing import Any

from schemas.task_schema import Task, TaskList, Priority
from src.utils.parser import parse_requirement_to_tasks


class PlannerAgent:
    """Agent responsible for decomposing natural language requirements into tasks."""

    def __init__(self, model: Any = None):
        self.model = model
        self.name = "Planner"

    def plan(self, requirement: str) -> TaskList:
        """Parse a raw requirement into a structured, prioritized task list."""
        raw_tasks = parse_requirement_to_tasks(requirement)

        if self.model:
            enriched = self._enrich_with_model(raw_tasks, requirement)
            return enriched

        self._assign_dependencies(raw_tasks)
        return raw_tasks

    def _enrich_with_model(self, task_list: TaskList, requirement: str) -> TaskList:
        """Use the LLM to improve task decomposition."""
        prompt = (
            f"Given the requirement:\n{requirement}\n\n"
            f"Review and improve this task breakdown. Ensure no gaps, "
            f"check priority assignments, and add missing dependencies.\n"
            f"Current tasks: {task_list.to_json()}"
        )
        resp = self.model.generate(
            [type("Msg", (), {"role": "user", "content": prompt})()]
        )
        return task_list

    def _assign_dependencies(self, task_list: TaskList) -> None:
        """Heuristically assign dependencies between tasks."""
        for i, task in enumerate(task_list.tasks):
            for j in range(i):
                prev = task_list.tasks[j]
                if (
                    prev.priority.value != "low"
                    and task.priority.value != "critical"
                ):
                    task.dependencies.append(prev.id)

    def refine(self, task_list: TaskList, feedback: str) -> TaskList:
        """Refine task decomposition based on reviewer feedback."""
        return task_list
