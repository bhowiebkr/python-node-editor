from PySide6 import QtCore, QtGui, QtWidgets


class NodeList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        for node in ["Input", "Output", "And", "Not", "Nor", "Empty"]:
            item = QtWidgets.QListWidgetItem(node)
            self.addItem(item)

        self.setDragEnabled(True)  # enable dragging

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

            super().mousePressEvent(event)
