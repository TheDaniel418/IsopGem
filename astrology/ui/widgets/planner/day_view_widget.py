"""
Purpose: Day view widget for the astrological planner.

This file is part of the astrology pillar and serves as a UI component.
It provides a day view with hourly breakdown and astrological events.
"""

from datetime import datetime
from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import QDate, Qt, QTime, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QTimeEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import Chart
from astrology.services.chart_service import ChartService
from astrology.services.planner_service import EventType, PlannerEvent, PlannerService
from astrology.ui.dialogs.location_search_window import LocationSearchWindow


class EventDialog(QDialog):
    """Dialog for creating/editing events."""

    def __init__(self, date: QDate, event: Optional[PlannerEvent] = None, parent=None):
        """Initialize the event dialog.

        Args:
            date: Date for the event
            event: Existing event to edit, or None for a new event
            parent: Parent widget
        """
        super().__init__(parent)

        self.date = date
        self.event = event

        # Set up UI
        self.setWindowTitle("Event Details")
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Title
        self.title_edit = QLineEdit()
        if event:
            self.title_edit.setText(event.title)
        form_layout.addRow("Title:", self.title_edit)

        # Time
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("hh:mm AP")
        if event:
            self.time_edit.setTime(
                QTime(event.start_time.hour, event.start_time.minute)
            )
        else:
            self.time_edit.setTime(QTime.currentTime())
        form_layout.addRow("Time:", self.time_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        if event:
            self.description_edit.setText(event.description)
        form_layout.addRow("Description:", self.description_edit)

        # Color
        self.color_combo = QComboBox()
        colors = [
            ("#3498db", "Blue"),
            ("#2ecc71", "Green"),
            ("#e74c3c", "Red"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Teal"),
            ("#34495e", "Dark Blue"),
            ("#7f8c8d", "Gray"),
        ]
        for color_code, color_name in colors:
            self.color_combo.addItem(color_name, color_code)

        if event:
            # Find the index of the event's color
            for i in range(self.color_combo.count()):
                if self.color_combo.itemData(i) == event.color:
                    self.color_combo.setCurrentIndex(i)
                    break

        form_layout.addRow("Color:", self.color_combo)

        # Repeat yearly
        self.repeat_check = QCheckBox("Repeat yearly")
        if event:
            self.repeat_check.setChecked(event.repeats_yearly)
        form_layout.addRow("", self.repeat_check)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

    def get_event(self) -> PlannerEvent:
        """Get the event from the dialog.

        Returns:
            PlannerEvent object
        """
        # Get values from form
        title = self.title_edit.text()
        time = self.time_edit.time()
        description = self.description_edit.toPlainText()
        color = self.color_combo.currentData()
        repeats_yearly = self.repeat_check.isChecked()

        # Create datetime
        start_time = datetime(
            self.date.year(),
            self.date.month(),
            self.date.day(),
            time.hour(),
            time.minute(),
        )

        # Create or update event
        if self.event:
            # Update existing event
            self.event.title = title
            self.event.start_time = start_time
            self.event.description = description
            self.event.color = color
            self.event.repeats_yearly = repeats_yearly
            return self.event
        else:
            # Create new event
            return PlannerEvent(
                title=title,
                description=description,
                event_type=EventType.USER_EVENT,
                start_time=start_time,
                color=color,
                repeats_yearly=repeats_yearly,
            )


class HourSection(QFrame):
    """Widget for a single hour in the day view."""

    # Signal emitted when a chart is requested for an event
    chart_requested = pyqtSignal(PlannerEvent)

    def __init__(self, hour: int, events: List[PlannerEvent] = None, parent=None):
        """Initialize the hour section.

        Args:
            hour: Hour of the day (0-23)
            events: List of events for this hour
            parent: Parent widget
        """
        super().__init__(parent)

        self.hour = hour
        self.events = events or []
        self.expanded = False

        # Set up UI
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumHeight(40)

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Header layout
        header_layout = QHBoxLayout()

        # Hour label
        hour_str = f"{hour:02d}:00 - {(hour+1) % 24:02d}:00"
        if hour < 12:
            am_pm = f"{hour if hour > 0 else 12}:00 AM - {(hour+1) if hour+1 < 12 else 12}:00 {'AM' if hour+1 < 12 else 'PM'}"
        else:
            am_pm = f"{hour-12 if hour > 12 else 12}:00 PM - {(hour+1-12) if hour+1 > 12 else 12}:00 {'PM' if hour+1 < 24 else 'AM'}"

        self.hour_label = QLabel(f"{hour_str} ({am_pm})")
        self.hour_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(self.hour_label)

        # Expand/collapse button
        self.expand_button = QToolButton()
        self.expand_button.setText("▼" if self.expanded else "▶")
        self.expand_button.clicked.connect(self._toggle_expanded)
        header_layout.addWidget(self.expand_button)

        self.layout.addLayout(header_layout)

        # Events container
        self.events_container = QFrame()
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_layout.setContentsMargins(10, 0, 0, 0)
        self.events_layout.setSpacing(5)

        # Add events
        self._add_events()

        # Initially hide events if not expanded
        self.events_container.setVisible(self.expanded)

        self.layout.addWidget(self.events_container)

    def _add_events(self):
        """Add events to the container."""
        # Sort events by start time
        sorted_events = sorted(self.events, key=lambda e: e.start_time)

        # Add each event
        for event in sorted_events:
            # Create event widget
            event_widget = QFrame()
            event_widget.setFrameShape(QFrame.Shape.StyledPanel)
            event_widget.setStyleSheet(
                f"background-color: {event.color}; color: white; border-radius: 5px;"
            )

            event_layout = QVBoxLayout(event_widget)
            event_layout.setContentsMargins(5, 5, 5, 5)
            event_layout.setSpacing(2)

            # Event time
            time_str = event.start_time.strftime("%I:%M %p")
            time_label = QLabel(time_str)
            time_label.setFont(QFont("Arial", 8))
            event_layout.addWidget(time_label)

            # Event title
            title_label = QLabel(event.title)
            title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            title_label.setWordWrap(True)
            event_layout.addWidget(title_label)

            # Event description (if any)
            if event.description:
                desc_label = QLabel(event.description)
                desc_label.setWordWrap(True)
                event_layout.addWidget(desc_label)

            # Add View Chart button
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 5, 0, 0)

            # Add stretch to push button to the right
            button_layout.addStretch()

            # Create View Chart button
            view_chart_button = QPushButton("View Chart")
            view_chart_button.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0.2); "
                "color: white; "
                "border: 1px solid white; "
                "border-radius: 3px; "
                "padding: 3px;"
            )
            view_chart_button.setFixedSize(80, 25)
            view_chart_button.setFont(QFont("Arial", 8))

            # Connect button to event
            view_chart_button.clicked.connect(
                lambda _, e=event: self.chart_requested.emit(e)
            )

            button_layout.addWidget(view_chart_button)
            event_layout.addLayout(button_layout)

            self.events_layout.addWidget(event_widget)

    def _toggle_expanded(self):
        """Toggle the expanded state."""
        self.expanded = not self.expanded
        self.expand_button.setText("▼" if self.expanded else "▶")
        self.events_container.setVisible(self.expanded)

    def set_expanded(self, expanded: bool):
        """Set the expanded state.

        Args:
            expanded: Whether to expand the section
        """
        if self.expanded != expanded:
            self._toggle_expanded()


