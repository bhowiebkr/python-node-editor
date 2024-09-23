from __future__ import annotations

from typing import Tuple

from node_editor.node import Node


class Add_Node(Node):
    def __init__(self) -> None:
        super().__init__()

        self.title_text: str = "Add"
        self.type_text: str = "Logic Nodes"
        self.set_color(title_color=(0, 128, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.add_pin(name="input A", is_output=False)
        self.add_pin(name="input B", is_output=False)
        self.add_pin(name="output", is_output=True)
        self.build()

    def set_color(self, title_color: Tuple[int, int, int]) -> None:
        # Assuming set_color is defined in the parent class
        super().set_color(title_color=title_color)

    def add_pin(self, name: str, is_output: bool, execution: bool = False) -> None:
        # Assuming add_pin is defined in the parent class
        super().add_pin(name=name, is_output=is_output, execution=execution)

    def build(self) -> None:
        # Assuming build is defined in the parent class
        super().build()
