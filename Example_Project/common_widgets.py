from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6.QtCore import Qt

class FloatLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(FloatValidator())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            event.ignore()
        else:
            super().keyPressEvent(event)

class FloatValidator(QtGui.QDoubleValidator):
    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, input_str, pos):
        state, num, pos = super().validate(input_str, pos)
        if state == QtGui.QValidator.Acceptable:
            return QtGui.QValidator.Acceptable, num, pos
        if str(num).count('.') > 1:
            return QtGui.QValidator.Invalid, num, pos
        if input_str[pos-1] == '.':
            return QtGui.QValidator.Acceptable, num, pos
        return QtGui.QValidator.Invalid, num, pos