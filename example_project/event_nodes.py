"""Event nodes. An event node starts a run.

A start node has exec outputs and no exec inputs. Run Graph runs each start node.
"""

from __future__ import annotations

from PySide6.QtWidgets import QPushButton

from node_editor.execution import run_from
from node_editor.node import Node


class ButtonNode(Node):
    """Click the button to run the nodes that connect to "clicked"."""

    title = "Button"
    category = "Events"
    color = (128, 0, 0)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_output("clicked")

    def create_widget(self) -> QPushButton:
        button = QPushButton("Run")
        button.clicked.connect(self.on_click)
        return button

    def on_click(self) -> None:
        if self.graph is not None:
            run_from(self.graph, self)
