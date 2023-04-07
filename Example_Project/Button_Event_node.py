from node_editor.gui.node import Node


class Button_Event_Node(Node):
    def __init__(self):
        super().__init__()

        self.title = "Button Event"
        self.type_text = "GUI Events"
        self.set_color(title_color=(128, 0, 0))

        self.add_port(name="Ex Out", is_output=True, execution=True)
        # self.add_port(name="input A", is_output=False)

        self.build()
