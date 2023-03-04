from PySide6 import QtWidgets, QtCore, QtGui


class NodeList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(NodeList, self).__init__(parent)

        for node in ["Input", "Output", "And", "Not", "Nor", "Empty"]:
            item = QtWidgets.QListWidgetItem(node)
            self.addItem(item)

        self.setDragEnabled(True)  # enable dragging

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        pos = event.pos()

        # actions
        delete_node = QtGui.QAction("Delete Node")
        edit_node = QtGui.QAction("Edit Node")
        menu.addAction(delete_node)

        action = menu.exec_(self.mapToGlobal(pos))

        if action == delete_node:
            item_name = self.selectedItems()[0].text()

            if item_name not in ["And", "Not", "Input", "Output Signal/Slot"]:
                print(f"delete node: {item_name}")
            else:
                print("Cannot delete default nodes")

        elif action == edit_node:
            print("editing node")

            # confirm to open in the editor replacing what is existing

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item and item.text():
            name = item.text()

            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(name)
            drag.setMimeData(mime_data)

            # Drag needs a pixmap or else it'll error due to a null pixmap
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtGui.QColor("darkgray"))
            drag.setPixmap(pixmap)
            drag.exec_()

            super(NodeList, self).mousePressEvent(event)
