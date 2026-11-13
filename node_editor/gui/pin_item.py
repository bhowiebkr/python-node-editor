"""The Qt item that draws one pin."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from node_editor.pin import Pin

DATA_COLOR = QColor(0, 128, 255)
EXEC_COLOR = QColor(255, 255, 255)

RADIUS = 5  # The radius of a data pin.
EXEC_ARROW = QPolygonF([QPointF(-6, -7), QPointF(-6, 7), QPointF(-2, 7), QPointF(6, 0), QPointF(-2, -7)])


class PinItem(QGraphicsItem):
    """Draws a pin: a circle for a data pin, or an arrow for an exec pin.

    The shape is filled when the pin has a connection. The node item is the parent of its pin items,
    so the pins move with the node.
    """

    def __init__(self, pin: Pin, parent: QGraphicsItem) -> None:
        super().__init__(parent)
        self.pin = pin
        self.setCursor(Qt.CursorShape.CrossCursor)

    def boundingRect(self) -> QRectF:
        return QRectF(-8, -8, 16, 16)

    def shape(self) -> QPainterPath:
        # A large circle, so that the pin is easy to hit with the mouse.
        path = QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def is_connected(self) -> bool:
        graph = self.pin.node.graph
        return graph is not None and bool(graph.connections_of(self.pin))

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        color = EXEC_COLOR if self.pin.is_exec else DATA_COLOR
        painter.setPen(QPen(color, 1.5))
        if self.is_connected():
            painter.setBrush(color)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        if self.pin.is_exec:
            painter.drawPolygon(EXEC_ARROW)
        else:
            painter.drawEllipse(QPointF(0, 0), RADIUS, RADIUS)
