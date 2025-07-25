from __future__ import annotations

from typing import Optional
from typing import Tuple

from node_editor.node import Node


class Print_Node(Node):
    def __init__(self) -> None:
        super().__init__()

        self.title_text: str = "Print"
        self.type_text: str = "Debug Nodes"
        self.set_color(title_color=(160, 32, 240))

        self.add_pin(name="Ex In", is_output=False, execution=True)

        self.add_pin(name="input", is_output=False)
        self.build()

    def set_color(
        self,
        title_color: Tuple[int, int, int],
        background_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        super().set_color(title_color, background_color)

    def add_pin(self, name: str, is_output: bool, execution: bool = False) -> None:
        # Assuming add_pin is defined in the parent class
        super().add_pin(name=name, is_output=is_output, execution=execution)

    def build(self) -> None:
        # Assuming build is defined in the parent class
        super().build()

    def compute(self) -> None:
        pin = self.get_pin("input")
        value = pin.value if pin and hasattr(pin, "value") else None
        print(f"[Print Node] Value: {value}")
