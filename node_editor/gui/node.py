from PySide6 import QtWidgets, QtGui, QtCore

from node_editor.gui.port import Port


class Node(QtWidgets.QGraphicsPathItem):
    """
    A QGraphicsPathItem representing a node in the node editor.

    Attributes
    ----------
    node_color : QtGui.QColor
        The color of the node.
    _title_text : str
        The text of the node's title.
    _type_text : str
        The text of the node's type.
    _width : int
        The width of the node.
    _height : int
        The height of the node.
    _ports : list
        A list of ports connected to this node.
    title_path : QtGui.QPainterPath
        The path for the title of the node.
    type_path : QtGui.QPainterPath
        The path for the type of the node.
    misc_path : QtGui.QPainterPath
        The path for miscellaneous items.
    horizontal_margin : int
        The horizontal margin of the node.
    vertical_margin : int
        The vertical margin of the node.

    """

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

    @property
    def title(self):
        return self._title_text

    @title.setter
    def title(self, title):
        self._title_text = title

    @property
    def type_text(self):
        return self._type_text

    @type_text.setter
    def type_text(self, type_text):
        self._type_text = type_text

    def paint(self, painter, option=None, widget=None):
        """
        Paints the node on the given painter.

        Args:
            painter (QtGui.QPainter): The painter to use for drawing the node.
            option (QStyleOptionGraphicsItem): The style options to use for drawing the node (optional).
            widget (QWidget): The widget to use for drawing the node (optional).
        """

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
        """
        Adds a new port to the node.

        Args:
            name (str): The name of the new port.
            is_output (bool, optional): True if the new port is an output port, False if it's an input port. Default is False.
            flags (int, optional): A set of flags to apply to the new port. Default is 0.
            ptr (Any, optional): A pointer to associate with the new port. Default is None.

        Returns:
            None: This method doesn't return anything.

        """
        port = Port(self, self.scene())
        port.set_is_output(is_output)
        port.set_name(name)
        port.set_node(node=self)
        port.set_port_flags(flags)
        port.set_ptr(ptr)

        self._ports.append(port)

    def build(self):
        """
        Builds the node by constructing its graphical representation.

        This method calculates the dimensions of the node, sets the fonts for various elements, and adds the necessary
        graphical components to the node, such as the title, type, and ports. Once the graphical representation of the node
        is constructed, the `setPath` method is called to set the path for the node.

        Returns:
            None.
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
            "w": QtGui.QFontMetrics(title_font).horizontalAdvance(self._title_text),
            "h": QtGui.QFontMetrics(title_font).height(),
        }

        title_type_dim = {
            "w": QtGui.QFontMetrics(title_type_font).horizontalAdvance("(" + self._type_text + ")"),
            "h": QtGui.QFontMetrics(title_type_font).height(),
        }

        # Get the max width
        for dim in [title_dim["w"], title_type_dim["w"]]:
            if dim > total_width:
                total_width = dim

        # Add both the title and type height together for the total height
        for dim in [title_dim["h"], title_type_dim["h"]]:
            total_height += dim

        port_dim = None
        # Add the heigth for each of the ports
        for port in self._ports:
            port_dim = {
                "w": QtGui.QFontMetrics(port_font).horizontalAdvance(port.name()),
                "h": QtGui.QFontMetrics(port_font).height(),
            }

            if port_dim["w"] > total_width:
                total_width = port_dim["w"]

            total_height += port_dim["h"]

        # Add the margin to the total_width
        total_width += self.horizontal_margin
        total_height += self.vertical_margin

        # Draw the background rectangle
        path.addRoundedRect(-total_width / 2, -total_height / 2, total_width, total_height, 5, 5)

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

        if port_dim:
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
        """
        Sets the highlighting of all connected ports to the specified value.

        This method takes a boolean value `value` as input and sets the `_do_highlight` attribute of all connected ports to
        this value. If a port is not connected, this method does nothing for that port. After setting the `_do_highlight`
        attribute for all connected ports, the `update_path` method is called for each connection.

        Args:
            value: A boolean value indicating whether to highlight the connected ports or not.

        Returns:
            None.
        """

        for port in self._ports:
            if port.connection:
                port.connection._do_highlight = value
                port.connection.update_path()

    def contextMenuEvent(self, event):
        """Open a context menu when the node is right-clicked.

        Args:
            event (QtGui.QContextMenuEvent): The context menu event.

        Returns:
            None
        """
        menu = QtWidgets.QMenu(self)
        pos = event.pos()

        # actions
        delete_node = QtWidgets.QAction("Delete Node")
        edit_node = QtWidgets.QAction("Edit Node")
        menu.addAction(delete_node)

        action = menu.exec_(self.mapToGlobal(pos))

        if action == delete_node:
            item_name = self.selectedItems()[0].text()

            if item_name not in ["And", "Not", "Input", "Output"]:
                print(f"delete node: {item_name}")
            else:
                print("Cannot delete default nodes")

        elif action == edit_node:
            print("editing node")

            # confirm to open in the editor replacing what is existing

    def delete(self):
        """Deletes the connection.

        This function removes any connected ports by calling :any:`Port.remove_connection` for each port
        connected to this connection. After all connections have been removed, the stored :any:`Port`
        references are set to None. Finally, :any:`QGraphicsScene.removeItem` is called on the scene to
        remove this widget.

        Returns:
            None
        """

        to_delete = []

        for port in self._ports:
            if port.connection:
                to_delete.append(port.connection)

        for connection in to_delete:
            connection.delete()

        self.scene().removeItem(self)
