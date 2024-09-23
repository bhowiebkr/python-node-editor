from __future__ import annotations

from typing import Optional
from typing import Tuple

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsScene

from node_editor.gui.connection_graphics import Connection_Graphics
from node_editor.node import Node
from node_editor.pin import Pin


class Connection(Connection_Graphics):
    def __init__(self, parent: Optional[Connection_Graphics]) -> None:
        super().__init__(parent)
        self.start_pin: Optional[Pin] = None
        self.end_pin: Optional[Pin] = None
        self.start_pos: QPointF = QPointF()
        self.end_pos: QPointF = QPointF()

    def delete(self) -> None:
        for pin in (self.start_pin, self.end_pin):
            if pin is not None:
                pin.connection = None
        self.start_pin = None
        self.end_pin = None
        scene = self.scene()
        if scene is not None:
            scene.removeItem(self)

    def set_start_pin(self, pin: Pin) -> None:
        self.start_pin = pin
        pin.connection = self

    def set_end_pin(self, pin: Pin) -> None:
        self.end_pin = pin
        pin.connection = self

    def nodes(self) -> Tuple[Optional[Node], Optional[Node]]:
        return (
            self.start_pin.node if self.start_pin is not None else None,
            self.end_pin.node if self.end_pin is not None else None,
        )

    def update_start_and_end_pos(self) -> None:
        if self.start_pin is not None and not self.start_pin.is_output:
            self.start_pin, self.end_pin = self.end_pin, self.start_pin

        if self.start_pin is not None:
            self.start_pos = self.start_pin.scenePos()

        if self.end_pin is not None:
            self.end_pos = self.end_pin.scenePos()

        self.update_path()

    def scene(self) -> Optional[QGraphicsScene]:
        return super().scene()

    def update_path(self) -> None:
        super().update_path()
