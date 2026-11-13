"""Flow nodes. They control which exec nodes run, and how many times.

After an exec node runs, the graph usually runs all of its exec outputs. Branch and the loop
nodes choose their exec outputs themselves: compute() calls run_exec_output().
"""

from __future__ import annotations

from node_editor.node import Node


class BranchNode(Node):
    """Runs "true" if the condition is True. Runs "false" if the condition is False."""

    title = "Branch"
    category = "Flow"
    color = (110, 110, 110)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("true")
        self.add_exec_output("false")
        self.add_input("condition", default=False)

    def compute(self) -> None:
        if self.get_input("condition"):
            self.run_exec_output("true")
        else:
            self.run_exec_output("false")


class ForLoopNode(Node):
    """Runs "loop body" one time for each whole number from first to last. Then runs "completed".

    "index" is the number of the loop now. For example, first 1 and last 3 run the loop body
    with index 1, then 2, then 3.
    """

    title = "For Loop"
    category = "Flow"
    color = (110, 110, 110)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("loop body")
        self.add_exec_output("completed")
        self.add_input("first", default=1)
        self.add_input("last", default=10)
        self.add_output("index")

    def compute(self) -> None:
        first = int(self.get_input("first"))
        last = int(self.get_input("last"))
        for index in range(first, last + 1):
            self.set_output("index", index)
            self.run_exec_output("loop body")
        self.run_exec_output("completed")


class ForEachNode(Node):
    """Runs "loop body" one time for each item in a list. Then runs "completed".

    "item" is the item now, and "index" is its position in the list (the first item is 0).
    """

    title = "For Each"
    category = "Flow"
    color = (110, 110, 110)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("loop body")
        self.add_exec_output("completed")
        self.add_input("items", default=[])
        self.add_output("item")
        self.add_output("index")

    def compute(self) -> None:
        for index, item in enumerate(self.get_input("items")):
            self.set_output("item", item)
            self.set_output("index", index)
            self.run_exec_output("loop body")
        self.run_exec_output("completed")


class SequenceNode(Node):
    """Runs "first", then "second", then "third".

    This node does not need a compute() method: the graph runs all exec outputs, in order.
    """

    title = "Sequence"
    category = "Flow"
    color = (110, 110, 110)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("first")
        self.add_exec_output("second")
        self.add_exec_output("third")


class CounterNode(Node):
    """Counts the number of times that it ran: 1 at the first run, then 2, then 3.

    The count starts at 0 again when you open the graph.
    """

    title = "Counter"
    category = "Flow"
    color = (110, 110, 110)

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_output("count")

    def compute(self) -> None:
        self.count += 1
        self.set_output("count", self.count)
