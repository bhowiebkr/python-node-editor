"""A pin is an input or an output on a node."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from node_editor.node import Node


class Pin:
    """One input or one output of a node.

    There are two kinds of pins:

    - A data pin carries a value (for example a number) from an output to an input.
    - An exec pin carries no value. An exec connection tells which node runs next.
    """

    def __init__(self, node: Node, name: str, is_output: bool, is_exec: bool = False, default: Any = None) -> None:
        self.node = node  # The node that owns this pin.
        self.name = name  # Unique in the node. Graph files use the name to find the pin.
        self.is_output = is_output
        self.is_exec = is_exec
        self.default = default  # The value of an input that has no connection.
        self.value: Any = default  # The value now. A run of the graph sets it.

    def __repr__(self) -> str:
        return f"Pin({self.node!r}, {self.name!r})"

    @property
    def allows_many_connections(self) -> bool:
        """Return True if more than one connection can use this pin.

        - A data output can send its value to many inputs.
        - A data input gets its value from one output only.
        - An exec output goes to one next node only.
        - An exec input can come from many nodes.
        """
        if self.is_exec:
            return not self.is_output
        return self.is_output
