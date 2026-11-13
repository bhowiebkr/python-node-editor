"""Start the Python Node Editor."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from node_editor.gui.main_window import MainWindow
from node_editor.gui.theme import apply_dark_theme

ROOT = Path(__file__).resolve().parent  # The repo folder. The app works from any current folder.


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    app = QApplication(sys.argv)
    app.setOrganizationName("python-node-editor")  # QSettings uses these names.
    app.setApplicationName("Python Node Editor")
    app.setWindowIcon(QIcon(str(ROOT / "resources" / "app.ico")))
    apply_dark_theme(app)

    window = MainWindow(
        nodes_folder=ROOT / "example_project",
        start_file=ROOT / "example_project" / "example.json",
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
