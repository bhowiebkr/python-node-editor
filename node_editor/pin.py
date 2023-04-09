from node_editor.gui.pin_graphics import Pin_Graphics


class Pin(Pin_Graphics):
    def __init__(self, parent, scene):
        super().__init__(parent, scene)

        self.name = None
        self.node = None
        self.connection = None

    def set_execution(self, execution):
        self.execution = execution
        super().set_execution(execution)

    def set_name(self, name):
        self.name = name
        super().set_name(name)

    def clear_connection(self):
        if self.connection:
            self.connection.delete()

    def can_connect_to(self, pin):
        if not pin:
            return False
        if pin.node == self.node:
            return False

        return self.is_output != pin.is_output

    def is_connected(self):
        return bool(self.connection)