class DayViewWidget(QWidget):
    """Widget for displaying a day view with hourly breakdown and astrological events."""

    # Signal emitted when the date changes
    date_changed = pyqtSignal(QDate)

    # Signal emitted when a chart is requested
    chart_requested = pyqtSignal(Chart)

    def __init__(self, parent=None):
        """Initialize the day view widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get the planner service
        self.planner_service = PlannerService.get_instance()

        # Get the chart service
        self.chart_service = ChartService.get_instance()

        # Current date
        self.current_date = QDate.currentDate()

        # Initialize UI
        self._init_ui()

        # Update view
        self._update_view()

        logger.debug("DayViewWidget initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Header with date and navigation
        header_layout = QHBoxLayout()

        # Previous day button
        self.prev_button = QPushButton("< Prev")
        self.prev_button.clicked.connect(self._previous_day)
        header_layout.addWidget(self.prev_button)

        # Date label
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.date_label, 1)

        # Next day button
        self.next_button = QPushButton("Next >")
        self.next_button.clicked.connect(self._next_day)
        header_layout.addWidget(self.next_button)

        main_layout.addLayout(header_layout)

        # Action buttons
        action_layout = QHBoxLayout()

        # View Chart button
        self.view_chart_button = QPushButton("View Chart")
        self.view_chart_button.clicked.connect(self._view_chart)
        action_layout.addWidget(self.view_chart_button)

        # Add Event button
        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self._add_event)
        action_layout.addWidget(self.add_event_button)

        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._show_settings)
        action_layout.addWidget(self.settings_button)

        main_layout.addLayout(action_layout)

        # Scroll area for hours
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container for hours
        self.hours_container = QWidget()
        self.hours_layout = QVBoxLayout(self.hours_container)
        self.hours_layout.setContentsMargins(0, 0, 0, 0)
        self.hours_layout.setSpacing(5)

        scroll_area.setWidget(self.hours_container)
        main_layout.addWidget(scroll_area)

    def _update_view(self):
        """Update the day view."""
        # Update date label
        self.date_label.setText(self.current_date.toString("dddd, MMMM d, yyyy"))

        # Clear hours container
        self._clear_hours()

        # Get events for the day
        date = datetime(
            self.current_date.year(), self.current_date.month(), self.current_date.day()
        ).date()
        user_events = self.planner_service.get_events_for_date(date)
        astro_events = self.planner_service.get_all_astrological_events_for_date(date)

        # Combine events
        all_events = user_events + astro_events

        # Organize events by hour
        events_by_hour = {}
        for event in all_events:
            hour = event.start_time.hour
            if hour not in events_by_hour:
                events_by_hour[hour] = []
            events_by_hour[hour].append(event)

        # Add hour sections
        for hour in range(24):
            hour_events = events_by_hour.get(hour, [])
            hour_section = HourSection(hour, hour_events)

            # Connect chart requested signal
            hour_section.chart_requested.connect(self._on_event_chart_requested)

            # Expand sections with events
            if hour_events:
                hour_section.set_expanded(True)

            self.hours_layout.addWidget(hour_section)

        # Add stretch to push everything to the top
        self.hours_layout.addStretch()

    def _clear_hours(self):
        """Clear the hours container."""
        # Remove all widgets from the layout
        while self.hours_layout.count():
            item = self.hours_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _previous_day(self):
        """Go to the previous day."""
        self.current_date = self.current_date.addDays(-1)
        self._update_view()
        self.date_changed.emit(self.current_date)

    def _next_day(self):
        """Go to the next day."""
        self.current_date = self.current_date.addDays(1)
        self._update_view()
        self.date_changed.emit(self.current_date)

    def _view_chart(self):
        """View the chart for this day."""
        # Get settings
        settings = self.planner_service.get_settings()

        # Check if default location is set
        if not settings.default_location:
            QMessageBox.warning(
                self,
                "No Default Location",
                "Please set a default location in the settings first.",
            )
            return

        # Create chart for noon
        self._create_day_chart()

    def _on_event_chart_requested(self, event: PlannerEvent):
        """Handle chart request for a specific event.

        Args:
            event: Event to create chart for
        """
        # Get settings
        settings = self.planner_service.get_settings()

        # Check if default location is set
        if not settings.default_location:
            # Inform user that a default location is needed
            QMessageBox.warning(
                self,
                "No Default Location",
                "Please set a default location in the settings first.",
            )
            return

        # Create chart for the event with default location
        chart = self.planner_service.send_event_to_chart_maker(
            event=event, location=settings.default_location
        )

        # Emit signal with the chart
        self.chart_requested.emit(chart)

    def _create_day_chart(self):
        """Create a chart for noon on the current day."""
        # Get settings
        settings = self.planner_service.get_settings()

        # Create a chart for noon on this day
        date_time = datetime(
            self.current_date.year(),
            self.current_date.month(),
            self.current_date.day(),
            12,
            0,  # Noon
        )

        # Calculate the chart
        chart = self.planner_service.calculate_chart(
            date_time=date_time, location=settings.default_location
        )

        # Emit signal with the chart
        self.chart_requested.emit(chart)

    def _add_event(self):
        """Add a new event."""
        # Show event dialog
        dialog = EventDialog(self.current_date)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the event
            event = dialog.get_event()

            # Save the event
            if self.planner_service.save_event(event):
                # Update the view
                self._update_view()
            else:
                QMessageBox.warning(self, "Error", "Failed to save event.")

    def _show_settings(self):
        """Show settings dialog."""
        # Get current settings
        settings = self.planner_service.get_settings()

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Planner Settings")
        dialog.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(dialog)

        # Form layout
        form_layout = QFormLayout()

        # Default location
        location_layout = QHBoxLayout()

        self.location_label = QLabel()
        if settings.default_location:
            self.location_label.setText(settings.default_location.display_name)
        else:
            self.location_label.setText("No location set")
        location_layout.addWidget(self.location_label, 1)

        # Change location button
        change_location_button = QPushButton("Change")
        change_location_button.clicked.connect(lambda: self._change_location(dialog))
        location_layout.addWidget(change_location_button)

        form_layout.addRow("Default Location:", location_layout)

        # Default view
        self.view_combo = QComboBox()
        self.view_combo.addItem("Month", "month")
        self.view_combo.addItem("Day", "day")

        # Set current value
        index = self.view_combo.findData(settings.default_view)
        if index >= 0:
            self.view_combo.setCurrentIndex(index)

        form_layout.addRow("Default View:", self.view_combo)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(dialog.accept)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update settings
            settings.default_view = self.view_combo.currentData()

            # Save settings
            if self.planner_service.save_settings(settings):
                logger.debug("Settings saved")
            else:
                QMessageBox.warning(self, "Error", "Failed to save settings.")

    def _change_location(self, parent_dialog):
        """Change the default location.

        Args:
            parent_dialog: Parent dialog
        """
        # Get current settings
        settings = self.planner_service.get_settings()

        # Create location search window
        location_window = LocationSearchWindow(parent_dialog)

        # Connect location selected signal
        def on_location_selected(location):
            # Update settings
            settings.default_location = location

            # Save settings
            if self.planner_service.save_settings(settings):
                # Update location label
                self.location_label.setText(location.display_name)
                logger.debug(f"Default location set to {location.display_name}")

                # Close the location window
                location_window.close()
            else:
                QMessageBox.warning(parent_dialog, "Error", "Failed to save location.")

        # Connect signal
        location_window.location_search_widget.location_selected.connect(
            on_location_selected
        )

        # Show window
        location_window.show()

    def set_date(self, date: QDate):
        """Set the current date.

        Args:
            date: Date to set
        """
        if date != self.current_date:
            self.current_date = date
            self._update_view()

    def get_date(self) -> QDate:
        """Get the current date.

        Returns:
            Current date
        """
        return self.current_date
