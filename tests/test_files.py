"""Tests for saving and opening graph files."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import pytest

from node_editor.execution import run_graph
from node_editor.graph import Graph
from node_editor.loader import load_node_classes
from tests.conftest import EXAMPLE_FOLDER
from tests.helpers import NODE_CLASSES, NumberNode, SumNode


def make_graph() -> Graph:
    graph = Graph()
    number = graph.add_node(NumberNode(4.5), x=10, y=20)
    total = graph.add_node(SumNode(), x=200, y=20)
    graph.connect(number.pin("value"), total.pin("a"))
    return graph


def test_save_and_open_give_the_same_graph(tmp_path: Path) -> None:
    path = tmp_path / "graph.json"
    make_graph().save(path)

    graph = Graph()
    graph.load(path, NODE_CLASSES)

    assert graph.to_dict() == make_graph().to_dict()
    number = graph.nodes[0]
    assert isinstance(number, NumberNode)
    assert number.value == 4.5
    assert (number.x, number.y) == (10, 20)


def test_new_node_after_open_gets_a_new_id() -> None:
    graph = Graph()
    graph.from_dict(make_graph().to_dict(), NODE_CLASSES)
    assert graph.add_node(NumberNode()).id == 3


def test_open_skips_unknown_node_types(caplog: pytest.LogCaptureFixture) -> None:
    data = make_graph().to_dict()
    data["nodes"][0]["type"] = "MissingNode"

    graph = Graph()
    with caplog.at_level(logging.WARNING):
        graph.from_dict(data, NODE_CLASSES)

    assert len(graph.nodes) == 1
    assert graph.connections == []  # The connection used the missing node.
    assert "MissingNode" in caplog.text


def test_open_skips_bad_connections(caplog: pytest.LogCaptureFixture) -> None:
    data = make_graph().to_dict()
    data["connections"][0]["to_pin"] = "no such pin"

    graph = Graph()
    with caplog.at_level(logging.WARNING):
        graph.from_dict(data, NODE_CLASSES)

    assert len(graph.nodes) == 2
    assert graph.connections == []
    assert "Bad connection" in caplog.text


def run_example(file_name: str, capsys: pytest.CaptureFixture[str]) -> list[str]:
    """Open an example graph, run it, and return the lines that it printed."""
    graph = Graph()
    graph.load(EXAMPLE_FOLDER / file_name, load_node_classes(EXAMPLE_FOLDER))
    run_graph(graph)
    return capsys.readouterr().out.splitlines()


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        ("example.json", ["Print: 5.0"]),
        ("temperature.json", ["Print: 100.0 Celsius = 212.0 Fahrenheit"]),
        ("word_count.json", ["Print: THE CAT SAT ON THE MAT", "Print: 6 words"]),
        ("pass_or_fail.json", ["Print: Pass"]),
        ("times_table.json", [f"Log: {n} x 7 = {n * 7}" for n in range(1, 11)]),
        (
            "shopping_list.json",
            ["Log: - apples", "Log: - bread", "Log: - eggs", "Log: - milk", "Log: - rice", "Print: 5 items"],
        ),
    ],
)
def test_example_graph_opens_and_runs(file_name: str, expected: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert run_example(file_name, capsys) == expected


def test_dice_example_adds_two_dice(capsys: pytest.CaptureFixture[str]) -> None:
    [line] = run_example("dice.json", capsys)
    match = re.fullmatch(r"Log: (\d+) \+ (\d+) = (\d+)", line)
    assert match is not None
    first, second, total = (int(number) for number in match.groups())
    assert 1 <= first <= 6
    assert 1 <= second <= 6
    assert total == first + second


@pytest.mark.parametrize("path", sorted(EXAMPLE_FOLDER.glob("*.json")), ids=lambda path: path.name)
def test_example_file_is_the_same_as_a_saved_file(path: Path, tmp_path: Path) -> None:
    graph = Graph()
    graph.load(path, load_node_classes(EXAMPLE_FOLDER))
    graph.save(tmp_path / "copy.json")
    saved = json.loads((tmp_path / "copy.json").read_text(encoding="utf-8"))
    assert saved == json.loads(path.read_text(encoding="utf-8"))
