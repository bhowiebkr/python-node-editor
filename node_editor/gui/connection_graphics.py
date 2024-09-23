from __future__ import annotations

from typing import Optional
from typing import Tuple

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from node_editor.node import Node


class Connection_Graphics(QtWidgets.QGraphicsPathItem):  # type: ignore
    """
    A Connection represents a graphical connection between two NodePorts in a PySide6 application.

    Attributes:
    start_pin (NodePort): The NodePort where the connection starts.
    end_pin (NodePort): The NodePort where the connection ends.
    start_pos (QPointF): The starting position of the connection.
    end_pos (QPointF): The ending position of the connection.

    Methods:
    delete(): Deletes the connection.
    nodes(): Returns a tuple of the two connected nodes.
    update_start_and_end_pos(): Updates the starting and ending positions of the connection.
    update_path(): Draws a smooth cubic curve from the starting to ending position of the connection.
    paint(painter, option=None, widget=None): Override the default paint method depending on if the object is selected.

    Example:
    conn = Connection(parent)
    conn.start_pin = start_pin
    conn.end_pin = end_pin
    conn.update_start_and_end_pos()
    conn.update_path()
    """

    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
        self.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        self.setZValue(-1)

        self.start_pos: QtCore.QPointF = QtCore.QPointF()
        self.end_pos: QtCore.QPointF = QtCore.QPointF()
        self.start_pin: Optional[NodePort] = None
        self.end_pin: Optional[NodePort] = None

        self._do_highlight: bool = False

    def update_path(self) -> None:
        """
        Draws a smooth cubic curve from the start to end pins.
        """
        path = QtGui.QPainterPath()
        path.moveTo(self.start_pos)

        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()

        ctr1 = QtCore.QPointF(self.start_pos.x() + dx * 0.5, self.start_pos.y())
        ctr2 = QtCore.QPointF(self.start_pos.x() + dx * 0.5, self.start_pos.y() + dy)
        path.cubicTo(ctr1, ctr2, self.end_pos)

        self.setPath(path)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: Optional[QtWidgets.QStyleOptionGraphicsItem] = None,
        widget: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        """
        Override the default paint method depending on if the object is selected.

        Args:
        painter (QPainter): The QPainter object used to paint the Connection.
        option (QStyleOptionGraphicsItem): The style options for the Connection.
        widget (QWidget): The widget used to paint the Connection.
        """

        thickness = 0
        color = QtGui.QColor(0, 128, 255)
        if self.start_pin:
            if self.start_pin.execution:
                thickness = 3
                color = QtGui.QColor(255, 255, 255)

        if self.isSelected() or self._do_highlight:
            painter.setPen(QtGui.QPen(color.lighter(), thickness + 2))
        else:
            painter.setPen(QtGui.QPen(color, thickness))

        painter.drawPath(self.path())

    def delete(self) -> None:
        pass

    def nodes(self) -> Tuple[Node, Node]:
        # Implement the logic to return the connected nodes
        if self.start_pin and self.end_pin:
            return (self.start_pin.node, self.end_pin.node)
        raise ValueError("Both start_pin and end_pin must be set")

    def update_start_and_end_pos(self) -> None:
        pass
