"""Tests for the Qt GUI. The tests use the example project and pytest-qt."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QMimeData, QPoint, QPointF, Qt
from PySide6.QtGui import QDropEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDoubleSpinBox, QFileDialog, QPushButton, QToolButton
from pytestqt.qtbot import QtBot

from node_editor.gui.main_window import MainWindow
from node_editor.gui.node_list import NODE_MIME_TYPE
from node_editor.node import Status
from tests.conftest import EXAMPLE_FOLDER
from tests.helpers import FailNode, NumberNode, SumNode


@pytest.fixture
def window(qtbot: QtBot) -> MainWindow:
    window = MainWindow(EXAMPLE_FOLDER, EXAMPLE_FOLDER / "example.json")
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    return window


def nodes_of_type(window: MainWindow, class_name: str) -> list[Any]:
    # The loader makes new classes for each window, so the tests find nodes by the class name.
    return [node for node in window.graph.nodes if type(node).__name__ == class_name]


def view_point(window: MainWindow, scene_point: QPointF) -> QPoint:
    """Return the position in the view viewport of a point in the scene."""
    window.view.centerOn(scene_point)
    return window.view.mapFromScene(scene_point)


def drag(window: MainWindow, start: QPoint, end: QPoint) -> None:
    viewport = window.view.viewport()
    QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=start)
    QTest.mouseMove(viewport, (start + end) / 2)
    QTest.mouseMove(viewport, end)
    QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=end)


def test_window_shows_the_example(window: MainWindow) -> None:
    assert len(window.scene.node_items) == 5
    assert len(window.scene.connection_items) == 4
    assert window.windowTitle() == "example.json - Python Node Editor"


def test_run_graph_shows_the_result(window: MainWindow) -> None:
    window.run_graph()
    assert nodes_of_type(window, "PrintNode")[0].label.text() == "5.0"
    assert all(node.status is Status.CLEAN for node in window.graph.nodes)


def test_button_node_runs_the_graph(window: MainWindow) -> None:
    button_item = window.scene.node_items[nodes_of_type(window, "ButtonNode")[0]]
    assert button_item.proxy is not None
    button = button_item.proxy.widget()
    assert isinstance(button, QPushButton)
    button.click()
    assert nodes_of_type(window, "PrintNode")[0].label.text() == "5.0"


def test_run_graph_button_in_the_toolbar_runs_the_graph(window: MainWindow) -> None:
    run_button = window.findChild(QToolButton, "RunButton")
    assert isinstance(run_button, QToolButton)
    run_button.click()
    assert nodes_of_type(window, "PrintNode")[0].label.text() == "5.0"
    assert window.message.text() == "The run is complete."


def test_file_shortcut_works_when_the_menu_is_closed(window: MainWindow, qtbot: QtBot) -> None:
    window.activateWindow()
    qtbot.waitActive(window)
    QTest.keyClick(window, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
    assert window.graph.nodes == []


def test_message_with_a_time_goes_away(window: MainWindow, qtbot: QtBot) -> None:
    window.show_message("Saved", 10)
    assert window.message.text() == "Saved"
    qtbot.waitUntil(lambda: window.message.text() == "")


def test_new_value_in_scalar_marks_the_add_node_dirty(window: MainWindow) -> None:
    window.run_graph()
    nodes_of_type(window, "ScalarNode")[0].on_value_changed(10.0)
    assert nodes_of_type(window, "AddNode")[0].status is Status.DIRTY
    window.run_graph()
    assert nodes_of_type(window, "PrintNode")[0].label.text() == "13.0"


def test_delete_key_removes_the_selected_node(window: MainWindow) -> None:
    scalar = nodes_of_type(window, "ScalarNode")[0]
    window.scene.node_items[scalar].setSelected(True)
    window.view.setFocus()
    QTest.keyClick(window.view, Qt.Key.Key_Delete)
    assert scalar not in window.graph.nodes
    assert len(window.scene.node_items) == 4
    assert len(window.scene.connection_items) == 3


def test_delete_key_in_a_node_widget_does_not_remove_the_node(window: MainWindow) -> None:
    scalar = nodes_of_type(window, "ScalarNode")[0]
    item = window.scene.node_items[scalar]
    item.setSelected(True)
    assert item.proxy is not None
    window.view.setFocus()
    window.scene.setFocusItem(item.proxy)  # As if you clicked in the number field.
    QTest.keyClick(window.view, Qt.Key.Key_Delete)
    assert scalar in window.graph.nodes


def test_click_selects_a_connection_and_delete_removes_it(window: MainWindow) -> None:
    window.graph.clear()
    number = window.graph.add_node(NumberNode(), 0, 0)
    total = window.graph.add_node(SumNode(), 400, 200)
    connection = window.graph.connect(number.pin("value"), total.pin("a"))
    assert connection is not None
    item = window.scene.connection_items[connection]

    middle = view_point(window, item.path().pointAtPercent(0.5))
    QTest.mouseClick(window.view.viewport(), Qt.MouseButton.LeftButton, pos=middle)
    assert item.isSelected()

    QTest.keyClick(window.view, Qt.Key.Key_Delete)
    assert window.graph.connections == []
    assert window.scene.connection_items == {}


def test_drag_from_pin_to_pin_makes_a_connection(window: MainWindow) -> None:
    window.graph.clear()
    number = window.graph.add_node(NumberNode(), 0, 0)
    total = window.graph.add_node(SumNode(), 300, 0)
    output_item = window.scene.node_items[number].pin_items[number.pin("value")]
    input_item = window.scene.node_items[total].pin_items[total.pin("a")]

    view_point(window, QPointF(150, 0))  # Show both nodes.
    start = window.view.mapFromScene(output_item.scenePos())
    end = window.view.mapFromScene(input_item.scenePos())
    drag(window, start, end)

    assert len(window.graph.connections) == 1
    assert window.graph.connections[0].start is number.pin("value")
    assert window.graph.connections[0].end is total.pin("a")
    assert window.scene.drag_line is None


def test_drag_from_pin_to_empty_space_makes_no_connection(window: MainWindow) -> None:
    window.graph.clear()
    number = window.graph.add_node(NumberNode(), 0, 0)
    output_item = window.scene.node_items[number].pin_items[number.pin("value")]

    start = view_point(window, output_item.scenePos())
    drag(window, start, start + QPoint(150, 80))

    assert window.graph.connections == []
    assert window.scene.drag_line is None
    assert (number.x, number.y) == (0, 0)  # A drag from a pin does not move the node.


def test_moving_a_node_moves_its_connections(window: MainWindow) -> None:
    add = nodes_of_type(window, "AddNode")[0]
    item = window.scene.node_items[add]
    item.setPos(500, 300)

    assert (add.x, add.y) == (500, 300)
    pin_item = item.pin_items[add.pin("a")]
    connection_item = next(c for c in window.scene.connection_items.values() if c.connection.end is add.pin("a"))
    assert connection_item.path().pointAtPercent(1) == pin_item.scenePos()


def test_drop_from_the_node_list_adds_a_node(window: MainWindow) -> None:
    mime_data = QMimeData()
    mime_data.setData(NODE_MIME_TYPE, b"AddNode")
    drop = QDropEvent(
        QPointF(100, 100),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    window.view.dropEvent(drop)
    assert len(nodes_of_type(window, "AddNode")) == 2


def test_node_list_drag_data_is_the_class_name(window: MainWindow) -> None:
    node_list = window.node_list
    add_item = node_list.findItems("Add", Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive)[0]
    data = node_list.mimeData([add_item]).data(NODE_MIME_TYPE)
    assert bytes(data.data()) == b"AddNode"


def test_cancel_in_the_save_dialog_does_not_save(window: MainWindow, monkeypatch: pytest.MonkeyPatch) -> None:
    # Issue #8: before, Cancel in the dialog caused an error.
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: ("", ""))
    window.save_as()
    assert window.file_path == EXAMPLE_FOLDER / "example.json"


def test_save_and_open_keep_the_node_values(window: MainWindow, tmp_path: Path) -> None:
    nodes_of_type(window, "ScalarNode")[0].on_value_changed(42.0)
    path = tmp_path / "saved.json"
    window.save_file(path)
    assert window.windowTitle() == "saved.json - Python Node Editor"

    window.new_file()
    assert window.scene.node_items == {}
    window.open_file(path)

    assert [node.value for node in nodes_of_type(window, "ScalarNode")] == [42.0, 3.0]
    proxy = window.scene.node_items[nodes_of_type(window, "ScalarNode")[0]].proxy
    assert proxy is not None
    spin_box = proxy.widget()
    assert isinstance(spin_box, QDoubleSpinBox)
    assert spin_box.value() == 42.0


def test_open_a_bad_file_shows_a_message(window: MainWindow, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    messages: list[str] = []
    monkeypatch.setattr("node_editor.gui.main_window.QMessageBox.warning", lambda *args: messages.append(args[2]))
    path = tmp_path / "bad.json"
    path.write_text("this is not JSON", encoding="utf-8")
    window.open_file(path)
    assert len(messages) == 1
    assert window.file_path == EXAMPLE_FOLDER / "example.json"


def test_error_shows_in_the_tooltip(window: MainWindow) -> None:
    window.graph.clear()
    fail = window.graph.add_node(FailNode())
    window.run_graph()
    assert window.scene.node_items[fail].toolTip() == "boom"
    assert "errors in 1 nodes" in window.message.text()


def test_each_example_node_can_be_shown(window: MainWindow) -> None:
    window.graph.clear()
    for node_class in window.node_classes.values():
        window.graph.add_node(node_class())
    assert len(window.scene.node_items) == len(window.node_classes)
