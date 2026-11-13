"""The Qt item that draws one node."""

from __future__ import annotations

from collections.abc import Callable
from itertools import zip_longest
from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QStyleOptionGraphicsItem, QWidget

from node_editor.gui.pin_item import PinItem
from node_editor.node import Node, Status
from node_editor.pin import Pin

TITLE_HEIGHT = 38  # The height of the title bar.
ROW_HEIGHT = 22  # The height of one row of pins.
LABEL_X = 12  # The distance from the side of the node to a pin label. The pins are on the sides.
LABEL_GAP = 24  # The smallest space between an input label and an output label.
MARGIN = 10
CORNER = 5  # The radius of the round corners.

BODY_COLOR = QColor(28, 28, 28)  # Opaque, so that the connections behind the node do not show.
OUTLINE_COLOR = QColor(12, 12, 12)
STATUS_COLORS = {
    Status.DIRTY: QColor(255, 165, 0),
    Status.CLEAN: QColor(0, 200, 0),
    Status.ERROR: QColor(230, 0, 0),
}


class NodeItem(QGraphicsItem):
    """Draws a node. You can move it and select it with the mouse.

    The layout from top to bottom::

        +------------------------------+
        | Title                    [#] |  title bar and status square
        | Category                     |
        >  exec                  then  >  exec pins
        o  a                   result  o  data pins
        o  b                           |
        |   [widget]                   |  widget (optional)
        +------------------------------+

    Inputs are on the left side and outputs are on the right side. The center of each pin is
    on the side of the node, so that the connections touch the pins. The position of the item
    is the top-left corner of the node.
    """

    def __init__(self, node: Node, on_move: Callable[[Node], None]) -> None:
        super().__init__()
        self.node = node
        self.on_move = on_move  # The scene gives this function, to move the connections with the node.
        self.pin_items: dict[Pin, PinItem] = {}
        self.proxy: QGraphicsProxyWidget | None = None

        self.title_font = QFont()
        self.title_font.setPointSize(11)
        self.title_font.setBold(True)
        self.small_font = QFont()
        self.small_font.setPointSize(8)
        self.label_font = QFont()

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPos(node.x, node.y)
        self._build()

    def _build(self) -> None:
        """Make the pin items and the widget, and calculate the size of the node."""
        # Put the pins in rows: first the exec pins, then the data pins.
        # Each row has an input (or None) at the left and an output (or None) at the right.
        self.rows: list[tuple[Pin | None, Pin | None]] = [
            *zip_longest(self.node.exec_inputs, self.node.exec_outputs),
            *zip_longest(self.node.data_inputs, self.node.data_outputs),
        ]

        # The width is the width of the widest part.
        title_width = QFontMetrics(self.title_font).horizontalAdvance(self.node.title) + 30
        category_width = QFontMetrics(self.small_font).horizontalAdvance(self.node.category) + MARGIN
        width: float = max(title_width, category_width, 100)
        label_metrics = QFontMetrics(self.label_font)
        for left, right in self.rows:
            left_width = label_metrics.horizontalAdvance(left.name) if left else 0
            right_width = label_metrics.horizontalAdvance(right.name) if right else 0
            width = max(width, 2 * LABEL_X + left_width + LABEL_GAP + right_width)

        widget = self.node.create_widget()
        widget_height = 0
        if widget is not None:
            widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.proxy = QGraphicsProxyWidget(self)
            self.proxy.setWidget(widget)
            width = max(width, self.proxy.size().width() + 2 * MARGIN)
            widget_height = int(self.proxy.size().height()) + MARGIN

        rows_bottom = TITLE_HEIGHT + len(self.rows) * ROW_HEIGHT
        self.rect = QRectF(0, 0, width, rows_bottom + widget_height + MARGIN / 2)

        if self.proxy is not None:
            self.proxy.setPos(MARGIN, rows_bottom + MARGIN / 2)
            self.proxy.resize(width - 2 * MARGIN, self.proxy.size().height())

        for row, (left, right) in enumerate(self.rows):
            y = TITLE_HEIGHT + row * ROW_HEIGHT + ROW_HEIGHT / 2
            if left is not None:
                self.pin_items[left] = PinItem(left, parent=self)
                self.pin_items[left].setPos(0, y)
            if right is not None:
                self.pin_items[right] = PinItem(right, parent=self)
                self.pin_items[right].setPos(width, y)

    def refresh(self) -> None:
        """Show the new status of the node. The scene calls this after each change to the graph."""
        self.setToolTip(self.node.error if self.node.status is Status.ERROR else "")
        self.update()
        for pin_item in self.pin_items.values():
            pin_item.update()

    def boundingRect(self) -> QRectF:
        return self.rect.adjusted(-2, -2, 2, 2)  # Add space for the selection outline.

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        width = self.rect.width()
        title_color = QColor(*self.node.color)

        # The body: a rectangle with round corners.
        outline = QPainterPath()
        outline.addRoundedRect(self.rect, CORNER, CORNER)
        painter.fillPath(outline, BODY_COLOR)

        # The title bar: the top part of the body, so it has the same round corners at the top.
        title_rect = QPainterPath()
        title_rect.addRect(QRectF(0, 0, width, TITLE_HEIGHT))
        gradient = QLinearGradient(0, 0, 0, TITLE_HEIGHT)
        gradient.setColorAt(0, title_color)
        gradient.setColorAt(1, title_color.darker())
        painter.fillPath(outline.intersected(title_rect), gradient)

        painter.strokePath(outline, QPen(OUTLINE_COLOR, 1))

        # The title and the category.
        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(self.title_font)
        painter.drawText(QRectF(MARGIN / 2, 2, width, 20), Qt.AlignmentFlag.AlignVCenter, self.node.title)
        painter.setFont(self.small_font)
        painter.drawText(QRectF(MARGIN / 2, 20, width, 14), Qt.AlignmentFlag.AlignVCenter, self.node.category)

        # The status square: orange (dirty), green (clean) or red (error).
        status_color = STATUS_COLORS[self.node.status]
        painter.setPen(status_color.darker())
        painter.setBrush(status_color)
        painter.drawRoundedRect(QRectF(width - 16, 6, 10, 10), 2, 2)

        # The pin labels.
        painter.setFont(self.label_font)
        painter.setPen(Qt.GlobalColor.white)
        for row, (left, right) in enumerate(self.rows):
            row_rect = QRectF(LABEL_X, TITLE_HEIGHT + row * ROW_HEIGHT, width - 2 * LABEL_X, ROW_HEIGHT)
            if left is not None:
                painter.drawText(row_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, left.name)
            if right is not None:
                painter.drawText(row_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, right.name)

        # The outline of a selected node.
        if self.isSelected():
            painter.strokePath(outline, QPen(title_color.lighter(), 2))

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Keep the position in the model, so that it is saved in the graph file.
            self.node.x = self.x()
            self.node.y = self.y()
            self.on_move(self.node)
        return super().itemChange(change, value)
