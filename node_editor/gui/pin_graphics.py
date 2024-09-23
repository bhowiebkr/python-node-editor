from __future__ import annotations

from typing import Optional
from typing import Union

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class Pin_Graphics(QtWidgets.QGraphicsPathItem):  # type: ignore
    def __init__(self, parent: Optional[QtWidgets.QGraphicsItem], scene: QtWidgets.QGraphicsScene) -> None:
        super().__init__(parent)

        self.radius_: float = 5
        self.margin: int = 2

        self.execution: bool = False

        path: QtGui.QPainterPath = QtGui.QPainterPath()
        path.addEllipse(-self.radius_, -self.radius_, 2 * self.radius_, 2 * self.radius_)

        self.setPath(path)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemSendsScenePositionChanges)
        self.font: QtGui.QFont = QtGui.QFont()
        self.font_metrics: QtGui.QFontMetrics = QtGui.QFontMetrics(self.font)

        self.pin_text_height: int = self.font_metrics.height()

        self.is_output: bool = False

        self.text_path: QtGui.QPainterPath = QtGui.QPainterPath()

        self.name: str = ""  # Add this line to define self.name
        self.connection: Optional[Union[QtWidgets.QGraphicsItem, QtCore.QObject]] = (
            None  # Add this line to define self.connection
        )

    def set_execution(self, execution: bool) -> None:
        if execution:
            path: QtGui.QPainterPath = QtGui.QPainterPath()

            points: list[QtCore.QPointF] = [
                QtCore.QPointF(-6, -7),
                QtCore.QPointF(-6, 7),
                QtCore.QPointF(-2, 7),
                QtCore.QPointF(6, 0),
                QtCore.QPointF(-2, -7),
                QtCore.QPointF(-6, -7),
            ]
            path.addPolygon(QtGui.QPolygonF(points))
            self.setPath(path)

    def set_name(self, name: str) -> None:
        self.name = name  # Add this line to set self.name
        nice_name: str = self.name.replace("_", " ").title()
        self.pin_text_width: int = self.font_metrics.horizontalAdvance(nice_name)

        if self.is_output:
            x = -self.radius_ - self.margin - self.pin_text_width
        else:
            x = self.radius_ + self.margin

        y: float = self.pin_text_height / 4

        self.text_path.addText(x, y, self.font, nice_name)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: Optional[QtWidgets.QStyleOptionGraphicsItem] = None,
        widget: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        if self.execution:
            painter.setPen(Qt.GlobalColor.white)
        else:
            painter.setPen(Qt.GlobalColor.green)

        if self.is_connected():
            if self.execution:
                painter.setBrush(Qt.GlobalColor.white)
            else:
                painter.setBrush(Qt.GlobalColor.green)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawPath(self.path())

        # Draw text
        if not self.execution:
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.white)
            painter.drawPath(self.text_path)

    def itemChange(self, change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: object) -> object:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged and self.connection:
            if hasattr(self.connection, "update_start_and_end_pos"):
                self.connection.update_start_and_end_pos()
        return value

    def is_connected(self) -> bool:
        # Add this method to resolve the 'is_connected' call in the paint method
        return self.connection is not None
