from PySide6 import QtWidgets

from node_editor.gui.node import Node


class Add_Node(Node):
    def __init__(self):
        super().__init__()

        self.title = "Add"
        self.type_text = "Logic Nodes"
        self.set_color(title_color=(0, 128, 0))

        self.add_port(name="Ex In", is_output=False, execution=True)
        self.add_port(name="Ex Out", is_output=True, execution=True)

        self.add_port(name="input A", is_output=False)
        self.add_port(name="input A", is_output=False)
        self.add_port(name="input B", is_output=False)
        self.add_port(name="output", is_output=True)
        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QPushButton("Button test")
        layout.addWidget(label)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

        # print(self.widget.layout().sizeHint())
        # print(self.widget.size())
