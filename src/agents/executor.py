from __future__ import annotations

import ast
from typing import Any, Optional

from schemas.task_schema import Task, TaskStatus
from models.mimo_v2_5_pro import MiMoV2_5Pro, MiMoMessage
from tools.code_formatter import format_code


class ExecutorAgent:
    """Agent that generates runnable Python code from task descriptions."""

    def __init__(self, model: Optional[Any] = None):
        self.model = model or MiMoV2_5Pro()
        self.name = "Executor"

    def execute(self, task: Task) -> Task:
        """Generate code for a single task."""
        task.status = TaskStatus.IN_PROGRESS

        try:
            code = self._generate_code(task)
            formatted = format_code(code)
            self._validate_syntax(formatted)
            task.output = formatted
            task.status = TaskStatus.COMPLETED
        except SyntaxError as e:
            task.error = f"Generated code has syntax errors: {e}"
            task.status = TaskStatus.FAILED
        except Exception as e:
            task.error = f"Execution failed: {e}"
            task.status = TaskStatus.FAILED

        return task

    def _generate_code(self, task: Task) -> str:
        """Prompt the model to generate code for the given task."""
        prompt = (
            f"Write a Python implementation for the following task:\n\n"
            f"Task: {task.description}\n"
            f"Priority: {task.priority.value}\n\n"
            f"Requirements:\n"
            f"- Include type annotations for all function signatures\n"
            f"- Follow PEP8 conventions (snake_case, 88 char line limit)\n"
            f"- Include a module-level docstring\n"
            f"- Use `from __future__ import annotations` for forward references\n"
            f"- Output ONLY the Python code, no markdown or explanation"
        )

        messages = [
            MiMoMessage(role="system", content=self._system_prompt()),
            MiMoMessage(role="user", content=prompt),
        ]

        response = self.model.generate(messages)
        return self._extract_code(response.text)

    def _system_prompt(self) -> str:
        return (
            "You are an expert Python engineer. Generate clean, "
            "production-ready code with proper type annotations and docstrings."
        )

    def _extract_code(self, text: str) -> str:
        """Extract Python code from model output, stripping markdown fences."""
        import re
        match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()

    def _validate_syntax(self, code: str) -> None:
        """Check that generated code is syntactically valid Python."""
        ast.parse(code)
