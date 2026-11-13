"""List nodes. A list is a row of values, for example [1, 2, 3] or ["milk", "eggs"].

To do something with each item in a list, use the For Each node.
"""

from __future__ import annotations

from node_editor.node import Node


class RangeNode(Node):
    """A list of the whole numbers from first to last. For example, 1 to 4 gives [1, 2, 3, 4]."""

    title = "Range"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("first", default=1)
        self.add_input("last", default=10)
        self.add_output("items")

    def compute(self) -> None:
        first = int(self.get_input("first"))
        last = int(self.get_input("last"))
        self.set_output("items", list(range(first, last + 1)))


class LengthNode(Node):
    """The number of items in a list. For a text, the number of characters."""

    title = "Length"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("items", default=[])
        self.add_output("length")

    def compute(self) -> None:
        self.set_output("length", len(self.get_input("items")))


class SumNode(Node):
    """Adds all the numbers in a list. For example, [1, 2, 3] gives 6."""

    title = "Sum"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("items", default=[])
        self.add_output("total")

    def compute(self) -> None:
        self.set_output("total", sum(self.get_input("items")))


class GetItemNode(Node):
    """One item from a list. The first item has index 0.

    A negative index counts from the end: -1 is the last item.
    """

    title = "Get Item"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("items", default=[])
        self.add_input("index", default=0)
        self.add_output("item")

    def compute(self) -> None:
        self.set_output("item", self.get_input("items")[int(self.get_input("index"))])


class SortNode(Node):
    """The items of a list, from the smallest to the largest (or from A to Z)."""

    title = "Sort"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("items", default=[])
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", sorted(self.get_input("items")))


class JoinListNode(Node):
    """Makes one text from the items of a list, with the separator between the items."""

    title = "Join List"
    category = "Lists"
    color = (0, 140, 140)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("items", default=[])
        self.add_input("separator", default=", ")
        self.add_output("text")

    def compute(self) -> None:
        separator = str(self.get_input("separator"))
        self.set_output("text", separator.join(str(item) for item in self.get_input("items")))
