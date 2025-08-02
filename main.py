from pathlib import Path
import importlib.util
import inspect
import logging
import sys
from typing import Any, Dict, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QByteArray

from node_editor.compute_graph import compute_dag_nodes
from node_editor.connection import Connection
from node_editor.gui.node_list import NodeList
from node_editor.gui.node_widget import NodeWidget
from node_editor.node import Node

logging.basicConfig(level=logging.DEBUG)


class NodeEditor(QtWidgets.QMainWindow):  # type: ignore
    OnProjectPathUpdate = QtCore.Signal(Path)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.settings: QtCore.QSettings = QtCore.QSettings("node-editor", "NodeEditor")
        self.project_path: Optional[Path] = None
        self.imports: Optional[Dict[str, Dict[str, Any]]] = None

        icon_path = Path("resources") / "app.ico"
        self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        self.setWindowTitle("Simple Node Editor")

        # Layout setup
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

        # Assemble layouts
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.node_widget)
        left_widget.setLayout(left_layout)
        left_layout.addWidget(self.node_list)
        left_layout.addWidget(execute_button)
        main_layout.addWidget(self.splitter)

        # Restore GUI layout
        self.restore_gui_state()

        # Load example project
        example_project_path = Path(__file__).parent.resolve() / "Example_Project"
        self.load_project(example_project_path)

    def restore_gui_state(self) -> None:
        if self.settings.contains("geometry"):
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)

        if self.settings.contains("splitterSize"):
            splitter_state = self.settings.value("splitterSize")
            if splitter_state:
                self.splitter.restoreState(splitter_state)

    def execute_graph(self) -> None:
        logging.info("Executing Graph")
        nodes = self.node_widget.scene.get_items_by_type(Node)
        edges = self.node_widget.scene.get_items_by_type(Connection)
        compute_dag_nodes(nodes, edges)

    def save_project(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Project", "", "JSON files (*.json);;All files (*)")
        if file_path:
            self.node_widget.save_project(file_path)

    def load_project(self, project_path: Optional[Path] = None) -> None:
        if not project_path:
            return

        project_path = Path(project_path)
        if not project_path.exists() or not project_path.is_dir():
            logging.warning(f"Invalid project path: {project_path}")
            return

        self.project_path = project_path
        self.imports = {}

        for file in project_path.glob("*.py"):
            if not file.stem.endswith("_node"):
                logging.debug(f"Skipping file: {file.stem}")
                continue

            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    logging.warning(f"Could not load spec for {file}")
                    continue
            except Exception as e:
                logging.error(f"Failed to import {file.name}: {e}")
                continue

            for name, obj in inspect.getmembers(module):
                if name.endswith("_Node") and inspect.isclass(obj):
                    self.imports[obj.__name__] = {"class": obj, "module": module}

        self.node_list.update_project(self.imports)

        for json_path in project_path.glob("*.json"):
            self.node_widget.load_scene(str(json_path), self.imports)
            break  # TODO: Support multiple JSON files

    def get_project_path(self) -> None:
        project_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Project Folder", "")
        if project_path:
            self.load_project(Path(project_path))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("splitterSize", self.splitter.saveState())
        super().closeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(str(Path("resources") / "app.ico")))

    # Apply QSS stylesheet
    style_file = Path("resources") / "dark_theme.qss"
    if style_file.exists():
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
    else:
        logging.warning(f"QSS file not found: {style_file}")

    launcher = NodeEditor()
    launcher.show()
    app.exec()
    sys.exit()