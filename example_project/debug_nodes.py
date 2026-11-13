"""Debug nodes. They show values, so that you can see what the graph does.

These are exec nodes: they run when an exec connection reaches them.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from node_editor.node import Node


class PrintNode(Node):
    """Prints its input value to the console, and shows the value in the node."""

    title = "Print"
    category = "Debug"
    color = (160, 32, 240)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_input("value")
        self.label: QLabel | None = None

    def create_widget(self) -> QLabel:
        self.label = QLabel("(not run)")
        self.label.setMinimumWidth(120)
        return self.label

    def compute(self) -> None:
        value = self.get_input("value")
        print(f"Print: {value}")
        if self.label is not None:
            self.label.setText(str(value))
