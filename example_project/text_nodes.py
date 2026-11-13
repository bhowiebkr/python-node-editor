"""Text nodes. Most of them are pure nodes that change a text."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLineEdit

from node_editor.node import Node


class JoinTextNode(Node):
    """Puts b after a. For example, "Hello, " and "World" give "Hello, World"."""

    title = "Join Text"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("a", default="")
        self.add_input("b", default="")
        self.add_output("text")

    def compute(self) -> None:
        self.set_output("text", f"{self.get_input('a')}{self.get_input('b')}")


class FormatTextNode(Node):
    """Puts the input values into a template. Type the template in the node.

    {a}, {b} and {c} in the template become the values of the inputs. For example, the
    template "{a} x {b} = {c}" gives "3 x 7 = 21". You can also use Python format codes:
    "{a:.2f}" shows a with 2 digits after the decimal point.
    """

    title = "Format Text"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.template = "{a}"
        self.add_input("a", default="")
        self.add_input("b", default="")
        self.add_input("c", default="")
        self.add_output("text")

    def create_widget(self) -> QLineEdit:
        line_edit = QLineEdit(self.template)
        line_edit.setMinimumWidth(160)
        line_edit.textChanged.connect(self.on_template_changed)
        return line_edit

    def on_template_changed(self, template: str) -> None:
        self.template = template
        self.mark_dirty()

    def compute(self) -> None:
        text = self.template.format(a=self.get_input("a"), b=self.get_input("b"), c=self.get_input("c"))
        self.set_output("text", text)

    def get_state(self) -> dict[str, Any]:
        return {"template": self.template}

    def set_state(self, state: dict[str, Any]) -> None:
        self.template = str(state.get("template", "{a}"))


class UpperCaseNode(Node):
    """Changes all letters to capital letters: "Hello" gives "HELLO"."""

    title = "Upper Case"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("text", default="")
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", str(self.get_input("text")).upper())


class LowerCaseNode(Node):
    """Changes all letters to small letters: "Hello" gives "hello"."""

    title = "Lower Case"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("text", default="")
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", str(self.get_input("text")).lower())


class ReplaceTextNode(Node):
    """Replaces each "old" in the text with "new"."""

    title = "Replace Text"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("text", default="")
        self.add_input("old", default="")
        self.add_input("new", default="")
        self.add_output("result")

    def compute(self) -> None:
        text = str(self.get_input("text"))
        self.set_output("result", text.replace(self.get_input("old"), self.get_input("new")))


class SplitTextNode(Node):
    """Cuts a text into a list of parts at each separator, for example at each comma.

    With no separator, the node cuts the text at the spaces, so that you get a list of words.
    The node removes the spaces at the start and the end of each part.
    """

    title = "Split Text"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("text", default="")
        self.add_input("separator", default="")
        self.add_output("items")

    def compute(self) -> None:
        text = str(self.get_input("text"))
        separator = self.get_input("separator") or None  # None tells split() to use the spaces.
        self.set_output("items", [part.strip() for part in text.split(separator)])


class ContainsTextNode(Node):
    """True if "part" is in the text. For example, "World" is in "Hello, World"."""

    title = "Contains Text"
    category = "Text"
    color = (200, 80, 150)

    def __init__(self) -> None:
        super().__init__()
        self.add_input("text", default="")
        self.add_input("part", default="")
        self.add_output("result")

    def compute(self) -> None:
        self.set_output("result", str(self.get_input("part")) in str(self.get_input("text")))
