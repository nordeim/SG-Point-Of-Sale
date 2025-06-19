# File: app/ui/widgets/managed_table_view.py
"""
A custom widget that manages the display state of a QTableView,
providing user-friendly loading and empty-state messages.
"""
from __future__ import annotations
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QLabel, QStackedLayout, QSizePolicy
)
from PySide6.QtCore import Qt, QAbstractItemModel

class ManagedTableView(QWidget):
    """
    A container widget that wraps a QTableView and provides methods to switch
    between a loading state, an empty state, and the table view itself.
    This promotes a consistent user experience for all data tables.
    """
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._table_view = QTableView()
        self._loading_widget = self._create_state_widget("Loading data, please wait...")
        self._empty_widget = self._create_state_widget("No data available.")

        self._stacked_layout = QStackedLayout()
        self._stacked_layout.addWidget(self._loading_widget)
        self._stacked_layout.addWidget(self._empty_widget)
        self._stacked_layout.addWidget(self._table_view)

        self.setLayout(self._stacked_layout)
        self.show_loading()

    def _create_state_widget(self, default_text: str) -> QWidget:
        """Creates a standardized, centered widget for displaying state messages."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addStretch()
        
        label = QLabel(default_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("QLabel { color: #888; font-size: 16px; }")
        
        layout.addWidget(label)
        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def table(self) -> QTableView:
        """
        Provides direct access to the underlying QTableView instance for configuration
        (e.g., setting selection behavior, connecting signals).
        """
        return self._table_view

    def set_model(self, model: QAbstractItemModel) -> None:
        """Sets the data model for the underlying table view."""
        self._table_view.setModel(model)

    def show_loading(self) -> None:
        """Switches the view to show the loading indicator."""
        self._stacked_layout.setCurrentWidget(self._loading_widget)

    def show_empty(self, message: str = "No data to display.") -> None:
        """
        Switches the view to show the empty-state message.
        
        Args:
            message: The specific message to display (e.g., "No products found.").
        """
        # Find the QLabel within the empty_widget to update its text
        label = self._empty_widget.findChild(QLabel)
        if label:
            label.setText(message)
        self._stacked_layout.setCurrentWidget(self._empty_widget)

    def show_table(self) -> None:
        """Switches the view to show the data table."""
        self._stacked_layout.setCurrentWidget(self._table_view)
