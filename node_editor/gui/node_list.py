"""The list of node types at the left side of the window."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QByteArray, QMimeData, Qt
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem, QWidget

from node_editor.node import Node

# The drag data type. The data is the class name of the node.
NODE_MIME_TYPE = "application/x-python-node-editor-node"


class NodeList(QTreeWidget):
    """Shows the node types in groups (the `category` of each node class).

    Drag a node type into the view to add a node.
    """

    def __init__(self, node_classes: dict[str, type[Node]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        categories: dict[str, QTreeWidgetItem] = {}
        for class_name, node_class in sorted(node_classes.items(), key=lambda item: (item[1].category, item[1].title)):
            if node_class.category not in categories:
                category_item = QTreeWidgetItem(self, [node_class.category])
                category_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # You cannot drag a group.
                categories[node_class.category] = category_item

            item = QTreeWidgetItem(categories[node_class.category], [node_class.title])
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
