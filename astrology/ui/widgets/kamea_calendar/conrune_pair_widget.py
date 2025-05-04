"""
Conrune Pair Widget for the Kamea Cosmic Calendar.

This widget provides an interactive view of the conrune pairs that
make up the mathematical foundation of the Kamea Cosmic Calendar.
"""

import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ConrunePairWidget(QWidget):
    """Widget for displaying and exploring the conrune pairs of the Kamea Calendar."""

    def __init__(self):
        """Initialize the conrune pair widget."""
        super().__init__()
        
        # Load the calendar data
        self.calendar_data = self._load_calendar_data()
        
        # Current date
        self.current_date = datetime.now()
        
        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Add description
        description = QLabel(
            "Explore the conrune pairs that form the mathematical foundation of the "
            "Kamea Cosmic Calendar. Each day corresponds to a unique differential value "
            "derived from a conrune pair."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-style: italic; color: #666; margin-bottom: 10px;")
        main_layout.addWidget(description)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Calendar/controls side
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        
        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(self.current_date.date())
        self.date_edit.dateChanged.connect(self._on_date_changed)
        date_layout.addWidget(self.date_edit)
        
        self.today_button = QPushButton("Today")
        self.today_button.clicked.connect(self._go_to_today)
        date_layout.addWidget(self.today_button)
        
        calendar_layout.addLayout(date_layout)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._on_calendar_date_clicked)
        calendar_layout.addWidget(self.calendar)
        
        # Detail view
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        
        # Date header
        self.date_header = QLabel("Selected Date")
        self.date_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.date_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail_layout.addWidget(self.date_header)
        
        # Conrune pair details
        detail_grid_layout = QHBoxLayout()
        
        # Left column - labels
        label_layout = QVBoxLayout()
        label_layout.addWidget(QLabel("Date:"))
        label_layout.addWidget(QLabel("Differential:"))
        label_layout.addWidget(QLabel("Zodiacal Position:"))
        label_layout.addWidget(QLabel("Ditrune:"))
        label_layout.addWidget(QLabel("Conrune:"))
        detail_grid_layout.addLayout(label_layout)
        
        # Right column - values
        value_layout = QVBoxLayout()
        self.date_value = QLabel()
        self.differential_value = QLabel()
        self.zodiacal_value = QLabel()
        self.ditrune_value = QLabel()
        self.conrune_value = QLabel()
        
        value_layout.addWidget(self.date_value)
        value_layout.addWidget(self.differential_value)
        value_layout.addWidget(self.zodiacal_value)
        value_layout.addWidget(self.ditrune_value)
        value_layout.addWidget(self.conrune_value)
        
        detail_grid_layout.addLayout(value_layout)
        detail_layout.addLayout(detail_grid_layout)
        
        # Add a separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #ccc;")
        detail_layout.addWidget(separator)
        
        # Explanation of the mathematical relationship
        explanation_header = QLabel("Mathematical Relationship")
        explanation_header.setStyleSheet("font-weight: bold; margin-top: 10px;")
        detail_layout.addWidget(explanation_header)
        
        self.math_explanation = QLabel(
            "Select a date to see the explanation of its mathematical relationship in the Kamea system."
        )
        self.math_explanation.setWordWrap(True)
        self.math_explanation.setStyleSheet("line-height: 1.4;")
        detail_layout.addWidget(self.math_explanation)
        
        # Add spacer
        detail_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(calendar_widget)
        splitter.addWidget(self.detail_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 400])
        
        # Initialize with today's date
        self._update_detail_view(self._find_entry_for_date(self.current_date))

    def _load_calendar_data(self) -> List[Dict]:
        """Load the calendar data from CSV.
        
        Returns:
            List of dictionaries containing the calendar data.
        """
        data = []
        try:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                'assets', 'cvs', 'day_count.csv'
            )
            
            with open(csv_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
                    
            logger.info(f"Loaded {len(data)} calendar entries from {csv_path}")
        except Exception as e:
            logger.error(f"Error loading calendar data: {e}")
            
        return data

    def _on_date_changed(self):
        """Handle date change in the date edit widget."""
        selected_date = self.date_edit.date().toPyDate()
        
        # Update the calendar selection
        self.calendar.setSelectedDate(self.date_edit.date())
        
        # Find and display the entry for the selected date
        entry = self._find_entry_for_date(selected_date)
        self._update_detail_view(entry)

    def _on_calendar_date_clicked(self, date):
        """Handle date click in the calendar widget."""
        # Update the date edit to match
        self.date_edit.setDate(date)
        
        # Find and display the entry for the selected date
        selected_date = date.toPyDate()
        entry = self._find_entry_for_date(selected_date)
        self._update_detail_view(entry)

    def _go_to_today(self):
        """Set the date to today."""
        today = datetime.now().date()
        self.date_edit.setDate(today)
        self.calendar.setSelectedDate(self.date_edit.date())
        
        # Find and display the entry for today
        entry = self._find_entry_for_date(today)
        self._update_detail_view(entry)

    def _find_entry_for_date(self, date) -> Optional[Dict]:
        """Find the calendar entry for the specified date.
        
        Args:
            date: The date to find the entry for
            
        Returns:
            Dictionary containing the entry data, or None if not found
        """
        # Convert to the format in the CSV (day-month)
        if isinstance(date, datetime):
            date_str = date.strftime("%-d-%b")
        else:  # Assume date object
            date_str = date.strftime("%-d-%b")
            
        # Find the matching entry
        for entry in self.calendar_data:
            if entry.get('Day', '') == date_str:
                return entry
                
        return None

    def _update_detail_view(self, entry: Optional[Dict]):
        """Update the detail view with the selected entry.
        
        Args:
            entry: Dictionary containing the entry data, or None if not found
        """
        # Map zodiac letters to sign names
        zodiac_sign_map = {
            'A': 'Aries',
            'B': 'Taurus',
            'C': 'Gemini',
            'D': 'Cancer',
            'E': 'Leo',
            'F': 'Virgo',
            'G': 'Libra',
            'H': 'Scorpio',
            'I': 'Sagittarius',
            'J': 'Capricorn',
            'K': 'Aquarius',
            'L': 'Pisces'
        }
        
        if entry:
            # Update the header
            self.date_header.setText(f"Selected Date: {entry.get('Day', '')}")
            
            # Update the values
            self.date_value.setText(entry.get('Day', ''))
            self.differential_value.setText(entry.get('Differential', ''))
            
            # Format zodiacal position to show sign name if applicable
            zodiacal = entry.get('Zodiacal', '').strip()
            if zodiacal != "XXXX" and len(zodiacal.split()) > 1:
                parts = zodiacal.split()
                if parts[-1] in "ABCDEFGHIJKL":
                    sign_letter = parts[-1]
                    sign_name = zodiac_sign_map.get(sign_letter, f"Sign {sign_letter}")
                    formatted_zodiacal = f"{' '.join(parts[:-1])} {sign_name}"
                    self.zodiacal_value.setText(formatted_zodiacal)
                else:
                    self.zodiacal_value.setText(zodiacal)
            else:
                self.zodiacal_value.setText(zodiacal)
                
            self.ditrune_value.setText(entry.get('Ditrune', ''))
            self.conrune_value.setText(entry.get('Conrune', ''))
            
            # Update the mathematical explanation
            is_special = zodiacal == "XXXX"
            differential = entry.get('Differential', '')
            
            if is_special:
                self.math_explanation.setText(
                    f"This is a special day in the Kamea Cosmic Calendar, "
                    f"marking one of the para-zodiacal points derived from the Prime Ditrunes. "
                    f"These special days represent celestial gateways in the calendar cycle."
                )
                self.math_explanation.setStyleSheet("line-height: 1.4; color: #8B4513; font-weight: bold;")
            else:
                self.math_explanation.setText(
                    f"This day corresponds to differential value {differential}, "
                    f"which is the absolute difference between the decimal values of "
                    f"the ditrune {entry.get('Ditrune', '')} and its conrune pair "
                    f"{entry.get('Conrune', '')}. Each day in the calendar has a unique "
                    f"differential value, creating a perfect mathematical mapping between "
                    f"the 360 conrune pairs and the days of the year."
                )
                self.math_explanation.setStyleSheet("line-height: 1.4;")
        else:
            # Clear the view if no entry is found
            self.date_header.setText("No data available for selected date")
            self.date_value.setText("")
            self.differential_value.setText("")
            self.zodiacal_value.setText("")
            self.ditrune_value.setText("")
            self.conrune_value.setText("")
            self.math_explanation.setText("Date not found in the Kamea Cosmic Calendar.")
            self.math_explanation.setStyleSheet("line-height: 1.4; color: red;")