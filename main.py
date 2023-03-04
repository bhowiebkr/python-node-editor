import sys

from PySide6 import QtWidgets, QtCore, QtGui

import logging
import os

from node_editor.gui.node_widget import NodeWidget
from node_editor.gui.palette import palette
from node_editor.gui.node_list import NodeList

logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.settings = None

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Logic Node Editor")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # Layouts
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        self.node_list = NodeList()
        self.splitter = QtWidgets.QSplitter()

        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)

        self.node_widget = NodeWidget(self)
        main_layout.addWidget(self.splitter)
        self.splitter.addWidget(self.node_list)
        self.splitter.addWidget(self.node_widget)

        try:
            self.restoreGeometry(settings.value("geometry"))
            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

        except AttributeError as e:
            logging.warning("Unable to load settings. First time opening the tool?\n" + str(e))

    def closeEvent(self, event):
        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    app.setPalette(palette)
    launcher = NodeEditor()
    launcher.show()
    app.exec()
    sys.exit()
