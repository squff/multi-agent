from __future__ import annotations

from src.bus.message_bus import MessageBus, Message, MessageType


class TestMessageBus:
    def setup_method(self) -> None:
        self.bus = MessageBus()
        self.bus.reset()

    def test_singleton(self) -> None:
        b1 = MessageBus()
        b2 = MessageBus()
        assert b1 is b2

    def test_publish_and_subscribe(self) -> None:
        received = []

        def handler(msg: Message) -> None:
            received.append(msg)

        self.bus.subscribe(MessageType.LOG, handler)
        self.bus.publish(Message(MessageType.LOG, "test", {"data": "hello"}))

        assert len(received) == 1
        assert received[0].sender == "test"
        assert received[0].payload["data"] == "hello"

    def test_unsubscribe(self) -> None:
        received = []

        def handler(msg: Message) -> None:
            received.append(msg)

        self.bus.subscribe(MessageType.LOG, handler)
        self.bus.unsubscribe(MessageType.LOG, handler)
        self.bus.publish(Message(MessageType.LOG, "test", {}))
        assert len(received) == 0

    def test_get_history(self) -> None:
        self.bus.publish(Message(MessageType.PIPELINE_STARTED, "orc", {}))
        self.bus.publish(Message(MessageType.TASK_COMPLETED, "exec", {"task_id": "t1"}))
        self.bus.publish(Message(MessageType.TASK_COMPLETED, "exec", {"task_id": "t2"}))

        all_msgs = self.bus.get_history()
        assert len(all_msgs) == 3

        task_msgs = self.bus.get_history(MessageType.TASK_COMPLETED)
        assert len(task_msgs) == 2

    def test_reset_clears_history(self) -> None:
        self.bus.publish(Message(MessageType.LOG, "test", {}))
        assert len(self.bus.get_history()) == 1
        self.bus.reset()
        assert len(self.bus.get_history()) == 0
