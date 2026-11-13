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


# --- Math ---


@pytest.mark.parametrize(
    ("class_name", "inputs", "expected"),
    [
        ("AddNode", {"a": 2, "b": 3}, 5),
        ("SubtractNode", {"a": 2, "b": 3}, -1),
        ("MultiplyNode", {"a": 2, "b": 3}, 6),
        ("DivideNode", {"a": 3, "b": 2}, 1.5),
        ("ModuloNode", {"a": 7, "b": 3}, 1),
        ("PowerNode", {"value": 3, "exponent": 2}, 9),
        ("SquareRootNode", {"value": 9}, 3),
        ("RoundNode", {"value": 2.567, "digits": 2}, 2.57),
        ("RoundNode", {"value": 2.567}, 3),
        ("MinNode", {"a": 2, "b": 3}, 2),
        ("MaxNode", {"a": 2, "b": 3}, 3),
    ],
)
def test_math_node_gives_the_result(class_name: str, inputs: dict[str, Any], expected: Any) -> None:
    assert outputs(make(class_name), **inputs) == {"result": expected}


def test_divide_by_zero_shows_an_error() -> None:
    assert error_of(make("DivideNode"), a=1, b=0) == "division by zero"


def test_random_integer_is_from_minimum_to_maximum() -> None:
    node = make("RandomIntegerNode")
    values = {outputs(node, minimum=1, maximum=3)["value"] for _ in range(100)}
    assert values == {1, 2, 3}


# --- Logic ---


@pytest.mark.parametrize(
    ("comparison", "expected"),
    [("==", False), ("!=", True), ("<", True), ("<=", True), (">", False), (">=", False)],
)
def test_compare_uses_the_selected_comparison(comparison: str, expected: bool) -> None:
    node = make("CompareNode", comparison=comparison)
    assert outputs(node, a=2, b=3) == {"result": expected}


@pytest.mark.parametrize(
    ("class_name", "inputs", "expected"),
    [
        ("AndNode", {"a": True, "b": True}, True),
        ("AndNode", {"a": True, "b": False}, False),
        ("OrNode", {"a": False, "b": True}, True),
        ("OrNode", {"a": False, "b": False}, False),
        ("NotNode", {"value": True}, False),
        ("SelectNode", {"condition": True, "if true": "yes", "if false": "no"}, "yes"),
        ("SelectNode", {"condition": False, "if true": "yes", "if false": "no"}, "no"),
    ],
)
def test_logic_node_gives_the_result(class_name: str, inputs: dict[str, Any], expected: Any) -> None:
    assert outputs(make(class_name), **inputs) == {"result": expected}
