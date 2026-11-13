"""The list of node types at the left side of the window."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QByteArray, QMimeData, QSize, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem, QWidget

from node_editor.node import Node

# The drag data type. The data is the class name of the node.
NODE_MIME_TYPE = "application/x-python-node-editor-node"

CATEGORY_COLOR = QColor(130, 130, 130)


def color_icon(color: tuple[int, int, int]) -> QIcon:
    """Make a small square with round corners, in the title bar color of a node."""
    pixmap = QPixmap(32, 32)  # Large, so that the icon is sharp on high-DPI screens.
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(*color))
    painter.drawRoundedRect(0, 0, 32, 32, 8, 8)
    painter.end()
    icon = QIcon(pixmap)
    icon.addPixmap(pixmap, QIcon.Mode.Selected)  # Without this, Qt changes the color of a selected item.
    return icon


class NodeList(QTreeWidget):
    """Shows the node types in groups (the `category` of each node class).

    Drag a node type into the view to add a node.
    """

    def __init__(self, node_classes: dict[str, type[Node]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("NodeList")  # The style sheet in theme.py uses this name.
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)  # No arrows. The groups are always open.
        self.setItemsExpandable(False)
        self.setIndentation(0)
        self.setIconSize(QSize(10, 10))
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        category_font = QFont()
        category_font.setPointSize(8)
        category_font.setBold(True)

        categories: dict[str, QTreeWidgetItem] = {}
        for class_name, node_class in sorted(node_classes.items(), key=lambda item: (item[1].category, item[1].title)):
            if node_class.category not in categories:
                category_item = QTreeWidgetItem(self, [node_class.category.upper()])
                category_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # You cannot select or drag a group.
                category_item.setFont(0, category_font)
                category_item.setForeground(0, CATEGORY_COLOR)
                # A tall row with the text at the bottom gives space above the group.
                category_item.setSizeHint(0, QSize(0, 32))
                category_item.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
                categories[node_class.category] = category_item

            item = QTreeWidgetItem(categories[node_class.category], [node_class.title])
            item.setIcon(0, color_icon(node_class.color))
            item.setData(0, Qt.ItemDataRole.UserRole, class_name)
            item.setToolTip(0, node_class.__doc__ or "")
        self.expandAll()

    def mimeTypes(self) -> list[str]:
        return [NODE_MIME_TYPE]

    def mimeData(self, items: Sequence[QTreeWidgetItem]) -> QMimeData:
        """Make the drag data: the class name of the dragged node type."""
        mime_data = QMimeData()
        class_name = items[0].data(0, Qt.ItemDataRole.UserRole) if items else None
        if class_name:
            mime_data.setData(NODE_MIME_TYPE, QByteArray(class_name.encode()))
        return mime_data
