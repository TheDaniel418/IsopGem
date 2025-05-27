"""
Defines the main window for the Stonehenge Eclipse Predictor simulation
and the Adyton of the Seven visualization.

This window houses the visualization of the Aubrey Holes, marker movements,
controls for the simulation, and a log for predicted eclipses. It also provides
access to the 3D Adyton visualization which represents the pillars of the seven.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-08-12
Dependencies: PyQt6, PyOpenGL (for 3D visualization)
"""

import webbrowser  # Added for opening URLs
from datetime import datetime

from kerykeion import AstrologicalSubject
from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import ChartType, NatalChart
from astrology.models.eclipse_data import EclipseData
from astrology.services.chart_service import ChartService
from astrology.services.eclipse_catalog_service import EclipseCatalogService
from astrology.services.ephemeris_service import EphemerisService
from astrology.services.location_service import Location  # Added this import
from astrology.services.stonehenge_simulation_service import StonehengeSimulationService
from astrology.ui.dialogs.ancient_date_dialog import AncientDateDialog
from astrology.ui.dialogs.location_search_window import LocationSearchWindow
from astrology.ui.widgets.stonehenge_predictor.circle_view_widget import (
    CircleViewWidget,
)
from astrology.ui.widgets.stonehenge_predictor.controls_panel_widget import (
    ControlsPanelWidget,
)
from astrology.ui.widgets.stonehenge_predictor.eclipse_catalog_widget import (
    EclipseCatalogWidget,
)
from astrology.ui.widgets.stonehenge_predictor.eclipse_log_view_widget import (
    EclipseLogViewWidget,
)
from astrology.ui.widgets.stonehenge_predictor.hole_reference_widget import (
    HoleReferenceWidget,
)
from astrology.ui.widgets.stonehenge_predictor.adyton_window import AdytonWindow

# Assuming your window management might need a specific base or registration
# For now, a standard QMainWindow


