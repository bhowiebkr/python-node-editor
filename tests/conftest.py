"""Settings and fixtures for all tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Run Qt without a screen. This must happen before Qt starts.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_FOLDER = ROOT / "example_project"


@pytest.fixture(autouse=True, scope="session")
def settings_in_temp_folder(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Keep the window settings of the tests out of the settings of the user."""
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    folder = str(tmp_path_factory.mktemp("settings"))
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, folder)
