from PySide2 import QtWidgets, QtGui, QtCore


class Connection(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent):
        super(Connection, self).__init__(parent)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)

        self.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
        self.setBrush(QtCore.Qt.NoBrush)
        self.setZValue(-1)

        self.m_port1 = None
        self.m_port2 = None

        self.pos1 = QtCore.QPointF()
        self.pos2 = QtCore.QPointF()

        self._do_highlight = False

    def __del__(self):
        """
        Skip this one
        :return:
        """
        pass

    def delete(self):
        """Delete the connection.
        Remove any found connections ports by calling :any:`Port.remove_connection`.  After connections
        have been removed set the stored :any:`Port` to None. Lastly call :any:`QGraphicsScene.removeItem`
        on the scene to remove this widget.
        """
        if self.m_port1:
            self.m_port1.remove_connection(self)
        if self.m_port2:
            self.m_port2.remove_connection(self)

        self.m_port1 = None
        self.m_port2 = None

        self.scene().removeItem(self)

    def set_pos_1(self, pos):
        """Set the start position of the connection by setting :py:attr:`Connection.pos1` value.

        :param pos: The position of the start point
        :type pos: QPointF
        """
        self.pos1 = pos

    def set_pos_2(self, pos):
        """Set the end position of the connection by setting :py:attr:`Connection.pos2` value.

        :param pos: The position of the end point
        :type pos: QPointF
        """
        self.pos2 = pos

    def set_port_1(self, port):
        """Set the start port and store it on this connection. After call the :any:`Port.add_connection` on that port.

        :param port: The start port
        :type port: Port
        """
        self.m_port1 = port
        self.m_port1.add_connection(self)

    def set_port_2(self, port):
        """Set the end port and store it on this connection. After call the :any:`Port.add_connection` on that port.

        :param port: The end port
        :type port: Port
        """
        self.m_port2 = port
        self.m_port2.add_connection(self)

    def update_pos_from_ports(self):
        """
        Update the position from the stored ports.

        Get the scene position of each stored :class:`.Port` and update the :py:attr:`Connection.pos1`
        and :py:attr:`Connection.pos2` attributes.
        """
        self.pos1 = self.m_port1.scenePos()

        # if we are pulling off an exiting connection we skip code below
        if self.m_port2:
            self.pos2 = self.m_port2.scenePos()

    def update_path(self):
        """
        Update the path line for the connection.

        Create a :class:`QPainterPath` and move it to the start position. Create a direct line to the end
        position. Use the base class method :class:`QGraphicsPathItem.setPath` to set this newly created path.

        .. note::
            Mike doesn't like smooth curves because he thinks they look ugly. LOL!

        .. todo::
            Look into creating elbow joints like found in Nuke to make Mike happy :)

        """
        path = QtGui.QPainterPath()
        path.moveTo(self.pos1)

        dx = self.pos2.x() - self.pos1.x()
        dy = self.pos2.y() - self.pos1.y()

        ctr1 = QtCore.QPointF(self.pos1.x() + dx * 0.5, self.pos1.y())
        ctr2 = QtCore.QPointF(self.pos1.x() + dx * 0.5, self.pos1.y() + dy)
        path.cubicTo(ctr1, ctr2, self.pos2)

        self.setPath(path)

    def port1(self):
        """
        Return the start :class:`.Port` associated with this :class:`Connection`.

        :return: The start port
        :rtype: Port
        """
        return self.m_port1

    def port2(self):
        """
        Return the end :class:`.Port` associated with this :class:`Connection`.

        :return: The end port
        :rtype: Port
        """
        return self.m_port2

    def nodes(self):
        return [self.port1().node(), self.port2().node()]

    def paint(self, painter, option=None, widget=None):
        """
        Override the default paint member from the base class to show color when the connection is selected.

        :param painter: The painter object
        :param option: Options that are not used
        :param widget: Widget that is not used
        :type painter: QPainter
        :type option: QStyleOptionGraphicsItem
        :type widget: QWidget
        """
        if self.isSelected() or self._do_highlight:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 102, 0), 3))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 128, 255), 2))

        painter.drawPath(self.path())
