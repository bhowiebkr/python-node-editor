import json
import uuid
from collections import OrderedDict

from PySide6 import QtGui, QtWidgets

from node_editor.gui.node import Node
from node_editor.gui.node_editor import NodeEditor
from node_editor.gui.view import View

from node_editor.gui.connection import Connection
from node_editor.gui.node import Node
from node_editor.gui.port import Port


class NodeScene(QtWidgets.QGraphicsScene):
    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # find item at these coordinates
        item = self.itemAt(e.scenePos())
        if item.setAcceptDrops:
            # pass on event to item at the coordinates
            item.dropEvent(e)

    def dragMoveEvent(self, e):
        e.acceptProposedAction()


class NodeWidget(QtWidgets.QWidget):
    """
    Widget for creating and displaying a node editor.

    Attributes:
        node_editor (NodeEditor): The node editor object.
        scene (NodeScene): The scene object for the node editor.
        view (View): The view object for the node editor.
    """

    def __init__(self, parent):
        """
        Initializes the NodeWidget object.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__(parent)

        self.node_lookup = {}  # A dictionary of nodes, by uuids for faster looking up. Refactor this in the future
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

    def create_node(self, node):
        node.uuid = uuid.uuid4()
        self.scene.addItem(node)
        pos = self.view.mapFromGlobal(QtGui.QCursor.pos())
        node.setPos(self.view.mapToScene(pos))

    def load_scene(self, json_path, imports):
        # load the scene json file
        data = None
        with open(json_path) as f:
            data = json.load(f)

        # clear out the node lookup
        self.node_lookup = {}

        # Add the nodes
        if data:
            for node in data["nodes"]:
                info = imports[node["type"]]
                node_item = info["class"]()
                node_item.uuid = node["uuid"]
                self.scene.addItem(node_item)
                node_item.setPos(node["x"], node["y"])

                self.node_lookup[node["uuid"]] = node_item

        # Add the connections
        for c in data["connections"]:
            connection = Connection(None)
            self.scene.addItem(connection)

            start_port = self.node_lookup[c["start_id"]].get_port(c["start_port"])
            end_port = self.node_lookup[c["end_id"]].get_port(c["end_port"])

            connection.start_port = start_port
            connection.end_port = end_port
            connection.update_start_and_end_pos()

    def save_project(self, json_path):
        # print(f"json path: {json_path}")

        from collections import OrderedDict

        # TODO possibly an ordered dict so things stay in order (better for git changes, and manual editing)
        # Maybe connections will need a uuid for each so they can be sorted and kept in order.
        scene = {"nodes": [], "connections": []}

        # Need the nodes, and connections of ports to nodes
        for item in self.scene.items():
            # Connections
            if isinstance(item, Connection):
                # print(f"Name: {item}")
                nodes = item.nodes()
                start_id = str(nodes[0].uuid)
                end_id = str(nodes[1].uuid)
                start_port = item.start_port.name()
                end_port = item.end_port.name()
                # print(f"Node ids {start_id, end_id}")
                # print(f"connected ports {item.start_port.name(), item.end_port.name()}")

                connection = {
                    "start_id": start_id,
                    "end_id": end_id,
                    "start_port": start_port,
                    "end_port": end_port,
                }
                scene["connections"].append(connection)
                continue

            # Ports
            if isinstance(item, Port):
                continue

            # Nodes
            if isinstance(item, Node):
                # print("found node")
                pos = item.pos().toPoint()
                x, y = pos.x(), pos.y()
                # print(f"pos: {x, y}")

                obj_type = type(item).__name__
                # print(f"node type: {obj_type}")

                node_id = str(item.uuid)

                node = {"type": obj_type, "x": x, "y": y, "uuid": node_id}
                scene["nodes"].append(node)

        # Write the items_info dictionary to a JSON file
        with open(json_path, "w") as f:
            json.dump(scene, f, indent=4)
