from node_editor.node import Node


class Print_Node(Node):
    def __init__(self):
        super().__init__()

        self.title_text = "Print"
        self.type_text = "Debug Nodes"
        self.set_color(title_color=(160, 32, 240))

        self.add_pin(name="Ex In", is_output=False, execution=True)

        self.add_pin(name="input", is_output=False)
        self.build()
