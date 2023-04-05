"""
A simple Node Editor application that allows the user to create, modify and connect nodes of various types.

The application consists of a main window that contains a splitter with a Node List and a Node Widget. The Node List
shows a list of available node types, while the Node Widget is where the user can create, edit and connect nodes.

This application uses PySide6 as a GUI toolkit.

Author: Bryan Howard
Repo: https://github.com/bhowiebkr/simple-node-editor
"""

import logging
from pathlib import Path
import importlib
import inspect

from PySide6 import QtCore, QtGui, QtWidgets

from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeWidget

logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = None
        self.project_path = None
        self.imports = None  # we will store the project import node types here for now.

        icon = QtGui.QIcon("resources\\app.ico")
        self.setWindowIcon(icon)

        self.setWindowTitle("Simple Node Editor")
        settings = QtCore.QSettings("node-editor", "NodeEditor")

        # create a "File" menu and add an "Export CSV" action to it
        file_menu = QtWidgets.QMenu("File", self)
        self.menuBar().addMenu(file_menu)

        load_action = QtGui.QAction("Load Project", self)
        load_action.triggered.connect(self.load_project)
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
        self.node_list = NodeList(self)
        left_widget = QtWidgets.QWidget()
        self.splitter = QtWidgets.QSplitter()
        self.node_widget = NodeWidget(self)

        # Add Widgets to layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        main_layout.addWidget(self.splitter)

        # Signals
        self.load_project("C:/Users/Howard/simple-node-editor/Example_project")

        # Restore GUI from last state
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))

            s = settings.value("splitterSize")
            self.splitter.restoreState(s)

    def save_project(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_dialog.setNameFilter("JSON files (*.json)")
        file_path, _ = file_dialog.getSaveFileName()
        self.node_widget.save_project(file_path)

    def load_project(self, project_path=None):
        if not project_path:
            return

        project_path = Path(project_path)
        if project_path.exists() and project_path.is_dir():
            self.project_path = project_path

            self.imports = {}

            for file in project_path.glob("*.py"):
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj):
                        self.imports[obj.__name__] = {"class": obj, "module": module}
                        break

            self.node_list.update_project(self.imports)

            # work on just the first json file. add the ablitity to work on multiple json files later
            for json_path in project_path.glob("*.json"):
                self.node_widget.load_scene(json_path, self.imports)
                break

    def get_project_path(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Project Folder", "")
        if not project_path:
            return

        self.load_project(project_path)

    def closeEvent(self, event):
        """
        Handles the close event by saving the GUI state and closing the application.

        Args:
            event: Close event.

        Returns:
            None.
        """

        # debugging lets save the scene:
        # self.node_widget.save_project("C:/Users/Howard/simple-node-editor/Example_Project/test.json")

        self.settings = QtCore.QSettings("node-editor", "NodeEditor")
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        QtWidgets.QWidget.closeEvent(self, event)


if __name__ == "__main__":
    import sys

    import qdarktheme

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("resources\\app.ico"))
    qdarktheme.setup_theme()

    launcher = NodeEditor()
    launcher.show()
    app.exec()
    sys.exit()
