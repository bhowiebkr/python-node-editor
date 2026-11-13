"""Run the nodes of a graph.

Exec pins decide WHEN a node runs. Data pins carry the VALUES.

- An exec node has exec pins (for example Print). It runs when an exec connection reaches it.
- A pure node has no exec pins (for example Add). It runs when another node needs its values.

Before a node runs, each data input gets the value of the output that connects to it.
After the node runs, its status is CLEAN. If compute() raises an exception, the status is ERROR.
"""

from __future__ import annotations

import logging

from node_editor.graph import Graph
from node_editor.node import Node, Status

logger = logging.getLogger(__name__)


def run_graph(graph: Graph) -> None:
    """Run the full graph.

    1. Start at each start node and follow the exec connections. A start node has exec outputs
       and no exec inputs (for example Button).
    2. Run the pure nodes that are not up to date, so that all nodes show their values.
    """
    for node in graph.nodes:
        if node.exec_outputs and not node.exec_inputs:
            run_from(graph, node)

    for node in graph.nodes:
        if node.is_pure and node.status is not Status.CLEAN:
            run_node(graph, node)


def run_from(graph: Graph, start: Node) -> None:
    """Run `start`. Then follow its exec outputs, and run the next nodes in the same way."""
    run_node(graph, start)
    if start.status is Status.ERROR:
        return  # Stop here. The next nodes do not run after an error.

    for pin in start.exec_outputs:
        for connection in graph.connections_of(pin):
            run_from(graph, connection.end.node)


def run_node(graph: Graph, node: Node) -> None:
    """Run the pure nodes that `node` needs (if they are not up to date). Then run `node`."""
    for needed in pure_nodes_needed_by(graph, node):
        if needed.status is not Status.CLEAN:
            _compute(graph, needed)
    _compute(graph, node)
    graph.changed()


def pure_nodes_needed_by(graph: Graph, node: Node) -> list[Node]:
    """Return the pure nodes that send values to `node`, directly or through other pure nodes.

    The list is in run order: each node comes after the nodes that send values to it.
    The search goes back along the data connections, and adds each node after its inputs.
    This is a depth-first "topological sort".
    """
    order: list[Node] = []

    def visit(current: Node) -> None:
        for source in graph.input_nodes(current):
            if source.is_pure and source not in order:
                visit(source)
                order.append(source)

    visit(node)
    return order


def _compute(graph: Graph, node: Node) -> None:
    """Copy the input values into `node`, call its compute(), and set its status."""
    for pin in node.data_inputs:
        source = graph.source_of(pin)
        if source is None:
            pin.value = pin.default
        elif source.node.status is Status.ERROR:
            node.status = Status.ERROR
            node.error = f"The input {pin.name!r} comes from a node with an error."
            return
        else:
            pin.value = source.value

    try:
        node.compute()
    except Exception as error:
        logger.exception("%s failed", node)
        node.status = Status.ERROR
        node.error = str(error) or type(error).__name__
        return

    node.status = Status.CLEAN
    node.error = ""
