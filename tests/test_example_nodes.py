"""Tests for the nodes in the example project. These tests do not show the nodes."""

from __future__ import annotations

from typing import Any

import pytest

from node_editor.execution import run_from, run_node
from node_editor.graph import Graph
from node_editor.loader import load_node_classes
from node_editor.node import Node, Status
from tests.conftest import EXAMPLE_FOLDER
from tests.helpers import LogNode, NumberNode, StartNode

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


# --- Text ---


@pytest.mark.parametrize(
    ("class_name", "inputs", "expected"),
    [
        ("JoinTextNode", {"a": "Hello, ", "b": "World"}, {"text": "Hello, World"}),
        ("JoinTextNode", {"a": "Total: ", "b": 5}, {"text": "Total: 5"}),
        ("UpperCaseNode", {"text": "Hello"}, {"result": "HELLO"}),
        ("LowerCaseNode", {"text": "Hello"}, {"result": "hello"}),
        ("ReplaceTextNode", {"text": "a-b-c", "old": "-", "new": "+"}, {"result": "a+b+c"}),
        ("SplitTextNode", {"text": "the quick  fox"}, {"items": ["the", "quick", "fox"]}),
        ("SplitTextNode", {"text": "milk, eggs,bread", "separator": ","}, {"items": ["milk", "eggs", "bread"]}),
        ("ContainsTextNode", {"text": "Hello, World", "part": "World"}, {"result": True}),
        ("ContainsTextNode", {"text": "Hello, World", "part": "world"}, {"result": False}),
    ],
)
def test_text_node_gives_the_result(class_name: str, inputs: dict[str, Any], expected: dict[str, Any]) -> None:
    assert outputs(make(class_name), **inputs) == expected


def test_format_text_puts_the_values_into_the_template() -> None:
    node = make("FormatTextNode", template="{a} x {b} = {c}")
    assert outputs(node, a=3, b=7, c=21) == {"text": "3 x 7 = 21"}

    node = make("FormatTextNode", template="{a:.2f}")
    assert outputs(node, a=2.0) == {"text": "2.00"}


def test_format_text_with_a_bad_template_shows_an_error() -> None:
    assert error_of(make("FormatTextNode", template="{d}")) == "'d'"


# --- Lists ---


@pytest.mark.parametrize(
    ("class_name", "inputs", "expected"),
    [
        ("RangeNode", {"first": 1, "last": 4}, {"items": [1, 2, 3, 4]}),
        ("LengthNode", {"items": ["a", "b"]}, {"length": 2}),
        ("LengthNode", {"items": "hello"}, {"length": 5}),
        ("SumNode", {"items": [1, 2, 3]}, {"total": 6}),
        ("GetItemNode", {"items": ["a", "b", "c"], "index": 1}, {"item": "b"}),
        ("GetItemNode", {"items": ["a", "b", "c"], "index": -1}, {"item": "c"}),
        ("SortNode", {"items": ["milk", "eggs", "bread"]}, {"result": ["bread", "eggs", "milk"]}),
        ("JoinListNode", {"items": [1, 2, 3]}, {"text": "1, 2, 3"}),
        ("JoinListNode", {"items": ["a", "b"], "separator": "-"}, {"text": "a-b"}),
    ],
)
def test_list_node_gives_the_result(class_name: str, inputs: dict[str, Any], expected: dict[str, Any]) -> None:
    assert outputs(make(class_name), **inputs) == expected


def test_get_item_after_the_end_shows_an_error() -> None:
    assert error_of(make("GetItemNode"), items=["a"], index=5) == "list index out of range"


# --- Flow ---


@pytest.mark.parametrize("condition", [True, False])
def test_branch_runs_the_output_for_the_condition(condition: bool) -> None:
    graph = Graph()
    start = graph.add_node(StartNode())
    branch = graph.add_node(make("BranchNode"))
    branch.pin("condition").default = condition
    graph.connect(start.pin("then"), branch.pin("exec"))
    logs: dict[str, list[Any]] = {"true": [], "false": []}
    for name, log in logs.items():
        graph.connect(branch.pin(name), graph.add_node(LogNode(log)).pin("exec"))

    run_from(graph, start)

    assert logs == {"true": [None] if condition else [], "false": [] if condition else [None]}


def test_for_loop_runs_the_loop_body_for_each_index() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    loop = graph.add_node(make("ForLoopNode"))
    loop.pin("first").default = 1
    loop.pin("last").default = 3
    body = graph.add_node(LogNode(log))
    completed = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), loop.pin("exec"))
    graph.connect(loop.pin("loop body"), body.pin("exec"))
    graph.connect(loop.pin("completed"), completed.pin("exec"))
    graph.connect(loop.pin("index"), body.pin("value"))

    run_from(graph, start)

    assert log == [1, 2, 3, None]


def test_for_each_runs_the_loop_body_for_each_item() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    loop = graph.add_node(make("ForEachNode"))
    loop.pin("items").default = ["milk", "eggs"]
    body = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), loop.pin("exec"))
    graph.connect(loop.pin("loop body"), body.pin("exec"))
    graph.connect(loop.pin("item"), body.pin("value"))

    run_from(graph, start)

    assert log == ["milk", "eggs"]
    assert loop.pin("index").value == 1


def test_sequence_runs_its_outputs_in_order() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    sequence = graph.add_node(make("SequenceNode"))
    graph.connect(start.pin("then"), sequence.pin("exec"))
    for number, name in enumerate(["first", "second", "third"], start=1):
        printer = graph.add_node(LogNode(log))
        graph.connect(sequence.pin(name), printer.pin("exec"))
        graph.connect(graph.add_node(NumberNode(number)).pin("value"), printer.pin("value"))

    run_from(graph, start)

    assert log == [1, 2, 3]


def test_counter_counts_its_runs() -> None:
    counter = make("CounterNode")
    assert outputs(counter) == {"count": 1}
    assert outputs(counter) == {"count": 2}
