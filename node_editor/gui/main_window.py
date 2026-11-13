"""The main window of the editor."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QPointF, QSettings, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSizePolicy,
    QSplitter,
    QToolBar,
    QToolButton,
    QWidget,
)

from node_editor.execution import run_graph
from node_editor.graph import Graph
from node_editor.gui.node_list import NodeList
from node_editor.gui.scene import NodeScene
from node_editor.gui.view import NodeView
from node_editor.loader import load_node_classes
from node_editor.node import Status

FILE_FILTER = "Graph files (*.json)"


class MainWindow(QMainWindow):
    """The toolbar at the top, the node list at the left side, and the node view at the right side.

    The style sheet in theme.py gives the colors. It finds the widgets by their object names.
    """

    def __init__(self, nodes_folder: Path, start_file: Path | None = None) -> None:
        super().__init__()
        self.node_classes = load_node_classes(nodes_folder)
        self.graph = Graph()
        self.file_path: Path | None = None  # The graph file that is open now.

        self.scene = NodeScene(self.graph, self)
        self.view = NodeView(self.scene)
        self.view.node_dropped.connect(self.add_node)
        self.node_list = NodeList(self.node_classes)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.node_list)
        self.splitter.addWidget(self.view)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([200, 1000])
        self.setCentralWidget(self.splitter)

        self._make_toolbar()
        self._restore_window_state()

        if start_file is not None:
            self.open_file(start_file)
        else:
            self._update_title()

    def _make_toolbar(self) -> None:
        """Make one row at the top: the File menu, the Run Graph button and the messages."""
        menu = QMenu(self)
        self._add_action(menu, "&New", "Ctrl+N", self.new_file)
        self._add_action(menu, "&Open...", "Ctrl+O", self.choose_file_to_open)
        self._add_action(menu, "&Save", "Ctrl+S", self.save)
        self._add_action(menu, "Save &As...", "Ctrl+Shift+S", self.save_as)
        menu.addSeparator()
        self._add_action(menu, "&Quit", "Ctrl+Q", self.close)
        file_button = QToolButton()
        file_button.setText("&File")
        file_button.setMenu(menu)
        file_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        run_action = QAction("Run Graph", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.setToolTip("Run the graph (F5)")
        run_action.triggered.connect(self.run_graph)
        run_button = QToolButton()
        run_button.setObjectName("RunButton")
        run_button.setDefaultAction(run_action)

        spacer = QWidget()  # Pushes the messages to the right side.
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.message = QLabel()
        self.message.setObjectName("Message")
        self.message_timer = QTimer(self)
        self.message_timer.setSingleShot(True)
        self.message_timer.timeout.connect(self.message.clear)

        toolbar = QToolBar()
        toolbar.setObjectName("ToolBar")
        toolbar.setMovable(False)
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)  # This menu can hide the toolbar.
        toolbar.addWidget(file_button)
        toolbar.addWidget(run_button)
        toolbar.addWidget(spacer)
        toolbar.addWidget(self.message)
        self.addToolBar(toolbar)

    def _add_action(self, menu: QMenu, text: str, shortcut: str, function: Callable[[], object]) -> None:
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(function)
        menu.addAction(action)

    # --- Nodes ---

    def add_node(self, class_name: str, position: QPointF) -> None:
        """Add a node of the type `class_name`. The view calls this when you drop a node type."""
        node_class = self.node_classes.get(class_name)
        if node_class is not None:
            self.graph.add_node(node_class(), position.x(), position.y())

    def run_graph(self) -> None:
        run_graph(self.graph)
        errors = [node for node in self.graph.nodes if node.status is Status.ERROR]
        if errors:
            self.show_message(f"The run has errors in {len(errors)} nodes. Put the mouse on a red node.")
        else:
            self.show_message("The run is complete.", 3000)

    def show_message(self, text: str, milliseconds: int = 0) -> None:
        """Show a message at the right side of the toolbar. If `milliseconds` is not 0, remove it after that time."""
        self.message.setText(text)
        if milliseconds:
            self.message_timer.start(milliseconds)
        else:
            self.message_timer.stop()

    # --- Files ---

    def new_file(self) -> None:
        self.graph.clear()
        self.file_path = None
        self._update_title()

    def choose_file_to_open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Graph", self._dialog_folder(), FILE_FILTER)
        if path:  # The path is empty when you click Cancel.
            self.open_file(Path(path))

    def open_file(self, path: Path) -> None:
        try:
            self.graph.load(path, self.node_classes)
        except (OSError, ValueError, KeyError, TypeError) as error:
            QMessageBox.warning(self, "Open Graph", f"Cannot open {path.name}:\n{error}")
            return
        self.file_path = path
        self._update_title()
        self.view.center_on_nodes()

    def save(self) -> None:
        if self.file_path is None:
            self.save_as()
        else:
            self.save_file(self.file_path)

    def save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Graph", self._dialog_folder(), FILE_FILTER)
        if path:  # The path is empty when you click Cancel.
            self.save_file(Path(path))

    def save_file(self, path: Path) -> None:
        try:
            self.graph.save(path)
        except OSError as error:
            QMessageBox.warning(self, "Save Graph", f"Cannot save {path.name}:\n{error}")
            return
        self.file_path = path
        self._update_title()
        self.show_message(f"Saved {path.name}", 3000)

    def _dialog_folder(self) -> str:
        return str(self.file_path.parent) if self.file_path else ""

    def _update_title(self) -> None:
        name = self.file_path.name if self.file_path else "Untitled"
        self.setWindowTitle(f"{name} - Python Node Editor")

    # --- Window size and position ---

    def _restore_window_state(self) -> None:
        settings = QSettings()
        geometry = settings.value("geometry")
        splitter_state = settings.value("splitter")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1200, 700)
        if splitter_state:
            self.splitter.restoreState(splitter_state)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("splitter", self.splitter.saveState())
        super().closeEvent(event)
