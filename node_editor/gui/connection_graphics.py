from PySide6 import QtCore, QtGui, QtWidgets


class Connection_Graphics(QtWidgets.QGraphicsPathItem):
    """
    A Connection represents a graphical connection between two NodePorts in a PySide6 application.

    Attributes:
    start_pin (NodePort): The NodePort where the connection starts.
    end_pin (NodePort): The NodePort where the connection ends.
    start_pos (QPointF): The starting position of the connection.
    end_pos (QPointF): The ending position of the connection.

    Methods:
    delete(): Deletes the connection.
    nodes(): Returns a tuple of the two connected nodes.
    update_start_and_end_pos(): Updates the starting and ending positions of the connection.
    update_path(): Draws a smooth cubic curve from the starting to ending position of the connection.
    paint(painter, option=None, widget=None): Override the default paint method depending on if the object is selected.

    Example:
    conn = Connection(parent)
    conn.start_pin = start_pin
    conn.end_pin = end_pin
    conn.update_start_and_end_pos()
    conn.update_path()
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)

        self.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
        self.setBrush(QtCore.Qt.NoBrush)
        self.setZValue(-1)

        self.start_pos = QtCore.QPointF()
        self.end_pos = QtCore.QPointF()
        self.start_pin = None
        self.end_pin = None

        self._do_highlight = False

    def update_path(self):
        """
        Draws a smooth cubic curve from the start to end pins.
        """
        path = QtGui.QPainterPath()
        path.moveTo(self.start_pos)

        dx = self.end_pos.x() - self.start_pos.x()
        dy = self.end_pos.y() - self.start_pos.y()

        ctr1 = QtCore.QPointF(self.start_pos.x() + dx * 0.5, self.start_pos.y())
        ctr2 = QtCore.QPointF(self.start_pos.x() + dx * 0.5, self.start_pos.y() + dy)
        path.cubicTo(ctr1, ctr2, self.end_pos)

        self.setPath(path)

    def paint(self, painter, option=None, widget=None):
        """
        Override the default paint method depending on if the object is selected.

        Args:
        painter (QPainter): The QPainter object used to paint the Connection.
        option (QStyleOptionGraphicsItem): The style options for the Connection.
        widget (QWidget): The widget used to paint the Connection.
        """

        thickness = 0
        color = QtGui.QColor(0, 128, 255)
        if self.start_pin:
            if self.start_pin.execution:
                thickness = 3
                color = QtGui.QColor(255, 255, 255)

        if self.isSelected() or self._do_highlight:
            painter.setPen(QtGui.QPen(color.lighter(), thickness + 2))
        else:
            painter.setPen(QtGui.QPen(color, thickness))

        painter.drawPath(self.path())
