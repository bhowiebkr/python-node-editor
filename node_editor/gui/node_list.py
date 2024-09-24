from __future__ import annotations

from types import ModuleType
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class CustomQListWidgetItem(QtWidgets.QListWidgetItem):  # type: ignore
    module: Any
    class_name: Any


class CustomQMimeData(QtCore.QMimeData):  # type: ignore
    item: CustomQListWidgetItem


class ImportData:
    def __init__(self, module: str, class_: str):
        self.module: Any = module
        self.class_: Any = class_


# class NodeList(QtWidgets.QListWidget):  # type: ignore
#    module: str
#    class_: str


class NodeList(QtWidgets.QListWidget):  # type: ignore
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)  # enable dragging

    def update_project(self, imports: Dict[str, Dict[str, Union[type, ModuleType]]]) -> None:

        # make an item for each custom class
        for name, data in imports.items():
            name = name.replace("_Node", "")

            item = CustomQListWidgetItem(name)

            item.module = data["module"]
            item.class_name = data["class"]
            self.addItem(item)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        item = self.itemAt(event.pos())

        if isinstance(item, CustomQListWidgetItem) and item.text():
            name = item.text()

            drag = QtGui.QDrag(self)
            mime_data = CustomQMimeData()
            mime_data.setText(name)
            mime_data.item = item
            drag.setMimeData(mime_data)

            # Drag needs a pixmap or else it'll error due to a null pixmap
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtGui.QColor("darkgray"))
            drag.setPixmap(pixmap)
            drag.exec_()

            print("Inside drag event from node list")

            super().mousePressEvent(event)
