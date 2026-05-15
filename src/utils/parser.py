import json
import re
from typing import Optional

from schemas.task_schema import Task, TaskList, Priority


def parse_requirement_to_tasks(raw_text: str) -> TaskList:
    """Parse a natural language requirement into a structured task list."""
    lines = raw_text.strip().split("\n")
    task_list = TaskList()
    stack: list[tuple[int, Task]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        indent_level = len(line) - len(line.lstrip())
        parsed = _parse_single_line(stripped)
        if parsed is None:
            continue

        task = parsed
        while stack and stack[-1][0] >= indent_level:
            stack.pop()

        if stack:
            parent = stack[-1][1]
            task.parent_id = parent.id
            parent.subtasks.append(task)
        else:
            task_list.add_task(task)

        stack.append((indent_level, task))

    return task_list


def _parse_single_line(line: str) -> Optional[Task]:
    """Extract task metadata from a single line, e.g. '- [ ] title (priority:high)'."""
    cleaned = re.sub(r"^[-*\d]+\.?\s*\[\s*[ xX]?\s*\]\s*", "", line).strip()
    if not cleaned:
        return None

    priority = Priority.MEDIUM
    prio_match = re.search(r"\(priority:\s*(\w+)\)", cleaned, re.IGNORECASE)
    if prio_match:
        try:
            priority = Priority(prio_match.group(1).lower())
        except ValueError:
            pass
        cleaned = cleaned[: prio_match.start()].strip()

    task_id = f"task-{abs(hash(cleaned)) % 10**6:06d}"
    return Task(id=task_id, description=cleaned, priority=priority)


def extract_code_blocks(text: str) -> list[str]:
    """Extract Python code blocks from markdown text."""
    pattern = r"```(?:python)?\s*\n(.*?)```"
    return re.findall(pattern, text, re.DOTALL)


def parse_json_response(text: str) -> Optional[dict]:
    """Extract and parse a JSON object from model response text."""
    json_pattern = r"```(?:json)?\s*\n(\{.*?\})\s*```"
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
