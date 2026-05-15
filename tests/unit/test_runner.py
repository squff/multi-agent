from __future__ import annotations

import tempfile
from pathlib import Path

from src.pipeline.runner import StateManager


class TestStateManager:
    def setup_method(self) -> None:
        self.tmpdir = tempfile.mkdtemp()
        self.mgr = StateManager(state_dir=self.tmpdir)

    def test_save_and_load(self) -> None:
        data = {"status": "completed", "requirement": "test", "artifacts": []}
        path = self.mgr.save("pipeline_001", data)
        assert Path(path).exists()

        loaded = self.mgr.load("pipeline_001")
        assert loaded is not None
        assert loaded["status"] == "completed"

    def test_load_nonexistent(self) -> None:
        result = self.mgr.load("nonexistent")
        assert result is None

    def test_list_pipelines(self) -> None:
        self.mgr.save("p1", {"status": "completed", "started_at": "2025-01-01"})
        self.mgr.save("p2", {"status": "failed", "started_at": "2025-01-02"})
        pipelines = self.mgr.list_pipelines()
        assert len(pipelines) == 2
        assert pipelines[0]["id"] == "p2"  # sorted by date desc
