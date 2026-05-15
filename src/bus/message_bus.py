from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class MessageType(Enum):
    TASK_DELEGATED = "task_delegated"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    REVIEW_REQUESTED = "review_requested"
    REVIEW_COMPLETED = "review_completed"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    LOG = "log"
    METRIC = "metric"


@dataclass
class Message:
    type: MessageType
    sender: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    correlation_id: Optional[str] = None


class MessageBus:
    """Simple pub/sub message bus for inter-agent communication."""

    _instance: Optional[MessageBus] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> MessageBus:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._subscribers = {}
                    cls._instance._history = []
                    cls._instance._max_history = 1000
        return cls._instance

    def subscribe(self, message_type: MessageType, callback: Callable[[Message], None]) -> None:
        self._subscribers.setdefault(message_type, []).append(callback)

    def unsubscribe(self, message_type: MessageType, callback: Callable) -> None:
        subs = self._subscribers.get(message_type, [])
        if callback in subs:
            subs.remove(callback)

    def publish(self, message: Message) -> None:
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        for callback in self._subscribers.get(message.type, []):
            try:
                callback(message)
            except Exception as e:
                print(f"[Bus] Error in subscriber {callback.__name__}: {e}")

    def get_history(self, message_type: Optional[MessageType] = None) -> list[Message]:
        if message_type:
            return [m for m in self._history if m.type == message_type]
        return list(self._history)

    def reset(self) -> None:
        self._history.clear()


bus = MessageBus()
