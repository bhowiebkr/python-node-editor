"""The Qt view that shows the scene, with a grid in the background."""

from __future__ import annotations

import math

from PySide6.QtCore import QLineF, QPointF, QRect, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent, QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import QFrame, QGraphicsScene, QGraphicsView, QWidget

from node_editor.gui.node_list import NODE_MIME_TYPE

BACKGROUND_COLOR = QColor(38, 38, 38)
FINE_GRID = 15
FINE_PEN = QPen(QColor(52, 52, 52), 0.5)
COARSE_GRID = 150
COARSE_PEN = QPen(QColor(22, 22, 22), 1.0)

ZOOM_STEP = 1.2  # The zoom factor for one step of the mouse wheel.
MIN_ZOOM = 0.2
MAX_ZOOM = 3.0


class NodeView(QGraphicsView):
    """Shows the scene.

    - Mouse wheel: zoom in and out.
    - Middle mouse button: move the view (pan).
    - Left mouse button on the background: select the nodes in a box.
    - Drop a node type from the node list to add a node.
    """

    node_dropped = Signal(str, QPointF)  # The class name of the node, and the drop position in the scene.

    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None) -> None:
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAcceptDrops(True)
        self._pan_start: QPointF | None = None

    def center_on_nodes(self) -> None:
        self.centerOn(self.scene().itemsBoundingRect().center())

    def drawBackground(self, painter: QPainter, rect: QRectF | QRect) -> None:
        rect = QRectF(rect)
        painter.fillRect(rect, BACKGROUND_COLOR)
        self._draw_grid(painter, rect, FINE_GRID, FINE_PEN)
        self._draw_grid(painter, rect, COARSE_GRID, COARSE_PEN)

    def _draw_grid(self, painter: QPainter, rect: QRectF, step: int, pen: QPen) -> None:
        lines = []
        x = math.floor(rect.left() / step) * step
        while x < rect.right():
            lines.append(QLineF(x, rect.top(), x, rect.bottom()))
            x += step
        y = math.floor(rect.top() / step) * step
        while y < rect.bottom():
            lines.append(QLineF(rect.left(), y, rect.right(), y))
            y += step
        painter.setPen(pen)
        painter.drawLines(lines)

    # --- Zoom ---

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = ZOOM_STEP ** (event.angleDelta().y() / 120)  # One wheel step is 120.
        new_zoom = self.transform().m11() * factor
        if MIN_ZOOM <= new_zoom <= MAX_ZOOM:
            self.scale(factor, factor)

    # --- Pan with the middle mouse button ---

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_start is not None:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - round(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - round(delta.y()))
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_start = None
            self.unsetCursor()
            return
        super().mouseReleaseEvent(event)

    # --- Drop a node type from the node list ---

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat(NODE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasFormat(NODE_MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData().hasFormat(NODE_MIME_TYPE):
            super().dropEvent(event)
            return
        data = event.mimeData().data(NODE_MIME_TYPE)  # A QByteArray.
        class_name = bytes(data.data()).decode()
        self.node_dropped.emit(class_name, self.mapToScene(event.position().toPoint()))
        event.acceptProposedAction()
