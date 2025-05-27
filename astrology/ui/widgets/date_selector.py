"""
Defines a custom date selector widget that supports ancient dates (including BCE).

Author: IsopGemini
Created: 2024-08-06
Last Modified: 2024-08-06
Dependencies: PyQt6
"""


from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class AncientDateSelector(QWidget):
    """
    A custom date selector widget that supports ancient dates, including BCE dates.
    Provides alternatives to QDateEdit with its 1753 limitation.

    Signals:
        dateChanged: Emitted when the date is changed
    """

    dateChanged = pyqtSignal(QDate)

    def __init__(self, parent=None):
        """
        Initialize the AncientDateSelector widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set up UI components
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Set default date to current date
        self.set_date(QDate.currentDate())

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        date_layout = QGridLayout()

        # Year components
        year_group = QGroupBox("Year")
        year_layout = QHBoxLayout(year_group)

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(
            -10000, 9999
        )  # Support dates from 10,000 BCE to 9999 CE
        self.year_spinbox.setValue(2024)
        self.year_spinbox.setFixedWidth(100)

        self.bce_checkbox = QCheckBox("BCE")
        self.bce_checkbox.setToolTip("Check for dates Before Common Era")

        year_layout.addWidget(self.year_spinbox)
        year_layout.addWidget(self.bce_checkbox)

        # Month components
        month_group = QGroupBox("Month")
        month_layout = QVBoxLayout(month_group)

        self.month_combo = QComboBox()
        for i, month in enumerate(
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
        ):
            self.month_combo.addItem(
                month, i + 1
            )  # Store 1-based month number as item data

        month_layout.addWidget(self.month_combo)

        # Day components
        day_group = QGroupBox("Day")
        day_layout = QVBoxLayout(day_group)

        self.day_spinbox = QSpinBox()
        self.day_spinbox.setRange(1, 31)
        self.day_spinbox.setValue(1)

        day_layout.addWidget(self.day_spinbox)

        # Add all components to main layout
        date_layout.addWidget(year_group, 0, 0)
        date_layout.addWidget(month_group, 0, 1)
        date_layout.addWidget(day_group, 0, 2)

        main_layout.addLayout(date_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.year_spinbox.valueChanged.connect(self._on_date_changed)
        self.month_combo.currentIndexChanged.connect(self._on_date_changed)
        self.day_spinbox.valueChanged.connect(self._on_date_changed)
        self.bce_checkbox.stateChanged.connect(self._on_bce_changed)

        # Update day range when month changes
        self.month_combo.currentIndexChanged.connect(self._update_day_range)
        self.year_spinbox.valueChanged.connect(self._update_day_range)

    def _on_bce_changed(self, state):
        """
        Handle BCE checkbox state change, adjusting year spinbox appropriately.

        Args:
            state: Checkbox state
        """
        year = abs(self.year_spinbox.value())

        # Block signals to prevent recursive calls
        self.year_spinbox.blockSignals(True)

        if state == Qt.CheckState.Checked.value:
            # Convert to BCE (negative year)
            if year > 0:  # Don't convert 0
                self.year_spinbox.setValue(-year)
        else:
            # Convert to CE (positive year)
            if year > 0:  # If already positive, keep as is
                pass
            else:  # Convert negative to positive
                self.year_spinbox.setValue(year)

        self.year_spinbox.blockSignals(False)
        self._on_date_changed()

    def _update_day_range(self):
        """Update the day spinbox range based on the selected month and year."""
        month = self.month_combo.currentData()
        year = self.get_effective_year()

        # Get the number of days in the month
        days_in_month = self._days_in_month(year, month)

        # Save current day
        current_day = self.day_spinbox.value()

        # Update range
        self.day_spinbox.setRange(1, days_in_month)

        # Adjust if current day is out of new range
        if current_day > days_in_month:
            self.day_spinbox.setValue(days_in_month)

    def _days_in_month(self, year, month):
        """
        Get the number of days in a month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            Number of days in the month
        """
        days_per_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        # Handle leap years
        if month == 2 and self._is_leap_year(year):
            return 29

        return days_per_month[month]

    def _is_leap_year(self, year):
        """
        Check if a year is a leap year in the proleptic Gregorian calendar.

        Args:
            year: Year to check

        Returns:
            True if leap year, False otherwise
        """
        # Handle negative years (BCE)
        effective_year = year
        if year <= 0:
            effective_year = (
                abs(year) + 1
            )  # Astronomical year numbering: 1 BCE = year 0, 2 BCE = year -1

        # Proleptic Gregorian calendar leap year rules
        if effective_year % 400 == 0:
            return True
        if effective_year % 100 == 0:
            return False
        if effective_year % 4 == 0:
            return True
        return False

    def _on_date_changed(self):
        """Handle date change and emit signal."""
        # Emit date changed signal
        self.dateChanged.emit(self.date())

    def get_effective_year(self):
        """
        Get the effective year value, considering BCE checkbox.

        Returns:
            int: Effective year value (negative for BCE)
        """
        year = self.year_spinbox.value()

        # If BCE checkbox is checked but year is positive, convert to negative
        if self.bce_checkbox.isChecked() and year > 0:
            year = -year
        # If BCE checkbox is unchecked but year is negative, convert to positive
        elif not self.bce_checkbox.isChecked() and year < 0:
            year = abs(year)

        return year

    def date(self):
        """
        Get the selected date as a QDate object.

        Returns:
            QDate: The selected date
        """
        year = self.get_effective_year()
        month = self.month_combo.currentData()
        day = self.day_spinbox.value()

        # For BCE dates, convert to astronomical year numbering for QDate
        # In astronomical year numbering: 1 BCE = year 0, 2 BCE = year -1, etc.
        if year <= 0:
            year_for_qdate = year
        else:
            year_for_qdate = year

        # Create QDate object (which will validate the date)
        date = QDate(year_for_qdate, month, day)

        # If invalid date (e.g., Feb 29 in non-leap year), return a valid date
        if not date.isValid():
            # Try with last day of the month
            date = QDate(
                year_for_qdate, month, self._days_in_month(year_for_qdate, month)
            )

        return date

    def set_date(self, date):
        """
        Set the date displayed in the widget.

        Args:
            date: QDate to display
        """
        if not date.isValid():
            return

        # Block signals while setting values
        self.year_spinbox.blockSignals(True)
        self.month_combo.blockSignals(True)
        self.day_spinbox.blockSignals(True)
        self.bce_checkbox.blockSignals(True)

        year = date.year()

        # Handle BCE dates
        if year <= 0:
            self.bce_checkbox.setChecked(True)
            self.year_spinbox.setValue(abs(year))
        else:
            self.bce_checkbox.setChecked(False)
            self.year_spinbox.setValue(year)

        # Set month (find the index with the matching month number in the data)
        for i in range(self.month_combo.count()):
            if self.month_combo.itemData(i) == date.month():
                self.month_combo.setCurrentIndex(i)
                break

        # Set day
        self.day_spinbox.setValue(date.day())

        # Unblock signals
        self.year_spinbox.blockSignals(False)
        self.month_combo.blockSignals(False)
        self.day_spinbox.blockSignals(False)
        self.bce_checkbox.blockSignals(False)

        # Update day range
        self._update_day_range()
