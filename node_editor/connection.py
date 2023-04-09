from node_editor.gui.connection_graphics import Connection_Graphics


class Connection(Connection_Graphics):
    def __init__(self, parent):
        super().__init__(parent)

        self.start_pin = None
        self.end_pin = None

    def delete(self):
        """
        Deletes the connection and removes it from the scene and any connected pins.
        """
        for pin in (self.start_pin, self.end_pin):
            if pin:
                pin.connection = None
            pin = None

        self.scene().removeItem(self)

    def set_start_pin(self, pin):
        self.start_pin = pin
        self.start_pin.connection = self

    def set_end_pin(self, pin):
        self.end_pin = pin
        self.end_pin.connection = self

    def nodes(self):
        """
        Returns a tuple of the two connected nodes.

        Returns:
        tuple: A tuple of the two Node objects connected by this Connection.
        """
        return (self.start_pin.node(), self.end_pin.node())

    def update_start_and_end_pos(self):
        """
        Update the start and end positions of the Connection.

        Get the start and end pins and use them to set the start and end positions.
        """

        if self.start_pin and not self.start_pin.is_output:
            temp = self.end_pin
            self.end_pin = self.start_pin
            self.start_pin = temp

        if self.start_pin:
            self.start_pos = self.start_pin.scenePos()

        if self.end_pin:
            self.end_pos = self.end_pin.scenePos()

        self.update_path()
