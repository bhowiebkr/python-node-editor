"""A connection joins an output pin to an input pin."""

from __future__ import annotations

from dataclasses import dataclass

from node_editor.pin import Pin


@dataclass(frozen=True)
class Connection:
    """A connection from an output pin (`start`) to an input pin (`end`).

    A data connection sends the value of `start` to `end`.
    An exec connection tells the graph to run the node of `end` after the node of `start`.
    """

    start: Pin
    end: Pin
