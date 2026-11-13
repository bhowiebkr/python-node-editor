"""Small nodes for the tests. They do not use Qt."""

from __future__ import annotations

from typing import Any

from node_editor.node import Node


class NumberNode(Node):
    """A pure node with one output. It counts its runs."""

    title = "Number"

    def __init__(self, value: float = 0.0) -> None:
        super().__init__()
        self.value = value
        self.runs = 0
        self.add_output("value")

    def compute(self) -> None:
        self.runs += 1
        self.set_output("value", self.value)

    def get_state(self) -> dict[str, Any]:
        return {"value": self.value}

    def set_state(self, state: dict[str, Any]) -> None:
        self.value = state["value"]


class SumNode(Node):
    """A pure node: result = a + b."""

    title = "Sum"

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0)
        self.add_input("b", default=0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") + self.get_input("b"))


class StartNode(Node):
    """A start node: one exec output."""

    title = "Start"

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_output("then")


class LogNode(Node):
    """An exec node. It adds its input value to `log`."""

    title = "Log"

    def __init__(self, log: list[Any]) -> None:
        super().__init__()
        self.log = log
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_input("value")

    def compute(self) -> None:
        self.log.append(self.get_input("value"))


class FailNode(Node):
    """A pure node that always raises an exception."""

    title = "Fail"

    def __init__(self) -> None:
        super().__init__()
        self.add_output("value")

    def compute(self) -> None:
        raise ValueError("boom")


NODE_CLASSES: dict[str, type[Node]] = {
    "NumberNode": NumberNode,
    "SumNode": SumNode,
    "StartNode": StartNode,
    "FailNode": FailNode,
}
