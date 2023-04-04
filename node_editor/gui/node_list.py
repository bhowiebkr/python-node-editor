from PySide6 import QtCore, QtGui, QtWidgets
import sys
import importlib
import inspect


class NodeList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)  # enable dragging

    def update_project_path(self, project_path):
        print("project path updated")
        for file in project_path.glob("*.py"):
            print(f"File: {file.stem}")
            spec = importlib.util.spec_from_file_location(file.stem, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            item = QtWidgets.QListWidgetItem(file.stem)
            item.module = module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj):
                    item.class_name = obj
                    break
            self.addItem(item)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item and item.text():
            name = item.text()

            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            mime_data.setText(name)
            mime_data.item = item
            drag.setMimeData(mime_data)

            # Drag needs a pixmap or else it'll error due to a null pixmap
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtGui.QColor("darkgray"))
            drag.setPixmap(pixmap)
            drag.exec_()

            super().mousePressEvent(event)
