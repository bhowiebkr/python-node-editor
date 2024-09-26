from __future__ import annotations

from typing import Any
from typing import List

from node_editor.connection import Connection
from node_editor.node import Node


def compute_dag_nodes(nodes: List[Node], edges: List[Connection]) -> None:
    print("Compute DAG Nodes")

    num_nodes = len(nodes)
    num_connections = len(edges)

    print(f"Number of nodes: {num_nodes}, Number of connections: {num_connections}")

    # Get the edges

    # Adjacency List
    adj: List[Any] = [[] for _ in range(num_nodes)]
    print(adj)

    for node in nodes:
        print(node)
