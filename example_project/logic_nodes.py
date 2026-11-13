"""Logic nodes. They work with True and False values.

To run different nodes for True and for False, use these nodes with the Branch node.
"""

from __future__ import annotations

import operator
from collections.abc import Callable
from typing import Any

from PySide6.QtWidgets import QComboBox

from node_editor.node import Node

# The comparisons in the Compare node, and the Python function for each one.
COMPARISONS: dict[str, Callable[[Any, Any], bool]] = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


class CompareNode(Node):
    """Compares a and b. Select the comparison in the node. The result is True or False."""

    title = "Compare"
    category = "Logic"
    color = (30, 100, 200)

    def __init__(self) -> None:
        super().__init__()
        self.comparison = "=="
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def create_widget(self) -> QComboBox:
        combo_box = QComboBox()
        combo_box.addItems(list(COMPARISONS))
        combo_box.setCurrentText(self.comparison)
        combo_box.currentTextChanged.connect(self.on_comparison_changed)
        return combo_box

    def on_comparison_changed(self, comparison: str) -> None:
        self.comparison = comparison
        self.mark_dirty()

    def compute(self) -> None:
        compare = COMPARISONS[self.comparison]
        self.set_output("result", compare(self.get_input("a"), self.get_input("b")))

    def get_state(self) -> dict[str, Any]:
        return {"comparison": self.comparison}

    def set_state(self, state: dict[str, Any]) -> None:
        self.comparison = str(state.get("comparison", "=="))


class AndNode(Node):
    """True if a and b are both True."""

    title = "And"
    category = "Logic"
    color = (30, 100, 200)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=False)
        self.add_input("b", default=False)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", bool(self.get_input("a") and self.get_input("b")))


class OrNode(Node):
    """True if a is True, b is True, or both are True."""

    title = "Or"
    category = "Logic"
    color = (30, 100, 200)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=False)
        self.add_input("b", default=False)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", bool(self.get_input("a") or self.get_input("b")))


class NotNode(Node):
    """True becomes False, and False becomes True."""

    title = "Not"
    category = "Logic"
    color = (30, 100, 200)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("value", default=False)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", not self.get_input("value"))


class SelectNode(Node):
    """Gives "if true" when the condition is True. Gives "if false" when the condition is False."""

    title = "Select"
    category = "Logic"
    color = (30, 100, 200)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("condition", default=False)
        self.add_input("if true")
        self.add_input("if false")
        self.add_output("result")

    def compute(self) -> None:
        name = "if true" if self.get_input("condition") else "if false"
        self.set_output("result", self.get_input(name))
