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

    def get_data(self):
        # Get a list of nodes in the order to be computed. Forward evaluation by default.
        def get_node_compute_order(node, forward=False):
            # Create a set to keep track of visited nodes
            visited = set()
            # Create a stack to keep track of nodes to visit
            stack = [node]
            # Create a list to store the evaluation order
            order = []

        # Get the next nodes that this node is dependent on
        def get_next_input_node(node):
            pass

        # Get the next nodes that is affected by the input node.
        def get_next_output_node(node):
            pass

        # if pin isn't connected, return it current data

        # get the evalutation order of the owning node of the pin

        # loop over each node and process it

        # return the pin's data
