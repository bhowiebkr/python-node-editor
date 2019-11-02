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

        for item in items:
            return item

            if item.type() > QtWidgets.QGraphicsItem.UserType:
                return item

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
                    self.connection.set_port_1(item)
                    self.connection.set_pos_1(item.scenePos())
                    self.connection.set_pos_2(event.scenePos())
                    self.connection.update_path()
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
                pass

        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Delete:

                for item in self.scene.selectedItems():
                    if item.type() == Connection.Type:
                        item.delete()
                    elif item.type() == Node.Type:
                        item.delete()
                return True

        elif event.type() == QtCore.QEvent.GraphicsSceneMouseMove:
            if self.connection:
                self.connection.set_pos_2(event.scenePos())
                self.connection.update_path()
                return True

        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease:
            if self.connection and event.button() == QtCore.Qt.LeftButton:
                item = self.item_at(event.scenePos())
                if isinstance(item, Port):
                    # if item and item.type() == Port.Type:
                    port1 = self.connection.port1()
                    port2 = item

                    if (
                        port1.node() != port2.node()
                        and port1.is_output() != port2.is_output()
                        and not port1.is_connected(port2)
                    ):
                        self.connection.set_pos_2(port2.scenePos())
                        self.connection.set_port_2(port2)
                        self.connection.update_path()
                        self.connection = None
                        return True

                self.connection.delete()
                self.connection = None
                return True

        return super(NodeEditor, self).eventFilter(watched, event)
