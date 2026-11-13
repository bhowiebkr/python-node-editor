"""Tests for the nodes in the example project. These tests do not show the nodes."""

from __future__ import annotations

from typing import Any

import pytest

from node_editor.execution import run_node
from node_editor.graph import Graph
from node_editor.loader import load_node_classes
from node_editor.node import Node, Status
from tests.conftest import EXAMPLE_FOLDER

NODE_CLASSES = load_node_classes(EXAMPLE_FOLDER)


def make(class_name: str, **state: Any) -> Node:
    node = NODE_CLASSES[class_name]()
    if state:
        node.set_state(state)
    return node


def outputs(node: Node, **inputs: Any) -> dict[str, Any]:
    """Run `node` with these input values, and return its output values."""
    graph = Graph()
    graph.add_node(node)
    for name, value in inputs.items():
        node.pin(name).default = value  # An input with no connection uses its default value.
    run_node(graph, node)
    if node.status is Status.ERROR:
        raise AssertionError(node.error)
    return {pin.name: pin.value for pin in node.data_outputs}


def error_of(node: Node, **inputs: Any) -> str:
    """Run `node` with these input values, and return its error message."""
    graph = Graph()
    graph.add_node(node)
    for name, value in inputs.items():
        node.pin(name).default = value
    run_node(graph, node)
    assert node.status is Status.ERROR
    return node.error


# --- Inputs ---


@pytest.mark.parametrize(
    ("class_name", "state", "expected"),
    [
        ("ScalarNode", {"value": 2.5}, {"value": 2.5}),
        ("IntegerNode", {"value": 7}, {"value": 7}),
        ("TextNode", {"text": "hello"}, {"text": "hello"}),
        ("BooleanNode", {"value": True}, {"value": True}),
    ],
)
def test_input_node_gives_its_value(class_name: str, state: dict[str, Any], expected: dict[str, Any]) -> None:
    node = make(class_name, **state)
    assert node.get_state() == state
    assert outputs(node) == expected
