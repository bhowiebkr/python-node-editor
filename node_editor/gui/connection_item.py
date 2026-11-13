"""The Qt item that draws one connection."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPainterPath, QPainterPathStroker, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QStyleOptionGraphicsItem, QWidget

from node_editor.connection import Connection
from node_editor.gui.pin_item import DATA_COLOR, EXEC_COLOR, PinItem


def curve_path(start: QPointF, end: QPointF) -> QPainterPath:
    """Return an S-shaped curve from an output at `start` to an input at `end`.

    The curve leaves `start` to the right and arrives at `end` from the left.
    """
    bend = max(abs(end.x() - start.x()) / 2, 50)
    path = QPainterPath(start)
    path.cubicTo(QPointF(start.x() + bend, start.y()), QPointF(end.x() - bend, end.y()), end)
    return path


class ConnectionItem(QGraphicsPathItem):
    """Draws a connection as a curve between two pin items.

    You can select a connection with a click, and remove it with the Delete key.
    The curve is brighter when the connection or one of its nodes is selected.
    """

    def __init__(self, connection: Connection, start_item: PinItem, end_item: PinItem) -> None:
        super().__init__()
        self.connection = connection
        self.start_item = start_item
        self.end_item = end_item
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)  # Draw the connections below the nodes.
        self.update_path()

    def update_path(self) -> None:
        """Move the ends of the curve to the pins. The scene calls this when a node moves."""
        self.setPath(curve_path(self.start_item.scenePos(), self.end_item.scenePos()))

    def is_highlighted(self) -> bool:
        start_node = self.start_item.parentItem()
        end_node = self.end_item.parentItem()
        return (
            self.isSelected()
            or (start_node is not None and start_node.isSelected())
            or (end_node is not None and end_node.isSelected())
        )

    def shape(self) -> QPainterPath:
        # A wide band around the curve, so that the connection is easy to click.
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(self.path())

    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        if self.connection.start.is_exec:
            color, width = EXEC_COLOR, 3
        else:
            color, width = DATA_COLOR, 2
        if self.is_highlighted():
            color, width = color.lighter(), width + 2

        painter.setPen(QPen(color, width))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())
