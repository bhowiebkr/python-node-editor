"""Math nodes.

These are pure nodes: they have no exec pins, so they run when another node needs their result.
"""

from __future__ import annotations

from node_editor.node import Node


class AddNode(Node):
    """Adds two numbers: result = a + b."""

    title = "Add"
    category = "Math"
    color = (0, 128, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default=0.0)
        self.add_input("b", default=0.0)
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", self.get_input("a") + self.get_input("b"))
