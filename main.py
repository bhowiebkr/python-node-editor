import sys

from PySide2 import QtWidgets, QtCore, QtGui

import qdarkstyle
import logging
import os

from node_editor.gui.node_widget import NodeWidget
from node_editor.gui.palette import palette

logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.settings = None

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Node Editor")
        settings = QtCore.QSettings("Howard", "NodeEditor")

        try:
            self.restoreGeometry(settings.value("geometry"))
        except AttributeError:
            logging.warning("Unable to load settings. First time opening the tool?")

        # Layouts
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()

        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)

        self.node_widget = NodeWidget(self)
        main_layout.addWidget(self.node_widget)

    def closeEvent(self, event):
        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    app.setPalette(palette)
    launcher = NodeEditor()
    launcher.show()
    app.exec_()
    sys.exit()
