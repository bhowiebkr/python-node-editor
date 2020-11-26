from PySide2 import QtWidgets, QtGui, QtCore


class Port(QtWidgets.QGraphicsPathItem):
    def __init__(self, parent, scene):
        super(Port, self).__init__(parent)

        self.radius_ = 5
        self.margin = 2

        path = QtGui.QPainterPath()
        path.addEllipse(
            -self.radius_, -self.radius_, 2 * self.radius_, 2 * self.radius_
        )
        self.setPath(path)

        self.setFlag(QtWidgets.QGraphicsPathItem.ItemSendsScenePositionChanges)
        self.font = QtGui.QFont()
        self.font_metrics = QtGui.QFontMetrics(self.font)

        self.port_text_height = self.font_metrics.height()

        self.is_output_ = False
        self._name = None
        self.margin = 2

        self.m_node = None
        self.m_connections = []

        self.text_path = QtGui.QPainterPath()

    def set_is_output(self, is_output):
        self.is_output_ = is_output

    def set_name(self, name):
        self._name = name
        nice_name = self._name.replace("_", " ").title()
        self.port_text_width = self.font_metrics.width(nice_name)

        if self.is_output_:
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
        return self.is_output_

    def node(self):
        return self.m_node

    def paint(self, painter, option=None, widget=None):
        painter.setPen(QtGui.QPen(1))
        painter.setBrush(QtCore.Qt.green)
        painter.drawPath(self.path())

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.white)
        painter.drawPath(self.text_path)

    def add_connection(self, connection):
        self.m_connections.append(connection)

    def remove_connection(self, connection):
        try:
            self.m_connections.remove(connection)
        except:
            pass

    def connections(self):
        return self.m_connections

    def is_connected(self, other):
        for connection in self.m_connections:
            if connection.start_port == other or connection.end_port == other:
                return True
        return False

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemScenePositionHasChanged:
            for connection in self.m_connections:
                connection.update_start_and_end_pos()

        return value
