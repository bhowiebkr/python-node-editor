from PySide6 import QtCore, QtGui, QtOpenGLWidgets, QtWidgets

from node_editor.node import Node


class View(QtWidgets.QGraphicsView):
    """
    View class for node editor.
    """

    _background_color = QtGui.QColor(38, 38, 38)

    _grid_pen_s = QtGui.QPen(QtGui.QColor(52, 52, 52, 255), 0.5)
    _grid_pen_l = QtGui.QPen(QtGui.QColor(22, 22, 22, 255), 1.0)

    _grid_size_fine = 15
    _grid_size_course = 150

    _mouse_wheel_zoom_rate = 0.0015

    request_node = QtCore.Signal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self._manipulationMode = 0

        gl_format = QtGui.QSurfaceFormat()
        gl_format.setSamples(10)
        QtGui.QSurfaceFormat.setDefaultFormat(gl_format)
        gl_widget = QtOpenGLWidgets.QOpenGLWidget()

        self.currentScale = 1
        self._pan = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        self._numScheduledScalings = 0
        self.lastMousePos = QtCore.QPoint()

        self.setViewport(gl_widget)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def wheelEvent(self, event):
        """
        Handles the wheel events, e.g. zoom in/out.

        :param event: Wheel event.
        """
        # sometimes you can triger the wheen when panning so we disable when panning
        if self._pan:
            return

        num_degrees = event.angleDelta() / 8.0
        num_steps = num_degrees.y() / 5.0
        self._numScheduledScalings += num_steps

        # If the user moved the wheel another direction, we reset previously scheduled scalings
        if self._numScheduledScalings * num_steps < 0:
            self._numScheduledScalings = num_steps

        self.anim = QtCore.QTimeLine(350)
        self.anim.setUpdateInterval(20)

        self.anim.valueChanged.connect(self.scaling_time)
        self.anim.finished.connect(self.anim_finished)
        self.anim.start()

    def scaling_time(self, x):
        """
        Updates the current scale based on the wheel events.

        :param x: The value of the current time.
        """
        factor = 1.0 + self._numScheduledScalings / 300.0

        self.currentScale *= factor

        self.scale(factor, factor)

    def anim_finished(self):
        """
        Called when the zoom animation is finished.
        """
        if self._numScheduledScalings > 0:
            self._numScheduledScalings -= 1
        else:
            self._numScheduledScalings += 1

    def drawBackground(self, painter, rect):
        """
        Draws the background for the node editor view.

        :param painter: The painter to draw with.
        :param rect: The rectangle to be drawn.
        """
        painter.fillRect(rect, self._background_color)

        left = int(rect.left()) - (int(rect.left()) % self._grid_size_fine)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size_fine)

        # Draw horizontal fine lines
        gridLines = []
        painter.setPen(self._grid_pen_s)
        y = float(top)
        while y < float(rect.bottom()):
            gridLines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size_fine
        painter.drawLines(gridLines)

        # Draw vertical fine lines
        gridLines = []
        painter.setPen(self._grid_pen_s)
        x = float(left)
        while x < float(rect.right()):
            gridLines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size_fine
        painter.drawLines(gridLines)

        # Draw thick grid
        left = int(rect.left()) - (int(rect.left()) % self._grid_size_course)
        top = int(rect.top()) - (int(rect.top()) % self._grid_size_course)

        # Draw vertical thick lines
        gridLines = []
        painter.setPen(self._grid_pen_l)
        x = left
        while x < rect.right():
            gridLines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
            x += self._grid_size_course
        painter.drawLines(gridLines)

        # Draw horizontal thick lines
        gridLines = []
        painter.setPen(self._grid_pen_l)
        y = top
        while y < rect.bottom():
            gridLines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
            y += self._grid_size_course
        painter.drawLines(gridLines)

        return super().drawBackground(painter, rect)

    def contextMenuEvent(self, event):
        """
        This method is called when a context menu event is triggered in the view. It finds the item at the event position and
        shows a context menu if the item is a Node.
        """
        cursor = QtGui.QCursor()
        # origin = self.mapFromGlobal(cursor.pos())
        pos = self.mapFromGlobal(cursor.pos())
        item = self.itemAt(event.pos())

        if item:
            if isinstance(item, Node):
                print("Found Node", item)

                menu = QtWidgets.QMenu(self)

                # hello_action = QtWidgets.QAction("Hello", self)

                # menu.addAction(hello_action)
                # action = menu.exec_(self.mapToGlobal(pos))

                # if action == hello_action:
                #    print("Hello")

    def dragEnterEvent(self, e):
        """
        This method is called when a drag and drop event enters the view. It checks if the mime data format is "text/plain"
        and accepts or ignores the event accordingly.
        """
        if e.mimeData().hasFormat("text/plain"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        This method is called when a drag and drop event is dropped onto the view. It retrieves the name of the dropped node
        from the mime data and emits a signal to request the creation of the corresponding node.
        """
        node = e.mimeData().item.class_name
        self.request_node.emit(node())

    def mousePressEvent(self, event):
        """
        This method is called when a mouse press event occurs in the view. It sets the cursor to a closed hand cursor and
        enables panning if the middle mouse button is pressed.
        """
        if event.button() == QtCore.Qt.MiddleButton:
            self._pan = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(QtCore.Qt.ClosedHandCursor)

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        This method is called when a mouse release event occurs in the view. It sets the cursor back to the arrow cursor and
        disables panning if the middle mouse button is released.
        """
        if event.button() == QtCore.Qt.MiddleButton:
            self._pan = False
            self.setCursor(QtCore.Qt.ArrowCursor)

        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """
        This method is called when a mouse move event occurs in the view. It pans the view if the middle mouse button is
        pressed and moves the mouse.
        """
        if self._pan:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - (event.x() - self._pan_start_x))

            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - (event.y() - self._pan_start_y))

            self._pan_start_x = event.x()
            self._pan_start_y = event.y()

        return super().mouseMoveEvent(event)
