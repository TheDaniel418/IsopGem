"""
@file adyton_window.py
@description Main window for the Adyton of the Seven 3D visualization.
@author IsopGemini
@created 2024-08-12
@lastModified 2024-08-12
@dependencies PyQt6, astrology.ui.widgets.stonehenge_predictor.adyton_opengl_widget, 
              astrology.ui.widgets.stonehenge_predictor.adyton_controls_widget
"""

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFrame,
    QGridLayout,
    QTabWidget,
)

from astrology.ui.widgets.stonehenge_predictor.adyton_controls_widget import AdytonControlsWidget
from astrology.ui.widgets.stonehenge_predictor.adyton_opengl_widget import AdytonOpenGLWidget
from astrology.ui.widgets.stonehenge_predictor.celestial_data_table_widget import CelestialDataTableWidget

from datetime import datetime, timedelta
# Attempt to import relativedelta, will use basic logic if not found
try:
    from dateutil.relativedelta import relativedelta
    _HAS_DATEUTIL = True
except ImportError:
    _HAS_DATEUTIL = False
    print("WARNING: dateutil.relativedelta not found. Month/Year stepping will be less precise.")


class AdytonWindow(QMainWindow):
    """
    Main window for the Adyton of the Seven 3D visualization.
    Integrates the 3D OpenGL view with control panels and synchronizes with marker positions.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Adyton of the Seven - 3D Visualization")
        self.setGeometry(100, 100, 1200, 800)
        
        # Autoplay state variables
        self.is_autoplaying = False
        self.current_autoplay_interval_ms = 1000  # Default to 1s
        self.autoplay_step_unit = "hour"  # Default step unit
        self.autoplay_direction = 1      # Default direction: forward
        self.autoplay_timer = QTimer(self)
        self.autoplay_timer.timeout.connect(self._perform_autoplay_step)
        
        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main horizontal layout with splitter
        self.main_layout = QHBoxLayout(self.central_widget)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create widgets
        self.adyton_view = AdytonOpenGLWidget()
        self.controls = AdytonControlsWidget()
        
        # Create the CelestialDataTableWidget instance
        self.celestial_data_table_widget = CelestialDataTableWidget()

        # Create a QTabWidget for the right pane
        self.right_pane_tab_widget = QTabWidget()
        self.right_pane_tab_widget.addTab(self.controls, "Controls")
        self.right_pane_tab_widget.addTab(self.celestial_data_table_widget, "Celestial Data")
        
        # Add widgets to splitter
        self.splitter.addWidget(self.adyton_view)
        self.splitter.addWidget(self.right_pane_tab_widget)
        
        # Set splitter sizes (3:1 ratio)
        self.splitter.setSizes([800, 200])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter)
        
        # Connect signals
        self._connect_signals()
        
        # Initial update of the celestial data table
        self.update_celestial_data_table()
        
    def _connect_signals(self):
        """Connect control signals to view methods."""
        # Visualization toggles
        self.controls.wireframe_toggled.connect(self.adyton_view.toggle_wireframe)
        self.controls.solid_toggled.connect(self.adyton_view.toggle_solid)
        self.controls.markers_toggled.connect(self.adyton_view.toggle_markers)
        self.controls.labels_toggled.connect(self.adyton_view.toggle_labels)
        self.controls.floor_toggled.connect(self.adyton_view.toggle_floor)
        
        # View controls
        self.controls.reset_view_requested.connect(self.adyton_view.reset_view)
        self.controls.top_view_requested.connect(self._set_top_view)
        self.controls.side_view_requested.connect(self._set_side_view)
        
        # Selection feedback
        self.adyton_view.pillar_selected.connect(self._handle_pillar_selected)
        
        # Connect to the new signals from AdytonControlsWidget
        self.controls.settings_applied.connect(self._handle_apply_settings)
        self.controls.default_time_reset_requested.connect(self._handle_reset_time)
        # Connect the new time_step_requested signal
        self.controls.time_step_requested.connect(self._handle_time_step)
        # Connect autoplay signals
        self.controls.autoplay_toggled.connect(self._handle_autoplay_toggle)
        self.controls.autoplay_speed_changed.connect(self._handle_autoplay_speed_change)
        
    def _set_top_view(self):
        """Set camera to top-down view."""
        self.adyton_view.rotation_x = 90.0
        self.adyton_view.rotation_y = 0.0
        self.adyton_view.update()
        
    def _set_side_view(self):
        """Set camera to side view."""
        self.adyton_view.rotation_x = 0.0
        self.adyton_view.rotation_y = 0.0
        self.adyton_view.update()
        
    def _handle_pillar_selected(self, pillar_index, cube_index, height):
        """Handle pillar selection events."""
        self.controls.update_selection_info(pillar_index, cube_index)
        
    def update_marker_positions(self, positions):
        """
        Update marker positions in the 3D view.
        
        Args:
            positions (dict): Dictionary mapping marker names to pillar indices.
        """
        self.adyton_view.set_marker_positions(positions)
        
    def get_marker_positions(self):
        """
        Get the current marker positions from the 3D view.
        
        Returns:
            dict: Dictionary mapping marker names to pillar indices.
        """
        return self.adyton_view.get_marker_positions()
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Add any cleanup if needed
        super().closeEvent(event)
        
    def _handle_apply_settings(self, dt: datetime, lat: float, lon: float):
        """
        Handles the settings_applied signal from AdytonControlsWidget.
        Updates the OpenGL view and the celestial data table.
        """
        try:
            self.adyton_view.update_celestial_view(dt, lat, lon)
            self.update_celestial_data_table() # Update table after opengl widget updates
            print(f"AdytonWindow: Settings applied - DT: {dt}, Lat: {lat}, Lon: {lon}")
        except Exception as e:
            print(f"Error in AdytonWindow applying settings: {e}")

    def _handle_reset_time(self):
        """
        Handles the default_time_reset_requested signal from AdytonControlsWidget.
        Resets the AdytonOpenGLWidget to its default time and location, 
        updates the celestial data table, and tells AdytonControlsWidget to update its display.
        """
        default_dt = datetime(2020, 12, 21, 12, 0, 0)
        # These should ideally come from a shared source or constants if AdytonOpenGLWidget doesn't expose them
        # For now, assuming AdytonOpenGLWidget has these as attributes or can provide them
        default_lat = self.adyton_view.latitude # Default from AdytonOpenGLWidget
        default_lon = self.adyton_view.longitude # Default from AdytonOpenGLWidget

        try:
            self.adyton_view.update_celestial_view(default_dt, default_lat, default_lon)
            self.update_celestial_data_table() # Update table after opengl widget updates

            # Tell AdytonControlsWidget to update its displayed values
            if hasattr(self.controls, 'update_displayed_datetime_location'):
                self.controls.update_displayed_datetime_location(default_dt, default_lat, default_lon)
            print("AdytonWindow: Time and location reset to default.")
        except Exception as e:
            print(f"Error in AdytonWindow resetting time: {e}")

    def _handle_time_step(self, unit: str, direction: int):
        """
        Handles time step requests from AdytonControlsWidget.
        Updates the current datetime, refreshes the 3D view, control display, and data table.
        """
        current_dt = self.adyton_view.current_datetime
        current_lat = self.adyton_view.current_latitude
        current_lon = self.adyton_view.current_longitude
        new_dt = current_dt

        print(f"[ADYTON TIME STEP] Unit: {unit}, Direction: {direction}, Current DT: {current_dt}")

        if unit == "hour":
            new_dt = current_dt + timedelta(hours=1 * direction)
        elif unit == "day":
            new_dt = current_dt + timedelta(days=1 * direction)
        elif unit == "week":
            new_dt = current_dt + timedelta(weeks=1 * direction)
        elif unit == "month":
            if _HAS_DATEUTIL:
                new_dt = current_dt + relativedelta(months=1 * direction)
            else:
                # Basic month stepping: add/subtract approx 30 days
                # This is not perfectly accurate across month boundaries
                new_dt = current_dt + timedelta(days=30 * direction)
                print("INFO: Using approximate 30-day month step.")
        elif unit == "year":
            if _HAS_DATEUTIL:
                new_dt = current_dt + relativedelta(years=1 * direction)
            else:
                # Basic year stepping: consider leap years simply by day count
                # This is also not perfectly accurate for all calendar details
                days_in_year = 366 if (current_dt.year % 4 == 0 and current_dt.year % 100 != 0) or current_dt.year % 400 == 0 else 365
                if direction < 0: # Going back a year
                    prev_year = current_dt.year -1
                    days_in_prev_year = 366 if (prev_year % 4 == 0 and prev_year % 100 != 0) or prev_year % 400 == 0 else 365
                    new_dt = current_dt - timedelta(days=days_in_prev_year)
                else: # Going forward a year
                    new_dt = current_dt + timedelta(days=days_in_year)
                print("INFO: Using approximate day-count year step.")
        
        try:
            self.adyton_view.update_celestial_view(new_dt, current_lat, current_lon)
            if hasattr(self.controls, 'update_displayed_datetime_location'):
                self.controls.update_displayed_datetime_location(new_dt, current_lat, current_lon)
            self.update_celestial_data_table()
            print(f"[ADYTON TIME STEP] New DT: {new_dt}")
        except Exception as e:
            print(f"Error in AdytonWindow handling time step: {e}")

    def _handle_autoplay_toggle(self, start_playing: bool):
        self.is_autoplaying = start_playing
        if self.is_autoplaying:
            self.autoplay_timer.start(self.current_autoplay_interval_ms)
            # Disable manual controls during autoplay
            self._set_manual_controls_enabled(False)
            print(f"[ADYTON AUTOPLAY] Started. Interval: {self.current_autoplay_interval_ms}ms, Unit: {self.autoplay_step_unit}")
        else:
            self.autoplay_timer.stop()
            # Enable manual controls when autoplay stops
            self._set_manual_controls_enabled(True)
            print("[ADYTON AUTOPLAY] Stopped.")

    def _handle_autoplay_speed_change(self, interval_ms: int):
        self.current_autoplay_interval_ms = interval_ms
        if self.is_autoplaying:
            self.autoplay_timer.start(self.current_autoplay_interval_ms) # Restart with new interval
        print(f"[ADYTON AUTOPLAY] Speed changed. New interval: {interval_ms}ms")

    def _perform_autoplay_step(self):
        if not self.is_autoplaying: # Should not happen if timer is stopped correctly
            return
        # Call the existing time step handler
        self._handle_time_step(self.autoplay_step_unit, self.autoplay_direction)
        print(f"[ADYTON AUTOPLAY] Step performed. Unit: {self.autoplay_step_unit}, Dir: {self.autoplay_direction}")

    def _set_manual_controls_enabled(self, enabled: bool):
        """Enables or disables manual time navigation and settings buttons."""
        # Date/Time/Location input fields and Apply button
        self.controls.year_edit.setEnabled(enabled)
        self.controls.month_edit.setEnabled(enabled)
        self.controls.day_edit.setEnabled(enabled)
        self.controls.hour_edit.setEnabled(enabled)
        self.controls.minute_edit.setEnabled(enabled)
        self.controls.latitude_edit.setEnabled(enabled)
        self.controls.longitude_edit.setEnabled(enabled)
        self.controls.apply_settings_button.setEnabled(enabled)
        self.controls.reset_time_button.setEnabled(enabled)
        
        # Time navigation buttons
        self.controls.prev_hour_btn.setEnabled(enabled)
        self.controls.next_hour_btn.setEnabled(enabled)
        self.controls.prev_day_btn.setEnabled(enabled)
        self.controls.next_day_btn.setEnabled(enabled)
        self.controls.prev_week_btn.setEnabled(enabled)
        self.controls.next_week_btn.setEnabled(enabled)
        self.controls.prev_month_btn.setEnabled(enabled)
        self.controls.next_month_btn.setEnabled(enabled)
        self.controls.prev_year_btn.setEnabled(enabled)
        self.controls.next_year_btn.setEnabled(enabled)
        
        # The autoplay button itself should always be enabled to stop/start
        # self.controls.autoplay_button.setEnabled(True) 
        # The speed combo should also generally be enabled
        # self.controls.autoplay_speed_combo.setEnabled(True)

    def update_celestial_data_table(self):
        """Fetches data from OpenGL widget and updates the celestial data table."""
        if hasattr(self.adyton_view, 'get_celestial_projection_data'):
            projection_data = self.adyton_view.get_celestial_projection_data()
            self.celestial_data_table_widget.update_data(projection_data)

    # Ensure the AdytonOpenGLWidget is updated when the window is shown or settings change.
    def showEvent(self, event):
        super().showEvent(event)
        # When window is shown, ensure the table is populated with current data
        self.update_celestial_data_table() 