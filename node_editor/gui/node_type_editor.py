from PySide6 import QtWidgets


class NodeTypeEditor(QtWidgets.QDialog):
    """
    A dialog window for editing node types.

    Attributes:
        edit (QtWidgets.QLineEdit): A line edit widget for editing the node type.
    """

    def __init__(self, parent=None):
        """
        Constructs a NodeTypeEditor object.

        Args:
            parent (QWidget): The parent widget of this dialog.
        """
        super().__init__(parent)

        self.setWindowTitle("Node Type Editor")

        # create the UI elements
        label = QtWidgets.QLabel("Node Type:")
        self.edit = QtWidgets.QLineEdit()
        button_ok = QtWidgets.QPushButton("OK")
        button_cancel = QtWidgets.QPushButton("Cancel")

        # set the layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.edit)
        layout.addWidget(button_ok)
        layout.addWidget(button_cancel)
        self.setLayout(layout)

        # connect the signals and slots
        button_ok.clicked.connect(self.accept)
        button_cancel.clicked.connect(self.reject)
