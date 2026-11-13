"""Tests for the graph: nodes, connection rules and dirty status."""

from __future__ import annotations

import pytest

from node_editor.graph import Graph
from node_editor.node import Status
from tests.helpers import LogNode, NumberNode, StartNode, SumNode


def test_add_node_gives_new_ids() -> None:
    graph = Graph()
    first = graph.add_node(NumberNode())
    second = graph.add_node(NumberNode())
    assert (first.id, second.id) == (1, 2)
    assert first.graph is graph


def test_add_node_refuses_an_id_that_is_used() -> None:
    graph = Graph()
    graph.add_node(NumberNode(), node_id=5)
    with pytest.raises(ValueError):
        graph.add_node(NumberNode(), node_id=5)
    assert graph.add_node(NumberNode()).id == 6


def test_connect_puts_the_output_at_the_start() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    connection = graph.connect(total.pin("a"), number.pin("value"))
    assert connection is not None
    assert connection.start is number.pin("value")
    assert connection.end is total.pin("a")


def test_connect_refuses_bad_connections() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    log = graph.add_node(LogNode([]))
    start = graph.add_node(StartNode())

    assert graph.connect(total.pin("a"), total.pin("result")) is None  # Same node.
    assert graph.connect(total.pin("a"), log.pin("value")) is None  # Two inputs.
    assert graph.connect(number.pin("value"), total.pin("result")) is None  # Two outputs.
    assert graph.connect(start.pin("then"), log.pin("value")) is None  # Exec to data.
    assert graph.connections == []


def test_connect_refuses_the_same_connection_two_times() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    assert graph.connect(number.pin("value"), total.pin("a")) is not None
    assert graph.connect(number.pin("value"), total.pin("a")) is None
    assert len(graph.connections) == 1


def test_connect_refuses_a_cycle() -> None:
    graph = Graph()
    first = graph.add_node(SumNode())
    second = graph.add_node(SumNode())
    assert graph.connect(first.pin("result"), second.pin("a")) is not None
    assert graph.connect(second.pin("result"), first.pin("a")) is None


def test_data_input_keeps_one_connection() -> None:
    graph = Graph()
    first = graph.add_node(NumberNode())
    second = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    graph.connect(first.pin("value"), total.pin("a"))
    graph.connect(second.pin("value"), total.pin("a"))
    assert [c.start for c in graph.connections] == [second.pin("value")]


def test_data_output_can_have_many_connections() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    graph.connect(number.pin("value"), total.pin("a"))
    graph.connect(number.pin("value"), total.pin("b"))
    assert len(graph.connections) == 2


def test_exec_output_keeps_one_connection() -> None:
    graph = Graph()
    start = graph.add_node(StartNode())
    first = graph.add_node(LogNode([]))
    second = graph.add_node(LogNode([]))
    graph.connect(start.pin("then"), first.pin("exec"))
    graph.connect(start.pin("then"), second.pin("exec"))
    assert [c.end for c in graph.connections] == [second.pin("exec")]


def test_exec_input_can_have_many_connections() -> None:
    graph = Graph()
    first = graph.add_node(StartNode())
    second = graph.add_node(StartNode())
    log = graph.add_node(LogNode([]))
    graph.connect(first.pin("then"), log.pin("exec"))
    graph.connect(second.pin("then"), log.pin("exec"))
    assert len(graph.connections) == 2


def test_remove_node_removes_its_connections() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    graph.connect(number.pin("value"), total.pin("a"))
    graph.remove_node(number)
    assert graph.nodes == [total]
    assert graph.connections == []
    assert number.graph is None


def test_mark_dirty_follows_data_connections_only() -> None:
    graph = Graph()
    number = graph.add_node(NumberNode())
    total = graph.add_node(SumNode())
    start = graph.add_node(StartNode())
    log = graph.add_node(LogNode([]))
    graph.connect(number.pin("value"), total.pin("a"))
    graph.connect(start.pin("then"), log.pin("exec"))
    for node in graph.nodes:
        node.status = Status.CLEAN

    graph.mark_dirty(number)
    graph.mark_dirty(start)

    assert number.status is Status.DIRTY
    assert total.status is Status.DIRTY  # It uses the value of `number`.
    assert start.status is Status.DIRTY
    assert log.status is Status.CLEAN  # An exec connection carries no value.


def test_listeners_get_each_change() -> None:
    graph = Graph()
    calls: list[str] = []
    graph.listeners.append(lambda: calls.append("changed"))
    node = graph.add_node(NumberNode())
    graph.remove_node(node)
    assert len(calls) == 2
