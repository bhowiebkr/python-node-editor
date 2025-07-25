from __future__ import annotations

from typing import List
from typing import Optional

from node_editor.gui.node_graphics import Node_Graphics
from node_editor.pin import Pin

# from PySide6 import QtCore
# from PySide6 import QtGui
# from PySide6 import QtWidgets
# from PySide6.QtCore import Qt
# rom node_editor.common import Node_Status


class Node(Node_Graphics):
    def __init__(self) -> None:
        super().__init__()
        self._pins: List[Pin] = []

    # Override me
    def init_widget(self) -> None:
        pass

    def compute(self) -> None:
        raise NotImplementedError("compute is not implemented")

    def execute(self) -> None:
        # Get the values from the input pins
        self.execute_inputs()

        # Compute the value
        self.compute()

        # execute nodes connected to output
        self.execute_outputs()

    def execute_inputs(self) -> None:
        """Pull values from connected output pins into this node's input pins."""
        for pin in self._pins:
            if pin.is_output:
                continue
            if pin.connection:
                other_pin = pin.connection.get_other_pin(pin)
                if other_pin and hasattr(other_pin, "value"):
                    pin.value = other_pin.value

    def execute_outputs(self) -> None:
        pass

    def delete(self) -> None:
        """Deletes the connection.

        This function removes any connected pins by calling :any:`Port.remove_connection` for each pin
        connected to this connection. After all connections have been removed, the stored :any:`Port`
        references are set to None. Finally, :any:`QGraphicsScene.removeItem` is called on the scene to
        remove this widget.

        Returns:
            None
        """

        to_delete = [pin.connection for pin in self._pins if pin.connection]
        for connection in to_delete:
            connection.delete()

        self.scene().removeItem(self)

    def get_pin(self, name: str) -> Optional[Pin]:
        for pin in self._pins:
            if pin.name == name:
                return pin
        return None

    def add_pin(self, name: str, is_output: bool, execution: bool = False) -> None:
        """
        Adds a new pin to the node.

        Args:
            name (str): The name of the new pin.
            is_output (bool, optional): True if the new pin is an output pin, False if it's an input pin. Default is
            False.
            flags (int, optional): A set of flags to apply to the new pin. Default is 0.
            ptr (Any, optional): A pointer to associate with the new pin. Default is None.

        Returns:
            None: This method doesn't return anything.

        """
        pin = Pin(self, self.scene())
        pin.is_output = is_output
        pin.set_name(name)
        pin.node = self
        pin.set_execution(execution)

        self._pins.append(pin)

    def select_connections(self, value: bool) -> None:
        """
        Sets the highlighting of all connected pins to the specified value.

        This method takes a boolean value `value` as input and sets the `_do_highlight` attribute of all
        connected pins to this value. If a pin is not connected, this method does nothing for that pin.
        After setting the `_do_highlight` attribute for all connected pins, the `update_path` method is
        called for each connection.

        Args:
            value: A boolean value indicating whether to highlight the connected pins or not.

        Returns:
            None.
        """

        for pin in self._pins:
            if pin.connection:
                pin.connection._do_highlight = value
                pin.connection.update_path()
