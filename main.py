"""
A simple Node Editor application that allows the user to create, modify and connect nodes of various types.

The application consists of a main window that contains a splitter with a Node List and a Node Widget. The Node List
shows a list of available node types, while the Node Widget is where the user can create, edit and connect nodes.

This application uses PySide6 as a GUI toolkit.

Author: Bryan Howard
Repo: https://github.com/bhowiebkr/simple-node-editor
"""

import sys

from PySide6 import QtWidgets, QtCore, QtGui

import logging
import os

from node_editor.gui.node_widget import NodeWidget
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_type_editor import NodeTypeEditor

logging.basicConfig(level=logging.DEBUG)

import importlib

# Import qdarktheme if you have it. If not install it with pip. Dark Themese are great!
if importlib.util.find_spec("qdarktheme") is not None:
    import qdarktheme


class NodeEditor(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(NodeEditor, self).__init__(parent)
        self.settings = None

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Simple Node Editor")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.node_list = NodeList()
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)
        new_node_type_btn = QtWidgets.QPushButton("New Node Type")
        new_node_type_btn.setFixedHeight(50)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        left_layout.addWidget(new_node_type_btn)
        main_layout.addWidget(self.splitter)

        # Logic
        new_node_type_btn.clicked.connect(self.new_node_cmd)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def new_node_cmd(self):
        """
        Handles the New Node Type button click event by showing the NodeTypeEditor dialog.

        Returns:
            None.
        """
        node_editor = NodeTypeEditor()

        if node_editor.exec() == QtWidgets.QDialog.Accepted:
            print("Dialog accepted")
        else:
            print("Dialog canceled")

    def closeEvent(self, event):
        """
        Handles the close event by saving the GUI state and closing the application.

        Args:
            event: Close event.

        Returns:
            None.
        """
        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    launcher = NodeEditor()
    launcher.show()
    app.exec()
    sys.exit()
