from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


@dataclass
class AgentConfig:
    planner_model: str = "mimo-v2.5-pro"
    executor_model: str = "mimo-v2.5-pro"
    reviewer_threshold: float = 7.0
    max_retries: int = 2
    max_concurrent_tasks: int = 3


@dataclass
class PipelineConfig:
    max_context_tokens: int = 4096
    persist_state: bool = True
    state_dir: str = ".pipeline_state"
    report_dir: str = "reports"
    log_level: str = "INFO"


@dataclass
class MiMoConfig:
    api_base: str = field(default_factory=lambda: os.getenv("MIMO_API_BASE", "https://api.mimo-platform.dev/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("MIMO_API_KEY", ""))
    model: str = "mimo-v2.5-pro"
    max_tokens: int = 32768
    temperature: float = 0.3
    top_p: float = 0.95
    max_context_length: int = 1_000_000


@dataclass
class AppConfig:
    agent: AgentConfig = field(default_factory=AgentConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    mimo: MiMoConfig = field(default_factory=MiMoConfig)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> AppConfig:
        return cls(
            agent=AgentConfig(**data.get("agent", {})),
            pipeline=PipelineConfig(**data.get("pipeline", {})),
            mimo=MiMoConfig(**data.get("mimo", {})),
        )

    @classmethod
    def load(cls, path: Optional[str] = None) -> AppConfig:
        config = cls()
        if path and Path(path).exists():
            with open(path, "r") as f:
                if path.endswith(".json"):
                    data = json.load(f)
                    config = cls.from_dict(data)
                elif path.endswith((".yaml", ".yml")):
                    import yaml
                    data = yaml.safe_load(f)
                    config = cls.from_dict(data)
        env_overrides = {
            "mimo.api_key": os.getenv("MIMO_API_KEY"),
            "mimo.api_base": os.getenv("MIMO_API_BASE"),
            "pipeline.log_level": os.getenv("PIPELINE_LOG_LEVEL"),
        }
        for key, value in env_overrides.items():
            if value:
                section, attr = key.split(".")
                getattr(config, section).__dict__[attr] = value
        return config


DEFAULT_CONFIG = AppConfig()
