from __future__ import annotations

from typing import List

from node_editor.connection import Connection
from node_editor.node import Node


def topologicalSortUtil(v: int, adj: List[List[int]], visited: List[bool], stack: List[int]) -> None:
    # Mark the current node as visited
    visited[v] = True

    # Recur for all adjacent vertices
    for i in adj[v]:
        if not visited[i]:
            topologicalSortUtil(i, adj, visited, stack)

    # Push current vertex to stack which stores the result
    stack.append(v)


# Function to perform Topological Sort
def topologicalSort(adj: List[List[int]], num_nodes: int) -> List[int]:
    # Stack to store the result
    stack: List[int] = []

    visited = [False] * num_nodes

    # Call the recursive helper function to store
    # Topological Sort starting from all vertices one by
    # one
    for i in range(num_nodes):
        if not visited[i]:
            topologicalSortUtil(i, adj, visited, stack)

    # Print contents of stack
    print("Topological sorting of the graph:", end=" ")

    topological_order = []
    while stack:
        # print(stack.pop(), end=" ")
        topological_order.append(stack.pop())

    return topological_order


def compute_dag_nodes(nodes: List[Node], connections: List[Connection]) -> None:
    print("Compute DAG Nodes")

    num_nodes = len(nodes)
    # Get the edges
    edges = []
    for connection in connections:
        edges.append([int(node.index) for node in connection.nodes() if node is not None])

    # Adjacency List
    adjacency: List[List[int]] = [[] for _ in range(num_nodes)]

    for edge in edges:
        adjacency[edge[0]].append(edge[1])

    print("adjacency:\n\n", adjacency)

    topological_order = topologicalSort(adjacency, num_nodes)

    print(topological_order)
