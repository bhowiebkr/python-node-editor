"""The Qt scene that shows a graph."""

from __future__ import annotations

from PySide6.QtCore import QObject, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QPen
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsProxyWidget, QGraphicsScene, QGraphicsSceneMouseEvent

from node_editor.connection import Connection
from node_editor.graph import Graph
from node_editor.gui.connection_item import ConnectionItem, curve_path
from node_editor.gui.node_item import NodeItem
from node_editor.gui.pin_item import PinItem
from node_editor.node import Node


class NodeScene(QGraphicsScene):
    """Shows a graph, with one Qt item for each node and for each connection.

    The scene does not change its items directly. A user action calls a graph method (for
    example `graph.connect`). The graph then calls `sync`, and `sync` adds, removes and
    updates the items, so that they agree with the graph.

    Mouse and keys:

    - Drag from a pin to another pin to connect them.
    - Click a node or a connection to select it. Press Delete to remove the selected items.
    """

    def __init__(self, graph: Graph, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.graph = graph
        self.node_items: dict[Node, NodeItem] = {}
        self.connection_items: dict[Connection, ConnectionItem] = {}

        # A temporary line that follows the mouse while you drag from a pin.
        self.drag_start: PinItem | None = None
        self.drag_line: QGraphicsPathItem | None = None

        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.selectionChanged.connect(self._repaint_connections)
        graph.listeners.append(self.sync)
        self.sync()

    def sync(self) -> None:
        """Make the items agree with the graph."""
        # 1. Remove the items of connections and nodes that are not in the graph now.
        for connection in list(self.connection_items):
            if connection not in self.graph.connections:
                self.removeItem(self.connection_items.pop(connection))
        for node in list(self.node_items):
            if node not in self.graph.nodes:
                self.removeItem(self.node_items.pop(node))

        # 2. Add items for new nodes and connections.
        for node in self.graph.nodes:
            if node not in self.node_items:
                self.node_items[node] = NodeItem(node, on_move=self.update_connection_paths)
                self.addItem(self.node_items[node])
        for connection in self.graph.connections:
            if connection not in self.connection_items:
                start_item = self.node_items[connection.start.node].pin_items[connection.start]
                end_item = self.node_items[connection.end.node].pin_items[connection.end]
                self.connection_items[connection] = ConnectionItem(connection, start_item, end_item)
                self.addItem(self.connection_items[connection])

        # 3. Show the status of each node, and fill the pins that have connections.
        for node_item in self.node_items.values():
            node_item.refresh()

    def update_connection_paths(self, node: Node) -> None:
        """Move the ends of the connections of `node`. A node item calls this when it moves."""
        for connection, item in self.connection_items.items():
            if node in (connection.start.node, connection.end.node):
                item.update_path()

    def _repaint_connections(self) -> None:
        # A connection is brighter when one of its nodes is selected.
        for item in self.connection_items.values():
            item.update()

    def pin_item_at(self, position: QPointF) -> PinItem | None:
        for item in self.items(position):
            if isinstance(item, PinItem):
                return item
        return None

    def delete_selected(self) -> None:
        """Remove the selected nodes and connections from the graph."""
        for item in self.selectedItems():
            if isinstance(item, NodeItem) and item.node in self.graph.nodes:
                self.graph.remove_node(item.node)
            elif isinstance(item, ConnectionItem) and item.connection in self.graph.connections:
                self.graph.disconnect(item.connection)

    # --- Drag from a pin to make a connection ---

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        pin_item = self.pin_item_at(event.scenePos())
        if event.button() == Qt.MouseButton.LeftButton and pin_item is not None:
            self.drag_start = pin_item
            self.drag_line = QGraphicsPathItem()
            self.drag_line.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))
            self.addItem(self.drag_line)
            self._move_drag_line(event.scenePos())
            event.accept()  # Do not start a node move or a selection box.
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.drag_line is not None:
            self._move_drag_line(event.scenePos())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.drag_start is not None and self.drag_line is not None:
            target = self.pin_item_at(event.scenePos())
            if target is not None:
                # The graph refuses the connection if it is not allowed.
                self.graph.connect(self.drag_start.pin, target.pin)
            self.removeItem(self.drag_line)
            self.drag_line = None
            self.drag_start = None
            return
        super().mouseReleaseEvent(event)

    def _move_drag_line(self, mouse: QPointF) -> None:
        assert self.drag_start is not None and self.drag_line is not None
        pin_position = self.drag_start.scenePos()
        if self.drag_start.pin.is_output:
            self.drag_line.setPath(curve_path(pin_position, mouse))
        else:
            self.drag_line.setPath(curve_path(mouse, pin_position))

    # --- Keys ---

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # When you type in a widget inside a node (for example a number field), the widget
        # must get the Delete key. It must not remove the node.
        typing_in_widget = isinstance(self.focusItem(), QGraphicsProxyWidget)
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and not typing_in_widget:
            self.delete_selected()
            event.accept()
            return
        super().keyPressEvent(event)
