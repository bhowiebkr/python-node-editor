"""Input nodes. Each one has a widget, where you type or select a value.

The graph file keeps the value (see get_state and set_state).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QDoubleSpinBox

from node_editor.node import Node


class ScalarNode(Node):
    """A number that you can type in."""

    title = "Scalar"
    category = "Inputs"
    color = (255, 165, 0)

    def __init__(self) -> None:
        super().__init__()
        self.value = 0.0
        self.add_output("value")

    def create_widget(self) -> QDoubleSpinBox:
        spin_box = QDoubleSpinBox()
        spin_box.setRange(-1_000_000.0, 1_000_000.0)
        spin_box.setValue(self.value)
        spin_box.valueChanged.connect(self.on_value_changed)
        return spin_box

    def on_value_changed(self, value: float) -> None:
        self.value = value
        self.mark_dirty()  # The nodes that use this value must run again.

    def compute(self) -> None:
        self.set_output("value", self.value)

    def get_state(self) -> dict[str, Any]:
        return {"value": self.value}

    def set_state(self, state: dict[str, Any]) -> None:
        self.value = float(state.get("value", 0.0))
