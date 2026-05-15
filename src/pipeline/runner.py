from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from schemas.task_schema import TaskList
from src.pipeline.orchestrator import Orchestrator


class StateManager:
    """Persist and restore pipeline state to/from disk."""

    def __init__(self, state_dir: str = ".pipeline_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save(self, pipeline_id: str, result: dict[str, Any]) -> str:
        path = self.state_dir / f"{pipeline_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return str(path)

    def load(self, pipeline_id: str) -> Optional[dict[str, Any]]:
        path = self.state_dir / f"{pipeline_id}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_pipelines(self) -> list[dict[str, str]]:
        pipelines = []
        for f in self.state_dir.glob("*.json"):
            data = self.load(f.stem)
            if data:
                pipelines.append({
                    "id": f.stem,
                    "status": data.get("status", "unknown"),
                    "started_at": data.get("started_at", ""),
                })
        return sorted(pipelines, key=lambda p: p.get("started_at", ""), reverse=True)


class PipelineRunner:
    """High-level runner wrapping Orchestrator with state persistence."""

    def __init__(self, orchestrator: Optional[Orchestrator] = None,
                 state_dir: str = ".pipeline_state"):
        self.orchestrator = orchestrator or Orchestrator()
        self.state = StateManager(state_dir)

    def run(self, requirement: str, pipeline_id: Optional[str] = None) -> dict[str, Any]:
        pid = pipeline_id or f"pipeline_{abs(hash(requirement)) % 10**6:06d}"
        print(f"[Runner] Starting pipeline {pid}")
        result = self.orchestrator.run(requirement)
        result["pipeline_id"] = pid
        state_path = self.state.save(pid, result)
        print(f"[Runner] State saved to {state_path}")
        return result

    def resume(self, pipeline_id: str) -> Optional[dict[str, Any]]:
        state = self.state.load(pipeline_id)
        if state and state.get("status") == "failed":
            print(f"[Runner] Resuming failed pipeline {pipeline_id}")
            requirement = state.get("requirement", "")
            return self.run(requirement, pipeline_id)
        return state
