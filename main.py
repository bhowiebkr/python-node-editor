from __future__ import annotations

import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

import qdarktheme
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6.QtCore import QByteArray  # Or from PySide2.QtCore import QByteArray

from node_editor.compute_graph import compute_dag_nodes
from node_editor.connection import Connection
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeWidget
from node_editor.node import Node

logging.basicConfig(level=logging.DEBUG)

"""
A simple Node Editor application that allows the user to create, modify and connect nodes of various types.

The application consists of a main window that contains a splitter with a Node List and a Node Widget. The Node List
shows a list of available node types, while the Node Widget is where the user can create, edit and connect nodes.

This application uses PySide6 as a GUI toolkit.

Author: Bryan Howard
Repo: https://github.com/bhowiebkr/simple-node-editor
"""


class NodeEditor(QtWidgets.QMainWindow):  # type: ignore
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.settings: Optional[QtCore.QSettings] = None
        self.project_path: Optional[Path] = None
        self.imports: Optional[Dict[str, Dict[str, Any]]] = (
            None  # we will store the project import node types here for now.
        )

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Simple Node Editor")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # create a "File" menu and add an "Export CSV" action to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.get_project_path)
        file_menu.addAction(load_action)

        save_action = QtGui.QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        # Layouts
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Widgets
        self.node_list: NodeList = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter: QtWidgets.QSplitter = QtWidgets.QSplitter()
        execute_button = QtWidgets.QPushButton("Execute Graph")
        execute_button.setFixedHeight(40)
        execute_button.clicked.connect(self.execute_graph)
        self.node_widget: NodeWidget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        left_layout.addWidget(execute_button)
        main_layout.addWidget(self.splitter)

        # Load the example project
        example_project_path = Path(__file__).parent.resolve() / "Example_project"
        self.load_project(example_project_path)

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(QByteArray(settings.value("geometry")))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def execute_graph(self) -> None:
        print("Executing Graph:")

        # Get a list of the nodes in the view
        nodes = self.node_widget.scene.get_items_by_type(Node)
        edges = self.node_widget.scene.get_items_by_type(Connection)
        # sort them
        compute_dag_nodes(nodes, edges)

    def save_project(self) -> None:
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self, project_path: Optional[Path] = None) -> None:
        if not project_path:
            return

        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                if not file.stem.endswith("_node"):
                    print("file:", file.stem)
                    continue
                spec = importlib.util.spec_from_file_location(file.stem, file)  # type: ignore
                module = importlib.util.module_from_spec(spec)  # type: ignore
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if not name.endswith("_Node"):
                        continue
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}
                        # break

            self.node_list.update_project(self.imports)

            # work on just the first json file. add the ablitity to work on multiple json files later
            for json_path in project_path.glob("*.json"):
                self.node_widget.load_scene(str(json_path), self.imports)
                break

    def get_project_path(self) -> None:
        project_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Project Folder", "")
        if not project_path:
            return

        self.load_project(Path(project_path))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
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
