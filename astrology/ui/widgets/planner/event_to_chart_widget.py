"""
Purpose: Widget for sending events to the chart maker.

This file is part of the astrology pillar and serves as a UI component.
It provides functionality to send events from the planner to the chart maker.
"""

from datetime import datetime

from loguru import logger
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from astrology.models.chart import Chart
from astrology.services.planner_service import PlannerService
from astrology.ui.dialogs.location_search_window import LocationSearchWindow


class EventToChartDialog(QDialog):
    """Dialog for sending events to the chart maker."""

    # Signal emitted when a chart is created
    chart_created = pyqtSignal(Chart)

    def __init__(self, date: QDate, parent=None):
        """Initialize the dialog.

        Args:
            date: Date to get events for
            parent: Parent widget
        """
        super().__init__(parent)

        self.date = date

        # Get the planner service
        self.planner_service = PlannerService.get_instance()

        # Initialize UI
        self._init_ui()

        # Load events
        self._load_events()

        logger.debug(f"EventToChartDialog initialized for {date.toString()}")

    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle(
            f"Send Event to Chart - {self.date.toString('MMMM d, yyyy')}"
        )
        self.resize(400, 300)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel("Select an event to create a chart for:")
        instructions.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        main_layout.addWidget(instructions)

        # Events list
        self.events_list = QListWidget()
        self.events_list.setAlternatingRowColors(True)
        main_layout.addWidget(self.events_list)

        # Buttons
        button_layout = QHBoxLayout()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Create Chart button
        self.create_button = QPushButton("Create Chart")
        self.create_button.clicked.connect(self._create_chart)
        self.create_button.setEnabled(False)
        button_layout.addWidget(self.create_button)

        main_layout.addLayout(button_layout)

    def _load_events(self):
        """Load events for the selected date."""
        # Get events for the date
        date = datetime(self.date.year(), self.date.month(), self.date.day()).date()
        events = self.planner_service.get_events_for_date(date)

        # Add events to list
        for event in events:
            item = QListWidgetItem(
                f"{event.start_time.strftime('%I:%M %p')} - {event.title}"
            )
            item.setData(Qt.ItemDataRole.UserRole, event)

            # Set background color based on event color
            item.setBackground(QColor(event.color))

            # Set text color to white or black depending on background brightness
            color = QColor(event.color)
            brightness = (
                color.red() * 299 + color.green() * 587 + color.blue() * 114
            ) / 1000
            if brightness > 128:
                item.setForeground(QColor(0, 0, 0))
            else:
                item.setForeground(QColor(255, 255, 255))

            self.events_list.addItem(item)

        # Connect selection changed signal
        self.events_list.itemSelectionChanged.connect(self._on_selection_changed)

        # Show message if no events
        if not events:
            self.events_list.addItem("No events for this date")

    def _on_selection_changed(self):
        """Handle selection changes in the events list."""
        # Enable/disable create button based on selection
        self.create_button.setEnabled(len(self.events_list.selectedItems()) > 0)

    def _create_chart(self):
        """Create a chart for the selected event."""
        # Get selected item
        selected_items = self.events_list.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]

        # Get event from item
        event = selected_item.data(Qt.ItemDataRole.UserRole)
        if not event:
            return

        # Get settings
        settings = self.planner_service.get_settings()

        # Check if default location is set
        if not settings.default_location:
            # Ask if user wants to select a location
            response = QMessageBox.question(
                self,
                "No Default Location",
                "No default location is set. Would you like to select a location now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )

            if response == QMessageBox.StandardButton.Yes:
                # Show location search window
                self._select_location(event)

            return

        # Ask if user wants to use default location or select a new one
        response = QMessageBox.question(
            self,
            "Location Selection",
            f"Use default location ({settings.default_location.display_name}) or select a new one?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if response == QMessageBox.StandardButton.No:
            # Show location search window
            self._select_location(event)
            return

        # Create chart for the event with default location
        chart = self.planner_service.send_event_to_chart_maker(
            event=event, location=settings.default_location
        )

        # Emit signal with the chart
        self.chart_created.emit(chart)

        # Close dialog
        self.accept()

    def _select_location(self, event):
        """Select a location for the chart.

        Args:
            event: Event to create chart for
        """
        # Create location search window
        location_window = LocationSearchWindow(self)

        # Connect location selected signal
        def on_location_selected(location):
            # Create chart for the event
            chart = self.planner_service.send_event_to_chart_maker(
                event=event, location=location
            )

            # Emit signal with the chart
            self.chart_created.emit(chart)

            # Close the location window
            location_window.close()

            # Close this dialog
            self.accept()

        # Connect signal
        location_window.location_search_widget.location_selected.connect(
            on_location_selected
        )

        # Show window
        location_window.show()
