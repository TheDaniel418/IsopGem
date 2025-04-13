"""Circle Tool toolbar for the Sacred Geometry Explorer.

This module contains the toolbar for the Circle Tool, which provides
options for creating different types of circles.
"""

from loguru import logger
from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDoubleSpinBox,
    QLabel,
    QToolBar,
)


class CircleToolbar(QToolBar):
    """Toolbar for the Circle Tool.

    This toolbar provides options for creating different types of circles,
    such as circles by center and point, circles with fixed radius, and
    circles by diameter.
    """

    # Signals
    mode_changed = pyqtSignal(str)  # Mode name
    radius_changed = pyqtSignal(float)  # Radius value

    # Circle creation modes
    MODE_CENTER_POINT = "center_point"  # Circle by center and point on circumference
    MODE_FIXED_RADIUS = "fixed_radius"  # Circle with fixed radius
    MODE_DIAMETER = "diameter"  # Circle by diameter (two points)
    MODE_THREE_POINTS = "three_points"  # Circle through three points

    def __init__(self, parent=None):
        """Initialize the Circle toolbar.

        Args:
            parent: Parent widget
        """
        super().__init__("Circle Options", parent)

        # Set properties
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(16, 16))

        # Current mode
        self.current_mode = self.MODE_CENTER_POINT

        # Fixed radius value
        self.fixed_radius = 100.0

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the toolbar UI."""
        # Create button group for circle modes
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        # Add mode buttons
        self.center_point_action = self._create_mode_button(
            "Center-Point",
            "Create circle by center and point on circumference",
            self.MODE_CENTER_POINT,
            QKeySequence("Ctrl+1"),
            True,  # Default checked
        )

        self.fixed_radius_action = self._create_mode_button(
            "Fixed Radius",
            "Create circle with fixed radius",
            self.MODE_FIXED_RADIUS,
            QKeySequence("Ctrl+2"),
        )

        self.diameter_action = self._create_mode_button(
            "Diameter",
            "Create circle by diameter (two points)",
            self.MODE_DIAMETER,
            QKeySequence("Ctrl+3"),
        )

        self.three_points_action = self._create_mode_button(
            "Three Points",
            "Create circle through three points",
            self.MODE_THREE_POINTS,
            QKeySequence("Ctrl+4"),
        )

        # Add separator
        self.addSeparator()

        # Add radius input for fixed radius mode
        self.addWidget(QLabel("Radius:"))

        self.radius_spinbox = QDoubleSpinBox()
        self.radius_spinbox.setRange(0.1, 10000.0)
        self.radius_spinbox.setValue(self.fixed_radius)
        self.radius_spinbox.setSingleStep(10.0)
        self.radius_spinbox.setDecimals(1)
        self.radius_spinbox.setToolTip("Set the radius for fixed radius circles")
        self.radius_spinbox.valueChanged.connect(self._on_radius_changed)
        self.addWidget(self.radius_spinbox)

        # Connect signals
        self.mode_group.buttonClicked.connect(self._on_mode_changed)

        logger.debug("Circle toolbar initialized")

    def _create_mode_button(self, text, tooltip, mode, shortcut=None, checked=False):
        """Create a mode button and add it to the toolbar.

        Args:
            text: Button text
            tooltip: Button tooltip
            mode: Mode identifier
            shortcut: Optional keyboard shortcut
            checked: Whether the button is initially checked

        Returns:
            Created action
        """
        action = QAction(text, self)
        action.setCheckable(True)
        action.setChecked(checked)
        action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(shortcut)

        # Store mode as data
        action.setData(mode)

        # Add to toolbar
        self.addAction(action)

        # Add to button group
        button = self.widgetForAction(action)
        if button:
            self.mode_group.addButton(button)

        return action

    def _on_mode_changed(self, button):
        """Handle mode change.

        Args:
            button: Clicked button
        """
        # Find the action for this button
        for action in self.actions():
            if self.widgetForAction(action) == button:
                # Get mode from action data
                mode = action.data()

                # Update current mode
                self.current_mode = mode

                # Enable/disable radius spinbox based on mode
                self.radius_spinbox.setEnabled(mode == self.MODE_FIXED_RADIUS)

                # Emit signal
                self.mode_changed.emit(mode)

                logger.debug(f"Circle mode changed to {mode}")
                break

    def _on_radius_changed(self, value):
        """Handle radius change.

        Args:
            value: New radius value
        """
        # Update fixed radius
        self.fixed_radius = value

        # Emit signal
        self.radius_changed.emit(value)

        logger.debug(f"Fixed radius changed to {value}")

    def get_current_mode(self):
        """Get the current circle creation mode.

        Returns:
            Current mode
        """
        return self.current_mode

    def get_fixed_radius(self):
        """Get the current fixed radius value.

        Returns:
            Fixed radius value
        """
        return self.fixed_radius
