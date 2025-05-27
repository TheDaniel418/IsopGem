"""
@file adyton_controls_widget.py
@description Control panel for the 3D Adyton of the Seven visualization.
@author IsopGemini
@created 2024-08-12
@lastModified 2024-08-12
@dependencies PyQt6
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from datetime import datetime


class AdytonControlsWidget(QWidget):
    """
    Widget providing controls for the 3D Adyton visualization.
    Includes toggles for visualization options and navigation controls.
    """
    
    # Define signals for control changes
    wireframe_toggled = pyqtSignal(bool)
    solid_toggled = pyqtSignal(bool)
    markers_toggled = pyqtSignal(bool)
    labels_toggled = pyqtSignal(bool)
    floor_toggled = pyqtSignal(bool)
    reset_view_requested = pyqtSignal()
    top_view_requested = pyqtSignal()
    side_view_requested = pyqtSignal()
    
    # New signals for date/time/location controls
    settings_applied = pyqtSignal(datetime, float, float)
    default_time_reset_requested = pyqtSignal()
    # New signal for time stepping
    time_step_requested = pyqtSignal(str, int) # unit (e.g., "day"), direction (+1 or -1)
    
    # New signals for autoplay
    autoplay_toggled = pyqtSignal(bool) # True to start, False to stop
    autoplay_speed_changed = pyqtSignal(int) # Interval in milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # === Visualization Options Group ===
        vis_group = QGroupBox("Visualization Options")
        vis_layout = QVBoxLayout(vis_group)
        
        # Checkboxes for toggles
        self.wireframe_checkbox = QCheckBox("Show Wireframe")
        self.wireframe_checkbox.setChecked(True)
        self.wireframe_checkbox.toggled.connect(self.wireframe_toggled)
        
        self.solid_checkbox = QCheckBox("Show Solid Pillars")
        self.solid_checkbox.setChecked(True)
        self.solid_checkbox.toggled.connect(self.solid_toggled)
        
        self.markers_checkbox = QCheckBox("Show Markers")
        self.markers_checkbox.setChecked(True)
        self.markers_checkbox.toggled.connect(self.markers_toggled)
        
        self.labels_checkbox = QCheckBox("Show Labels")
        self.labels_checkbox.setChecked(True)
        self.labels_checkbox.toggled.connect(self.labels_toggled)
        
        self.floor_checkbox = QCheckBox("Show Floor")
        self.floor_checkbox.setChecked(True)
        self.floor_checkbox.toggled.connect(self.floor_toggled)
        
        # Add checkboxes to layout
        vis_layout.addWidget(self.wireframe_checkbox)
        vis_layout.addWidget(self.solid_checkbox)
        vis_layout.addWidget(self.markers_checkbox)
        vis_layout.addWidget(self.labels_checkbox)
        vis_layout.addWidget(self.floor_checkbox)
        
        # === View Controls Group ===
        view_group = QGroupBox("View Controls")
        view_layout = QGridLayout(view_group)
        
        # View buttons
        self.reset_view_btn = QPushButton("Reset View")
        self.reset_view_btn.clicked.connect(self.reset_view_requested)
        
        self.top_view_btn = QPushButton("Top View")
        self.top_view_btn.clicked.connect(self.top_view_requested)
        
        self.side_view_btn = QPushButton("Side View")
        self.side_view_btn.clicked.connect(self.side_view_requested)
        
        # Add buttons to grid layout
        view_layout.addWidget(self.reset_view_btn, 0, 0)
        view_layout.addWidget(self.top_view_btn, 0, 1)
        view_layout.addWidget(self.side_view_btn, 1, 0)
        
        # === Information Group ===
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        
        # Information about the Adyton
        info_text = (
            "The Adyton of the Seven visualization shows the heptagonal "
            "structure with 56 pillars that are each 13 cubes high. "
            "This 3D representation is based on the 2D Stonehenge predictor."
        )
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        
        # === Cube Selection Group ===
        selection_group = QGroupBox("Cube Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        self.selection_label = QLabel("No cube selected")
        selection_layout.addWidget(self.selection_label)
        
        # === Date, Time & Location Group ===
        dtl_group = QGroupBox("Date, Time & Location")
        dtl_layout = QGridLayout(dtl_group)

        # Default values (from AdytonOpenGLWidget constants)
        # These should ideally come from a shared config or passed in if they can vary
        default_year, default_month, default_day = 2020, 12, 21
        default_hour, default_minute = 12, 0
        # ADYTON_LATITUDE_DEG = 25.718738888888886 (approx)
        # ADYTON_LONGITUDE_DEG = 32.657399999999996 (approx)
        # For display, let's use a reasonable precision for lat/lon
        default_lat_str = "25.718739"
        default_lon_str = "32.657400"

        dtl_layout.addWidget(QLabel("Year:"), 0, 0)
        self.year_edit = QLineEdit(str(default_year))
        dtl_layout.addWidget(self.year_edit, 0, 1)
        dtl_layout.addWidget(QLabel("Month:"), 1, 0)
        self.month_edit = QLineEdit(str(default_month))
        dtl_layout.addWidget(self.month_edit, 1, 1)
        dtl_layout.addWidget(QLabel("Day:"), 2, 0)
        self.day_edit = QLineEdit(str(default_day))
        dtl_layout.addWidget(self.day_edit, 2, 1)
        dtl_layout.addWidget(QLabel("Hour (UTC):"), 3, 0)
        self.hour_edit = QLineEdit(str(default_hour))
        dtl_layout.addWidget(self.hour_edit, 3, 1)
        dtl_layout.addWidget(QLabel("Minute:"), 4, 0)
        self.minute_edit = QLineEdit(str(default_minute))
        dtl_layout.addWidget(self.minute_edit, 4, 1)

        dtl_layout.addWidget(QLabel("Latitude (°N):", alignment=Qt.AlignmentFlag.AlignRight), 0, 2)
        self.latitude_edit = QLineEdit(default_lat_str)
        dtl_layout.addWidget(self.latitude_edit, 0, 3)
        dtl_layout.addWidget(QLabel("Longitude (°E):", alignment=Qt.AlignmentFlag.AlignRight), 1, 2)
        self.longitude_edit = QLineEdit(default_lon_str)
        dtl_layout.addWidget(self.longitude_edit, 1, 3)

        self.apply_settings_button = QPushButton("Apply Date/Time/Location")
        self.apply_settings_button.clicked.connect(self._emit_apply_settings)
        dtl_layout.addWidget(self.apply_settings_button, 5, 0, 1, 2) # Span 2 columns

        self.reset_time_button = QPushButton("Reset to Default Date/Time/Location")
        self.reset_time_button.clicked.connect(self.default_time_reset_requested)
        # We also want to visually reset the fields when this is clicked.
        # The AdytonWindow._handle_reset_time will update these fields after this signal is emitted.
        dtl_layout.addWidget(self.reset_time_button, 5, 2, 1, 2) # Span 2 columns

        main_layout.addWidget(vis_group)
        main_layout.addWidget(view_group)
        main_layout.addWidget(selection_group)
        main_layout.addWidget(info_group)
        main_layout.addWidget(dtl_group)
        
        # === Time Navigation Group ===
        time_nav_group = QGroupBox("Time Navigation")
        time_nav_layout = QGridLayout(time_nav_group)

        # Row 0: Hour
        time_nav_layout.addWidget(QLabel("Hour:"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        self.prev_hour_btn = QPushButton("< Hour")
        self.prev_hour_btn.clicked.connect(lambda: self.time_step_requested.emit("hour", -1))
        time_nav_layout.addWidget(self.prev_hour_btn, 0, 0)
        self.next_hour_btn = QPushButton("Hour >")
        self.next_hour_btn.clicked.connect(lambda: self.time_step_requested.emit("hour", 1))
        time_nav_layout.addWidget(self.next_hour_btn, 0, 2)

        # Row 1: Day
        time_nav_layout.addWidget(QLabel("Day:"), 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.prev_day_btn = QPushButton("< Day")
        self.prev_day_btn.clicked.connect(lambda: self.time_step_requested.emit("day", -1))
        time_nav_layout.addWidget(self.prev_day_btn, 1, 0)
        self.next_day_btn = QPushButton("Day >")
        self.next_day_btn.clicked.connect(lambda: self.time_step_requested.emit("day", 1))
        time_nav_layout.addWidget(self.next_day_btn, 1, 2)

        # Row 2: Week
        time_nav_layout.addWidget(QLabel("Week:"), 2, 1, Qt.AlignmentFlag.AlignCenter)
        self.prev_week_btn = QPushButton("< Week")
        self.prev_week_btn.clicked.connect(lambda: self.time_step_requested.emit("week", -1))
        time_nav_layout.addWidget(self.prev_week_btn, 2, 0)
        self.next_week_btn = QPushButton("Week >")
        self.next_week_btn.clicked.connect(lambda: self.time_step_requested.emit("week", 1))
        time_nav_layout.addWidget(self.next_week_btn, 2, 2)

        # Row 3: Month
        time_nav_layout.addWidget(QLabel("Month:"), 3, 1, Qt.AlignmentFlag.AlignCenter)
        self.prev_month_btn = QPushButton("< Month")
        self.prev_month_btn.clicked.connect(lambda: self.time_step_requested.emit("month", -1))
        time_nav_layout.addWidget(self.prev_month_btn, 3, 0)
        self.next_month_btn = QPushButton("Month >")
        self.next_month_btn.clicked.connect(lambda: self.time_step_requested.emit("month", 1))
        time_nav_layout.addWidget(self.next_month_btn, 3, 2)

        # Row 4: Year
        time_nav_layout.addWidget(QLabel("Year:"), 4, 1, Qt.AlignmentFlag.AlignCenter)
        self.prev_year_btn = QPushButton("< Year")
        self.prev_year_btn.clicked.connect(lambda: self.time_step_requested.emit("year", -1))
        time_nav_layout.addWidget(self.prev_year_btn, 4, 0)
        self.next_year_btn = QPushButton("Year >")
        self.next_year_btn.clicked.connect(lambda: self.time_step_requested.emit("year", 1))
        time_nav_layout.addWidget(self.next_year_btn, 4, 2)
        
        main_layout.addWidget(time_nav_group) # Add the time navigation group

        # === Autoplay Group ===
        autoplay_group = QGroupBox("Autoplay Controls")
        autoplay_layout = QHBoxLayout(autoplay_group) # Use QHBoxLayout for a single row

        self.autoplay_button = QPushButton("Start Autoplay")
        self.autoplay_button.setCheckable(True)
        self.autoplay_button.clicked.connect(self._emit_autoplay_toggle)

        autoplay_layout.addWidget(self.autoplay_button)

        autoplay_layout.addWidget(QLabel("Speed:"))
        self.autoplay_speed_combo = QComboBox()
        self.autoplay_speeds = {
            "Slow (2s)": 2000,
            "Medium (1s)": 1000,
            "Fast (0.5s)": 500,
            "Very Fast (0.2s)": 200
        }
        self.autoplay_speed_combo.addItems(self.autoplay_speeds.keys())
        self.autoplay_speed_combo.setCurrentText("Medium (1s)") # Default speed
        self.autoplay_speed_combo.currentTextChanged.connect(self._emit_autoplay_speed_change)
        
        autoplay_layout.addWidget(self.autoplay_speed_combo)
        autoplay_layout.addStretch()

        main_layout.addWidget(autoplay_group) # Add the autoplay group
        main_layout.addStretch(1)  # Add stretch at the end
        
    def update_selection_info(self, pillar_index, cube_index):
        """Update the selection information display."""
        if pillar_index is None or cube_index is None:
            self.selection_label.setText("No cube selected")
        else:
            self.selection_label.setText(
                f"Selected: Pillar {pillar_index + 1}, Cube {cube_index + 1}"
            )
            
    def reset_toggles(self):
        """Reset all toggle controls to their default state."""
        # Block signals temporarily to prevent emit cascade
        self.wireframe_checkbox.blockSignals(True)
        self.solid_checkbox.blockSignals(True)
        self.markers_checkbox.blockSignals(True)
        self.labels_checkbox.blockSignals(True)
        self.floor_checkbox.blockSignals(True)
        
        # Reset to defaults
        self.wireframe_checkbox.setChecked(True)
        self.solid_checkbox.setChecked(True)
        self.markers_checkbox.setChecked(True)
        self.labels_checkbox.setChecked(True)
        self.floor_checkbox.setChecked(True)
        
        # Unblock signals
        self.wireframe_checkbox.blockSignals(False)
        self.solid_checkbox.blockSignals(False)
        self.markers_checkbox.blockSignals(False)
        self.labels_checkbox.blockSignals(False)
        self.floor_checkbox.blockSignals(False) 

    def _emit_apply_settings(self):
        try:
            year = int(self.year_edit.text())
            month = int(self.month_edit.text())
            day = int(self.day_edit.text())
            hour = int(self.hour_edit.text())
            minute = int(self.minute_edit.text())
            
            lat = float(self.latitude_edit.text())
            lon = float(self.longitude_edit.text())
            
            dt = datetime(year, month, day, hour, minute)
            self.settings_applied.emit(dt, lat, lon)
        except ValueError as e:
            print(f"Error in AdytonControlsWidget parsing settings: {e}")
            # Optionally, show an error message to the user (e.g., via a status label)

    # Method to update displayed date/time/location (called by AdytonWindow after a reset)
    def update_displayed_datetime_location(self, dt: datetime, lat: float, lon: float):
        self.year_edit.setText(str(dt.year))
        self.month_edit.setText(str(dt.month))
        self.day_edit.setText(str(dt.day))
        self.hour_edit.setText(str(dt.hour))
        self.minute_edit.setText(str(dt.minute))
        self.latitude_edit.setText(f"{lat:.6f}")
        self.longitude_edit.setText(f"{lon:.6f}") 

    def _emit_autoplay_toggle(self):
        is_checked = self.autoplay_button.isChecked()
        self.autoplay_button.setText("Stop Autoplay" if is_checked else "Start Autoplay")
        self.autoplay_toggled.emit(is_checked)

    def _emit_autoplay_speed_change(self, speed_text: str):
        interval_ms = self.autoplay_speeds.get(speed_text, 1000) # Default to 1s if key not found
        self.autoplay_speed_changed.emit(interval_ms) 