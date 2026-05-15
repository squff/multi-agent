from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from src.config.settings import AppConfig, AgentConfig, PipelineConfig, MiMoConfig


class TestAppConfig:
    def test_default_config(self) -> None:
        config = AppConfig()
        assert config.agent.max_retries == 2
        assert config.agent.reviewer_threshold == 7.0
        assert config.pipeline.max_context_tokens == 4096
        assert config.mimo.model == "mimo-v2.5-pro"
        assert config.mimo.temperature == 0.3

    def test_load_from_json(self) -> None:
        data = {
            "agent": {"max_retries": 5, "reviewer_threshold": 8.0},
            "pipeline": {"log_level": "DEBUG"},
            "mimo": {"temperature": 0.1},
        }
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            tmp_path = f.name

        try:
            config = AppConfig.load(tmp_path)
            assert config.agent.max_retries == 5
            assert config.agent.reviewer_threshold == 8.0
            assert config.pipeline.log_level == "DEBUG"
            assert config.mimo.temperature == 0.1
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_env_overrides(self) -> None:
        os.environ["MIMO_API_KEY"] = "test-key-12345"
        os.environ["PIPELINE_LOG_LEVEL"] = "ERROR"
        try:
            config = AppConfig.load()
            assert config.mimo.api_key == "test-key-12345"
            assert config.pipeline.log_level == "ERROR"
        finally:
            del os.environ["MIMO_API_KEY"]
            del os.environ["PIPELINE_LOG_LEVEL"]

    def test_to_dict_roundtrip(self) -> None:
        original = AppConfig()
        original.agent.max_retries = 3
        data = original.to_dict()
        restored = AppConfig.from_dict(data)
        assert restored.agent.max_retries == 3


class TestAgentConfig:
    def test_defaults(self) -> None:
        c = AgentConfig()
        assert c.max_concurrent_tasks == 3


class TestPipelineConfig:
    def test_defaults(self) -> None:
        c = PipelineConfig()
        assert c.persist_state is True


class TestMiMoConfig:
    def test_defaults(self) -> None:
        c = MiMoConfig()
        assert c.max_context_length == 1_000_000
        assert c.top_p == 0.95
