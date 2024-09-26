from __future__ import annotations

import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from PySide6 import QtGui
from PySide6 import QtWidgets

from node_editor.connection import Connection
from node_editor.gui.node_editor import NodeEditor
from node_editor.gui.view import View
from node_editor.node import Node
from node_editor.pin import Pin


class NodeScene(QtWidgets.QGraphicsScene):  # type: ignore
    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        e.acceptProposedAction()

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        item = self.itemAt(e.scenePos(), QtGui.QTransform())
        if item and hasattr(item, "setAcceptDrops"):
            item.dropEvent(e)

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        e.acceptProposedAction()


class NodeWidget(QtWidgets.QWidget):  # type: ignore
    """
    Widget for creating and displaying a node editor.

    Attributes:
        node_editor (NodeEditor): The node editor object.
        scene (NodeScene): The scene object for the node editor.
        view (View): The view object for the node editor.
    """

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        """
        Initializes the NodeWidget object.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__(parent)

        self.node_lookup: Dict[int, Node] = (
            {}
        )  # A dictionary of nodes, by uuids for faster looking up. Refactor this in the future
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.node_editor = NodeEditor(self)
        self.scene = NodeScene()
        self.scene.setSceneRect(0, 0, 9999, 9999)
        self.view = View(self)
        self.view.setScene(self.scene)
        self.node_editor.install(self.scene)

        main_layout.addWidget(self.view)

        self.view.request_node.connect(self.create_node)

    def create_node(self, node: Node, index: int) -> None:
        node.index = index
        self.scene.addItem(node)
        pos = self.view.mapFromGlobal(QtGui.QCursor.pos())
        node.setPos(self.view.mapToScene(pos))

    def load_scene(self, json_path: str, imports: Dict[str, Dict[str, Node]]) -> None:
        # load the scene json file
        data = None
        with open(json_path) as f:
            data = json.load(f)

        # clear out the node lookup
        self.node_lookup = {}

        # Add the nodes
        if data:
            for node in data["nodes"]:
                try:
                    info = imports[node["type"]]
                except KeyError:
                    continue
                node_item = info["class"]()
                node_item.index = node["index"]
                self.scene.addItem(node_item)
                node_item.setPos(node["x"], node["y"])

                self.node_lookup[node["index"]] = node_item

        # Add the connections
        for c in data["connections"]:
            connection = Connection(None)
            self.scene.addItem(connection)

            try:
                start_pin = self.node_lookup[c["start_id"]].get_pin(c["start_pin"])
                end_pin = self.node_lookup[c["end_id"]].get_pin(c["end_pin"])
            except KeyError:  # Node might be missing so we skip it
                continue

            if start_pin:
                connection.set_start_pin(start_pin)

            if end_pin:
                connection.set_end_pin(end_pin)
            connection.update_start_and_end_pos()

    def save_project(self, json_path: str) -> None:
        # from collections import OrderedDict

        # TODO possibly an ordered dict so things stay in order (better for git changes, and manual editing)
        # Maybe connections will need an index for each so they can be sorted and kept in order.
        scene: Dict[str, List[Any]] = {"nodes": [], "connections": []}

        # Need the nodes, and connections of ports to nodes
        for item in self.scene.items():
            # Connections
            if isinstance(item, Connection):
                # print(f"Name: {item}")
                nodes = item.nodes()
                if nodes[0]:
                    start_id = str(nodes[0].index)
                else:
                    continue
                end_id = str(nodes[1].index)  # type: ignore
                start_pin = item.start_pin.name  # type: ignore
                end_pin = item.end_pin.name  # type: ignore
                # print(f"Node ids {start_id, end_id}")
                # print(f"connected ports {item.start_pin.name(), item.end_pin.name()}")

                connection = {
                    "start_id": start_id,
                    "end_id": end_id,
                    "start_pin": start_pin,
                    "end_pin": end_pin,
                }
                scene["connections"].append(connection)
                continue

            # Pins
            if isinstance(item, Pin):
                continue

            # Nodes
            if isinstance(item, Node):
                # print("found node")
                pos = item.pos().toPoint()
                x, y = pos.x(), pos.y()
                # print(f"pos: {x, y}")

                obj_type = type(item).__name__
                # print(f"node type: {obj_type}")

                node_id = str(item.index)

                node = {"type": obj_type, "x": x, "y": y, "index": node_id}
                scene["nodes"].append(node)

        # Write the items_info dictionary to a JSON file
        with open(json_path, "w") as f:
            json.dump(scene, f, indent=4)
