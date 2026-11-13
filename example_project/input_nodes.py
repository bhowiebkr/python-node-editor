"""Input nodes. Each one has a widget, where you type or select a value.

The graph file keeps the value (see get_state and set_state).
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QLineEdit, QSpinBox

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


class IntegerNode(Node):
    """A whole number that you can type in. Use it to count (for example, in a For Loop)."""

    title = "Integer"
    category = "Inputs"
    color = (255, 165, 0)

    def __init__(self) -> None:
        super().__init__()
        self.value = 0
        self.add_output("value")

    def create_widget(self) -> QSpinBox:
        spin_box = QSpinBox()
        spin_box.setRange(-1_000_000, 1_000_000)
        spin_box.setValue(self.value)
        spin_box.valueChanged.connect(self.on_value_changed)
        return spin_box

    def on_value_changed(self, value: int) -> None:
        self.value = value
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output("value", self.value)

    def get_state(self) -> dict[str, Any]:
        return {"value": self.value}

    def set_state(self, state: dict[str, Any]) -> None:
        self.value = int(state.get("value", 0))


class TextNode(Node):
    """A line of text that you can type in."""

    title = "Text"
    category = "Inputs"
    color = (255, 165, 0)

    def __init__(self) -> None:
        super().__init__()
        self.text = ""
        self.add_output("text")

    def create_widget(self) -> QLineEdit:
        line_edit = QLineEdit(self.text)
        line_edit.setMinimumWidth(160)
        line_edit.textChanged.connect(self.on_text_changed)
        return line_edit

    def on_text_changed(self, text: str) -> None:
        self.text = text
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output("text", self.text)

    def get_state(self) -> dict[str, Any]:
        return {"text": self.text}

    def set_state(self, state: dict[str, Any]) -> None:
        self.text = str(state.get("text", ""))


class BooleanNode(Node):
    """True or False. Click the check box to change the value."""

    title = "Boolean"
    category = "Inputs"
    color = (255, 165, 0)

    def __init__(self) -> None:
        super().__init__()
        self.value = False
        self.add_output("value")

    def create_widget(self) -> QCheckBox:
        check_box = QCheckBox("True")
        check_box.setChecked(self.value)
        check_box.toggled.connect(self.on_toggled)
        return check_box

    def on_toggled(self, checked: bool) -> None:
        self.value = checked
        self.mark_dirty()

    def compute(self) -> None:
        self.set_output("value", self.value)

    def get_state(self) -> dict[str, Any]:
        return {"value": self.value}

    def set_state(self, state: dict[str, Any]) -> None:
        self.value = bool(state.get("value", False))
