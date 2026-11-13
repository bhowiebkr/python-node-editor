"""Tests for running a graph."""

from __future__ import annotations

from typing import Any

from node_editor.execution import pure_nodes_needed_by, run_from, run_graph, run_node
from node_editor.graph import Graph
from node_editor.node import Status
from tests.helpers import ChooseNode, CountNode, FailNode, LogNode, NumberNode, RepeatNode, StartNode, SumNode


def test_run_node_runs_the_pure_inputs_first() -> None:
    graph = Graph()
    two = graph.add_node(NumberNode(2))
    three = graph.add_node(NumberNode(3))
    total = graph.add_node(SumNode())
    graph.connect(two.pin("value"), total.pin("a"))
    graph.connect(three.pin("value"), total.pin("b"))

    run_node(graph, total)

    assert total.pin("result").value == 5
    assert [node.status for node in graph.nodes] == [Status.CLEAN] * 3


def test_input_with_no_connection_uses_its_default() -> None:
    graph = Graph()
    total = graph.add_node(SumNode())
    run_node(graph, total)
    assert total.pin("result").value == 0


def test_clean_node_does_not_run_again_until_it_is_dirty() -> None:
    graph = Graph()
    number = NumberNode(1)
    graph.add_node(number)
    total = graph.add_node(SumNode())
    graph.connect(number.pin("value"), total.pin("a"))

    run_node(graph, total)
    run_node(graph, total)
    assert number.runs == 1

    number.value = 10
    number.mark_dirty()
    run_node(graph, total)
    assert number.runs == 2
    assert total.pin("result").value == 10


def test_pure_nodes_needed_by_gives_the_run_order() -> None:
    # number -> left  -> total
    #        -> right ->
    graph = Graph()
    number = graph.add_node(NumberNode(1))
    left = graph.add_node(SumNode())
    right = graph.add_node(SumNode())
    total = graph.add_node(SumNode())
    graph.connect(number.pin("value"), left.pin("a"))
    graph.connect(number.pin("value"), right.pin("a"))
    graph.connect(left.pin("result"), total.pin("a"))
    graph.connect(right.pin("result"), total.pin("b"))

    order = pure_nodes_needed_by(graph, total)

    assert order == [number, left, right]


def test_run_from_follows_the_exec_connections() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    first = graph.add_node(LogNode(log))
    second = graph.add_node(LogNode(log))
    number = graph.add_node(NumberNode(7))
    graph.connect(start.pin("then"), first.pin("exec"))
    graph.connect(first.pin("then"), second.pin("exec"))
    graph.connect(number.pin("value"), second.pin("value"))

    run_from(graph, start)

    assert log == [None, 7]


def test_error_sets_the_status_and_stops_the_exec_chain() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    first = graph.add_node(LogNode(log))
    second = graph.add_node(LogNode(log))
    fail = graph.add_node(FailNode())
    graph.connect(start.pin("then"), first.pin("exec"))
    graph.connect(first.pin("then"), second.pin("exec"))
    graph.connect(fail.pin("value"), first.pin("value"))

    run_from(graph, start)

    assert fail.status is Status.ERROR
    assert fail.error == "boom"
    assert first.status is Status.ERROR  # Its input comes from a node with an error.
    assert second.status is Status.DIRTY  # It did not run.
    assert log == []


def test_run_graph_starts_at_the_start_nodes() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    printer = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), printer.pin("exec"))
    lonely = graph.add_node(LogNode(log))  # No exec connection goes to it, so it does not run.
    total = graph.add_node(SumNode())  # A pure node with no connections. It runs at the end.

    run_graph(graph)

    assert log == [None]
    assert printer.status is Status.CLEAN
    assert lonely.status is Status.DIRTY
    assert total.status is Status.CLEAN


def test_node_can_choose_its_exec_output() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    choose = graph.add_node(ChooseNode())
    yes = graph.add_node(LogNode(log))
    no = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), choose.pin("exec"))
    graph.connect(choose.pin("yes"), yes.pin("exec"))
    graph.connect(choose.pin("no"), no.pin("exec"))

    run_from(graph, start)

    assert no.status is Status.CLEAN
    assert yes.status is Status.DIRTY  # It did not run.
    assert log == [None]


def test_node_can_run_an_exec_output_many_times() -> None:
    # The Sum node must run again for each index, because the index changes.
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    repeat = graph.add_node(RepeatNode())
    ten = graph.add_node(NumberNode(10))
    total = graph.add_node(SumNode())
    body = graph.add_node(LogNode(log))
    done = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), repeat.pin("exec"))
    graph.connect(repeat.pin("body"), body.pin("exec"))
    graph.connect(repeat.pin("done"), done.pin("exec"))
    graph.connect(repeat.pin("index"), total.pin("a"))
    graph.connect(ten.pin("value"), total.pin("b"))
    graph.connect(total.pin("result"), body.pin("value"))

    run_from(graph, start)

    assert log == [10, 11, 12, None]
    assert repeat.status is Status.CLEAN
    # "done" did not change the index, so the nodes in the loop body stay clean.
    assert total.status is Status.CLEAN
    assert body.status is Status.CLEAN


def test_new_value_from_an_exec_node_makes_its_users_run_again() -> None:
    log: list[Any] = []
    graph = Graph()
    start = graph.add_node(StartNode())
    count = graph.add_node(CountNode())
    total = graph.add_node(SumNode())
    printer = graph.add_node(LogNode(log))
    graph.connect(start.pin("then"), count.pin("exec"))
    graph.connect(count.pin("then"), printer.pin("exec"))
    graph.connect(count.pin("count"), total.pin("a"))
    graph.connect(total.pin("result"), printer.pin("value"))

    run_from(graph, start)
    run_from(graph, start)

    assert log == [1, 2]
