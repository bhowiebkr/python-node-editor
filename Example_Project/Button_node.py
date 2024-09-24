from __future__ import annotations

from PySide6 import QtWidgets

from node_editor.node import Node


class Button_Node(Node):
    def __init__(self) -> None:
        super().__init__()

        self.title_text = "Button"
        self.type_text = "Inputs"
        self.set_color(title_color=(128, 0, 0))

        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.build()

    def init_widget(self) -> None:
        self.widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        btn = QtWidgets.QPushButton("Button test")
        btn.clicked.connect(self.btn_cmd)
        layout.addWidget(btn)
        self.widget.setLayout(layout)

        proxy = QtWidgets.QGraphicsProxyWidget()
        proxy.setWidget(self.widget)
        proxy.setParentItem(self)

        super().init_widget()

    def btn_cmd(self) -> None:
        print("btn command")
        self.execute()
