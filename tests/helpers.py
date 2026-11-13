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


class CountNode(Node):
    """An exec node. Its output is the number of times that it ran."""

    title = "Count"

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_output("count")

    def compute(self) -> None:
        self.count += 1
        self.set_output("count", self.count)


class ChooseNode(Node):
    """An exec node that runs "yes" or "no", as the input "condition" tells."""

    title = "Choose"

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("yes")
        self.add_exec_output("no")
        self.add_input("condition", default=False)

    def compute(self) -> None:
        self.run_exec_output("yes" if self.get_input("condition") else "no")


class RepeatNode(Node):
    """An exec node that runs "body" three times, with index 0, 1 and 2. Then it runs "done"."""

    title = "Repeat"

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("body")
        self.add_exec_output("done")
        self.add_output("index")

    def compute(self) -> None:
        for index in range(3):
            self.set_output("index", index)
            self.run_exec_output("body")
        self.run_exec_output("done")


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
