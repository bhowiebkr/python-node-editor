from PySide6 import QtWidgets, QtGui

from node_editor.gui.view import View
from node_editor.gui.node import Node
from node_editor.gui.node_editor import NodeEditor


def create_input():
    node = Node()
    node.title = "A"
    node.type_text = "input"
    node.add_port(name="output", is_output=True)
    node.build()
    return node


def create_output():
    node = Node()
    node.title = "A"
    node.type_text = "output"
    node.add_port(name="input", is_output=False)
    node.build()
    return node


def create_and():
    node = Node()
    node.title = "AND"
    node.type_text = "built-in"
    node.add_port(name="input A", is_output=False)
    node.add_port(name="input B", is_output=False)
    node.add_port(name="output", is_output=True)
    node.build()
    return node


def create_not():
    node = Node()
    node.title = "NOT"
    node.type_text = "built-in"
    node.add_port(name="input", is_output=False)
    node.add_port(name="output", is_output=True)
    node.build()
    return node


def create_nor():
    node = Node()
    node.title = "NOR"
    node.type_text = "built-in"
    node.add_port(name="input", is_output=False)
    node.add_port(name="output", is_output=True)
    node.build()
    return node


def create_empty():
    node = Node()
    node.title = "NOR"
    node.type_text = "empty node"
    node.build()
    return node


class NodeScene(QtWidgets.QGraphicsScene):
    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # find item at these coordinates
        item = self.itemAt(e.scenePos())
        if item.setAcceptDrops == True:
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
        super(NodeWidget, self).__init__(parent)
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

    def create_node(self, name):
        """
        Creates a new node and adds it to the node editor.

        Args:
            name (str): The name of the node to be created.
        """
        print("creating node:", name)

        if name == "Input":
            node = create_input()
        elif name == "Output":
            node = create_output()
        elif name == "And":
            node = create_and()
        elif name == "Not":
            node = create_not()
        elif name == "Nor":
            node = create_nor()
        elif name == "Empty":
            node = create_empty()
        else:
            print(f"Can't find a premade node for {name}")
            return

        self.scene.addItem(node)

        pos = self.view.mapFromGlobal(QtGui.QCursor.pos())
        node.setPos(self.view.mapToScene(pos))
