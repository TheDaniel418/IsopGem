"""
Purpose: Provides a widget for creating and viewing birth charts.

This file is part of the astrology pillar and serves as a UI component.
It provides a form for entering birth data and displays the resulting chart.

Key components:
- BirthChartWidget: Widget for creating and viewing birth charts

Dependencies:
- PyQt6: For UI components
- datetime: For date and time handling
- astrology.models: For astrological data models
- astrology.services: For astrological services
"""

from datetime import datetime
import math
from typing import Optional, Dict, List, Tuple
import tzlocal

from PyQt6.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QDateTimeEdit, QComboBox, QCheckBox,
    QGroupBox, QScrollArea, QWidget, QSplitter, QTabWidget
)
from PyQt6.QtGui import QFont

from loguru import logger

from astrology.models.chart import Chart, NatalChart
from astrology.models.zodiac import HouseSystem, PerspectiveType
from astrology.services.kerykeion_service import KerykeionService
from astrology.services.location_service import Location
from astrology.ui.widgets.planetary_positions_widget import PlanetaryPositionsWidget
from astrology.ui.widgets.new_house_positions_widget import NewHousePositionsWidget
from astrology.ui.widgets.midpoints_widget import MidpointsWidget
from astrology.ui.dialogs.location_search_window import LocationSearchWindow


