"""
Purpose: Monthly calendar widget for the astrological planner.

This file is part of the astrology pillar and serves as a UI component.
It provides a monthly calendar view showing moon phases and user events.
"""

from datetime import datetime
from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from astrology.services.planner_service import EventType, PlannerEvent, PlannerService


class DayCell(QFrame):
    """Widget for a single day in the calendar."""

    # Signal emitted when the day is clicked
    day_clicked = pyqtSignal(QDate)

    def __init__(self, date: QDate, events: List[PlannerEvent] = None, parent=None):
        """Initialize the day cell.

        Args:
            date: Date for this cell
            events: List of events for this day
            parent: Parent widget
        """
        super().__init__(parent)

        self.date = date
        self.events = events or []
        self.is_current_month = True

        # Set up UI
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumSize(100, 100)  # Increased size for better visibility
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Set rounded corners and border
        self.setStyleSheet(
            "QFrame {"
            "    border-radius: 8px;"
            "    border: 1px solid #CCCCCC;"
            "    background-color: #FFFFFF;"
            "}"
        )

        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)  # Increased margins
        self.layout.setSpacing(2)  # Increased spacing

        # Header layout for day number and moon phase
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Day number label
        self.day_label = QLabel(str(date.day()))
        self.day_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.day_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # Larger font
        self.day_label.setStyleSheet("color: #333333; padding: 2px;")
        header_layout.addWidget(self.day_label)

        # Add stretch to push day number and moon phase to opposite sides
        header_layout.addStretch()

        # Moon phase indicator
        self.moon_phase = self._get_moon_phase()
        if self.moon_phase:
            self.moon_label = QLabel(self.moon_phase)
            self.moon_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.moon_label.setFont(QFont("Arial", 14))  # Larger font for moon emoji
            self.moon_label.setStyleSheet("padding: 2px;")
            header_layout.addWidget(self.moon_label)

        self.layout.addLayout(header_layout)

        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #E0E0E0; max-height: 1px;")
        self.layout.addWidget(separator)

        # Event indicators
        self._add_event_indicators()

        # Add stretch to push everything to the top
        self.layout.addStretch()

    def _get_moon_phase(self) -> Optional[str]:
        """Get the moon phase for this day.

        Returns:
            Moon phase emoji or None
        """
        # Convert QDate to Python date for comparison
        date_py = datetime(self.date.year(), self.date.month(), self.date.day()).date()

        # Debug logging - only for the 1st and 15th to avoid too much output
        if date_py.day in [1, 15]:
            logger.debug(
                f"Checking moon phase for {date_py}, events: {len(self.events)}"
            )

        for event in self.events:
            if event.event_type == EventType.MOON_PHASE:
                # Check if event is on this day
                event_date = event.start_time.date()
                if event_date == date_py:
                    if "New Moon" in event.title:
                        logger.debug(f"Found New Moon on {date_py}")
                        return "🌑"
                    elif "Full Moon" in event.title:
                        logger.debug(f"Found Full Moon on {date_py}")
                        return "🌕"
                    elif "First Quarter" in event.title:
                        logger.debug(f"Found First Quarter on {date_py}")
                        return "🌓"
                    elif "Last Quarter" in event.title:
                        logger.debug(f"Found Last Quarter on {date_py}")
                        return "🌗"
        return None

    def _add_event_indicators(self):
        """Add indicators for events."""
        # Count events by type
        event_counts = {}
        for event in self.events:
            event_type = event.event_type
            if event_type not in event_counts:
                event_counts[event_type] = 0
            event_counts[event_type] += 1

        # Create a container for event indicators
        if event_counts and any(et != EventType.MOON_PHASE for et in event_counts):
            events_container = QFrame()
            events_container.setStyleSheet(
                "background-color: rgba(240, 240, 240, 0.5); "
                "border-radius: 4px; "
                "padding: 2px;"
            )
            events_layout = QVBoxLayout(events_container)
            events_layout.setContentsMargins(4, 4, 4, 4)
            events_layout.setSpacing(2)

            # Add indicators for each event type
            for event_type, count in event_counts.items():
                if event_type == EventType.MOON_PHASE:
                    # Moon phases are already shown
                    continue

                # Create indicator with colored dot and text
                indicator_layout = QHBoxLayout()
                indicator_layout.setContentsMargins(0, 0, 0, 0)
                indicator_layout.setSpacing(4)

                # Colored dot
                dot_label = QLabel("•")
                dot_label.setStyleSheet(
                    f"color: {self._get_color_for_event_type(event_type)}; "
                    f"font-size: 16px; font-weight: bold;"
                )
                indicator_layout.addWidget(dot_label)

                # Event type and count
                text = f"{event_type.name.replace('_', ' ').title()}"
                if count > 1:
                    text += f" ({count})"
                text_label = QLabel(text)
                text_label.setStyleSheet("color: #333333; font-size: 9px;")
                text_label.setWordWrap(True)
                indicator_layout.addWidget(text_label, 1)  # Give text label stretch

                events_layout.addLayout(indicator_layout)

            self.layout.addWidget(events_container)

            # Add stretch to push everything to the top
            self.layout.addStretch()

    def _get_color_for_event_type(self, event_type: EventType) -> str:
        """Get the color for an event type.

        Args:
            event_type: Event type

        Returns:
            Color as CSS string
        """
        colors = {
            EventType.MOON_PHASE: "#808080",  # Gray
            EventType.PLANETARY_ASPECT: "#FFA500",  # Orange
            EventType.RETROGRADE: "#800000",  # Maroon
            EventType.ECLIPSE: "#000080",  # Navy
            EventType.VENUS_CYCLE: "#00FFFF",  # Cyan
            EventType.USER_EVENT: "#008000",  # Green
            EventType.PLANETARY_PHASE: "#9370DB",  # Medium purple
        }
        return colors.get(event_type, "#000000")

    def set_current_month(self, is_current: bool):
        """Set whether this day is in the current month.

        Args:
            is_current: Whether this day is in the current month
        """
        self.is_current_month = is_current

        # Update appearance
        if is_current:
            self.setStyleSheet(
                "QFrame {"
                "    border-radius: 8px;"
                "    border: 1px solid #CCCCCC;"
                "    background-color: #FFFFFF;"
                "}"
            )
            self.day_label.setStyleSheet("color: #333333; padding: 2px;")
        else:
            self.setStyleSheet(
                "QFrame {"
                "    border-radius: 8px;"
                "    border: 1px solid #E0E0E0;"
                "    background-color: #F8F8F8;"
                "}"
            )
            self.day_label.setStyleSheet("color: #A0A0A0; padding: 2px;")

    def set_today(self, is_today: bool):
        """Set whether this day is today.

        Args:
            is_today: Whether this day is today
        """
        if is_today:
            # Highlight today with a gradient background and bold border
            self.setStyleSheet(
                "QFrame {"
                "    border-radius: 8px;"
                "    border: 2px solid #4080FF;"
                "    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
                "                              stop:0 #E0F0FF, stop:1 #D0E8FF);"
                "}"
            )
            self.day_label.setStyleSheet(
                "color: #4080FF; " "padding: 2px; " "font-weight: bold;"
            )
        elif not self.is_current_month:
            self.setStyleSheet(
                "QFrame {"
                "    border-radius: 8px;"
                "    border: 1px solid #E0E0E0;"
                "    background-color: #F8F8F8;"
                "}"
            )
            self.day_label.setStyleSheet("color: #A0A0A0; padding: 2px;")
        else:
            self.setStyleSheet(
                "QFrame {"
                "    border-radius: 8px;"
                "    border: 1px solid #CCCCCC;"
                "    background-color: #FFFFFF;"
                "}"
            )
            self.day_label.setStyleSheet("color: #333333; padding: 2px;")

    def mousePressEvent(self, event):
        """Handle mouse press events.

        Args:
            event: Mouse event
        """
        # Emit signal with this day's date
        self.day_clicked.emit(self.date)

        # Call parent implementation
        super().mousePressEvent(event)


