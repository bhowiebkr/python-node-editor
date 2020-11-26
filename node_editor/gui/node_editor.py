from PySide2 import QtWidgets, QtCore

from node_editor.gui.connection import Connection
from node_editor.gui.node import Node
from node_editor.gui.port import Port


class NodeEditor(QtCore.QObject):
    def __init__(self, parent):
        super(NodeEditor, self).__init__(parent)
        self.connection = None
        self.scene = None
        self._last_selected = None

    def install(self, scene):
        self.scene = scene
        self.scene.installEventFilter(self)

    def item_at(self, position):
        items = self.scene.items(
            QtCore.QRectF(position - QtCore.QPointF(1, 1), QtCore.QSizeF(3, 3))
        )

        if items:
            return items[0]
        return None

    def eventFilter(self, watched, event):
        if type(event) == QtWidgets.QWidgetItem:
            return False

        if event.type() == QtCore.QEvent.GraphicsSceneMousePress:

            if event.button() == QtCore.Qt.LeftButton:
                item = self.item_at(event.scenePos())

                if isinstance(item, Port):
                    self.connection = Connection(None)
                    self.scene.addItem(self.connection)
                    self.connection.start_port = item
                    self.connection.start_pos = item.scenePos()
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_path()
                    return True

                elif isinstance(item, Connection):
                    self.connection = Connection(None)
                    self.scene.addItem(self.connection)
                    self.connection.start_port = item.start_port
                    self.connection.end_pos = event.scenePos()
                    self.connection.update_start_and_end_pos()  # to fix the offset
                    return True

                elif isinstance(item, Node):
                    if self._last_selected:
                        # If we clear the scene, we loose the last selection
                        try:
                            self._last_selected.select_connections(False)
                        except RuntimeError:
                            pass

                    item.select_connections(True)
                    self._last_selected = item

                else:
                    try:
                        if self._last_selected:
                            self._last_selected.select_connections(False)
                    except RuntimeError:
                        pass

                    self._last_selected = None

            elif event.button() == QtCore.Qt.RightButton:
                # context menu
                pass

        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:

                for item in self.scene.selectedItems():

                    if isinstance(item, (Connection, Node)):
                        item.delete()

                return True

        elif event.type() == QtCore.QEvent.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.end_pos = event.scenePos()
                self.connection.update_path()
                return True

        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            if self.connection and event.button() == QtCore.Qt.LeftButton:
                item = self.item_at(event.scenePos())
                if isinstance(item, Port):
                    start_port = self.connection.start_port
                    end_port = item

                    if (
                        start_port.node() != end_port.node()
                        and start_port.is_output() != end_port.is_output()
                        and not start_port.is_connected(end_port)
                    ):
                        self.connection.end_port = end_port

                        self.connection.update_start_and_end_pos()
                        self.connection = None

                        # # Flip them aroud if wired the wrong way
                        # if not self.connection.start_port.is_output():
                        #     self.connection.flip_connections()

                        return True

                self.connection.delete()
                self.connection = None
                return True

        return super(NodeEditor, self).eventFilter(watched, event)
