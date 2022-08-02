from PySide6 import QtWidgets, QtGui, QtCore


class Connection(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent):
        super(Connection, self).__init__(parent)

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
        return (self._start_port().node(), self._end_port().node())

    def update_start_and_end_pos(self):
        """Update the ends of the connection

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
        """Draw a smooth cubic curve from the start to end ports
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
        Override the default paint method depending on if the object is selected
        """
        if self.isSelected() or self._do_highlight:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 102, 0), 3))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 128, 255), 2))

        painter.drawPath(self.path())

