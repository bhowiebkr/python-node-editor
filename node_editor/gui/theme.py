"""The dark colors of the editor."""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

COLORS = {
    QPalette.ColorRole.Window: QColor(43, 43, 43),
    QPalette.ColorRole.WindowText: QColor(220, 220, 220),
    QPalette.ColorRole.Base: QColor(49, 51, 53),
    QPalette.ColorRole.AlternateBase: QColor(60, 63, 65),
    QPalette.ColorRole.Text: QColor(220, 220, 220),
    QPalette.ColorRole.Button: QColor(60, 63, 65),
    QPalette.ColorRole.ButtonText: QColor(220, 220, 220),
    QPalette.ColorRole.ToolTipBase: QColor(49, 51, 53),
    QPalette.ColorRole.ToolTipText: QColor(220, 220, 220),
    QPalette.ColorRole.Highlight: QColor(42, 130, 218),
    QPalette.ColorRole.HighlightedText: QColor(255, 255, 255),
}

# A Qt style sheet works like CSS. "#Name" finds the widget with that object name.
STYLE_SHEET = """
#ToolBar {
    background: #1f1f1f;
    border: none;
    border-bottom: 1px solid #141414;
    padding: 4px;
    spacing: 6px;
}
#ToolBar QToolButton {
    background: transparent;
    border: none;
    padding: 4px 12px;
    border-radius: 4px;
}
#ToolBar QToolButton:hover {
    background: #3a3a3a;
}
#ToolBar QToolButton::menu-indicator {
    image: none;
}
#ToolBar #RunButton {
    background: #2e7d32;
    color: white;
    font-weight: bold;
}
#ToolBar #RunButton:hover {
    background: #388e3c;
}
#ToolBar #RunButton:pressed {
    background: #1b5e20;
}
QMenu {
    border: 1px solid #141414;
    padding: 4px 0;
}
#Message {
    color: #a0a0a0;
    padding-right: 8px;
}
#LeftPanel {
    background: #1f1f1f;
}
#PanelTitle {
    font-size: 11pt;
    font-weight: bold;
    padding: 12px 12px 0 12px;
}
#PanelHint {
    color: #8c8c8c;
    padding: 2px 12px 8px 12px;
}
#NodeList {
    background: transparent;
    border: none;
    outline: none;
    padding: 0 6px;
}
#NodeList::item {
    padding: 4px 6px;
    border-radius: 4px;
}
#NodeList::item:selected {
    background: #2a82da;
}
QSplitter::handle {
    background: #141414;
}
QSplitter::handle:horizontal {
    width: 3px;
}
"""


def apply_dark_theme(app: QApplication) -> None:
    """Use the Fusion style with dark colors, and the style sheet.

    Fusion looks the same on Windows, macOS and Linux. The palette also gives dark colors
    to the widgets inside the nodes.
    """
    app.setStyle("Fusion")
    palette = QPalette()
    for role, color in COLORS.items():
        palette.setColor(role, color)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    app.setPalette(palette)
    app.setStyleSheet(STYLE_SHEET)
