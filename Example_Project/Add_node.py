from node_editor.gui.node import Node


class Add_Node(Node):
    def __init__(self):
        super().__init__()

        self.title = "Add"
        self.type_text = "Logic Nodes"
        self.add_port(name="input A", is_output=False)
        self.add_port(name="input B", is_output=False)
        self.add_port(name="output", is_output=True)
        self.build()
