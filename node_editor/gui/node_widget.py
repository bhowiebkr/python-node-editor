from PySide2.QtWidgets import QWidget, QVBoxLayout, QGraphicsScene

from node_editor.gui.view import View
from node_editor.gui.node import Node
from node_editor.gui.node_editor import NodeEditor

import lorem
import random


class NodeWidget(QWidget):
    def __init__(self, parent):
        super(NodeWidget, self).__init__(parent)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.node_editor = NodeEditor(self)
        self.scene = QGraphicsScene()
        self.view = View(self)
        self.view.setScene(self.scene)
        self.node_editor.install(self.scene)

        main_layout.addWidget(self.view)

        self.create_random_nodes(10)

    def create_random_nodes(self, num):

        for i in range(num):
            node = Node()
            for i in range(random.randrange(2, 10)):
                word = lorem.sentence().split(" ")[0]
                node.add_port(name=word, is_output=bool(random.getrandbits(1)))
                node.title = "Title"
                node.type = "example"
            node.build()
            self.scene.addItem(node)
