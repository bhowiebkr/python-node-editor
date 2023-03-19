from PySide6 import QtCore, QtGui, QtWidgets


class Connection(QtWidgets.QGraphicsPathItem):
    """
    A Connection represents a graphical connection between two NodePorts in a PySide6 application.

    Attributes:
    start_port (NodePort): The NodePort where the connection starts.
    end_port (NodePort): The NodePort where the connection ends.
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
    conn.start_port = start_port
    conn.end_port = end_port
    conn.update_start_and_end_pos()
    conn.update_path()
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)

        self.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
        self.setBrush(QtCore.Qt.NoBrush)
        self.setZValue(-1)

        self._start_port = None
        self._end_port = None

        self.start_pos = QtCore.QPointF()
        self.end_pos = QtCore.QPointF()

        self._do_highlight = False

    def delete(self):
        """
        Deletes the connection and removes it from the scene and any connected ports.
        """
        for port in (self._start_port, self._end_port):
            if port:
                # port.remove_connection(self)
                port.connection = None
            port = None

        self.scene().removeItem(self)

    @property
    def start_port(self):
        return self._start_port

    @property
    def end_port(self):
        return self._end_port

    @start_port.setter
    def start_port(self, port):
        self._start_port = port
        self._start_port.connection = self

    @end_port.setter
    def end_port(self, port):
        self._end_port = port
        self._end_port.connection = self

    def nodes(self):
        """
        Returns a tuple of the two connected nodes.

        Returns:
        tuple: A tuple of the two Node objects connected by this Connection.
        """
        return (self._start_port().node(), self._end_port().node())

    def update_start_and_end_pos(self):
        """
        Update the start and end positions of the Connection.

        Get the start and end ports and use them to set the start and end positions.
        """

        if self.start_port and not self.start_port.is_output():
            print("flipping connection")
            temp = self.end_port
            self._end_port = self.start_port
            self._start_port = temp

        if self._start_port:
            self.start_pos = self._start_port.scenePos()

        # if we are pulling off an exiting connection we skip code below
        if self._end_port:
            self.end_pos = self._end_port.scenePos()

        self.update_path()

    def update_path(self):
        """
        Draws a smooth cubic curve from the start to end ports.
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
        if self.isSelected() or self._do_highlight:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 102, 0), 3))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 128, 255), 2))

        painter.drawPath(self.path())
