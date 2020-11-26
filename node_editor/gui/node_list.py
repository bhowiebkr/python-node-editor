from PySide2 import QtWidgets, QtCore, QtGui


class NodeList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(NodeList, self).__init__(parent)

        self.addItem("Input")
        self.addItem("Output")
        self.addItem("And")
        self.addItem("Not")
        self.addItem("Nor")

        self.setDragEnabled(True)  # enable dragging

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        pos = event.pos()

        # actions
        delete_node = QtWidgets.QAction("Delete Node")
        edit_node = QtWidgets.QAction("Edit Node")
        menu.addAction(delete_node)

        action = menu.exec_(self.mapToGlobal(pos))

        if action == delete_node:
            item_name = self.selectedItems()[0].text()

            if item_name not in ["And", "Not", "Input", "Output"]:
                print(f"delete node: {item_name}")
            else:
                print("Cannot delete default nodes")

        elif action == edit_node:
            print("editing node")

            # confirm to open in the editor replacing what is existing

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        name = item.text()

        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()

        mime_data.setText(name)
        drag.setMimeData(mime_data)
        drag.exec_()

        super(NodeList, self).mousePressEvent(event)
