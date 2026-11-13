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


def apply_dark_theme(app: QApplication) -> None:
    """Use the Fusion style with dark colors.

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
