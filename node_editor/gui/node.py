from PySide2 import QtWidgets, QtGui, QtCore

from node_editor.gui.port import Port


class Node(QtWidgets.QGraphicsPathItem):
    def __init__(self):
        super(Node, self).__init__()

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)

        self._title_text = "Title"
        self._type_text = "base"

        self._width = 30  # The Width of the node
        self._height = 30  # the height of the node
        self._ports = []  # A list of ports

        self.node_color = QtGui.QColor(20, 20, 20, 200)

        self.title_path = QtGui.QPainterPath()  # The path for the title
        self.type_path = QtGui.QPainterPath()  # The path for the type
        self.misc_path = QtGui.QPainterPath()  # a bunch of other stuff

        self.horizontal_margin = 30  # horizontal margin
        self.vertical_margin = 15  # vertical margin

    def paint(self, painter, option=None, widget=None):
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(241, 175, 0), 2))
            painter.setBrush(self.node_color)
        else:
            painter.setPen(self.node_color.lighter())
            painter.setBrush(self.node_color)

        painter.drawPath(self.path())
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)

        painter.drawPath(self.title_path)
        painter.drawPath(self.type_path)
        painter.drawPath(self.misc_path)

    def add_port(self, name, is_output=False, flags=0, ptr=None):
        port = Port(self, self.scene())
        port.set_is_output(is_output)
        port.set_name(name)
        port.set_node(node=self)
        port.set_port_flags(flags)
        port.set_ptr(ptr)

        self._ports.append(port)

    def build(self):
        """ Build the node
        """

        self.title_path = QtGui.QPainterPath()  # reset
        self.type_path = QtGui.QPainterPath()  # The path for the type
        self.misc_path = QtGui.QPainterPath()  # a bunch of other stuff

        total_width = 0
        total_height = 0
        path = QtGui.QPainterPath()  # The main path

        # The fonts what will be used
        title_font = QtGui.QFont("Lucida Sans Unicode", pointSize=16)
        title_type_font = QtGui.QFont("Lucida Sans Unicode", pointSize=8)
        port_font = QtGui.QFont("Lucida Sans Unicode")

        # Get the dimentions of the title and type
        title_dim = {
            "w": QtGui.QFontMetrics(title_font).width(self._title_text),
            "h": QtGui.QFontMetrics(title_font).height(),
        }

        title_type_dim = {
            "w": QtGui.QFontMetrics(title_type_font).width("(" + self._type_text + ")"),
            "h": QtGui.QFontMetrics(title_type_font).height(),
        }

        # Get the max width
        for dim in [title_dim["w"], title_type_dim["w"]]:
            if dim > total_width:
                total_width = dim

        # Add both the title and type height together for the total height
        for dim in [title_dim["h"], title_type_dim["h"]]:
            total_height += dim

        # Add the heigth for each of the ports
        for port in self._ports:
            port_dim = {
                "w": QtGui.QFontMetrics(port_font).width(port.name()),
                "h": QtGui.QFontMetrics(port_font).height(),
            }

            if port_dim["w"] > total_width:
                total_width = port_dim["w"]

            total_height += port_dim["h"]

        # Add the margin to the total_width
        total_width += self.horizontal_margin
        total_height += self.vertical_margin

        # Draw the background rectangle
        path.addRoundedRect(
            -total_width / 2, -total_height / 2, total_width, total_height, 5, 5
        )

        # Draw the title
        self.title_path.addText(
            -title_dim["w"] / 2,
            (-total_height / 2) + title_dim["h"],
            title_font,
            self._title_text,
        )

        # Draw the type
        self.type_path.addText(
            -title_type_dim["w"] / 2,
            (-total_height / 2) + title_dim["h"] + title_type_dim["h"],
            title_type_font,
            "(" + self._type_text + ")",
        )

        y = (-total_height / 2) + title_dim["h"] + title_type_dim["h"] + port_dim["h"]

        for port in self._ports:
            if port.is_output():
                port.setPos(total_width / 2 - 10, y)
            else:
                port.setPos(-total_width / 2 + 10, y)
            y += port_dim["h"]

        self.setPath(path)

        self._width = total_width
        self._height = total_height

    def select_connections(self, value):
        for port in self._ports:
            for connection in port.connections():
                connection._do_highlight = value
                connection.update_path()

