"""The graph holds the nodes and the connections between them."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from node_editor.connection import Connection
from node_editor.node import Node, Status
from node_editor.pin import Pin

logger = logging.getLogger(__name__)


class Graph:
    """A set of nodes and the connections between their pins.

    The graph is the "model" of the editor. It does not know about Qt.
    The GUI shows the graph, and it calls the graph methods to change it.
    After each change, the graph calls each function in `listeners`, so that the GUI can update.
    """

    def __init__(self) -> None:
        self.nodes: list[Node] = []
        self.connections: list[Connection] = []
        self.listeners: list[Callable[[], None]] = []
        self._next_id = 1

    def changed(self) -> None:
        """Tell the listeners that the graph changed."""
        for listener in list(self.listeners):
            listener()

    # --- Nodes ---

    def add_node(self, node: Node, x: float = 0.0, y: float = 0.0, node_id: int | None = None) -> Node:
        """Add `node` at the position (x, y). Give it the id `node_id`, or a new id if `node_id` is None."""
        if node_id is None:
            node_id = self._next_id
        if self.node_by_id(node_id) is not None:
            raise ValueError(f"The graph already has a node with the id {node_id}")
        self._next_id = max(self._next_id, node_id + 1)

        node.id = node_id
        node.graph = self
        node.x = x
        node.y = y
        self.nodes.append(node)
        self.changed()
        return node

    def remove_node(self, node: Node) -> None:
        """Remove `node` and its connections."""
        for connection in [c for c in self.connections if node in (c.start.node, c.end.node)]:
            self.disconnect(connection)
        self.nodes.remove(node)
        node.graph = None
        self.changed()

    def node_by_id(self, node_id: int) -> Node | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def clear(self) -> None:
        """Remove all nodes and connections."""
        for node in self.nodes:
            node.graph = None
        self.nodes.clear()
        self.connections.clear()
        self._next_id = 1
        self.changed()

    # --- Connections ---

    def can_connect(self, a: Pin, b: Pin) -> bool:
        """Return True if a connection between the pins `a` and `b` is allowed."""
        if a.node is b.node:
            return False  # A node cannot connect to itself.
        if a.is_output == b.is_output:
            return False  # A connection goes from one output to one input.
        if a.is_exec != b.is_exec:
            return False  # Connect exec pins to exec pins, and data pins to data pins.

        start, end = (a, b) if a.is_output else (b, a)
        if any(c.start is start and c.end is end for c in self.connections):
            return False  # The pins already have this connection.
        # The connection must not make a loop. A loop has no first node, so the graph cannot run it.
        return not self.reaches(end.node, start.node)

    def connect(self, a: Pin, b: Pin) -> Connection | None:
        """Connect the pins `a` and `b`. The order of the pins is not important.

        Return the new connection, or None if the connection is not allowed.
        If a pin allows only one connection, its old connection is removed first.
        """
        if not self.can_connect(a, b):
            return None

        start, end = (a, b) if a.is_output else (b, a)
        for pin in (start, end):
            if not pin.allows_many_connections:
                for old in self.connections_of(pin):
                    self.disconnect(old)

        connection = Connection(start, end)
        self.connections.append(connection)
        self.mark_dirty(end.node)
        return connection

    def disconnect(self, connection: Connection) -> None:
        self.connections.remove(connection)
        self.mark_dirty(connection.end.node)

    def connections_of(self, pin: Pin) -> list[Connection]:
        """Return the connections that start or end at `pin`."""
        return [c for c in self.connections if pin in (c.start, c.end)]

    def source_of(self, pin: Pin) -> Pin | None:
        """Return the output pin that sends a value to the input `pin`, or None if no connection goes to it."""
        for connection in self.connections:
            if connection.end is pin:
                return connection.start
        return None

    def input_nodes(self, node: Node) -> list[Node]:
        """Return the nodes that send values to the data inputs of `node`."""
        return [c.start.node for c in self.connections if c.end.node is node and not c.end.is_exec]

    def reaches(self, start: Node, target: Node) -> bool:
        """Return True if you can go from `start` to `target` along the connections (from output to input)."""
        to_visit = [start]
        visited: set[Node] = set()
        while to_visit:
            node = to_visit.pop()
            if node is target:
                return True
            if node in visited:
                continue
            visited.add(node)
            to_visit.extend(c.end.node for c in self.connections if c.start.node is node)
        return False

    # --- Status ---

    def mark_dirty(self, node: Node) -> None:
        """Mark `node`, and all nodes that use its values, as dirty."""
        to_mark = [node]
        while to_mark:
            current = to_mark.pop()
            current.status = Status.DIRTY
            current.error = ""
            to_mark.extend(c.end.node for c in self.connections if c.start.node is current and not c.start.is_exec)
        self.changed()

    # --- Save and open ---

    def to_dict(self) -> dict[str, Any]:
        """Return the graph as a dict that the json module can write."""
        return {
            "nodes": [
                {"id": node.id, "type": type(node).__name__, "x": node.x, "y": node.y, "state": node.get_state()}
                for node in self.nodes
            ],
            "connections": [
                {
                    "from_node": c.start.node.id,
                    "from_pin": c.start.name,
                    "to_node": c.end.node.id,
                    "to_pin": c.end.name,
                }
                for c in self.connections
            ],
        }

    def from_dict(self, data: dict[str, Any], node_classes: dict[str, type[Node]]) -> None:
        """Replace the graph with the nodes and connections in `data`.

        `node_classes` gives the class for each node type name.
        The graph skips unknown node types and bad connections, and writes a warning to the log.
        """
        self.clear()
        for item in data.get("nodes", []):
            node_class = node_classes.get(item["type"])
            if node_class is None:
                logger.warning("Unknown node type %r. The node is skipped.", item["type"])
                continue
            node = node_class()
            node.set_state(item.get("state", {}))
            self.add_node(node, item["x"], item["y"], node_id=item["id"])

        for item in data.get("connections", []):
            start = self._find_pin(item["from_node"], item["from_pin"])
            end = self._find_pin(item["to_node"], item["to_pin"])
            if start is None or end is None or self.connect(start, end) is None:
                logger.warning("Bad connection %s. The connection is skipped.", item)

    def _find_pin(self, node_id: int, pin_name: str) -> Pin | None:
        node = self.node_by_id(node_id)
        if node is None:
            return None
        for pin in node.pins:
            if pin.name == pin_name:
                return pin
        return None

    def save(self, path: Path) -> None:
        """Write the graph to a JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=4) + "\n", encoding="utf-8")

    def load(self, path: Path, node_classes: dict[str, type[Node]]) -> None:
        """Replace the graph with the graph in a JSON file."""
        self.from_dict(json.loads(path.read_text(encoding="utf-8")), node_classes)
