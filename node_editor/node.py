"""A node is one step in the graph. Make a subclass of Node to make a new kind of node."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from node_editor.pin import Pin

if TYPE_CHECKING:
    # These imports are for type hints only. The model does not import Qt when it runs.
    from PySide6.QtWidgets import QWidget

    from node_editor.graph import Graph


class Status(Enum):
    """The state of a node. The editor shows it as a colored square on the node."""

    DIRTY = "dirty"  # Orange: the node did not run after its inputs changed.
    CLEAN = "clean"  # Green: the outputs are up to date.
    ERROR = "error"  # Red: compute() raised an exception.


class Node:
    """The base class for all nodes.

    To make a new kind of node:

    1. Make a subclass. Set `title`, `category` and `color`.
    2. In `__init__`, add the pins.
    3. In `compute`, read the inputs and set the outputs.

    Example::

        class AddNode(Node):
            title = "Add"
            category = "Math"

            def __init__(self) -> None:
                super().__init__()
                self.add_input("a", default=0.0)
                self.add_input("b", default=0.0)
                self.add_output("result")

            def compute(self) -> None:
                self.set_output("result", self.get_input("a") + self.get_input("b"))
    """

    title = "Node"  # The name in the node list and in the title bar.
    category = "Other"  # The group in the node list.
    color: tuple[int, int, int] = (123, 33, 177)  # The color of the title bar (red, green, blue).

    def __init__(self) -> None:
        self.id = 0  # The graph sets the id when you add the node.
        self.graph: Graph | None = None  # The graph that holds this node.
        self.x = 0.0  # The position of the top-left corner in the editor.
        self.y = 0.0
        self.pins: list[Pin] = []
        self.status = Status.DIRTY
        self.error = ""  # The error message when the status is ERROR.

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id})"

    # --- Pins ---

    def add_input(self, name: str, default: Any = None) -> Pin:
        """Add a data input. `default` is the value when no connection goes to the pin."""
        return self._add_pin(Pin(self, name, is_output=False, default=default))

    def add_output(self, name: str) -> Pin:
        """Add a data output."""
        return self._add_pin(Pin(self, name, is_output=True))

    def add_exec_input(self, name: str = "exec") -> Pin:
        """Add an exec input. The node runs when an exec connection reaches this pin."""
        return self._add_pin(Pin(self, name, is_output=False, is_exec=True))

    def add_exec_output(self, name: str = "then") -> Pin:
        """Add an exec output. After this node runs, the node at the other end runs."""
        return self._add_pin(Pin(self, name, is_output=True, is_exec=True))

    def _add_pin(self, pin: Pin) -> Pin:
        if any(other.name == pin.name for other in self.pins):
            raise ValueError(f"{self.title} already has a pin with the name {pin.name!r}")
        self.pins.append(pin)
        return pin

    def pin(self, name: str) -> Pin:
        """Return the pin with this name."""
        for pin in self.pins:
            if pin.name == name:
                return pin
        raise KeyError(f"{self.title} has no pin with the name {name!r}")

    @property
    def data_inputs(self) -> list[Pin]:
        return [pin for pin in self.pins if not pin.is_output and not pin.is_exec]

    @property
    def data_outputs(self) -> list[Pin]:
        return [pin for pin in self.pins if pin.is_output and not pin.is_exec]

    @property
    def exec_inputs(self) -> list[Pin]:
        return [pin for pin in self.pins if not pin.is_output and pin.is_exec]

    @property
    def exec_outputs(self) -> list[Pin]:
        return [pin for pin in self.pins if pin.is_output and pin.is_exec]

    @property
    def is_pure(self) -> bool:
        """A pure node has no exec pins. It runs when another node needs its values."""
        return not any(pin.is_exec for pin in self.pins)

    # --- Values ---

    def get_input(self, name: str) -> Any:
        """Return the value of an input pin. Use this in compute()."""
        return self.pin(name).value

    def set_output(self, name: str, value: Any) -> None:
        """Set the value of an output pin. Use this in compute()."""
        self.pin(name).value = value

    def mark_dirty(self) -> None:
        """Tell the graph that a value in this node changed (for example, from its widget)."""
        if self.graph is not None:
            self.graph.mark_dirty(self)
        else:
            self.status = Status.DIRTY

    # --- Methods to override in a subclass ---

    def compute(self) -> None:
        """Read the inputs and set the outputs.

        The base node does nothing. For example, the Button node does not override it.
        """

    def create_widget(self) -> QWidget | None:
        """Return a Qt widget to show inside the node, or None for no widget.

        The editor calls this one time, when it draws the node.
        """
        return None

    def get_state(self) -> dict[str, Any]:
        """Return the values to keep in the graph file (for example, the number in a Scalar node).

        The values must be JSON values: numbers, strings, lists, dicts, True, False or None.
        """
        return {}

    def set_state(self, state: dict[str, Any]) -> None:
        """Set the values from get_state() again, when the editor opens a graph file."""
