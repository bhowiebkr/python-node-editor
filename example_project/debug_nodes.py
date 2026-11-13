"""Debug nodes. They show values, so that you can see what the graph does.

These are exec nodes: they run when an exec connection reaches them.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

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


class LogNode(Node):
    """Adds its input value to the node as a new line. Use it to see each value from a loop.

    Print shows only the last value. Log keeps all the values, until you click Clear.
    """

    title = "Log"
    category = "Debug"
    color = (160, 32, 240)

    def __init__(self) -> None:
        super().__init__()
        self.add_exec_input("exec")
        self.add_exec_output("then")
        self.add_input("value")
        self.lines: list[str] = []
        self.text_box: QPlainTextEdit | None = None

    def create_widget(self) -> QWidget:
        self.text_box = QPlainTextEdit("\n".join(self.lines))
        self.text_box.setReadOnly(True)
        self.text_box.setFixedSize(220, 140)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear)

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_box)
        layout.addWidget(clear_button)
        return widget

    def compute(self) -> None:
        line = str(self.get_input("value"))
        print(f"Log: {line}")
        self.lines.append(line)
        if self.text_box is not None:
            self.text_box.appendPlainText(line)

    def clear(self) -> None:
        self.lines.clear()
        if self.text_box is not None:
            self.text_box.clear()