class MonthlyCalendarWidget(QWidget):
    """Widget for displaying a monthly calendar with astrological events."""

    # Signal emitted when a day is selected
    day_selected = pyqtSignal(QDate)

    def __init__(self, parent=None):
        """Initialize the monthly calendar widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get the planner service
        self.planner_service = PlannerService.get_instance()

        # Current date
        self.current_date = QDate.currentDate()

        # Settings
        self.show_minor_aspects = True

        # Initialize UI
        self._init_ui()

        # Update calendar
        self._update_calendar()

        logger.debug("MonthlyCalendarWidget initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Header with month/year and navigation
        header_frame = QFrame()
        header_frame.setStyleSheet(
            "QFrame {"
            "    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            "                              stop:0 #6A5ACD, stop:1 #483D8B);"
            "    border-radius: 8px;"
            "    color: white;"
            "}"
            "QPushButton {"
            "    background-color: rgba(255, 255, 255, 0.2);"
            "    border: 1px solid rgba(255, 255, 255, 0.3);"
            "    border-radius: 4px;"
            "    color: white;"
            "    padding: 5px 10px;"
            "}"
            "QPushButton:hover {"
            "    background-color: rgba(255, 255, 255, 0.3);"
            "}"
            "QPushButton:pressed {"
            "    background-color: rgba(255, 255, 255, 0.1);"
            "}"
        )
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)

        # Previous month button
        self.prev_button = QPushButton("< Prev")
        self.prev_button.setFont(QFont("Arial", 10))
        self.prev_button.clicked.connect(self._previous_month)
        header_layout.addWidget(self.prev_button)

        # Month/year label
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setFont(
            QFont("Arial", 16, QFont.Weight.Bold)
        )  # Increased font size
        self.month_label.setStyleSheet("color: white;")
        header_layout.addWidget(self.month_label, 1)

        # Next month button
        self.next_button = QPushButton("Next >")
        self.next_button.setFont(QFont("Arial", 10))
        self.next_button.clicked.connect(self._next_month)
        header_layout.addWidget(self.next_button)

        main_layout.addWidget(header_frame)

        # Settings frame
        settings_frame = QFrame()
        settings_frame.setStyleSheet(
            "QFrame {"
            "    background-color: #F5F5F5;"
            "    border-radius: 8px;"
            "    border: 1px solid #E0E0E0;"
            "    padding: 5px;"
            "}"
            "QCheckBox {"
            "    font-size: 11px;"
            "}"
        )
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(10, 5, 10, 5)

        # Minor aspects checkbox
        self.minor_aspects_checkbox = QCheckBox("Show Minor Aspects")
        self.minor_aspects_checkbox.setChecked(self.show_minor_aspects)
        self.minor_aspects_checkbox.stateChanged.connect(self._toggle_minor_aspects)
        settings_layout.addWidget(self.minor_aspects_checkbox)

        # Add spacer to push checkbox to the left
        settings_layout.addStretch(1)

        main_layout.addWidget(settings_frame)

        # Add some spacing
        main_layout.addSpacing(5)

        # Day of week headers
        days_frame = QFrame()
        days_frame.setStyleSheet(
            "QFrame {"
            "    background-color: #F0F0F0;"
            "    border-radius: 8px;"
            "    padding: 5px;"
            "}"
            "QLabel {"
            "    color: #333333;"
            "    font-weight: bold;"
            "}"
        )
        days_layout = QHBoxLayout(days_frame)
        days_layout.setContentsMargins(5, 5, 5, 5)

        # Weekend colors
        weekend_style = "color: #E74C3C;"  # Red for weekends

        for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # Increased font size

            # Set weekend days to red
            if i == 0 or i == 6:  # Sunday or Saturday
                label.setStyleSheet(weekend_style)

            days_layout.addWidget(label)

        main_layout.addWidget(days_frame)

        # Add some spacing
        main_layout.addSpacing(5)

        # Calendar grid
        grid_frame = QFrame()
        grid_frame.setStyleSheet(
            "QFrame {"
            "    background-color: #FFFFFF;"
            "    border-radius: 8px;"
            "    border: 1px solid #E0E0E0;"
            "    padding: 5px;"
            "}"
        )
        grid_layout = QVBoxLayout(grid_frame)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(8)  # Increased spacing between cells
        grid_layout.addLayout(self.calendar_grid)

        main_layout.addWidget(grid_frame, 1)  # Give the grid stretch

        # Add some spacing
        main_layout.addSpacing(10)

        # Legend
        legend_frame = QFrame()
        legend_frame.setStyleSheet(
            "QFrame {"
            "    background-color: #F8F8F8;"
            "    border-radius: 8px;"
            "    border: 1px solid #E0E0E0;"
            "    padding: 10px;"
            "}"
            "QLabel {"
            "    color: #333333;"
            "}"
            "QLabel#LegendTitle {"
            "    font-weight: bold;"
            "    color: #333333;"
            "    font-size: 12px;"
            "}"
        )
        legend_layout = QVBoxLayout(legend_frame)
        legend_layout.setContentsMargins(10, 10, 10, 10)

        legend_title = QLabel("Legend:")
        legend_title.setObjectName("LegendTitle")
        legend_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        legend_layout.addWidget(legend_title)

        # Moon phases with better styling
        moon_phases_frame = QFrame()
        moon_phases_frame.setStyleSheet(
            "QFrame {"
            "    background-color: rgba(240, 240, 240, 0.5);"
            "    border-radius: 4px;"
            "    padding: 5px;"
            "}"
            "QLabel {"
            "    font-size: 11px;"
            "}"
        )
        moon_phases = QHBoxLayout(moon_phases_frame)
        moon_phases.setContentsMargins(5, 5, 5, 5)

        # Create moon phase labels with larger emoji
        for phase, name in [
            ("🌑", "New Moon"),
            ("🌓", "First Quarter"),
            ("🌕", "Full Moon"),
            ("🌗", "Last Quarter"),
        ]:
            phase_label = QLabel(
                f"<span style='font-size:16px;'>{phase}</span> = {name}"
            )
            phase_label.setTextFormat(Qt.TextFormat.RichText)
            moon_phases.addWidget(phase_label)

        legend_layout.addWidget(moon_phases_frame)

        main_layout.addWidget(legend_frame)

    def _update_calendar(self):
        """Update the calendar display."""
        # Clear the grid
        self._clear_grid()

        # Update month/year label
        self.month_label.setText(self.current_date.toString("MMMM yyyy"))

        # Get first day of month
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)

        # Get the day of week for the first day (0 = Sunday, 6 = Saturday)
        first_day_of_week = first_day.dayOfWeek() % 7

        # Get the number of days in the month
        days_in_month = first_day.daysInMonth()

        # Get events for the month
        events_by_day = self.planner_service.get_events_for_month(
            self.current_date.year(),
            self.current_date.month(),
            include_minor_aspects=self.show_minor_aspects,
        )

        # Add moon phases
        moon_phases = self.planner_service.get_moon_phases_for_month(
            self.current_date.year(), self.current_date.month()
        )

        # Log moon phases
        logger.debug(
            f"Moon phases for {self.current_date.year()}-{self.current_date.month()}: {len(moon_phases)}"
        )

        # Organize moon phases by day
        for event in moon_phases:
            day = event.start_time.day
            if day in events_by_day:
                events_by_day[day].append(event)
            else:
                events_by_day[day] = [event]

        # Get today's date
        today = QDate.currentDate()

        # Add days from previous month
        prev_month = QDate(first_day).addMonths(-1)
        days_in_prev_month = prev_month.daysInMonth()

        for i in range(first_day_of_week):
            day = days_in_prev_month - first_day_of_week + i + 1
            date = QDate(prev_month.year(), prev_month.month(), day)

            # Create day cell
            day_cell = DayCell(date)
            day_cell.set_current_month(False)
            day_cell.day_clicked.connect(self._on_day_clicked)

            # Add to grid
            self.calendar_grid.addWidget(day_cell, 0, i)

        # Add days from current month
        row = 0
        col = first_day_of_week

        for day in range(1, days_in_month + 1):
            date = QDate(self.current_date.year(), self.current_date.month(), day)

            # Get events for this day
            day_events = events_by_day.get(day, [])

            # Create day cell
            day_cell = DayCell(date, day_events)

            # Check if this is today
            if date == today:
                day_cell.set_today(True)

            day_cell.day_clicked.connect(self._on_day_clicked)

            # Add to grid
            self.calendar_grid.addWidget(day_cell, row, col)

            # Move to next cell
            col += 1
            if col > 6:
                col = 0
                row += 1

        # Add days from next month
        next_month = QDate(first_day).addMonths(1)
        day = 1

        while row < 6:
            date = QDate(next_month.year(), next_month.month(), day)

            # Create day cell
            day_cell = DayCell(date)
            day_cell.set_current_month(False)
            day_cell.day_clicked.connect(self._on_day_clicked)

            # Add to grid
            self.calendar_grid.addWidget(day_cell, row, col)

            # Move to next cell
            col += 1
            if col > 6:
                col = 0
                row += 1

            day += 1

    def _clear_grid(self):
        """Clear the calendar grid."""
        # Remove all widgets from the grid
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _previous_month(self):
        """Go to the previous month."""
        self.current_date = self.current_date.addMonths(-1)
        self._update_calendar()

    def _next_month(self):
        """Go to the next month."""
        self.current_date = self.current_date.addMonths(1)
        self._update_calendar()

    def _on_day_clicked(self, date: QDate):
        """Handle day cell clicks.

        Args:
            date: Date that was clicked
        """
        # Emit signal with selected date
        self.day_selected.emit(date)

    def set_date(self, date: QDate):
        """Set the current date.

        Args:
            date: Date to set
        """
        if (
            date.year() != self.current_date.year()
            or date.month() != self.current_date.month()
        ):
            self.current_date = QDate(date.year(), date.month(), 1)
            self._update_calendar()

    def get_date(self) -> QDate:
        """Get the current date.

        Returns:
            Current date
        """
        return self.current_date

    def _toggle_minor_aspects(self, state):
        """Toggle showing minor aspects.

        Args:
            state: Checkbox state
        """
        self.show_minor_aspects = state == Qt.CheckState.Checked.value
        logger.debug(f"Minor aspects toggled: {self.show_minor_aspects}")
        self._update_calendar()
