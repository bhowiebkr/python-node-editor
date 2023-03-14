from PySide6 import QtWidgets, QtGui, QtCore


class Port(QtWidgets.QGraphicsPathItem):
    """A graphics item representing an input or output port for a node in a node-based graphical user interface.

    Attributes:
        radius_ (int): The radius of the port circle.
        margin (int): The margin between the port circle and the port name text.
        port_text_height (int): The height of the port name text.
        port_text_width (int): The width of the port name text.
        _is_output (bool): True if the port is an output port, False if it is an input port.
        _name (str): The name of the port.
        m_node (Node): The node to which the port belongs.
        connection (Connection): The connection attached to the port, if any.
        text_path (QPainterPath): The path used to draw the port name text.

    Methods:
        set_is_output(is_output: bool) -> None: Set the output status of the port.
        set_name(name: str) -> None: Set the name of the port.
        set_node(node: Node) -> None: Set the node to which the port belongs.
        set_port_flags(flags: int) -> None: Set the port flags.
        set_ptr(ptr: Any) -> None: Set the pointer to the port.
        name() -> str: Get the name of the port.
        is_output() -> bool: Check if the port is an output port.
        node() -> Node: Get the node to which the port belongs.
        paint(painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: Optional[QtWidgets.QWidget]) -> None: Paint the port.
        clear_connection() -> None: Clear the connection attached to the port.
        can_connect_to(port: Port) -> bool: Check if the port can be connected to another port.
        is_connected() -> bool: Check if the port is connected to another port.
        itemChange(change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any: Handle item change events.
    """

    def __init__(self, parent, scene):
        super(Port, self).__init__(parent)

        self.radius_ = 5
        self.margin = 2

        path = QtGui.QPainterPath()
        path.addEllipse(-self.radius_, -self.radius_, 2 * self.radius_, 2 * self.radius_)
        self.setPath(path)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemSendsScenePositionChanges)
        self.font = QtGui.QFont()
        self.font_metrics = QtGui.QFontMetrics(self.font)

        self.port_text_height = self.font_metrics.height()

        self._is_output = False
        self._name = None
        self.margin = 2

        self.m_node = None
        self.connection = None

        self.text_path = QtGui.QPainterPath()

    def set_is_output(self, is_output):
        self._is_output = is_output

    def set_name(self, name):
        self._name = name
        nice_name = self._name.replace("_", " ").title()
        self.port_text_width = self.font_metrics.horizontalAdvance(nice_name)

        if self._is_output:
            x = -self.radius_ - self.margin - self.port_text_width
            y = self.port_text_height / 4

            self.text_path.addText(x, y, self.font, nice_name)

        else:
            x = self.radius_ + self.margin
            y = self.port_text_height / 4

            self.text_path.addText(x, y, self.font, nice_name)

    def set_node(self, node):
        self.m_node = node

    def set_port_flags(self, flags):
        self.m_port_flags = flags

    def set_ptr(self, ptr):
        self.m_ptr = ptr

    def name(self):
        return self._name

    def is_output(self):
        return self._is_output

    def node(self):
        return self.m_node

    def paint(self, painter, option=None, widget=None):
        painter.setPen(QtGui.QPen(1))
        painter.setBrush(QtCore.Qt.green)
        painter.drawPath(self.path())

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawPath(self.text_path)

    def clear_connection(self):
        if self.connection:
            self.connection.delete()

    def can_connect_to(self, port):
        print(port.node(), self.node())
        if not port:
            return False
        if port.node() == self.node():
            return False

        if self._is_output == port._is_output:
            return False

        return True

    def is_connected(self):
        if self.connection:
            return True
        return False

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemScenePositionHasChanged:
            if self.connection:
                self.connection.update_start_and_end_pos()

        return value
