from PySide6 import QtCore, QtGui, QtWidgets


class Pin(QtWidgets.QGraphicsPathItem):
    """A graphics item representing an input or output pin for a node in a node-based graphical user interface.

    Attributes:
        radius_ (int): The radius of the pin circle.
        margin (int): The margin between the pin circle and the pin name text.
        pin_text_height (int): The height of the pin name text.
        pin_text_width (int): The width of the pin name text.
        _is_output (bool): True if the pin is an output pin, False if it is an input pin.
        _name (str): The name of the pin.
        m_node (Node): The node to which the pin belongs.
        connection (Connection): The connection attached to the pin, if any.
        text_path (QPainterPath): The path used to draw the pin name text.

    Methods:
        set_is_output(is_output: bool) -> None: Set the output status of the pin.
        set_name(name: str) -> None: Set the name of the pin.
        set_node(node: Node) -> None: Set the node to which the pin belongs.
        set_pin_flags(flags: int) -> None: Set the pin flags.
        set_ptr(ptr: Any) -> None: Set the pointer to the pin.
        name() -> str: Get the name of the pin.
        is_output() -> bool: Check if the pin is an output pin.
        node() -> Node: Get the node to which the pin belongs.
        paint(painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: Optional[QtWidgets.QWidget]) -> None: Paint the pin.
        clear_connection() -> None: Clear the connection attached to the pin.
        can_connect_to(pin: Pin) -> bool: Check if the pin can be connected to another pin.
        is_connected() -> bool: Check if the pin is connected to another pin.
        itemChange(change: QtWidgets.QGraphicsItem.GraphicsItemChange, value: Any) -> Any: Handle item change events.
    """

    def __init__(self, parent, scene):
        super().__init__(parent)

        self.radius_ = 5
        self.margin = 2

        self.execution = False

        path = QtGui.QPainterPath()

        path.addEllipse(-self.radius_, -self.radius_, 2 * self.radius_, 2 * self.radius_)

        self.setPath(path)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemSendsScenePositionChanges)
        self.font = QtGui.QFont()
        self.font_metrics = QtGui.QFontMetrics(self.font)

        self.pin_text_height = self.font_metrics.height()

        self._is_output = False
        self._name = None
        self.margin = 2

        self.m_node = None
        self.connection = None

        self.text_path = QtGui.QPainterPath()

    def is_execution(self):
        return self.execution

    def set_execution(self, execution):
        self.execution = execution

        if execution:
            path = QtGui.QPainterPath()

            points = []
            points.append(QtCore.QPointF(-6, -7))
            points.append(QtCore.QPointF(-6, 7))
            points.append(QtCore.QPointF(-2, 7))
            points.append(QtCore.QPointF(6, 0))
            points.append(QtCore.QPointF(-2, -7))
            points.append(QtCore.QPointF(-6, -7))
            path.addPolygon(QtGui.QPolygonF(points))
            self.setPath(path)

    def set_is_output(self, is_output):
        self._is_output = is_output

    def set_name(self, name):
        self._name = name
        nice_name = self._name.replace("_", " ").title()
        self.pin_text_width = self.font_metrics.horizontalAdvance(nice_name)

        if self._is_output:
            x = -self.radius_ - self.margin - self.pin_text_width
        else:
            x = self.radius_ + self.margin

        y = self.pin_text_height / 4

        self.text_path.addText(x, y, self.font, nice_name)

    def set_node(self, node):
        self.m_node = node

    def name(self):
        return self._name

    def is_output(self):
        return self._is_output

    def node(self):
        return self.m_node

    def paint(self, painter, option=None, widget=None):
        if self.execution:
            painter.setPen(QtCore.Qt.white)
        else:
            painter.setPen(QtCore.Qt.green)

        if self.is_connected():
            if self.execution:
                painter.setBrush(QtCore.Qt.white)
            else:
                painter.setBrush(QtCore.Qt.green)

        else:
            painter.setBrush(QtCore.Qt.NoBrush)

        painter.drawPath(self.path())

        # Draw text

        if not self.execution:
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtCore.Qt.white)
            painter.drawPath(self.text_path)

    def clear_connection(self):
        if self.connection:
            self.connection.delete()

    def can_connect_to(self, pin):
        # print(pin.node(), self.node())
        if not pin:
            return False
        if pin.node() == self.node():
            return False

        return self._is_output != pin._is_output

    def is_connected(self):
        return bool(self.connection)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemScenePositionHasChanged and self.connection:
            self.connection.update_start_and_end_pos()

        return value
