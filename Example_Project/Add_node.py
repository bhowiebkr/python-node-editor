from node_editor.gui.node import Node


class Add_Node(Node):
    def __init__(self):
        super().__init__()

        self.title = "Add"
        self.type_text = "Logic Nodes"
        self.set_color(title_color=(0, 128, 0))

        self.add_pin(name="Ex In", is_output=False, execution=True)
        self.add_pin(name="Ex Out", is_output=True, execution=True)

        self.add_pin(name="input A", is_output=False)
        self.add_pin(name="input B", is_output=False)
        self.add_pin(name="output", is_output=True)
        self.build()
