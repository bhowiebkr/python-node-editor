from PySide6 import QtWidgets

from node_editor.node import Node
from Example_Project.common_widgets import FloatLineEdit


class Scaler_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Scaler"
        self.type_text = "Constants"
        self.set_color(title_color=(255, 165, 0))

        self.add_pin(name="value", is_output=True)

        self.build()

    def init_widget(self):
        self.widget = QtWidgets.QWidget()
        self.widget.setFixedWidth(100)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.scaler_line = FloatLineEdit()
        layout.addWidget(self.scaler_line)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()
