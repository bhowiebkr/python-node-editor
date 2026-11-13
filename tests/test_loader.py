"""Tests for finding node classes in a folder."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

import pytest

from node_editor.loader import load_node_classes
from tests.conftest import EXAMPLE_FOLDER, ROOT

GOOD_FILE = """
from node_editor.node import Node, Status


class GoodNode(Node):
    title = "Good"
"""


def test_loader_finds_the_example_nodes() -> None:
    classes = load_node_classes(EXAMPLE_FOLDER)
    assert {"AddNode", "ButtonNode", "PrintNode", "ScalarNode"} <= set(classes)


def test_loader_uses_only_the_classes_that_the_file_defines(tmp_path: Path) -> None:
    (tmp_path / "good.py").write_text(GOOD_FILE, encoding="utf-8")
    assert list(load_node_classes(tmp_path)) == ["GoodNode"]


def test_loader_skips_private_files(tmp_path: Path) -> None:
    (tmp_path / "_private.py").write_text(GOOD_FILE, encoding="utf-8")
    assert load_node_classes(tmp_path) == {}


def test_loader_skips_a_broken_file(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    (tmp_path / "broken.py").write_text("this is not Python", encoding="utf-8")
    (tmp_path / "good.py").write_text(GOOD_FILE, encoding="utf-8")
    with caplog.at_level(logging.ERROR):
        classes = load_node_classes(tmp_path)
    assert list(classes) == ["GoodNode"]
    assert "broken.py" in caplog.text


def test_model_does_not_import_qt() -> None:
    # Only the files in node_editor/gui/ can use Qt. Use a new Python process, because
    # this test process already imported Qt.
    code = (
        "import sys\n"
        "import node_editor.execution, node_editor.graph, node_editor.loader\n"
        "assert not [name for name in sys.modules if name.startswith('PySide6')]\n"
    )
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True)
