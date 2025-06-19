# File: app/ui/widgets/kpi_widget.py
"""
A custom QFrame widget to display a single Key Performance Indicator (KPI).
"""
from __future__ import annotations
from typing import Optional

from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class KpiWidget(QFrame):
    """
    A styled frame that displays a title and a large value, representing a KPI.
    """
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setMinimumSize(200, 120)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(5)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet("font-size: 16px; color: #555;")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._value_label = QLabel("...")
        self._value_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #1E90FF;")
        self.set_value_color("#1E90FF") # Default color
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self._title_label)
        main_layout.addStretch()
        main_layout.addWidget(self._value_label)

    def set_kpi_value(self, value: str) -> None:
        """Sets the main display value of the KPI widget."""
        self._value_label.setText(value)

    def set_value_color(self, color_hex: str) -> None:
        """Allows customizing the color of the KPI value text."""
        self._value_label.setStyleSheet(
            f"font-size: 36px; font-weight: bold; color: {color_hex};"
        )