class BirthChartWidget(QWidget):
    """Widget for creating and viewing birth charts."""

    # Signal emitted when a chart is created
    chart_created = pyqtSignal(NatalChart)

    def __init__(self, parent=None):
        """Initialize the birth chart widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Create the kerykeion service
        self.kerykeion_service = KerykeionService()

        # Current chart
        self.current_chart = None

        # Initialize UI
        self._init_ui()

        logger.debug("BirthChartWidget initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)

        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left side: Input form
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)

        # Form group
        form_group = QGroupBox("Birth Information")
        form_layout = QFormLayout()

        # Name input
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        # Date and time input
        self.date_time_input = QDateTimeEdit()
        self.date_time_input.setDateTime(QDateTime.currentDateTime())
        self.date_time_input.setCalendarPopup(True)
        form_layout.addRow("Birth Date & Time:", self.date_time_input)

        # Time known checkbox
        self.time_known_checkbox = QCheckBox("Birth time is known")
        self.time_known_checkbox.setChecked(True)
        self.time_known_checkbox.stateChanged.connect(self._on_time_known_changed)
        form_layout.addRow("", self.time_known_checkbox)

        # Location inputs
        location_layout = QHBoxLayout()
        self.location_input = QLineEdit()
        location_layout.addWidget(self.location_input)

        self.location_search_button = QPushButton("Search")
        self.location_search_button.clicked.connect(self._open_location_search)
        location_layout.addWidget(self.location_search_button)

        form_layout.addRow("Location:", location_layout)

        # Latitude and longitude inputs
        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("e.g., 40.7128 (North is positive)")
        form_layout.addRow("Latitude:", self.latitude_input)

        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("e.g., -74.0060 (East is positive)")
        form_layout.addRow("Longitude:", self.longitude_input)

        # House system selection
        self.house_system_combo = QComboBox()
        for system in HouseSystem:
            self.house_system_combo.addItem(system.value, system)
        form_layout.addRow("House System:", self.house_system_combo)

        # Perspective type selection
        self.perspective_combo = QComboBox()
        for perspective in PerspectiveType:
            self.perspective_combo.addItem(perspective.value, perspective)
        form_layout.addRow("Perspective:", self.perspective_combo)

        # Set the form layout to the group
        form_group.setLayout(form_layout)
        input_layout.addWidget(form_group)

        # Create chart button
        self.create_button = QPushButton("Create Chart")
        self.create_button.clicked.connect(self._on_create_chart)
        input_layout.addWidget(self.create_button)

        # Add stretch to push everything to the top
        input_layout.addStretch()

        # Right side: Chart display
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)

        # Tabs for different chart views
        self.chart_tabs = QTabWidget()

        # Chart wheel is now opened in the browser on demand using kerykeion

        # Add a button to open the chart in the browser
        self.open_browser_button = QPushButton("Open Kerykeion Chart in Browser")
        self.open_browser_button.clicked.connect(self._open_chart_in_browser)
        display_layout.addWidget(self.open_browser_button)

        # Debug: Add a button to switch to the Houses tab
        self.show_houses_button = QPushButton("Show Houses Tab")
        self.show_houses_button.clicked.connect(self._show_houses_tab)
        self.show_houses_button.setStyleSheet("background-color: #ffcccc;")
        display_layout.addWidget(self.show_houses_button)

        # Debug: Add a button to switch to the Midpoints tab
        self.show_midpoints_button = QPushButton("Show Midpoints Tab")
        self.show_midpoints_button.clicked.connect(self._show_midpoints_tab)
        self.show_midpoints_button.setStyleSheet("background-color: #ccffcc;")
        display_layout.addWidget(self.show_midpoints_button)

        # Add a button for advanced midpoint analysis
        self.midpoint_analysis_button = QPushButton("Advanced Midpoint Analysis")
        self.midpoint_analysis_button.clicked.connect(self._show_midpoint_analysis)
        self.midpoint_analysis_button.setStyleSheet("background-color: #ccccff;")
        display_layout.addWidget(self.midpoint_analysis_button)


        # Positions tab
        self.positions_tab = QWidget()
        positions_layout = QVBoxLayout(self.positions_tab)
        self.positions_widget = PlanetaryPositionsWidget()
        positions_layout.addWidget(self.positions_widget)
        self.chart_tabs.addTab(self.positions_tab, "Positions")

        # Houses tab
        self.houses_tab = QWidget()
        houses_layout = QVBoxLayout(self.houses_tab)
        self.houses_widget = NewHousePositionsWidget()
        houses_layout.addWidget(self.houses_widget)
        self.chart_tabs.addTab(self.houses_tab, "Houses")

        # Midpoints tab
        self.midpoints_tab = QWidget()
        midpoints_layout = QVBoxLayout(self.midpoints_tab)
        self.midpoints_widget = MidpointsWidget()
        midpoints_layout.addWidget(self.midpoints_widget)
        self.chart_tabs.addTab(self.midpoints_tab, "Midpoints")

        # Add tabs to display layout
        display_layout.addWidget(self.chart_tabs)

        # Add widgets to splitter
        splitter.addWidget(input_widget)
        splitter.addWidget(display_widget)

        # Set initial sizes
        splitter.setSizes([300, 700])

    def _on_time_known_changed(self, state):
        """Handle changes to the time known checkbox.

        Args:
            state: Checkbox state
        """
        time_known = state == Qt.CheckState.Checked.value
        self.date_time_input.setTimeEnabled(time_known)
        self.house_system_combo.setEnabled(time_known)
        self.perspective_combo.setEnabled(time_known)

    def _on_create_chart(self):
        """Handle the create chart button click."""
        # Get input values
        name = self.name_input.text()
        birth_date = self.date_time_input.dateTime().toPyDateTime()
        time_known = self.time_known_checkbox.isChecked()
        location_name = self.location_input.text()

        # Validate latitude and longitude
        try:
            latitude = float(self.latitude_input.text())
            longitude = float(self.longitude_input.text())
        except ValueError:
            # Show error message
            logger.error("Invalid latitude or longitude")
            return

        # We'll get the house system and perspective type later

        # Create the chart
        try:
            # Get the timezone string for the location
            try:
                # Get the local timezone
                local_tz = tzlocal.get_localzone()
                timezone_str = str(local_tz)
                logger.debug(f"Using local timezone: {timezone_str}")
            except Exception as e:
                # Fall back to UTC if there's an error
                timezone_str = "UTC"
                logger.warning(f"Error getting local timezone, using UTC: {e}")

            # Get the selected house system
            house_system_data = self.house_system_combo.currentData()

            # Map house system to kerykeion code
            house_system_codes = {
                HouseSystem.PLACIDUS: "P",
                HouseSystem.KOCH: "K",
                HouseSystem.EQUAL: "E",
                HouseSystem.WHOLE_SIGN: "W",
                HouseSystem.REGIOMONTANUS: "R",
                HouseSystem.CAMPANUS: "C",
                HouseSystem.TOPOCENTRIC: "T",
                HouseSystem.MORINUS: "M",
                HouseSystem.PORPHYRY: "O",
                HouseSystem.ALCABITIUS: "B"
            }
            house_system_code = house_system_codes.get(house_system_data, "P")  # Default to Placidus
            logger.debug(f"Using house system: {house_system_data.value} (code: {house_system_code})")

            # Get the selected perspective type
            perspective_type_data = self.perspective_combo.currentData()
            perspective_type = perspective_type_data.value
            logger.debug(f"Using perspective type: {perspective_type}")

            # Create the chart using kerykeion
            chart = self.kerykeion_service.create_natal_chart(
                name=name,
                birth_date=birth_date,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str,
                house_system=house_system_code,
                perspective_type=perspective_type
            )

            # Add additional information to the chart
            chart.location_name = location_name
            chart.house_system = house_system_data

            # Store the current chart
            self.current_chart = chart

            # Log chart details
            logger.debug(f"Created chart with {len(chart.planets)} planets and {len(chart.houses)} houses")
            for house in chart.houses:
                logger.debug(f"House {house.number}: {house.sign} at {house.cusp_degree}°, planets: {house.planets}")

            # Update the chart display
            self._update_chart_display()

            # Emit the chart created signal
            # Convert the Chart to NatalChart if needed
            if isinstance(chart, NatalChart):
                self.chart_created.emit(chart)
            else:
                # Create a NatalChart from the Chart
                natal_chart = NatalChart(
                    name=chart.name,
                    date=chart.date,
                    planets=chart.planets if hasattr(chart, 'planets') else [],
                    houses=chart.houses if hasattr(chart, 'houses') else [],
                    aspects=chart.aspects if hasattr(chart, 'aspects') else [],
                    latitude=chart.latitude,
                    longitude=chart.longitude,
                    location_name=chart.location_name,
                    house_system=chart.house_system if hasattr(chart, 'house_system') else None,
                    kerykeion_subject=chart.kerykeion_subject
                )
                self.chart_created.emit(natal_chart)

            logger.debug(f"Created natal chart for {name} using kerykeion")
        except Exception as e:
            logger.error(f"Error creating chart: {e}")

    def _open_location_search(self):
        """Open the location search window."""
        # Create the location search window
        self.location_search_window = LocationSearchWindow()

        # Connect the location selected signal
        self.location_search_window.location_selected.connect(self._on_location_selected)

        # Show the window
        self.location_search_window.show()

    def _on_location_selected(self, location):
        """Handle location selection.

        Args:
            location: Selected location
        """
        # Update location fields
        self.location_input.setText(location.display_name)
        self.latitude_input.setText(str(location.latitude))
        self.longitude_input.setText(str(location.longitude))

    def _open_chart_in_browser(self):
        """Open the current chart in the browser using kerykeion."""
        if not self.current_chart:
            logger.warning("No chart available to open in browser")
            return

        try:
            # Generate the SVG and open it in the browser
            self.kerykeion_service.generate_chart_svg(
                chart=self.current_chart,
                open_in_browser=True
            )
            logger.debug(f"Opened chart for {self.current_chart.name} in browser")
        except Exception as e:
            logger.error(f"Error opening chart in browser: {e}")



    def _show_houses_tab(self):
        """Debug method to switch to the Houses tab."""
        # Find the index of the Houses tab
        houses_index = -1
        for i in range(self.chart_tabs.count()):
            if self.chart_tabs.tabText(i) == "Houses":
                houses_index = i
                break

        if houses_index >= 0:
            logger.debug(f"Switching to Houses tab (index {houses_index})")
            self.chart_tabs.setCurrentIndex(houses_index)
        else:
            logger.warning("Houses tab not found")

    def _show_midpoints_tab(self):
        """Debug method to switch to the Midpoints tab."""
        # Find the index of the Midpoints tab
        midpoints_index = -1
        for i in range(self.chart_tabs.count()):
            if self.chart_tabs.tabText(i) == "Midpoints":
                midpoints_index = i
                break

        if midpoints_index >= 0:
            logger.debug(f"Switching to Midpoints tab (index {midpoints_index})")
            self.chart_tabs.setCurrentIndex(midpoints_index)
        else:
            logger.warning("Midpoints tab not found")

    def _show_midpoint_analysis(self):
        """Open the advanced midpoint analysis window."""
        from astrology.ui.windows.midpoint_analysis_window import MidpointAnalysisWindow

        if not hasattr(self, 'midpoint_analysis_window') or self.midpoint_analysis_window is None:
            if self.current_chart is None:
                logger.warning("No chart available for midpoint analysis")
                return

            self.midpoint_analysis_window = MidpointAnalysisWindow(self.current_chart)

        self.midpoint_analysis_window.show()
        self.midpoint_analysis_window.raise_()

    def _update_chart_display(self):
        """Update the chart display with the current chart."""
        if not self.current_chart:
            return

        # The chart is now opened in the browser on demand using kerykeion

        # Update the positions widget
        self.positions_widget.set_chart(self.current_chart)

        # Update the houses widget
        logger.debug(f"Setting chart with {len(self.current_chart.houses)} houses to houses widget")
        self.houses_widget.set_chart(self.current_chart)

        # Update the midpoints widget
        logger.debug(f"Setting chart to midpoints widget")
        self.midpoints_widget.set_chart(self.current_chart)

        # Switch to the positions tab
        self.chart_tabs.setCurrentIndex(0)  # Index 0 is now the positions tab