class StonehengePredictorWindow(QMainWindow):
    """
    Main application window for the Stonehenge Eclipse Predictor simulation.
    Manages the layout of the simulation view, controls, and log.
    """

    def _initialize_gregorian_start_date_tracker(self):
        self._simulation_gregorian_start_date: QDate | None = None

    def __init__(self, parent=None):
        """
        Initializes the StonehengePredictorWindow.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self.setWindowTitle("Circle of 56: Stonehenge Eclipse Predictor")
        self.setGeometry(100, 100, 1000, 800)

        self._initialize_gregorian_start_date_tracker()  # Call the new method
        self.placeholder_label = None  # Initialize placeholder_label for safety
        
        # Set default location to Luxor, Egypt
        self.current_latitude = 25.6872  # Luxor, Egypt latitude
        self.current_longitude = 32.6396  # Luxor, Egypt longitude
        self.default_location_name = "Luxor, Egypt"

        self.ephemeris_service = EphemerisService()
        self.simulation_service = StonehengeSimulationService(proximity_threshold=1)
        self.eclipse_catalog_service = EclipseCatalogService(
            "assets/ephemeris/eclipse_besselian_from_mysqldump2.csv"
        )

        self.eclipse_catalog_widget = EclipseCatalogWidget(self.eclipse_catalog_service)
        self.controls_panel = ControlsPanelWidget()
        self.circle_view = CircleViewWidget()
        self.eclipse_log_view = EclipseLogViewWidget()
        self.hole_reference_widget = HoleReferenceWidget()  # Add the new widget

        # Initialize the auto-run timer and interval
        self.auto_run_timer = QTimer(self)
        self.current_auto_run_interval = 1000  # Default to 1000ms (1 second)
        self.auto_run_timer.timeout.connect(self._next_step)

        self._init_simulation_and_ui()
        self._connect_signals()
        
        # Set default epoch to Dec 21, 2020 and apply orientation
        self._apply_default_epoch()

    def _init_simulation_and_ui(self):
        """Initialize the simulation and user interface components with a tabbed layout."""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Set a larger minimum window size
        self.setMinimumSize(800, 600)

        # Create tab widget to organize components
        self.tab_widget = QTabWidget()
        # Configure tab widget to expand and take all available space
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Tab 1: Stonehenge Circle View
        circle_tab = QWidget()
        circle_layout = QVBoxLayout(circle_tab)
        circle_layout.setContentsMargins(
            10, 10, 10, 10
        )  # Add some padding around the circle

        # Make the circle view much larger and ensure it expands properly
        self.circle_view.setMinimumSize(500, 500)
        self.circle_view.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Create a frame to contain the circle view for better visual separation
        circle_frame = QFrame()
        circle_frame.setFrameShape(QFrame.Shape.StyledPanel)
        circle_frame.setFrameShadow(QFrame.Shadow.Raised)
        circle_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Add the circle view to a layout within the frame
        circle_frame_layout = QVBoxLayout(circle_frame)
        circle_frame_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No internal margins in the frame
        circle_frame_layout.addWidget(self.circle_view)

        # Add the frame to the main circle tab layout
        circle_layout.addWidget(circle_frame, 1)

        # Add controls for zodiacal degree display
        zodiac_control_layout = QHBoxLayout()
        self.show_zodiac_checkbox = QCheckBox("Show Zodiacal Degrees")
        self.show_zodiac_checkbox.setChecked(True)  # Default to showing zodiac degrees
        self.show_zodiac_checkbox.toggled.connect(self._toggle_zodiac_degrees)
        
        # Add toggle for showing/hiding Node markers
        self.show_nodes_checkbox = QCheckBox("Show Nodes")
        self.show_nodes_checkbox.setChecked(True)  # Default to showing nodes
        self.show_nodes_checkbox.toggled.connect(self._toggle_nodes_visibility)
        
        # Add toggle for showing/hiding Sun/Moon markers
        self.show_sun_moon_checkbox = QCheckBox("Show Sun/Moon")
        self.show_sun_moon_checkbox.setChecked(True)  # Default to showing Sun/Moon
        self.show_sun_moon_checkbox.toggled.connect(self._toggle_sun_moon_visibility)

        # Add a button to update GC alignment
        self.update_gc_button = QPushButton("Update GC & Zodiac Alignment")
        self.update_gc_button.clicked.connect(self._handle_update_gc_alignment)
        
        # Add zoom control buttons
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.setToolTip("Zoom in (or use mouse wheel)")
        self.zoom_in_button.clicked.connect(self._handle_zoom_in)
        
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.setToolTip("Zoom out (or use mouse wheel)")
        self.zoom_out_button.clicked.connect(self._handle_zoom_out)
        
        self.reset_view_button = QPushButton("Reset View")
        self.reset_view_button.setToolTip("Reset zoom and pan (or double-click)")
        self.reset_view_button.clicked.connect(self._handle_reset_view)
        
        # Add button to launch 3D Adyton view - REMOVED FROM HERE
        # self.open_3d_view_button = QPushButton("Open 3D Adyton View")
        # self.open_3d_view_button.setStyleSheet("background-color: #4b6eaf; color: white;")
        # self.open_3d_view_button.setToolTip("Open the 3D visualization of the Adyton of the Seven")
        # self.open_3d_view_button.clicked.connect(self.launch_adyton_viewer) # Changed from _handle_open_3d_view

        zodiac_control_layout.addWidget(self.show_zodiac_checkbox)
        zodiac_control_layout.addWidget(self.show_nodes_checkbox)
        zodiac_control_layout.addWidget(self.show_sun_moon_checkbox)
        zodiac_control_layout.addWidget(self.update_gc_button)
        # zodiac_control_layout.addWidget(self.open_3d_view_button) # REMOVED FROM HERE
        zodiac_control_layout.addStretch(1)
        zodiac_control_layout.addWidget(self.zoom_out_button)
        zodiac_control_layout.addWidget(self.reset_view_button)
        zodiac_control_layout.addWidget(self.zoom_in_button)

        circle_layout.addLayout(zodiac_control_layout)

        # Add a small control strip below the circle if needed
        status_layout = QHBoxLayout()
        status_label = QLabel("Position Status:")
        status_label.setStyleSheet("font-weight: bold;")
        self.position_status = QLabel(
            "No zodiac positions available - use 'Set GC Epoch & Orient' to set alignment"
        )
        self.position_status.setWordWrap(True)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.position_status, 1)
        circle_layout.addLayout(status_layout)
        
        # Add interaction hints
        interaction_layout = QHBoxLayout()
        interaction_label = QLabel(
            "<i>Interactions: Use mouse wheel to zoom, drag to pan, double-click to reset view</i>"
        )
        interaction_label.setStyleSheet("color: #666666; font-size: 10px;")
        interaction_layout.addWidget(interaction_label)
        circle_layout.addLayout(interaction_layout)

        self.tab_widget.addTab(circle_tab, "Circle View")

        # Tab 2: Hole Reference Table
        reference_tab = QWidget()
        reference_layout = QVBoxLayout(reference_tab)
        reference_layout.addWidget(self.hole_reference_widget)
        self.tab_widget.addTab(reference_tab, "Hole Reference")

        # Tab 3: Controls Panel
        controls_tab = QWidget()
        controls_layout = QVBoxLayout(controls_tab)
        controls_layout.addWidget(self.controls_panel)
        controls_layout.addWidget(
            self.eclipse_log_view, 1
        )  # Give log view the ability to expand
        self.tab_widget.addTab(controls_tab, "Controls & Log")

        # Tab 4: Eclipse Catalog
        catalog_tab = QWidget()
        catalog_layout = QVBoxLayout(catalog_tab)
        catalog_layout.addWidget(self.eclipse_catalog_widget)
        self.tab_widget.addTab(catalog_tab, "Eclipse Catalog")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Initialize the simulation and UI state
        self.simulation_service.reset_simulation(proximity_threshold=1)
        self._simulation_gregorian_start_date = None  # Reset here
        self._update_simulation_display()
        self.eclipse_log_view.clear_log()
        self.eclipse_log_view.add_log_message(
            "Welcome to the Stonehenge Eclipse Predictor!"
        )
        self.eclipse_log_view.add_log_message(
            "Initialize simulation or load an eclipse."
        )
        self.circle_view.set_orientation(0.0)

        # Connect a resize event listener to ensure proper layout updates
        self.resizeEvent = self._handle_window_resize

    def _update_simulation_display(self):
        """
        Updates the UI elements to reflect the current state of the simulation.
        This includes the time display on the controls panel and the marker positions
        on the circle view.
        """
        if not self.simulation_service:
            self.eclipse_log_view.add_log_message(
                "Error: Simulation service not available for UI update."
            )
            return

        # Assuming StonehengeSimulationService has these getter methods or public attributes
        # We will add get_current_day and get_current_year to the service.
        # get_current_marker_positions should already exist.
        try:
            current_day = self.simulation_service.get_current_day()
            current_year = self.simulation_service.get_current_year()
            current_positions = self.simulation_service.get_current_marker_positions()
        except AttributeError as e:
            self.eclipse_log_view.add_log_message(
                f"Error: Missing method in SimulationService: {e}"
            )
            return

        if self.controls_panel:
            self.controls_panel.update_time_display(current_day, current_year)

        if self.circle_view:
            self.circle_view.update_marker_positions(current_positions)
            # Clear any zodiac position labels when simulation is updated
            self.circle_view.update_marker_zodiac_positions(
                {"S": None, "M": None, "N": None, "N'": None}
            )

            # Update the hole reference widget with marker positions
            if hasattr(self, "hole_reference_widget"):
                self.hole_reference_widget.update_marker_positions(current_positions)
                
            # Update 3D view if Adyton window is open
            if hasattr(self, "adyton_window") and self.adyton_window is not None:
                if not self.adyton_window.isVisible():
                    # Clean up reference if window was closed
                    self.adyton_window = None
                else:
                    # This part is for marker positions in 3D (if ever implemented directly)
                    # self.adyton_window.update_marker_positions(current_positions)
                    pass # Pass if no other action needed when Adyton window is visible here

        # Reset the position status display
        if hasattr(self, "position_status"):
            self.position_status.setText(
                "No zodiac positions available - use 'Set GC Epoch & Orient' to set alignment"
            )

    def _handle_set_from_ephemeris_date(self, date_qdate: QDate):
        if not self.simulation_service:
            self.eclipse_log_view.add_log_message(
                "Error: Simulation service not initialized."
            )
            return

        log_message = f"Attempting to set markers from ephemeris for {date_qdate.toString('yyyy-MM-dd')}..."
        self.eclipse_log_view.add_log_message(log_message)

        new_positions = self.simulation_service.initialize_markers_from_ephemeris(
            date_qdate
        )

        if new_positions:
            self._simulation_gregorian_start_date = date_qdate  # Set on success
            self.circle_view.update_marker_positions(new_positions)
            self.eclipse_log_view.add_log_message(
                f"<b><font color='green'>Success!</font></b> Markers set from ephemeris for {date_qdate.toString('yyyy-MM-dd')}.<br>"
                f"Hoyle simulation time has been reset to Day 1, Year 1.<br>"
                f"Marker positions: {', '.join([f'{k}:{v}' for k,v in new_positions.items()])}"
            )
        else:
            self._simulation_gregorian_start_date = None  # Clear on failure
            self.eclipse_log_view.add_log_message(
                f"<b><font color='red'>Failed.</font></b> Could not retrieve ephemeris data or set markers for {date_qdate.toString('yyyy-MM-dd')}. Please check console output."
            )
        # self.controls_panel.reset_alignment_inputs_to_default() # This was moved to _reset_simulation_from_ephemeris/almanac

    def _handle_set_from_almanac(self, selected_eclipse: EclipseData):
        if not self.simulation_service or not self.ephemeris_service:
            self.eclipse_log_view.add_log_message(
                "Error: Services not initialized for Almanac operation."
            )
            return

        try:
            eclipse_qdate = QDate.fromString(
                selected_eclipse.calendar_date, "yyyy-MM-dd"
            )
            if not eclipse_qdate.isValid():
                self.eclipse_log_view.add_log_message(
                    f"Error: Invalid date string '{selected_eclipse.calendar_date}' from almanac."
                )
                self._simulation_gregorian_start_date = (
                    None  # Clear on conversion failure
                )
                return
        except Exception as e:
            self.eclipse_log_view.add_log_message(f"Error converting almanac date: {e}")
            self._simulation_gregorian_start_date = (
                None  # Clear on conversion exception
            )
            return

        log_message = f"Attempting to set markers from Almanac for selected eclipse: {eclipse_qdate.toString('yyyy-MM-dd')} (Cat: {selected_eclipse.catalog_number})..."
        self.eclipse_log_view.add_log_message(log_message)

        new_positions = self.simulation_service.initialize_markers_from_ephemeris(
            eclipse_qdate
        )

        if new_positions:
            self._simulation_gregorian_start_date = eclipse_qdate  # Set on success
            self.circle_view.update_marker_positions(new_positions)
            self.eclipse_log_view.add_log_message(
                f"<b><font color='green'>Success!</font></b> Markers set from Almanac for {eclipse_qdate.toString('yyyy-MM-dd')}.<br>"
                f"Hoyle simulation time has been reset to Day 1, Year 1.<br>"
                f"Marker positions: {', '.join([f'{k}:{v}' for k,v in new_positions.items()])}"
            )
        else:
            self._simulation_gregorian_start_date = None  # Clear on failure
            self.eclipse_log_view.add_log_message(
                f"<b><font color='red'>Failed.</font></b> Could not set markers from Almanac for {eclipse_qdate.toString('yyyy-MM-dd')}. Please check console output."
            )
        # self.controls_panel.reset_alignment_inputs_to_default() # This was moved to _reset_simulation_from_ephemeris/almanac

    def _connect_signals(self):
        self.controls_panel.next_step_requested.connect(self._next_step)
        self.controls_panel.reset_requested.connect(self._reset_simulation)
        self.controls_panel.auto_run_toggled.connect(self._handle_auto_run_toggle)
        self.controls_panel.speed_changed.connect(self._handle_speed_change)
        self.controls_panel.check_alignment_requested.connect(
            self._handle_check_alignment_request
        )
        self.controls_panel.reset_from_ephemeris_requested.connect(
            self._handle_reset_from_ephemeris_request
        )
        self.controls_panel.set_from_almanac_requested.connect(
            self._handle_set_from_almanac_request
        )
        self.controls_panel.set_location_orientation_requested.connect(
            self._handle_set_location_orientation_request
        )
        self.controls_panel.set_gc_epoch_and_cardinals_requested.connect(
            self._handle_set_gc_epoch_and_cardinals
        )
        self.eclipse_catalog_widget.eclipse_selected.connect(
            self._handle_catalog_eclipse_selected
        )
        self.eclipse_catalog_widget.view_nasa_map_requested.connect(
            self._handle_view_nasa_map_requested
        )
        self.eclipse_catalog_widget.create_chart_requested.connect(
            self._handle_create_eclipse_chart
        )

    def _next_step(self):
        """
        Advances the simulation by one step and updates the view.
        """
        result = self.simulation_service.advance_simulation_step()
        day = result["day"]
        year = result["year"]
        current_positions = result["marker_positions"]
        eclipse_event = result["eclipses_detected"]

        self.circle_view.update_marker_positions(current_positions)

        log_message = f"Advanced to Day {day}, Year {year}."
        if eclipse_event:
            # Using a little HTML for highlighting
            event_str = ", ".join(eclipse_event)
            log_message += (
                f" <font color='red'><b>ECLIPSE PREDICTED: {event_str}</b></font>"
            )
            self.eclipse_log_view.add_log_message(log_message)
        else:
            log_message += " No eclipse."
            self.eclipse_log_view.add_log_message(log_message)

        # TODO: Update an EclipseLogViewWidget later -- This is now done

    def _reset_simulation(self):
        """
        Resets the simulation to its initial state and updates the view.
        Also stops auto-run if it is active.
        """
        if self.auto_run_timer.isActive():
            self.auto_run_timer.stop()
            # Visually reset the Start/Stop button in the panel
            # This assumes the button's state is managed internally by its 'checked' property
            # and clicking it again (if it was checked) would uncheck it and emit the signal.
            # A more direct way would be if ControlsPanelWidget had a reset_auto_run_button_state() method.
            # Manually call the toggle to ensure text updates and signal emits if needed for consistency,
            # though toggling it false here should be enough since _handle_auto_run_toggle(False) will be hit.
            if self.controls_panel.start_stop_button.isChecked():
                self.controls_panel.start_stop_button.setChecked(False)  # Uncheck it
                self.controls_panel._toggle_auto_run(False)

        self.controls_panel.set_next_step_enabled(True)

        initial_positions = self.simulation_service.reset_simulation(
            proximity_threshold=1
        )
        self.circle_view.update_marker_positions(initial_positions)

        # Clear any zodiac position labels
        self.circle_view.update_marker_zodiac_positions(
            {"S": None, "M": None, "N": None, "N'": None}
        )

        # Reset the position status display
        if hasattr(self, "position_status"):
            self.position_status.setText(
                "No zodiac positions available - use 'Set GC Epoch & Orient' to set alignment"
            )

        self.eclipse_log_view.clear_log()
        self.eclipse_log_view.add_log_message(
            "Simulation reset to initial state (with proximity threshold 1)."
        )
        # TODO: Clear EclipseLogViewWidget later -- This is now done

        self.simulation_service.reset_simulation(proximity_threshold=1)
        self._simulation_gregorian_start_date = None  # RESET HERE
        self._update_simulation_display()
        self.eclipse_log_view.add_log_message(
            "Simulation state has been completely reset."
        )

    def _handle_auto_run_toggle(self, is_running: bool):
        """
        Starts or stops the auto-run timer based on the toggle state.
        """
        if is_running:
            self.auto_run_timer.start(self.current_auto_run_interval)
            self.controls_panel.set_next_step_enabled(False)
            self.eclipse_log_view.add_log_message(
                f"Auto-run started (Interval: {self.current_auto_run_interval}ms)."
            )
        else:
            self.auto_run_timer.stop()
            self.controls_panel.set_next_step_enabled(True)
            self.eclipse_log_view.add_log_message("Auto-run stopped.")

    def _handle_speed_change(self, interval: int):
        """
        Updates the auto-run interval and restarts the timer if active.
        """
        self.current_auto_run_interval = interval
        if self.auto_run_timer.isActive():  # Update timer if it's already running
            self.auto_run_timer.start(self.current_auto_run_interval)
        self.eclipse_log_view.add_log_message(
            f"Auto-run speed changed. New interval: {interval}ms."
        )

    def _handle_check_alignment_request(
        self, year: int, day: int, expected_eclipse_type: str
    ):
        if not self.simulation_service:
            self.eclipse_log_view.add_log_message(
                "Error: Simulation service not available for alignment check."
            )
            return

        log_message_parts = []
        log_message_parts.append(
            f"<b>Alignment Check ({expected_eclipse_type}) for Hoyle Year {year}, Day {day}:</b>"
        )

        prediction_result = self.simulation_service.get_hoyle_prediction_for_date(
            target_year=year, target_day=day
        )

        # --- Hoyle Model Progression Results ---
        hoyle_markers = prediction_result.get("hoyle_marker_positions_on_date")
        hoyle_eclipses_predicted = prediction_result.get("hoyle_predicted_eclipses", [])

        log_message_parts.append("  <u>Hoyle Model Prediction:</u>")
        if hoyle_markers:
            hoyle_marker_str = ", ".join([f"{k}:{v}" for k, v in hoyle_markers.items()])
            log_message_parts.append(f"    Markers (Hoyle): {hoyle_marker_str}")
            self.circle_view.update_marker_positions(
                hoyle_markers
            )  # Update circle view with Hoyle markers
        else:
            log_message_parts.append("    Hoyle marker positions not available.")

        hoyle_match_message = "No specific eclipse type predicted by Hoyle model."
        if expected_eclipse_type.lower() in [
            e.lower() for e in hoyle_eclipses_predicted
        ]:
            hoyle_match_message = f"<font color='green'><b>Matches expectation!</b></font> ({expected_eclipse_type} predicted by Hoyle)"
        elif hoyle_eclipses_predicted:
            hoyle_match_message = f"<font color='orange'>Does NOT match expectation.</font> (Hoyle predicted: {', '.join(hoyle_eclipses_predicted)})"
        else:
            hoyle_match_message = "<font color='red'>Does NOT match expectation.</font> (No eclipse predicted by Hoyle model)"
        log_message_parts.append(f"    Prediction (Hoyle): {hoyle_match_message}")

        # Calculate Gregorian date based on Hoyle progression from seed (original method)
        if self._simulation_gregorian_start_date:
            # The service now resets Hoyle Y/D to 1/1 when seeded.
            # So, elapsed days are from Y1,D1 of the Hoyle calendar.
            days_elapsed_in_hoyle_calendar = (year - 1) * 364 + (
                day - 1
            )  # day is 1-indexed
            gregorian_date_for_hoyle_progression = (
                self._simulation_gregorian_start_date.addDays(
                    days_elapsed_in_hoyle_calendar
                )
            )
            log_message_parts.append(
                f"    Hoyle Progression Gregorian Date: {gregorian_date_for_hoyle_progression.toString('yyyy-MM-dd')}"
            )
        else:
            log_message_parts.append(
                "    Hoyle Progression Gregorian Date: N/A (Simulation not seeded from a Gregorian date)"
            )

        # --- Astronomical Sky Data Results (if available) ---
        log_message_parts.append(
            "  <u>Astronomical Sky Data (for equivalent Gregorian date):</u>"
        )
        sky_gregorian_date_str = prediction_result.get(
            "equivalent_gregorian_date_str", "N/A"
        )
        log_message_parts.append(
            f"    Sky Data Gregorian Date: {sky_gregorian_date_str}"
        )

        sky_error = prediction_result.get("error")
        if sky_error:
            log_message_parts.append(
                f"    <font color='red'>Sky Data Error: {sky_error}</font>"
            )
        else:
            sky_markers = prediction_result.get("sky_marker_positions_on_date")
            sky_eclipses_predicted = prediction_result.get("sky_predicted_eclipses", [])

            if sky_markers:
                sky_marker_str = ", ".join([f"{k}:{v}" for k, v in sky_markers.items()])
                log_message_parts.append(f"    Markers (Sky): {sky_marker_str}")
            else:
                log_message_parts.append("    Sky marker positions not available.")

            if sky_eclipses_predicted:
                sky_eclipse_types = ", ".join(sky_eclipses_predicted)
                log_message_parts.append(
                    f"    Eclipse Condition (Sky): <font color='blue'>{sky_eclipse_types} conditions met by sky data.</font>"
                )
            else:
                log_message_parts.append(
                    "    Eclipse Condition (Sky): No specific eclipse conditions met by sky data."
                )

        self.eclipse_log_view.add_log_message("<br>".join(log_message_parts))

    def _handle_reset_from_ephemeris_request(self):
        """
        Handles the request to reset the simulation markers based on a specific
        calendar date using ephemeris data.
        """
        selected_qdate = AncientDateDialog.get_date_from_dialog(
            self, title="Select Ephemeris Date"
        )

        if selected_qdate:
            year = selected_qdate.year()
            month = selected_qdate.month()
            day = selected_qdate.day()

            self.eclipse_log_view.add_log_message(
                f"<br>Attempting to set markers from ephemeris for <b>{year}-{month:02d}-{day:02d}</b>..."
            )

            # Common teardown for simulation reset (stops timer etc.)
            self._reset_simulation_common_teardown()

            new_positions = self.simulation_service.reset_simulation_from_ephemeris(
                year, month, day
            )

            if new_positions:
                self._simulation_gregorian_start_date = selected_qdate  # <--- SET HERE!
                print(
                    f"[DEBUG][EphemerisRequestSuccess] BEFORE reset_alignment_inputs: _simulation_gregorian_start_date IS: {self._simulation_gregorian_start_date.toString('yyyy-MM-dd') if self._simulation_gregorian_start_date else 'None'}"
                )
                self.circle_view.update_marker_positions(new_positions)
                self.eclipse_log_view.add_log_message(
                    f"<b><font color='green'>Success!</font></b> Markers set from ephemeris for {year}-{month:02d}-{day:02d}.<br>"
                    f"Hoyle simulation time has been reset to Day 1, Year 1.<br>"
                    f"Marker positions: {', '.join([f'{k}:{v}' for k,v in new_positions.items()])}"
                )
                self.controls_panel.reset_alignment_inputs_to_default()  # Reset alignment inputs

                # Also update the Epoch to the selected date if location is set
                if (
                    self.current_latitude is not None
                    and self.current_longitude is not None
                ):
                    self._update_orientation_for_date(selected_qdate)
            else:
                self.eclipse_log_view.add_log_message(
                    f"<b><font color='red'>Failed.</font></b> Could not retrieve ephemeris data or set markers for {year}-{month:02d}-{day:02d}. Please check console output."
                )
        else:
            self.eclipse_log_view.add_log_message("Ephemeris date selection cancelled.")

    def _handle_set_from_almanac_request(self):
        """
        Handles the 'Set from Almanac' button click.
        Resets the simulation markers based on the currently selected eclipse in the catalog.
        """
        if (
            not hasattr(self, "eclipse_catalog_widget")
            or not self.eclipse_catalog_widget
        ):
            self.eclipse_log_view.add_log_message(
                "<font color='orange'>Eclipse Catalog is not available to set from.</font>"
            )
            return

        selected_eclipse = (
            self.eclipse_catalog_widget.get_currently_selected_eclipse_data()
        )

        if selected_eclipse:
            year = selected_eclipse.year
            month = selected_eclipse.month
            day = selected_eclipse.day

            self.eclipse_log_view.add_log_message(
                f"<br>Attempting to set markers from Almanac for selected eclipse: <b>{year}-{month:02d}-{day:02d} (Cat: {selected_eclipse.cat_no})</b>..."
            )

            # Common teardown for simulation reset (stops timer etc.)
            self._reset_simulation_common_teardown()

            new_positions = self.simulation_service.reset_simulation_from_ephemeris(
                year, month, day
            )

            if new_positions:
                # Create the QDate object from the parts of selected_eclipse
                current_eclipse_qdate = QDate(year, month, day)

                self._simulation_gregorian_start_date = current_eclipse_qdate
                print(
                    f"[DEBUG][AlmanacRequestSuccess] BEFORE reset_alignment_inputs: _simulation_gregorian_start_date IS: {self._simulation_gregorian_start_date.toString('yyyy-MM-dd') if self._simulation_gregorian_start_date else 'None'}"
                )
                self.circle_view.update_marker_positions(new_positions)
                self.eclipse_log_view.add_log_message(
                    f"<b><font color='green'>Success!</font></b> Markers set from Almanac for {year}-{month:02d}-{day:02d}.<br>"
                    f"Hoyle simulation time has been reset to Day 1, Year 1.<br>"
                    f"Marker positions: {', '.join([f'{k}:{v}' for k,v in new_positions.items()])}"
                )
                self.controls_panel.reset_alignment_inputs_to_default()  # Reset alignment inputs

                # Also update the Epoch to the selected date if location is set
                if (
                    self.current_latitude is not None
                    and self.current_longitude is not None
                ):
                    self._update_orientation_for_date(current_eclipse_qdate)
            else:
                self.eclipse_log_view.add_log_message(
                    f"<b><font color='red'>Failed.</font></b> Could not retrieve ephemeris data or set markers for Almanac date {year}-{month:02d}-{day:02d}."
                )
        else:
            self.eclipse_log_view.add_log_message(
                "<font color='orange'>No eclipse selected in the Almanac. Please select an eclipse first.</font>"
            )

    def _handle_set_location_orientation_request(self):
        dialog = LocationSearchWindow(parent=self)

        # Temporary storage for the selected location from the dialog's signal
        # We'll use an attribute on self to make it accessible in the slot
        self._temp_selected_location_data_holder = [
            None
        ]  # Use a list to allow modification in nested func

        def handle_dialog_location_selected(location: Location):
            if location:
                self._temp_selected_location_data_holder[0] = {
                    "name": location.display_name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
            else:
                self._temp_selected_location_data_holder[0] = None

        dialog.location_selected.connect(handle_dialog_location_selected)

        if (
            dialog.exec() == QDialog.DialogCode.Accepted
        ):  # Use QDialog.DialogCode.Accepted
            location_data = self._temp_selected_location_data_holder[0]
            if location_data:
                self.current_latitude = location_data["latitude"]
                self.current_longitude = location_data["longitude"]
                self.eclipse_log_view.add_log_message(
                    f"Location set: {location_data['name']} ({self.current_latitude:.2f}, {self.current_longitude:.2f}). "
                    "Use 'Set GC Epoch & Orient' to align the circle."
                )
            else:
                self.eclipse_log_view.add_log_message(
                    "Location selection accepted, but no valid location data was processed."
                )
        else:
            self.eclipse_log_view.add_log_message(
                "Location search dialog closed or cancelled."
            )

        # Clear the temporary holder to avoid holding references if not needed
        self._temp_selected_location_data_holder[0] = None

    def _handle_set_gc_epoch_and_cardinals(self):
        """
        Handles the request to set the circle orientation based on the Galactic Center
        for a user-selected epoch date.
        """
        if self.current_latitude is None or self.current_longitude is None:
            self.eclipse_log_view.add_log_message(
                "<b><font color='orange'>Location Not Set:</font></b> Please set a location first using the 'Set Location/Orientation...' button."
            )
            return

        epoch_qdate = AncientDateDialog.get_date_from_dialog(
            parent=self,
            initial_date=QDate.currentDate(),
            title="Select Epoch Date for Galactic Center Orientation",
        )
        if epoch_qdate:
            self.eclipse_log_view.add_log_message(
                f"Calculating orientation for epoch: {epoch_qdate.toString('yyyy-MM-dd')}..."
            )

            # Get zodiac information along with azimuths
            zodiac_data = self.ephemeris_service.get_cardinal_points_with_zodiac(
                epoch_qdate, float(self.current_latitude), float(self.current_longitude)
            )

            # Also get the raw values for circle view
            gc_azimuth = self.ephemeris_service.get_galactic_center_azimuth_for_date_and_location(
                epoch_qdate, float(self.current_latitude), float(self.current_longitude)
            )

            # We still get the cardinal points for logging, but we won't set them on the circle view
            # since we're now using a heptagon without cardinal point display
            cardinal_azimuths = self.ephemeris_service.get_cardinal_point_azimuths_for_date_and_location(
                epoch_qdate, float(self.current_latitude), float(self.current_longitude)
            )

            if gc_azimuth is not None:
                self.circle_view.set_orientation(gc_azimuth)

                # Set Galactic Center zodiac label for visual display
                if zodiac_data and "GC" in zodiac_data:
                    gc_zodiac = zodiac_data["GC"]["zodiac"]
                    self.circle_view.set_galactic_center_zodiac(gc_zodiac)

                    # Update the position status with GC position
                    self.position_status.setText(
                        f"Galactic Center: {gc_zodiac} (Hole 28) - All holes are labeled with their zodiacal degrees"
                    )

                    # Also update the hole reference table with zodiacal positions
                    if hasattr(self.circle_view, "_hole_zodiac_positions"):
                        self.hole_reference_widget.update_zodiacal_positions(
                            self.circle_view._hole_zodiac_positions
                        )

                        # Also update marker positions in the table
                        marker_positions = (
                            self.simulation_service.get_current_marker_positions()
                        )
                        self.hole_reference_widget.update_marker_positions(
                            marker_positions
                        )

                # Display GC information with zodiac position
                if zodiac_data and "GC" in zodiac_data:
                    self.eclipse_log_view.add_log_message(
                        f"Heptagon Hole 0 oriented to Galactic Center azimuth: {zodiac_data['GC']['azimuth']} ({zodiac_data['GC']['zodiac']}) for epoch {epoch_qdate.toString('yyyy-MM-dd')}."
                    )
                else:
                    self.eclipse_log_view.add_log_message(
                        f"Heptagon Hole 0 oriented to Galactic Center azimuth: {gc_azimuth:.2f}° for epoch {epoch_qdate.toString('yyyy-MM-dd')}."
                    )
            else:
                self.eclipse_log_view.add_log_message(
                    "<b><font color='red'>Error:</font></b> Could not determine Galactic Center azimuth. Check console."
                )

            # Log information about cardinal points for reference only
            if cardinal_azimuths and zodiac_data:
                log_parts = [
                    f"Cardinal point data for reference (epoch {epoch_qdate.toString('yyyy-MM-dd')}):"
                ]

                # Map the short codes to full names for better readability
                name_map = {
                    "VE": "Vernal Equinox",
                    "SS": "Summer Solstice",
                    "AE": "Autumnal Equinox",
                    "WS": "Winter Solstice",
                }

                for key in ["VE", "SS", "AE", "WS"]:
                    if key in zodiac_data:
                        log_parts.append(
                            f"  {name_map[key]}: {zodiac_data[key]['azimuth']} ({zodiac_data[key]['zodiac']})"
                        )

                self.eclipse_log_view.add_log_message("<br>".join(log_parts))
        else:
            self.eclipse_log_view.add_log_message(
                "Galactic Center epoch selection cancelled."
            )

    def _reset_simulation_common_teardown(self):
        """
        Common actions to perform when any kind of simulation reset occurs,
        like stopping auto-run and re-enabling manual stepping.
        """
        if self.auto_run_timer.isActive():
            self.auto_run_timer.stop()
            if self.controls_panel.start_stop_button.isChecked():
                self.controls_panel.start_stop_button.setChecked(False)
                self.controls_panel._toggle_auto_run(
                    False
                )  # Ensure button text/state is correct
        self.controls_panel.set_next_step_enabled(True)

    def load_simulation_components(self):
        """
        Placeholder method for loading and arranging the main simulation widgets.
        This will be filled out in Phase 2.
        """
        # Clear placeholder if any
        if self.placeholder_label:
            self.layout.removeWidget(self.placeholder_label)
            self.placeholder_label.deleteLater()
            self.placeholder_label = None

        # This method is now largely handled by __init__
        # Kept for compatibility if other parts of the system call it,
        # but primary setup is in __init__.
        # Removed: print("load_simulation_components called, but main setup is in __init__.")
        pass

    def closeEvent(self, event):
        """
        Handle the window close event.
        Can be used for cleanup or confirming exit if simulation is running.
        """
        # Removed: print("StonehengePredictorWindow closing.")
        # Add any cleanup logic here if needed in the future
        super().closeEvent(event)

    def _handle_simulation_step_result(self, step_result: dict):
        """
        Processes the result from a simulation step and updates the UI.
        """
        current_day = step_result["day"]
        current_year = step_result["year"]
        eclipses = step_result["eclipses_detected"]
        marker_positions = step_result["marker_positions"]
        recalibration_logs = step_result.get(
            "recalibration_logs", []
        )  # Get recalibration logs

        self.controls_panel.update_time_display(current_day, current_year)
        self.circle_view.update_marker_positions(marker_positions)

        # Display recalibration logs first if any
        for r_log in recalibration_logs:
            self.eclipse_log_view.add_log_message(
                f"<i>✨ {r_log}</i>", "info"
            )  # Italicize and add emoji

        if eclipses:
            log_message = (
                f"<b>Year {current_year}, Day {current_day}: Event Predicted!</b><br>"
            )
            for i, eclipse_type in enumerate(eclipses):
                log_message += f"{eclipse_type} "
            self.eclipse_log_view.add_log_message(log_message)

    def _update_orientation_for_date(self, q_date: QDate):
        """
        Updates the orientation based on a given date.
        This is a helper method to update GC and cardinal points without duplicating code.

        Args:
            q_date (QDate): The date to use for orientation update
        """
        if self.current_latitude is None or self.current_longitude is None:
            # Can't update orientation without location
            return

        self.eclipse_log_view.add_log_message(
            f"Automatically updating orientation for epoch: {q_date.toString('yyyy-MM-dd')}..."
        )

        # Get zodiac information along with azimuths
        zodiac_data = self.ephemeris_service.get_cardinal_points_with_zodiac(
            q_date, float(self.current_latitude), float(self.current_longitude)
        )

        # Get the raw values for circle view
        gc_azimuth = (
            self.ephemeris_service.get_galactic_center_azimuth_for_date_and_location(
                q_date, float(self.current_latitude), float(self.current_longitude)
            )
        )

        cardinal_azimuths = (
            self.ephemeris_service.get_cardinal_point_azimuths_for_date_and_location(
                q_date, float(self.current_latitude), float(self.current_longitude)
            )
        )

        if gc_azimuth is not None:
            self.circle_view.set_orientation(gc_azimuth)

            # Set Galactic Center zodiac label for visual display
            if zodiac_data and "GC" in zodiac_data:
                gc_zodiac = zodiac_data["GC"]["zodiac"]
                self.circle_view.set_galactic_center_zodiac(gc_zodiac)

            # Display GC information with zodiac position
            if zodiac_data and "GC" in zodiac_data:
                self.eclipse_log_view.add_log_message(
                    f"Circle Hole 0 oriented to Galactic Center azimuth: {zodiac_data['GC']['azimuth']} ({zodiac_data['GC']['zodiac']}) for epoch {q_date.toString('yyyy-MM-dd')}."
                )
            else:
                self.eclipse_log_view.add_log_message(
                    f"Circle Hole 0 oriented to Galactic Center azimuth: {gc_azimuth:.2f}° for epoch {q_date.toString('yyyy-MM-dd')}."
                )

        # Display cardinal points in log but don't attempt to set them on the view
        # These methods have been removed since we're using a heptagon view now

            # Display cardinal points with zodiac positions
            if zodiac_data:
                log_parts = [
                    f"Cardinal points displayed for epoch {q_date.toString('yyyy-MM-dd')}:"
                ]

                # Map the short codes to full names for better readability
                name_map = {
                    "VE": "Vernal Equinox",
                    "SS": "Summer Solstice",
                    "AE": "Autumnal Equinox",
                    "WS": "Winter Solstice",
                }

                for key in ["VE", "SS", "AE", "WS"]:
                    if key in zodiac_data:
                        log_parts.append(
                            f"  {name_map[key]}: {zodiac_data[key]['azimuth']} ({zodiac_data[key]['zodiac']})"
                        )

                self.eclipse_log_view.add_log_message("<br>".join(log_parts))

    def _handle_catalog_eclipse_selected(self, eclipse_data: EclipseData):
        """
        Handles the selection of an eclipse from the catalog.
        Resets the simulation to the date of the selected eclipse.
        """
        self.eclipse_log_view.add_log_message(
            f"<br><b>Eclipse selected from catalog: {eclipse_data.cat_no} ({eclipse_data.year}-{eclipse_data.month:02d}-{eclipse_data.day:02d})</b>"
        )
        # For automatic orientation update on selection - only update if checkbox or setting is enabled
        # This could be controlled by a user preference

    def _handle_view_nasa_map_requested(self, eclipse_data: EclipseData):
        """
        Handles the request to view the NASA eclipse map for a given catalog number.
        Constructs the URL for the direct GIF map and opens it.
        """
        year = eclipse_data.year
        month = eclipse_data.month
        day = eclipse_data.day

        # Determine century directory segment
        century_dir_segment = ""
        if 1501 <= year <= 1600:
            century_dir_segment = "1501-1600"
        elif 1601 <= year <= 1700:
            century_dir_segment = "1601-1700"
        elif 1701 <= year <= 1800:
            century_dir_segment = "1701-1800"
        elif 1801 <= year <= 1900:
            century_dir_segment = "1801-1900"
        elif 1901 <= year <= 2000:
            century_dir_segment = "1901-2000"
        elif 2001 <= year <= 2100:
            century_dir_segment = "2001-2100"
        else:
            self.eclipse_log_view.add_log_message(
                f"Century not in NASA map ranges: {year}"
            )
            return

        # Handle image format
        catalog_number = eclipse_data.cat_no
        if catalog_number and len(catalog_number) == 5:
            catalog_number = catalog_number  # Just use the 5-digit catalog number
        else:
            self.eclipse_log_view.add_log_message(
                f"Invalid catalog number format: {catalog_number}"
            )
            return

        # Construct URL
        base_url = "https://eclipse.gsfc.nasa.gov/SEplot/SEplot"
        century_abbr = century_dir_segment[:2]
        url = f"{base_url}{century_abbr}/{century_dir_segment}/graphics/{catalog_number}.gif"

        # Log and open URL in browser
        self.eclipse_log_view.add_log_message(
            f"Opening NASA map for eclipse {catalog_number} ({year}-{month:02d}-{day:02d}) in browser: <a href='{url}'>{url}</a>"
        )
        webbrowser.open(url)

    def _handle_create_eclipse_chart(self, eclipse_data: EclipseData):
        """
        Handles the request to create an astrological chart for a solar eclipse.

        Args:
            eclipse_data (EclipseData): The eclipse data containing date and location information.
        """
        # Check if we have lat/long data for the eclipse
        if eclipse_data.lat_dd_ge is None or eclipse_data.lng_dd_ge is None:
            self.eclipse_log_view.add_log_message(
                f"<font color='orange'>Cannot create chart for eclipse {eclipse_data.cat_no}: "
                f"Missing location data (latitude/longitude).</font>"
            )
            return

        # Get the chart service
        chart_service = ChartService.get_instance()

        # Parse the time from td_ge field if available
        hour = 12  # Default to noon if time not available
        minute = 0

        if eclipse_data.td_ge:
            try:
                # Parse time string in format "HH:MM:SS"
                time_parts = eclipse_data.td_ge.split(":")
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    self.eclipse_log_view.add_log_message(
                        f"Using exact eclipse time: {hour:02d}:{minute:02d} UTC"
                    )
            except Exception as e:
                self.eclipse_log_view.add_log_message(
                    f"<font color='orange'>Could not parse eclipse time '{eclipse_data.td_ge}', using noon UTC instead: {e}</font>"
                )
        else:
            self.eclipse_log_view.add_log_message(
                f"<font color='orange'>No exact time data available for eclipse {eclipse_data.cat_no}, using noon UTC.</font>"
            )

        try:
            # IMPORTANT: Based on our tests, we have two reliable methods to ensure accurate planetary positions:
            # 1. Use ISO UTC time method in Kerykeion
            # 2. Use Method 4 - explicitly calculate local time from UTC

            # We'll use Method 1 - ISO UTC time which we confirmed works correctly in our tests

            # Create ISO format UTC string
            iso_utc_str = f"{eclipse_data.year}-{eclipse_data.month:02d}-{eclipse_data.day:02d}T{hour:02d}:{minute:02d}:00Z"

            # Log what we're doing
            self.eclipse_log_view.add_log_message(
                f"Creating chart with ISO UTC time: {iso_utc_str} at coordinates: "
                f"Lat {eclipse_data.lat_dd_ge:.2f}, Lng {eclipse_data.lng_dd_ge:.2f}"
            )

            # Create the chart name
            chart_name = f"Solar Eclipse {eclipse_data.year}-{eclipse_data.month:02d}-{eclipse_data.day:02d} {hour:02d}:{minute:02d} UTC"

            # Create the astrological subject directly using the ISO UTC time method
            # This ensures the time is properly interpreted as UTC
            subject = AstrologicalSubject.get_from_iso_utc_time(
                name=chart_name,
                iso_utc_time=iso_utc_str,
                city="Custom Location",
                nation="",
                lat=eclipse_data.lat_dd_ge,
                lng=eclipse_data.lng_dd_ge,
                tz_str="UTC",  # Ensure UTC is used
                online=False,
            )

            # Now create the natal chart using our chart service
            # We'll create it from the AstrologicalSubject that was properly initialized

            # Create a chart using the properly created subject
            natal_chart = NatalChart(
                name=chart_name,
                type=ChartType.NATAL,
                date=datetime(
                    eclipse_data.year,
                    eclipse_data.month,
                    eclipse_data.day,
                    hour,
                    minute,
                ),
                kerykeion_subject=subject,
                latitude=eclipse_data.lat_dd_ge,
                longitude=eclipse_data.lng_dd_ge,
                location_name=f"Eclipse Maximum Point ({eclipse_data.lat_dd_ge:.2f}, {eclipse_data.lng_dd_ge:.2f})",
                house_system="Placidus",
                birth_date=datetime(
                    eclipse_data.year,
                    eclipse_data.month,
                    eclipse_data.day,
                    hour,
                    minute,
                ),
                birth_time_known=True,
                planets=chart_service.kerykeion_service._extract_planets(subject),
                houses=chart_service.kerykeion_service._extract_houses(subject),
                aspects=[],  # We'll calculate aspects later
            )

            # Get the planet positions and display them
            sun_pos = f"{subject.sun.sign} {subject.sun.position:.2f}°"
            moon_pos = f"{subject.moon.sign} {subject.moon.position:.2f}°"
            north_node_pos = (
                f"{subject.north_node.sign} {subject.north_node.position:.2f}°"
            )
            south_node_pos = (
                f"{subject.south_node.sign} {subject.south_node.position:.2f}°"
            )

            # Create a dictionary of marker zodiac positions
            zodiac_positions = {
                "S": sun_pos,
                "M": moon_pos,
                "N": north_node_pos,
                "N'": south_node_pos,
            }

            # Update the CircleViewWidget with zodiac positions
            self.circle_view.update_marker_zodiac_positions(zodiac_positions)

            # Get current marker positions and update the hole reference widget
            marker_positions = self.simulation_service.get_current_marker_positions()
            if hasattr(self, "hole_reference_widget"):
                self.hole_reference_widget.update_marker_positions(marker_positions)

            # Update the status display with detailed position information
            self.position_status.setText(
                f"Sun: {sun_pos} | Moon: {moon_pos} | North Node: {north_node_pos} | South Node: {south_node_pos}"
            )

            # Switch to the Circle View tab to show the updated positions
            self.tab_widget.setCurrentIndex(0)

            # Log success message with the planetary positions
            self.eclipse_log_view.add_log_message(
                f"<font color='green'>Successfully created astrological chart for Solar Eclipse "
                f"{eclipse_data.year}-{eclipse_data.month:02d}-{eclipse_data.day:02d} {hour:02d}:{minute:02d} UTC (Cat: {eclipse_data.cat_no}).</font><br>"
                f"Chart created at maximum eclipse location: Lat {eclipse_data.lat_dd_ge:.2f}, Lng {eclipse_data.lng_dd_ge:.2f}.<br>"
                f"Sun: {sun_pos}, Moon: {moon_pos}, North Node: {north_node_pos}, South Node: {south_node_pos}"
            )

            # Optionally generate and display chart SVG
            svg_path = chart_service.kerykeion_service.generate_chart_svg(
                chart=natal_chart, open_in_browser=True
            )

            self.eclipse_log_view.add_log_message(f"Chart saved to: {svg_path}")

        except Exception as e:
            self.eclipse_log_view.add_log_message(
                f"<font color='red'>Error creating chart for eclipse {eclipse_data.cat_no}: {e}</font>"
            )

    def _handle_window_resize(self, event):
        """Handle window resize events to maintain proper layout."""
        super().resizeEvent(event)
        # Update the circle view if needed
        self.circle_view.update()

    def _handle_zoom_in(self):
        """Handle zoom in button click."""
        if hasattr(self.circle_view, "_zoom_factor"):
            current_zoom = self.circle_view._zoom_factor
            new_zoom = min(current_zoom + 0.2, self.circle_view._max_zoom)
            self.circle_view._zoom_factor = new_zoom
            self.circle_view.update()
            self.eclipse_log_view.add_log_message(f"Zoomed in to {new_zoom:.1f}x")
            
    def _handle_zoom_out(self):
        """Handle zoom out button click."""
        if hasattr(self.circle_view, "_zoom_factor"):
            current_zoom = self.circle_view._zoom_factor
            new_zoom = max(current_zoom - 0.2, self.circle_view._min_zoom)
            self.circle_view._zoom_factor = new_zoom
            self.circle_view.update()
            self.eclipse_log_view.add_log_message(f"Zoomed out to {new_zoom:.1f}x")
            
    def _handle_reset_view(self):
        """Handle reset view button click."""
        if hasattr(self.circle_view, "_zoom_factor"):
            self.circle_view._zoom_factor = 1.0
            self.circle_view._pan_offset_x = 0.0
            self.circle_view._pan_offset_y = 0.0
            self.circle_view.update()
            self.eclipse_log_view.add_log_message("View reset to default")
    
    def _toggle_zodiac_degrees(self, checked: bool):
        """Toggle the display of zodiacal degrees on the circle view."""
        self.circle_view.toggle_zodiac_degrees_display(checked)

    def _toggle_nodes_visibility(self, checked: bool):
        """Toggle the visibility of Node markers (N and N') on the circle view."""
        self.circle_view.toggle_nodes_visibility(checked)
        
    def _toggle_sun_moon_visibility(self, checked: bool):
        """Toggle the visibility of Sun and Moon markers (S and M) on the circle view."""
        self.circle_view.toggle_sun_moon_visibility(checked)
        
    def _handle_update_gc_alignment(self):
        """Update the Galactic Center alignment and zodiac display."""
        # This is just a shortcut to the existing GC epoch orientation function
        self._handle_set_gc_epoch_and_cardinals()

    def _apply_default_epoch(self):
        """
        Apply the default epoch (Dec 21, 2020) and update orientation
        with the default location (Luxor, Egypt).
        """
        # Create a QDate for December 21, 2020
        default_epoch = QDate(2020, 12, 21)
        
        # Only proceed if we have location set
        if self.current_latitude is not None and self.current_longitude is not None:
            # Log that we're using the default configuration
            self.eclipse_log_view.add_log_message(
                f"Setting default epoch to {default_epoch.toString('yyyy-MM-dd')} "
                f"with location {self.default_location_name} "
                f"({self.current_latitude:.4f}, {self.current_longitude:.4f})"
            )
            
            # Get zodiac information along with azimuths using the ephemeris service
            zodiac_data = self.ephemeris_service.get_cardinal_points_with_zodiac(
                default_epoch, 
                float(self.current_latitude), 
                float(self.current_longitude)
            )

            # Get the raw values for circle view
            gc_azimuth = self.ephemeris_service.get_galactic_center_azimuth_for_date_and_location(
                default_epoch, 
                float(self.current_latitude), 
                float(self.current_longitude)
            )
            
            # Get cardinal points for logging only
            cardinal_azimuths = self.ephemeris_service.get_cardinal_point_azimuths_for_date_and_location(
                default_epoch, 
                float(self.current_latitude), 
                float(self.current_longitude)
            )

            if gc_azimuth is not None:
                self.circle_view.set_orientation(gc_azimuth)

                # Set Galactic Center zodiac label for visual display
                if zodiac_data and "GC" in zodiac_data:
                    gc_zodiac = zodiac_data["GC"]["zodiac"]
                    self.circle_view.set_galactic_center_zodiac(gc_zodiac)

                    # Update the position status with GC position
                    self.position_status.setText(
                        f"Galactic Center: {gc_zodiac} (Hole 28) - All holes are labeled with their zodiacal degrees"
                    )

                    # Also update the hole reference table with zodiacal positions
                    if hasattr(self.circle_view, "_hole_zodiac_positions"):
                        self.hole_reference_widget.update_zodiacal_positions(
                            self.circle_view._hole_zodiac_positions
                        )

                        # Also update marker positions in the table
                        marker_positions = (
                            self.simulation_service.get_current_marker_positions()
                        )
                        self.hole_reference_widget.update_marker_positions(
                            marker_positions
                        )

                # Display GC information with zodiac position
                if zodiac_data and "GC" in zodiac_data:
                    self.eclipse_log_view.add_log_message(
                        f"Heptagon Hole 28 oriented to Galactic Center azimuth: {zodiac_data['GC']['azimuth']} ({zodiac_data['GC']['zodiac']}) "
                        f"for default epoch {default_epoch.toString('yyyy-MM-dd')}."
                    )
                else:
                    self.eclipse_log_view.add_log_message(
                        f"Heptagon Hole 28 oriented to Galactic Center azimuth: {gc_azimuth:.2f}° "
                        f"for default epoch {default_epoch.toString('yyyy-MM-dd')}."
                    )


# To allow running this file directly for testing the window (optional)
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # In a real app, window management would handle creation and showing.
    # This is just for direct testing of this window file.
    window = StonehengePredictorWindow()
    window.show()
    sys.exit(app.exec())
