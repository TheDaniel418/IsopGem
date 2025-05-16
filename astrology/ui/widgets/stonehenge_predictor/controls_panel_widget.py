"""
Defines the ControlsPanelWidget for the Stonehenge Eclipse Predictor.

This widget will house controls for the simulation, such as step, reset,
start/stop auto-run, and speed controls.

Author: IsopGemini
Created: 2024-07-30
Last Modified: 2024-07-30
Dependencies: PyQt6
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class ControlsPanelWidget(QWidget):
    """
    A panel containing controls for the Stonehenge simulation.

    Signals:
        next_step_requested: Emitted when the 'Next Step' button is clicked.
        reset_requested: Emitted when the 'Reset Simulation' button is clicked.
        auto_run_toggled = pyqtSignal(bool) # True to start, False to stop
        speed_changed = pyqtSignal(int)     # Emits new interval in milliseconds
        check_alignment_requested = pyqtSignal(int, int, str) # year, day, eclipse_type
        reset_from_ephemeris_requested = pyqtSignal()
        set_from_almanac_requested = pyqtSignal()
        set_location_orientation_requested = pyqtSignal()
        set_gc_epoch_and_cardinals_requested = pyqtSignal()
    """

    next_step_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    auto_run_toggled = pyqtSignal(bool)
    speed_changed = pyqtSignal(int)
    check_alignment_requested = pyqtSignal(int, int, str)
    reset_from_ephemeris_requested = pyqtSignal()
    set_from_almanac_requested = pyqtSignal()
    set_location_orientation_requested = pyqtSignal()
    set_gc_epoch_and_cardinals_requested = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initializes the ControlsPanelWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """
        Initializes the UI components of the control panel.
        """
        main_layout = QVBoxLayout(
            self
        )  # Main layout will be vertical to stack button row and slider row
        main_layout.setContentsMargins(0, 5, 0, 5)  # Add a bit of vertical margin

        # --- Current Time Display ---
        self.current_year_label = QLabel("Current Year: 1", self)
        self.current_year_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_day_label = QLabel("Current Day: 1", self)
        self.current_day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.current_year_label)
        main_layout.addWidget(self.current_day_label)

        # --- Button Row ---
        button_row_widget = QWidget()
        button_layout = QHBoxLayout(button_row_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.next_step_button = QPushButton("Next Step", self)
        self.next_step_button.setToolTip("Advance the simulation by one day.")
        self.next_step_button.clicked.connect(self.next_step_requested.emit)
        button_layout.addWidget(self.next_step_button)

        self.reset_button = QPushButton("Reset Simulation", self)
        self.reset_button.setToolTip("Reset the simulation to its initial state.")
        self.reset_button.clicked.connect(self.reset_requested.emit)
        button_layout.addWidget(self.reset_button)

        self.reset_from_ephemeris_button = QPushButton("Set from Ephemeris...", self)
        self.reset_from_ephemeris_button.setToolTip(
            "Set marker positions from a specific calendar date using ephemeris data and reset Hoyle time."
        )
        self.reset_from_ephemeris_button.clicked.connect(
            self.reset_from_ephemeris_requested.emit
        )
        button_layout.addWidget(self.reset_from_ephemeris_button)

        self.set_from_almanac_button = QPushButton("Set from Almanac...", self)
        self.set_from_almanac_button.setToolTip(
            "Set marker positions based on the currently selected eclipse in the Almanac (Eclipse Catalog) and reset Hoyle time."
        )
        self.set_from_almanac_button.clicked.connect(
            self.set_from_almanac_requested.emit
        )
        button_layout.addWidget(self.set_from_almanac_button)

        self.set_location_orientation_button = QPushButton(
            "Set Location/Orientation...", self
        )
        self.set_location_orientation_button.setToolTip(
            "Set your location to orient the circle to true north at your site."
        )
        self.set_location_orientation_button.clicked.connect(
            self.set_location_orientation_requested.emit
        )
        button_layout.addWidget(self.set_location_orientation_button)

        self.set_gc_epoch_button = QPushButton("Set GC Epoch & Orient", self)
        self.set_gc_epoch_button.setToolTip(
            "Choose a date to align Hole 0 with the Galactic Center's azimuth and show Solstice/Equinox lines for that epoch."
        )
        self.set_gc_epoch_button.clicked.connect(
            self.set_gc_epoch_and_cardinals_requested.emit
        )
        button_layout.addWidget(self.set_gc_epoch_button)

        self.start_stop_button = QPushButton("Start Auto-Run", self)
        self.start_stop_button.setToolTip("Toggle automatic simulation steps.")
        self.start_stop_button.setCheckable(True)  # Makes it a toggle button
        self.start_stop_button.clicked.connect(self._toggle_auto_run)
        button_layout.addWidget(self.start_stop_button)

        main_layout.addWidget(button_row_widget)

        # --- Speed Control Row ---
        speed_control_widget = QWidget()
        speed_layout = QHBoxLayout(speed_control_widget)
        speed_layout.setContentsMargins(0, 5, 0, 0)  # Margin above the slider

        speed_label = QLabel("Speed:", self)
        speed_layout.addWidget(speed_label)

        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.setToolTip(
            "Controls the speed of auto-run (delay between steps)."
        )
        self.speed_slider.setMinimum(50)  # Min delay 50 ms (fast)
        self.speed_slider.setMaximum(2000)  # Max delay 2000 ms (slow)
        self.speed_slider.setValue(500)  # Default delay 500 ms
        self.speed_slider.setTickInterval(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.valueChanged.connect(self.speed_changed.emit)
        speed_layout.addWidget(self.speed_slider, 1)  # Slider takes available space

        main_layout.addWidget(speed_control_widget)

        # --- Recalibration / Check Alignment Section ---
        recal_groupbox = QGroupBox("Check Alignment with Known Eclipse")
        recal_layout = QVBoxLayout()

        # Date Input Row
        date_input_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        self.target_year_spinbox = QSpinBox()
        self.target_year_spinbox.setMinimum(1)
        self.target_year_spinbox.setMaximum(10000)  # Arbitrary large number
        self.target_year_spinbox.setValue(1)
        day_label = QLabel("Day (1-364):")
        self.target_day_spinbox = QSpinBox()
        self.target_day_spinbox.setMinimum(1)
        self.target_day_spinbox.setMaximum(364)  # Hoyle year
        date_input_layout.addWidget(year_label)
        date_input_layout.addWidget(self.target_year_spinbox)
        date_input_layout.addWidget(day_label)
        date_input_layout.addWidget(self.target_day_spinbox)
        date_input_layout.addStretch()
        recal_layout.addLayout(date_input_layout)

        # Eclipse Type and Button Row
        type_button_layout = QHBoxLayout()
        type_label = QLabel("Eclipse Type:")
        self.eclipse_type_combo = QComboBox()
        self.eclipse_type_combo.addItems(["Solar", "Lunar"])
        self.check_alignment_button = QPushButton("Check Alignment")
        self.check_alignment_button.clicked.connect(self._emit_check_alignment_request)
        type_button_layout.addWidget(type_label)
        type_button_layout.addWidget(self.eclipse_type_combo)
        type_button_layout.addStretch()
        type_button_layout.addWidget(self.check_alignment_button)
        recal_layout.addLayout(type_button_layout)

        recal_groupbox.setLayout(recal_layout)
        main_layout.addWidget(recal_groupbox)

        self.setLayout(main_layout)

        self.target_year_spinbox.valueChanged.connect(
            self._emit_check_alignment_request
        )
        self.target_day_spinbox.valueChanged.connect(self._emit_check_alignment_request)
        self.eclipse_type_combo.currentIndexChanged.connect(
            self._emit_check_alignment_request
        )

    def _emit_check_alignment_request(self):
        """
        Emits the check_alignment_requested signal with current UI values.
        """
        year = self.target_year_spinbox.value()
        day = self.target_day_spinbox.value()
        eclipse_type = self.eclipse_type_combo.currentText()
        self.check_alignment_requested.emit(year, day, eclipse_type)

    def _toggle_auto_run(self, checked: bool):
        """
        Handles the Start/Stop button click.
        Emits auto_run_toggled signal and updates button text.
        """
        if checked:
            self.start_stop_button.setText("Stop Auto-Run")
        else:
            self.start_stop_button.setText("Start Auto-Run")
        self.auto_run_toggled.emit(checked)

    def set_next_step_enabled(self, enabled: bool):
        """
        Allows the main window to enable/disable the Next Step button.
        Typically disabled during auto-run.
        """
        self.next_step_button.setEnabled(enabled)

    def reset_alignment_inputs_to_default(self):
        """
        Resets the 'Check Alignment' input fields to their default values (Year 1, Day 1, Type 'Solar').
        Signals are temporarily blocked during programmatic value changes.
        """
        self.target_year_spinbox.blockSignals(True)
        self.target_day_spinbox.blockSignals(True)
        self.eclipse_type_combo.blockSignals(True)

        self.target_year_spinbox.setValue(1)
        self.target_day_spinbox.setValue(1)
        self.eclipse_type_combo.setCurrentIndex(0)  # Assuming 'Solar' is at index 0

        self.target_year_spinbox.blockSignals(False)
        self.target_day_spinbox.blockSignals(False)
        self.eclipse_type_combo.blockSignals(False)

        # Explicitly emit the signal after values are set and signals unblocked
        self._emit_check_alignment_request()

    def update_time_display(self, day: int, year: int):
        self.current_day_label.setText(f"Current Day: {day}")
        self.current_year_label.setText(f"Current Year: {year}")

    def update_run_button_text(self, is_running: bool):
        self.start_stop_button.setText(
            "Stop Auto-Run" if is_running else "Start Auto-Run"
        )


# Example usage for testing this widget directly
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication, QVBoxLayout

    app = QApplication(sys.argv)
    window = QWidget()  # Main window for testing
    main_layout_for_test = QVBoxLayout(
        window
    )  # Renamed to avoid conflict if pasting into other files

    controls_panel = ControlsPanelWidget()
    # control_panel.next_step_requested.connect(on_next)
    # control_panel.reset_requested.connect(on_reset)
    # control_panel.auto_run_toggled.connect(on_auto_run_toggle)
    # control_panel.speed_changed.connect(on_speed_change)
    # control_panel.check_alignment_requested.connect(on_check_alignment)
    # control_panel.reset_from_ephemeris_requested.connect(on_reset_from_ephemeris)
    # control_panel.set_from_almanac_requested.connect(on_set_from_almanac)
    # control_panel.set_location_orientation_requested.connect(on_set_location_orientation)
    # control_panel.set_gc_epoch_and_cardinals_requested.connect(on_set_gc_epoch) # Example connection

    main_layout_for_test.addWidget(controls_panel)

    window.setWindowTitle("Controls Panel Test")
    window.setGeometry(300, 300, 400, 150)  # Adjusted height for new controls
    window.show()

    # Set initial state for buttons for testing visual appearance
    controls_panel._toggle_auto_run(False)  # Ensure it starts as "Start Auto-Run"
    controls_panel.set_next_step_enabled(True)

    sys.exit(app.exec())
