"""
Purpose: Provides a dialog for searching and analyzing cosmic cycles.

This file is part of the astrology pillar and serves as a UI component.
It provides a dialog for searching for specific cosmic events and analyzing
planetary cycles over long time periods.

Key components:
- CycleCalculatorWindow: Main dialog class for cycle calculations
- _search_aspects: Method for finding aspects between selected planets
- _search_venus_cycle: Method for analyzing Venus 8-year cycles
- _search_saturn_pluto: Method for finding Saturn-Pluto conjunctions
- _search_retrogrades: Method for finding retrograde periods

Dependencies:
- PyQt6: For UI components
- astrology.models.aspect: For aspect type definitions
- astrology.services.astrology_calculation_service: For calculations
- datetime: For date/time handling
- loguru: For logging
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger
from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import Chart
from astrology.services.astrology_calculation_service import AstrologyCalculationService
from astrology.models.aspect import AspectType, Aspect, AspectInfo
from astrology.repositories.astrological_events_repository import AstrologicalEventsRepository
from astrology.services.astrological_event_calculator import LunarPhaseType, PlanetPhaseType
import pytz


class CycleCalculatorWindow(QDialog):
    """Dialog for searching and analyzing cosmic cycles."""

    # Signal emitted when a chart is requested for a specific date/time
    chart_requested = pyqtSignal(Chart)

    def __init__(self, parent=None):
        """Initialize the dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get the calculation service
        self.calculation_service = AstrologyCalculationService.get_instance()

        # Get the repository from the calculation service
        if hasattr(self.calculation_service, 'repository') and self.calculation_service.repository:
            self.repository = self.calculation_service.repository
        else:
            from shared.repositories.database import Database
            db = Database.get_instance()
            self.repository = AstrologicalEventsRepository(db)
            # Assign it to the calculation service for future use
            self.calculation_service.repository = self.repository

        # Get available date range from the repository
        min_year, max_year = self.repository.get_available_date_range()
        if min_year is None or max_year is None:
            # Use default range if not available
            self.min_year = 1900
            self.max_year = 2100
            logger.warning(f"No calculated data range found in repository. Using defaults: {self.min_year}-{self.max_year}")
        else:
            self.min_year = min_year
            self.max_year = max_year
            logger.info(f"Available calculation date range: {self.min_year}-{self.max_year}")

        # Initialize UI
        self._init_ui()

        logger.debug("CycleCalculatorWindow initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("Cosmic Cycle Calculator")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create search parameters section
        self._create_search_parameters(main_layout)

        # Create results section
        self._create_results_section(main_layout)

        # Create buttons
        self._create_buttons(main_layout)

    def _create_search_parameters(self, parent_layout):
        """Create the search parameters section.

        Args:
            parent_layout: Parent layout to add to
        """
        # Search parameters group
        params_group = QGroupBox("Search Parameters")
        params_layout = QFormLayout(params_group)

        # Event type selection
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItem("Planetary Aspect", "aspect")
        self.event_type_combo.addItem("Lunar Phases", "lunar_phases")
        self.event_type_combo.addItem("Venus 8-Year Cycle", "venus_cycle")
        self.event_type_combo.addItem("Saturn-Pluto Conjunctions", "saturn_pluto")
        self.event_type_combo.addItem("Retrograde Periods", "retrograde")
        self.event_type_combo.currentIndexChanged.connect(self._update_parameter_fields)
        params_layout.addRow("Event Type:", self.event_type_combo)

        # Parameter container (will hold different parameter widgets)
        self.param_container = QWidget()
        self.param_layout = QFormLayout(self.param_container)
        self.param_layout.setContentsMargins(0, 0, 0, 0)
        params_layout.addRow("", self.param_container)

        # Date range
        date_range_layout = QHBoxLayout()

        # Start date - default to current date minus 6 months, but within available range
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        default_start = QDate.currentDate().addMonths(-6)
        # Ensure start date is within available range
        min_date = QDate(self.min_year, 1, 1)
        if default_start < min_date:
            default_start = min_date
        self.start_date_edit.setDate(default_start)
        self.start_date_edit.setMinimumDate(min_date)
        date_range_layout.addWidget(QLabel("From:"))
        date_range_layout.addWidget(self.start_date_edit)

        # End date - default to current date plus 6 months, but within available range
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        default_end = QDate.currentDate().addMonths(6)
        # Ensure end date is within available range
        max_date = QDate(self.max_year, 12, 31)
        if default_end > max_date:
            default_end = max_date
        self.end_date_edit.setDate(default_end)
        self.end_date_edit.setMaximumDate(max_date)
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.end_date_edit)

        # Add an info label about available data
        date_range_info = QLabel(f"<i>Available data range: {self.min_year} to {self.max_year}</i>")
        date_range_info.setStyleSheet("color: #666666; font-size: 9pt;")

        params_layout.addRow("Date Range:", date_range_layout)
        params_layout.addRow("", date_range_info)

        # Preset date ranges
        preset_layout = QHBoxLayout()

        preset_combo = QComboBox()
        preset_combo.addItem("Custom", "custom")
        preset_combo.addItem("1 Year", "1y")
        preset_combo.addItem("5 Years", "5y")
        preset_combo.addItem("10 Years", "10y")
        preset_combo.addItem("20 Years", "20y")
        preset_combo.addItem("50 Years", "50y")
        preset_combo.addItem("100 Years", "100y")
        preset_combo.addItem("Full Range", "full")
        preset_combo.currentIndexChanged.connect(self._update_date_range)

        preset_layout.addWidget(QLabel("Preset:"))
        preset_layout.addWidget(preset_combo)
        preset_layout.addStretch()

        params_layout.addRow("", preset_layout)

        # Add to parent layout
        parent_layout.addWidget(params_group)

        # Create parameter widgets for different event types
        self._create_aspect_parameters()
        self._create_venus_cycle_parameters()
        self._create_saturn_pluto_parameters()
        self._create_retrograde_parameters()
        self._create_lunar_phases_parameters()

        # Initialize parameter visibility
        self._update_parameter_fields()

    def _create_aspect_parameters(self):
        """Create parameter widgets for planetary aspect search."""
        self.aspect_params = QWidget()
        aspect_layout = QFormLayout(self.aspect_params)
        aspect_layout.setContentsMargins(0, 0, 0, 0)

        # Planet 1 selection
        self.aspect_planet1_combo = QComboBox()
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            self.aspect_planet1_combo.addItem(planet, planet)
        aspect_layout.addRow("Planet 1:", self.aspect_planet1_combo)

        # Planet 2 selection
        self.aspect_planet2_combo = QComboBox()
        for planet in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            self.aspect_planet2_combo.addItem(planet, planet)
        self.aspect_planet2_combo.setCurrentIndex(5)  # Default to Jupiter
        aspect_layout.addRow("Planet 2:", self.aspect_planet2_combo)

        # Aspect type selection
        self.aspect_type_combo = QComboBox()

        # Major aspects
        self.aspect_type_combo.addItem("Conjunction (0°)", AspectType.CONJUNCTION)
        self.aspect_type_combo.addItem("Sextile (60°)", AspectType.SEXTILE)
        self.aspect_type_combo.addItem("Square (90°)", AspectType.SQUARE)
        self.aspect_type_combo.addItem("Trine (120°)", AspectType.TRINE)
        self.aspect_type_combo.addItem("Opposition (180°)", AspectType.OPPOSITION)

        # Minor aspects
        self.aspect_type_combo.addItem("Semi-Sextile (30°)", AspectType.SEMISEXTILE)
        self.aspect_type_combo.addItem("Semi-Square (45°)", AspectType.SEMISQUARE)
        self.aspect_type_combo.addItem("Sesquiquadrate (135°)", AspectType.SESQUISQUARE)
        self.aspect_type_combo.addItem("Quincunx (150°)", AspectType.QUINCUNX)

        aspect_layout.addRow("Aspect:", self.aspect_type_combo)

        # Hide initially
        self.aspect_params.hide()

    def _create_venus_cycle_parameters(self):
        """Create parameter widgets for Venus 8-year cycle analysis."""
        self.venus_params = QWidget()
        venus_layout = QFormLayout(self.venus_params)
        venus_layout.setContentsMargins(0, 0, 0, 0)

        # Number of cycles
        self.venus_cycles_combo = QComboBox()
        for i in range(1, 11):
            self.venus_cycles_combo.addItem(f"{i} {'cycle' if i == 1 else 'cycles'}", i)
        self.venus_cycles_combo.setCurrentIndex(2)  # Default to 3 cycles
        venus_layout.addRow("Number of Cycles:", self.venus_cycles_combo)

        # Include visualization
        self.venus_visualize_check = QCheckBox("Include visualization")
        self.venus_visualize_check.setChecked(True)
        venus_layout.addRow("", self.venus_visualize_check)

        # Hide initially
        self.venus_params.hide()

    def _create_saturn_pluto_parameters(self):
        """Create parameter widgets for Saturn-Pluto conjunction search."""
        self.saturn_pluto_params = QWidget()
        sp_layout = QFormLayout(self.saturn_pluto_params)
        sp_layout.setContentsMargins(0, 0, 0, 0)

        # Include historical context
        self.sp_context_check = QCheckBox("Include historical context")
        self.sp_context_check.setChecked(True)
        sp_layout.addRow("", self.sp_context_check)

        # Hide initially
        self.saturn_pluto_params.hide()

    def _create_retrograde_parameters(self):
        """Create parameter widgets for retrograde period search."""
        self.retrograde_params = QWidget()
        retro_layout = QFormLayout(self.retrograde_params)
        retro_layout.setContentsMargins(0, 0, 0, 0)

        # Planet selection
        self.retrograde_planet_combo = QComboBox()
        self.retrograde_planet_combo.addItem("All Planets", None)
        for planet in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
            self.retrograde_planet_combo.addItem(planet, planet)
        retro_layout.addRow("Planet:", self.retrograde_planet_combo)

        # Add a checkbox for showing shadow periods (pre and post retrograde)
        self.retrograde_shadow_check = QCheckBox("Include shadow periods")
        self.retrograde_shadow_check.setChecked(False)
        self.retrograde_shadow_check.setEnabled(False)  # Disabled for now, to be implemented later
        retro_layout.addRow("", self.retrograde_shadow_check)

        # Hide initially
        self.retrograde_params.hide()

    def _create_lunar_phases_parameters(self):
        """Create parameter widgets for lunar phases search."""
        self.lunar_params = QWidget()
        lunar_layout = QFormLayout(self.lunar_params)
        lunar_layout.setContentsMargins(0, 0, 0, 0)

        # Phase type selection
        self.lunar_phase_combo = QComboBox()
        self.lunar_phase_combo.addItem("All Phases", None)
        self.lunar_phase_combo.addItem("New Moon", LunarPhaseType.NEW_MOON)
        self.lunar_phase_combo.addItem("Full Moon", LunarPhaseType.FULL_MOON)
        self.lunar_phase_combo.addItem("First Quarter", LunarPhaseType.FIRST_QUARTER)
        self.lunar_phase_combo.addItem("Last Quarter", LunarPhaseType.LAST_QUARTER)
        lunar_layout.addRow("Phase Type:", self.lunar_phase_combo)

        # Hide initially
        self.lunar_params.hide()

    def _create_results_section(self, parent_layout):
        """Create the results section.

        Args:
            parent_layout: Parent layout to add to
        """
        # Results group
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Date", "Time", "Event", "Details", "Position"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.results_table)

        # Add to parent layout
        parent_layout.addWidget(results_group)

    def _create_buttons(self, parent_layout):
        """Create the button section.

        Args:
            parent_layout: Parent layout to add to
        """
        # Button layout
        button_layout = QHBoxLayout()

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)
        button_layout.addWidget(self.search_button)

        # Export button
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self._export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

        # View Chart button
        self.view_chart_button = QPushButton("View Chart")
        self.view_chart_button.clicked.connect(self._view_chart_for_selected)
        self.view_chart_button.setEnabled(False)
        button_layout.addWidget(self.view_chart_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        # Add to parent layout
        parent_layout.addLayout(button_layout)

    def _update_parameter_fields(self):
        """Update the parameter fields based on the selected event type."""
        # Hide all parameter widgets
        self.aspect_params.hide()
        self.venus_params.hide()
        self.saturn_pluto_params.hide()
        self.retrograde_params.hide()
        if hasattr(self, 'lunar_params'):
            self.lunar_params.hide()

        # Show the appropriate parameter widget
        event_type = self.event_type_combo.currentData()
        if event_type == "aspect":
            self.aspect_params.show()
            self.param_layout.addWidget(self.aspect_params)
        elif event_type == "venus_cycle":
            self.venus_params.show()
            self.param_layout.addWidget(self.venus_params)
        elif event_type == "saturn_pluto":
            self.saturn_pluto_params.show()
            self.param_layout.addWidget(self.saturn_pluto_params)
        elif event_type == "retrograde":
            self.retrograde_params.show()
            self.param_layout.addWidget(self.retrograde_params)
        elif event_type == "lunar_phases":
            self.lunar_params.show()
            self.param_layout.addWidget(self.lunar_params)

    def _update_date_range(self, index):
        """Update the date range based on the selected preset.

        Args:
            index: Selected index in the preset combo
        """
        if index <= 0:
            return  # Custom option selected, do nothing

        # Get end date as current date or the maximum available date, whichever is lower
        today = QDate.currentDate()
        max_available = QDate(self.max_year, 12, 31)
        end_date = today if today < max_available else max_available

        # Get the preset value
        combo = self.sender()
        preset = combo.itemData(index)

        # Calculate start date based on preset
        if preset == "1y":
            start_date = end_date.addYears(-1)
        elif preset == "5y":
            start_date = end_date.addYears(-5)
        elif preset == "10y":
            start_date = end_date.addYears(-10)
        elif preset == "20y":
            start_date = end_date.addYears(-20)
        elif preset == "50y":
            start_date = end_date.addYears(-50)
        elif preset == "100y":
            start_date = end_date.addYears(-100)
        elif preset == "200y":
            start_date = end_date.addYears(-200)
        elif preset == "full":
            # Use the full available date range
            start_date = QDate(self.min_year, 1, 1)
            end_date = QDate(self.max_year, 12, 31)
            self.start_date_edit.setDate(start_date)
            self.end_date_edit.setDate(end_date)
            return

        # Ensure start date is not before the minimum available date
        min_available = QDate(self.min_year, 1, 1)
        if start_date < min_available:
            start_date = min_available

        self.start_date_edit.setDate(start_date)
        self.end_date_edit.setDate(end_date)

    def _perform_search(self):
        """Perform search based on selected parameters."""
        # Clear previous results
        self.results_table.setRowCount(0)

        # Get search parameters
        event_type = self.event_type_combo.currentData()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        # Validate date range
        if start_date > end_date:
            QMessageBox.warning(self, "Invalid Date Range", "Start date must be before end date.")
            return

        # Create progress dialog
        progress = QProgressDialog("Searching...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Search Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        try:
            # Perform search based on event type
            if event_type == "aspect":
                self._search_aspects(start_date, end_date, progress)
            elif event_type == "lunar_phases":
                self._search_lunar_phases(start_date, end_date, progress)
            elif event_type == "venus_cycle":
                self._search_venus_cycle(start_date, progress)
            elif event_type == "saturn_pluto":
                self._search_saturn_pluto(start_date, end_date, progress)
            elif event_type == "retrograde":
                self._search_retrogrades(start_date, end_date, progress)

            # Enable export button if we have results
            self.export_button.setEnabled(self.results_table.rowCount() > 0)

        finally:
            progress.close()

    def _export_results(self):
        """Export search results to a file."""
        # This will be implemented in a future update
        QMessageBox.information(self, "Not Implemented", "Export functionality will be available in a future update.")

    def _view_chart_for_selected(self):
        """View chart for the selected event."""
        # This will be implemented in a future update
        QMessageBox.information(self, "Not Implemented", "Chart viewing functionality will be available in a future update.")

    def _search_aspects(self, start_date, end_date, progress):
        """Search for aspects between selected planets.

        Args:
            start_date: Start date for search
            end_date: End date for search
            progress: Progress dialog
        """
        # Get selected planets and aspect type
        planet1 = self.aspect_planet1_combo.currentData()
        planet2 = self.aspect_planet2_combo.currentData()
        target_aspect_type = self.aspect_type_combo.currentData()

        # Update progress
        progress.setValue(10)
        progress.setLabelText(f"Searching for {target_aspect_type.value} between {planet1} and {planet2}...")

        try:
            # Convert to Python dates for repository query
            start_datetime = datetime.combine(start_date.toPyDate(), datetime.min.time())
            end_datetime = datetime.combine(end_date.toPyDate(), datetime.max.time())

            # Query aspects directly from the repository
            aspects = self.repository.get_aspects(
                start_date=start_datetime,
                end_date=end_datetime,
                planet1=planet1,
                planet2=planet2,
                aspect_type=target_aspect_type.value
            )

            # Update progress
            progress.setValue(50)
            if progress.wasCanceled():
                return

            count = 0
            total = len(aspects)
            logger.info(f"Found {total} aspects between {planet1} and {planet2} ({target_aspect_type.value})")

            # Safely get timezone for display
            try:
                local_tz = datetime.now().astimezone().tzinfo
                # Handle timezone as a string safely
                if hasattr(local_tz, 'tzname'):
                    timezone_name = local_tz.tzname(None) or 'UTC'
                else:
                    timezone_name = str(local_tz) or 'UTC'
            except Exception as e:
                logger.warning(f"Could not determine local timezone: {e}, using UTC")
                timezone_name = 'UTC'

            # Add each aspect to the results table
            for i, aspect in enumerate(aspects):
                # Update progress periodically
                if i % 10 == 0:
                    progress_value = 50 + int((i / total) * 50) if total > 0 else 100
                    progress.setValue(progress_value)
                if progress.wasCanceled():
                    break

                # Get the aspect time and convert to local timezone safely
                aspect_time = aspect['exact_timestamp']
                if aspect_time.tzinfo is None:
                    # Localize if time is naive
                    try:
                        aspect_time = pytz.timezone('UTC').localize(aspect_time)
                        try:
                            # Try to convert to local timezone
                            aspect_time = aspect_time.astimezone()  # Use system default timezone
                        except:
                            # If local timezone conversion fails, stay with UTC
                            pass
                    except Exception as e:
                        logger.warning(f"Timezone conversion failed: {e}, using original time")

                # Format zodiac positions
                body1_position = aspect['exact_position1']
                zodiac_sign1 = self._get_zodiac_sign_for_position(body1_position)
                degrees1 = body1_position % 30

                # Add to results table
                self._add_result_to_table(
                    date=aspect_time.date(),
                    time_value=aspect_time.time(),
                    event=f"{planet1} {target_aspect_type.value} {planet2}",
                    details=f"Exact aspect at {round(degrees1, 1)}° {zodiac_sign1}",
                    position=f"{round(degrees1, 1)}° {zodiac_sign1}"
                )
                count += 1

            # Set final progress and update count
            progress.setValue(100)
            if count == 0:
                logger.info(f"No matching aspects found in the specified date range")
                QMessageBox.information(self, "No Results",
                    f"No {target_aspect_type.value} aspects between {planet1} and {planet2} found in the specified date range.")
            else:
                logger.info(f"Added {count} aspects to the results table")

        except Exception as e:
            logger.error(f"Error searching for aspects: {e}", exc_info=True)
            QMessageBox.warning(self, "Search Error", f"An error occurred while searching for aspects: {e}")

    def _get_zodiac_sign_for_position(self, position: float) -> str:
        """Get the zodiac sign for a given position in degrees.

        Args:
            position: Position in degrees (0-360)

        Returns:
            Zodiac sign name
        """
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        sign_index = int(position / 30) % 12
        return signs[sign_index]

    def _search_venus_cycle(self, start_date, progress):
        """Search for Venus 8-year cycle patterns.

        Args:
            start_date: Start date for analysis (QDate)
            progress: Progress dialog
        """
        # Get number of cycles
        num_cycles = self.venus_cycles_combo.currentData()

        # Venus completes 5 synodic periods in almost exactly 8 years
        # (13 Venus years ≈ 8 Earth years)
        cycle_length_days = 365.25 * 8

        # Log search parameters
        logger.debug(f"Analyzing Venus 8-year cycle starting from {start_date}, {num_cycles} cycles")

        # Update progress
        progress.setValue(10)
        if progress.wasCanceled():
            return

        # Convert QDate to Python datetime for calculation
        start_datetime = datetime.combine(start_date.toPyDate(), datetime.min.time())

        # Calculate end date for the analysis
        end_datetime = start_datetime + timedelta(days=int(cycle_length_days * num_cycles))

        # Convert back to QDate for display consistency
        end_date = QDate(end_datetime.year, end_datetime.month, end_datetime.day)

        # Add cycle start point
        self._add_result_to_table(
            date=start_datetime.date(),
            time_value=datetime.min.time(),
            event="Venus Cycle Analysis",
            details=f"Starting point for {num_cycles} cycle analysis",
            position="N/A"
        )

        # Add cycle points
        for i in range(1, num_cycles + 1):
            # Calculate cycle completion date
            cycle_datetime = start_datetime + timedelta(days=int(cycle_length_days * i))

            self._add_result_to_table(
                date=cycle_datetime.date(),
                time_value=datetime.min.time(),
                event=f"Venus Cycle {i} Completion",
                details=f"End of {i} complete 8-year cycle{'s' if i > 1 else ''}",
                position="N/A"
            )

            # Update progress - ensure value is an integer
            progress_value = int(10 + (i / num_cycles) * 90)
            progress.setValue(progress_value)
            if progress.wasCanceled():
                break

        # Add note about the pattern
        self._add_result_to_table(
            date=end_datetime.date(),
            time_value=datetime.min.time(),
            event="Venus Cycle Pattern",
            details="Venus traces a five-pointed star pattern over each 8-year cycle",
            position="N/A"
        )

    def _search_saturn_pluto(self, start_date, end_date, progress):
        """Search for Saturn-Pluto conjunctions.

        Args:
            start_date: Start date for search (QDate)
            end_date: End date for search (QDate)
            progress: Progress dialog
        """
        # Update progress dialog
        progress.setValue(10)
        progress.setLabelText("Searching for Saturn-Pluto conjunctions...")

        try:
            # Convert QDate to Python datetime
            start_datetime = datetime.combine(start_date.toPyDate(), datetime.min.time())
            end_datetime = datetime.combine(end_date.toPyDate(), datetime.max.time())

            # Query conjunctions directly from the repository
            # Saturn-Pluto conjunctions are simply aspects of type "conjunction" between Saturn and Pluto
            conjunctions = self.repository.get_aspects(
                start_date=start_datetime,
                end_date=end_datetime,
                planet1="Saturn",
                planet2="Pluto",
                aspect_type="conjunction"
            )

            # Update progress
            progress.setValue(50)
            if progress.wasCanceled():
                return

            count = 0
            total = len(conjunctions)
            logger.info(f"Found {total} Saturn-Pluto conjunctions")

            # Include historical context if checked
            include_context = self.sp_context_check.isChecked()

            # Safely get timezone for display
            try:
                local_tz = datetime.now().astimezone().tzinfo
                # Handle timezone as a string safely
                if hasattr(local_tz, 'tzname'):
                    timezone_name = local_tz.tzname(None) or 'UTC'
                else:
                    timezone_name = str(local_tz) or 'UTC'
            except Exception as e:
                logger.warning(f"Could not determine local timezone: {e}, using UTC")
                timezone_name = 'UTC'

            # Add results to table
            for i, conjunction in enumerate(conjunctions):
                # Update progress periodically
                if i % 10 == 0:
                    progress_value = 50 + int((i / total) * 50) if total > 0 else 100
                    progress.setValue(progress_value)
                if progress.wasCanceled():
                    break

                # Get the conjunction time and convert to local timezone safely
                conjunction_time = conjunction['exact_timestamp']
                if conjunction_time.tzinfo is None:
                    # Localize if time is naive
                    try:
                        conjunction_time = pytz.timezone('UTC').localize(conjunction_time)
                        try:
                            # Try to convert to local timezone
                            conjunction_time = conjunction_time.astimezone()  # Use system default timezone
                        except:
                            # If local timezone conversion fails, stay with UTC
                            pass
                    except Exception as e:
                        logger.warning(f"Timezone conversion failed: {e}, using original time")

                # Format position details
                position = conjunction['exact_position1']
                zodiac_sign = self._get_zodiac_sign_for_position(position)
                degrees = position % 30

                # Add to results table
                self._add_result_to_table(
                    date=conjunction_time.date(),
                    time_value=conjunction_time.time(),
                    event="Saturn-Pluto Conjunction",
                    details=f"Exact conjunction in {zodiac_sign}",
                    position=f"{round(degrees, 1)}° {zodiac_sign}"
                )
                count += 1

                # Add historical context if requested
                if include_context:
                    context = self._get_saturn_pluto_context(conjunction_time.date())
                    if context:
                        self._add_result_to_table(
                            date=conjunction_time.date(),
                            time_value=conjunction_time.time(),
                            event="Historical Context",
                            details=context,
                            position="N/A"
                        )

            # Set final progress and update count
            progress.setValue(100)
            if count == 0:
                logger.info(f"No Saturn-Pluto conjunctions found in the specified date range")
                QMessageBox.information(self, "No Results",
                    "No Saturn-Pluto conjunctions found in the specified date range.")
            else:
                logger.info(f"Added {count} Saturn-Pluto conjunctions to the results table")

        except Exception as e:
            logger.error(f"Error searching for Saturn-Pluto conjunctions: {e}", exc_info=True)
            QMessageBox.warning(self, "Search Error",
                f"An error occurred while searching for Saturn-Pluto conjunctions: {e}")

    def _search_retrogrades(self, start_date, end_date, progress):
        """Search for retrograde periods.

        Args:
            start_date: Start date for search (QDate)
            end_date: End date for search (QDate)
            progress: Progress dialog
        """
        # Get selected planet (or all planets)
        planet_combo = getattr(self, 'retrograde_planet_combo', None)
        selected_planet = planet_combo.currentData() if planet_combo else None
        planet_name = planet_combo.currentText() if planet_combo and selected_planet else "All Planets"

        # Update progress dialog
        progress.setValue(10)
        progress.setLabelText(f"Searching for retrograde periods of {planet_name}...")

        try:
            # Convert QDate to Python datetime
            start_datetime = datetime.combine(start_date.toPyDate(), datetime.min.time())
            end_datetime = datetime.combine(end_date.toPyDate(), datetime.max.time())

            # Query retrograde periods from the repository
            # Retrograde periods are stored as planet phases with phase_type "stationary_retrograde" and "stationary_direct"
            retrograde_query = {
                'start_date': start_datetime,
                'end_date': end_datetime,
                'phase_type': PlanetPhaseType.STATIONARY_RETROGRADE.value  # Convert enum to string
            }

            direct_query = {
                'start_date': start_datetime,
                'end_date': end_datetime,
                'phase_type': PlanetPhaseType.STATIONARY_DIRECT.value  # Convert enum to string
            }

            # Only add body_name if it's not None
            if selected_planet is not None:
                retrograde_query['body_name'] = selected_planet
                direct_query['body_name'] = selected_planet

            retrograde_phases = self.repository.get_planet_phases(**retrograde_query)
            direct_phases = self.repository.get_planet_phases(**direct_query)

            # Update progress
            progress.setValue(50)
            if progress.wasCanceled():
                return

            # Process retrograde stations
            count = 0
            total_events = len(retrograde_phases) + len(direct_phases)
            logger.info(f"Found {len(retrograde_phases)} retrograde stations and {len(direct_phases)} direct stations")

            # Safely get timezone for display
            try:
                local_tz = datetime.now().astimezone().tzinfo
                # Handle timezone as a string safely
                if hasattr(local_tz, 'tzname'):
                    timezone_name = local_tz.tzname(None) or 'UTC'
                else:
                    timezone_name = str(local_tz) or 'UTC'
            except Exception as e:
                logger.warning(f"Could not determine local timezone: {e}, using UTC")
                timezone_name = 'UTC'

            # Add retrograde stations to results
            for i, phase in enumerate(retrograde_phases):
                try:
                    # Update progress periodically
                    if total_events > 0:
                        progress_value = 50 + int((i / total_events) * 25)
                    else:
                        progress_value = 75
                    progress.setValue(progress_value)

                    if progress.wasCanceled():
                        break

                    # Get the phase time
                    phase_time = phase['timestamp']

                    # Get zodiac sign - handle both string format and numeric format
                    zodiac_sign_value = phase.get('zodiac_sign')
                    if zodiac_sign_value is not None:
                        if isinstance(zodiac_sign_value, str):
                            # If it's already a string like "Sagittarius", use it directly
                            zodiac_sign = zodiac_sign_value
                        else:
                            # If it's a numeric index, convert to position and get sign
                            try:
                                # Convert to float first to handle different numeric types
                                zodiac_value_num = float(zodiac_sign_value)
                                zodiac_sign = self._get_zodiac_sign_for_position(zodiac_value_num * 30)
                            except (ValueError, TypeError):
                                zodiac_sign = "Unknown Sign"
                    else:
                        zodiac_sign = "Unknown Sign"

                    planet = phase.get('body_name', "Unknown Planet")

                    # Add to results table
                    self._add_result_to_table(
                        date=phase_time.date(),
                        time_value=phase_time.time(),
                        event=f"{planet} Stations Retrograde",
                        details=f"Begins retrograde motion in {zodiac_sign}",
                        position=f"{zodiac_sign}"
                    )
                    count += 1
                except Exception as phase_err:
                    logger.error(f"Error processing retrograde phase: {phase_err}")
                    # Continue with next phase
                    continue

            # Add direct stations to results
            for i, phase in enumerate(direct_phases):
                try:
                    # Update progress periodically
                    if total_events > 0:
                        progress_value = 75 + int((i / total_events) * 25)
                    else:
                        progress_value = 100
                    progress.setValue(progress_value)

                    if progress.wasCanceled():
                        break

                    # Get the phase time
                    phase_time = phase['timestamp']

                    # Get zodiac sign - handle both string format and numeric format
                    zodiac_sign_value = phase.get('zodiac_sign')
                    if zodiac_sign_value is not None:
                        if isinstance(zodiac_sign_value, str):
                            # If it's already a string like "Leo", use it directly
                            zodiac_sign = zodiac_sign_value
                        else:
                            # If it's a numeric index, convert to position and get sign
                            try:
                                # Convert to float first to handle different numeric types
                                zodiac_value_num = float(zodiac_sign_value)
                                zodiac_sign = self._get_zodiac_sign_for_position(zodiac_value_num * 30)
                            except (ValueError, TypeError):
                                zodiac_sign = "Unknown Sign"
                    else:
                        zodiac_sign = "Unknown Sign"

                    planet = phase.get('body_name', "Unknown Planet")

                    # Add to results table
                    self._add_result_to_table(
                        date=phase_time.date(),
                        time_value=phase_time.time(),
                        event=f"{planet} Stations Direct",
                        details=f"Resumes forward motion in {zodiac_sign}",
                        position=f"{zodiac_sign}"
                    )
                    count += 1
                except Exception as phase_err:
                    logger.error(f"Error processing direct phase: {phase_err}")
                    # Continue with next phase
                    continue

            # Set final progress and update count
            progress.setValue(100)
            if count == 0:
                logger.info(f"No retrograde periods found in the specified date range")
                QMessageBox.information(self, "No Results",
                    f"No retrograde periods for {planet_name} found in the specified date range.")
            else:
                logger.info(f"Added {count} retrograde events to the results table")

        except Exception as e:
            logger.error(f"Error searching for retrograde periods: {e}", exc_info=True)
            QMessageBox.warning(self, "Search Error",
                f"An error occurred while searching for retrograde periods: {e}")

    def _search_lunar_phases(self, start_date, end_date, progress):
        """Search for lunar phases.

        Args:
            start_date: Start date for search (QDate)
            end_date: End date for search (QDate)
            progress: Progress dialog
        """
        # Get selected phase type, if any
        phase_type = self.lunar_phase_combo.currentData()
        phase_type_name = self.lunar_phase_combo.currentText() if phase_type else "All Lunar Phases"

        # Update progress dialog
        progress.setValue(10)
        progress.setLabelText(f"Searching for {phase_type_name}...")

        try:
            # Convert QDate to Python datetime
            start_datetime = datetime.combine(start_date.toPyDate(), datetime.min.time())
            end_datetime = datetime.combine(end_date.toPyDate(), datetime.max.time())

            # Debug log the query parameters
            logger.debug(f"Lunar phases search params: start={start_datetime}, end={end_datetime}")
            if phase_type:
                logger.debug(f"Phase type: {phase_type}, value: {phase_type.value}, type: {type(phase_type)}")

            # Query lunar phases from the repository
            # Only pass phase_type if it's not None, and convert enum to string
            query_params = {
                'start_date': start_datetime,
                'end_date': end_datetime
            }

            if phase_type is not None:
                # Convert enum to string value before passing to repository
                query_params['phase_type'] = phase_type.value
                logger.debug(f"Using phase_type query param: {query_params['phase_type']}")

            try:
                lunar_phases = self.repository.get_lunar_phases(**query_params)
                logger.debug(f"Repository query successful, returned {len(lunar_phases)} results")
            except Exception as repo_error:
                logger.error(f"Error in repository query: {repo_error}", exc_info=True)
                raise

            # Update progress
            progress.setValue(50)
            if progress.wasCanceled():
                return

            count = 0
            total = len(lunar_phases)
            logger.info(f"Found {total} lunar phases matching criteria")

            # Debug log the first result to understand its structure
            if total > 0:
                logger.debug(f"First result structure: {lunar_phases[0]}")
                logger.debug(f"phase_type value: {lunar_phases[0]['phase_type']}, type: {type(lunar_phases[0]['phase_type'])}")
                logger.debug(f"moon_position value: {lunar_phases[0]['moon_position']}, type: {type(lunar_phases[0]['moon_position'])}")
                logger.debug(f"zodiac_sign value: {lunar_phases[0]['zodiac_sign']}, type: {type(lunar_phases[0]['zodiac_sign'])}")

            # Safely get timezone for display
            try:
                local_tz = datetime.now().astimezone().tzinfo
                # Handle timezone as a string safely
                if hasattr(local_tz, 'tzname'):
                    timezone_name = local_tz.tzname(None) or 'UTC'
                else:
                    timezone_name = str(local_tz) or 'UTC'
            except Exception as e:
                logger.warning(f"Could not determine local timezone: {e}, using UTC")
                timezone_name = 'UTC'

            # Add results to table
            for i, phase in enumerate(lunar_phases):
                try:
                    # Update progress periodically
                    if i % 10 == 0:
                        progress_value = 50 + int((i / total) * 50) if total > 0 else 100
                        progress.setValue(progress_value)
                        if progress.wasCanceled():
                            break

                    # Debug log problematic fields when we approach the error
                    if i >= 195 and i < 197:  # Log around the potential error point
                        logger.debug(f"Processing phase {i}: {phase}")

                    # Get the phase time and convert to local timezone safely
                    phase_time = phase['timestamp']
                    if phase_time.tzinfo is None:
                        # Localize if time is naive
                        try:
                            phase_time = pytz.timezone('UTC').localize(phase_time)
                            phase_time = phase_time.astimezone(pytz.timezone('UTC'))  # First convert to UTC
                            try:
                                # Then try to convert to local timezone if possible
                                phase_time = phase_time.astimezone()  # Use system default timezone
                            except Exception as e:
                                logger.warning(f"Local timezone conversion failed: {e}")
                                # If local timezone conversion fails, stay with UTC
                                pass
                        except Exception as e:
                            logger.warning(f"Timezone conversion failed: {e}, using original time")

                    # Get zodiac sign - handle different types of zodiac_sign values
                    try:
                        # If zodiac_sign is a string (like 'Aries'), use it directly
                        if isinstance(phase['zodiac_sign'], str):
                            zodiac_sign = phase['zodiac_sign']
                        # If zodiac_sign is a number (0-11), convert using our helper function
                        elif isinstance(phase['zodiac_sign'], (int, float)):
                            # If moon_position is present, use that for more accurate sign
                            if 'moon_position' in phase and phase['moon_position'] is not None:
                                zodiac_sign = self._get_zodiac_sign_for_position(phase['moon_position'])
                            else:
                                # Multiply zodiac_sign by 30 to get position in degrees (0=Aries, 1=Taurus, etc.)
                                zodiac_sign = self._get_zodiac_sign_for_position(phase['zodiac_sign'] * 30)
                        else:
                            # Fallback
                            zodiac_sign = "Unknown Sign"
                            logger.warning(f"Unknown zodiac_sign type: {type(phase['zodiac_sign'])}")
                    except Exception as e:
                        logger.warning(f"Error determining zodiac sign: {e}")
                        zodiac_sign = "Unknown Sign"

                    # Format display details - ensure phase_type is handled as a string
                    phase_type_value = phase['phase_type']
                    if not isinstance(phase_type_value, str):
                        # Handle the case where phase_type might not be a string
                        logger.warning(f"phase_type is not a string: {phase_type_value}, type: {type(phase_type_value)}")
                        if hasattr(phase_type_value, 'value'):  # If it's an enum
                            phase_type_value = phase_type_value.value
                        else:
                            phase_type_value = str(phase_type_value)

                    phase_title = phase_type_value.replace('_', ' ').title()

                    # Safely get moon position for display
                    moon_position = phase.get('moon_position')
                    if moon_position is not None:
                        position_text = f"{round(moon_position % 30, 1)}° {zodiac_sign}"
                    else:
                        position_text = zodiac_sign

                    # Add to results table
                    self._add_result_to_table(
                        date=phase_time.date(),
                        time_value=phase_time.time(),
                        event=phase_title,
                        details=f"Moon in {zodiac_sign}",
                        position=position_text
                    )
                    count += 1
                except Exception as loop_err:
                    logger.error(f"Error processing phase {i}: {loop_err}", exc_info=True)
                    # Continue with next phase rather than breaking the entire loop
                    continue

            # Set final progress and update count
            progress.setValue(100)
            if count == 0:
                logger.info(f"No lunar phases found in the specified date range")
                QMessageBox.information(self, "No Results",
                    f"No {phase_type_name.lower()} found in the specified date range.")
            else:
                logger.info(f"Added {count} lunar phases to the results table")

        except Exception as e:
            logger.error(f"Error searching for lunar phases: {e}", exc_info=True)
            QMessageBox.warning(self, "Search Error",
                f"An error occurred while searching for lunar phases: {e}")

    def _add_result_to_table(self, date, time_value, event, details, position):
        """Add a result to the results table.

        Args:
            date: Date of the event
            time_value: Time of the event
            event: Event name/description
            details: Additional details
            position: Zodiac position
        """
        # Add a new row
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # Format date and time
        date_str = date.strftime("%Y-%m-%d")
        # Use type name checking to avoid conflict with datetime.time
        time_str = "--:--"
        if time_value is not None:
            if type(time_value).__name__ == 'time':
                time_str = time_value.strftime("%H:%M")
        else:
                try:
                    time_str = str(time_value)
                except:
                    time_str = "--:--"

        # Create items
        date_item = QTableWidgetItem(date_str)
        time_item = QTableWidgetItem(time_str)
        event_item = QTableWidgetItem(event)
        details_item = QTableWidgetItem(details)
        position_item = QTableWidgetItem(position)

        # Set items
        self.results_table.setItem(row, 0, date_item)
        self.results_table.setItem(row, 1, time_item)
        self.results_table.setItem(row, 2, event_item)
        self.results_table.setItem(row, 3, details_item)
        self.results_table.setItem(row, 4, position_item)

        # Enable view chart button
        self.view_chart_button.setEnabled(True)

    def _get_planet_id(self, planet_name):
        """Get the Swiss Ephemeris planet ID for a planet name.

        Args:
            planet_name: Name of the planet

        Returns:
            Swiss Ephemeris planet ID or None if not found
        """
        import swisseph as swe

        planet_map = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Uranus": swe.URANUS,
            "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO
        }

        return planet_map.get(planet_name)

    def _get_saturn_pluto_context(self, date):
        """Get historical context for a Saturn-Pluto conjunction.

        Args:
            date: Date of the conjunction

        Returns:
            Historical context string
        """
        # Historical contexts for major Saturn-Pluto conjunctions
        contexts = {
            1914: "World War I begins",
            1947: "Cold War begins",
            1982: "Economic recession, Cold War tensions",
            2020: "COVID-19 pandemic"
        }

        # Find the closest year
        year = date.year
        closest_year = min(contexts.keys(), key=lambda y: abs(y - year))

        if abs(closest_year - year) <= 2:  # Within 2 years
            return f"{contexts[closest_year]} ({closest_year})"
        else:
            return "Major structural transformation"
