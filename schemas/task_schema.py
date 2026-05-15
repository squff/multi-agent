from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    id: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    parent_id: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    subtasks: list[Task] = field(default_factory=list)
    output: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "dependencies": self.dependencies,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "output": self.output,
            "error": self.error,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        subtasks = [cls.from_dict(st) for st in data.pop("subtasks", [])]
        data["priority"] = Priority(data.get("priority", "medium"))
        data["status"] = TaskStatus(data.get("status", "pending"))
        task = cls(**data)
        task.subtasks = subtasks
        return task


@dataclass
class TaskList:
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def to_json(self) -> str:
        return json.dumps(
            [t.to_dict() for t in self.tasks], ensure_ascii=False, indent=2
        )

    @classmethod
    def from_json(cls, data: str) -> TaskList:
        items = json.loads(data)
        return cls(tasks=[Task.from_dict(item) for item in items])
