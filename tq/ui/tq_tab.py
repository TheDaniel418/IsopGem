"""TQ tab implementation.

This module provides the main tab for the TQ pillar.
"""

import math
import random

from loguru import logger
from PyQt6.QtCore import QRectF, Qt, QTime, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import TabManager, WindowManager
from tq.services import tq_analysis_service
from tq.ui.panels.kamea_of_maut_panel import KameaOfMautPanel
from tq.ui.panels.pair_finder_panel import PairFinderPanel
from tq.ui.panels.ternary_dimension_panel import TernaryDimensionalAnalysisPanel
from tq.ui.widgets.planar_expansion_visualizer import PlanarExpansionVisualizer
from tq.ui.widgets.ternary_visualizer import TernaryVisualizerPanel


class TernaryDigit:
    """A ternary digit (0, 1, 2) with animation and visual properties."""

    def __init__(self):
        # Ternary value (0, 1, 2)
        self.value = random.randint(0, 2)

        # Position (as percentage of width/height)
        self.x = random.uniform(5, 95)
        self.y = random.uniform(5, 95)

        # Vertical movement only (Matrix-style)
        self.dy = random.uniform(
            0.2, 0.6
        )  # Slightly slower for better trail visibility

        # Size (0 is smallest, 2 is largest)
        base_size = random.uniform(18, 26)
        self.size = base_size + (self.value * 2)

        # For Matrix effect: longer tail with more segments
        self.tail_length = random.randint(15, 25)  # Increased from 5-12 to 15-25
        self.segments = []
        for i in range(self.tail_length):
            # Each segment is a single ternary digit (0, 1, 2)
            self.segments.append(
                {
                    "value": random.randint(
                        0, 2
                    ),  # Each segment can be a different value
                    "y_offset": -i
                    * (self.size * 0.4),  # Space segments vertically (closer together)
                    # Slower fade-out with longer visible trail
                    "alpha": max(
                        0.0, min(1.0, 1.0 - (i * 0.5 / self.tail_length))
                    ),  # More gradual alpha reduction
                }
            )

        # Visual properties
        # Green hues for Matrix effect (clamped to valid range)
        self.hue = random.uniform(0.31, 0.39)  # Green range, safely within 0-1
        self.saturation = random.uniform(0.7, 0.9)  # Always < 1.0
        self.value_prop = random.uniform(0.7, 0.9)  # Always < 1.0

        # Higher digits are brighter (0 is dimmest, 2 is brightest)
        self.brightness_factor = 0.7 + (
            self.value * 0.1
        )  # Reduced from 0.15 to 0.1 to stay < 1.0
        self.alpha = min(0.9, 0.7 + (self.value * 0.07))  # Ensure < 1.0

        # For color transition
        self.glow_amount = random.uniform(0.0, 1.0)
        self.glow_speed = random.uniform(0.01, 0.02)  # Slightly slower glow

        # For digit changing
        self.change_probability = 0.02  # 2% chance to change each frame
        self.time_until_next_change = random.uniform(2.0, 5.0)  # Initial timer

        # For 'born' effect - new digits start small and grow
        self.age = random.uniform(0.5, 1.0)  # Start with some existing
        self.grow_speed = random.uniform(0.03, 0.1)

    def update(self, dt):
        """Update the ternary digit's animation state."""
        # Move the digit down
        self.y += self.dy

        # If it goes off screen, reset at the top with a new value
        if self.y > 105:  # Add a buffer so digits appear to fall off screen
            self.y = -5 - random.uniform(0, 10)  # Start above the top edge, staggered
            self.value = random.randint(0, 2)  # New random value
            self.age = 0.0  # Reset age for grow effect

            # Update segments for the new digit
            for segment in self.segments:
                segment["value"] = random.randint(0, 2)

        # Grow new digits
        if self.age < 1.0:
            self.age += self.grow_speed * dt
            if self.age > 1.0:
                self.age = 1.0

        # Animate the glow
        self.glow_amount += self.glow_speed * dt
        if self.glow_amount > 1.0:
            self.glow_amount = 0.0

        # Random chance to change digit value (to add dynamism)
        self.time_until_next_change -= dt
        if self.time_until_next_change <= 0:
            # Change to a different value
            new_value = random.randint(0, 2)
            while new_value == self.value:
                new_value = random.randint(0, 2)
            self.value = new_value

            # Also cascade changes down the tail
            for segment in self.segments:
                if random.random() < 0.7:  # 70% chance to change each segment
                    segment["value"] = random.randint(0, 2)

            # Reset timer with some randomness
            self.time_until_next_change = random.uniform(2.0, 5.0)


class MatrixCanvas(QWidget):
    """A canvas widget for drawing the Matrix-like ternary digits effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.digits = []
        self.num_digits = 60  # Increased from 40 to 60 for more digits

        # Initialize digits
        for _ in range(self.num_digits):
            self.digits.append(TernaryDigit())

        # Make widget transparent for mouse events and backgrounds
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(40)  # ~25 FPS

        # Debug info
        logger.debug(f"MatrixCanvas initialized with {self.num_digits} ternary digits")

    def update_animation(self):
        """Update all digit animations."""
        # Get elapsed time since last update
        current_time = QTime.currentTime().msecsSinceStartOfDay() * 0.001  # To seconds
        if not hasattr(self, "last_update_time"):
            self.last_update_time = current_time

        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # Update each ternary digit
        for digit in self.digits:
            digit.update(dt)

        # Remove debug logging to reduce console spam
        # (previously logged animation updates every 60 frames)

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        """Paint the Matrix-like ternary effect."""
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Draw background with very slight dark green tint
        painter.fillRect(self.rect(), QColor(0, 10, 0, 15))  # Slightly more transparent

        # Draw each ternary digit with its trail
        for digit in self.digits:
            # Calculate actual position
            x = self.width() * digit.x / 100.0
            y = self.height() * digit.y / 100.0

            # Draw the trail segments first (back to front)
            for segment in reversed(digit.segments):
                segment_y = y + segment["y_offset"]

                # Skip if the segment is off-screen
                if segment_y < -50 or segment_y > self.height() + 50:
                    continue

                # Set color for this segment - ensure all values are within valid range
                segment_color = QColor()
                segment_color.setHsvF(
                    max(0.0, min(1.0, digit.hue)),
                    max(0.0, min(1.0, digit.saturation * 0.7)),
                    max(0.0, min(1.0, digit.value_prop * 0.7)),
                    max(0.0, min(1.0, segment["alpha"])),
                )

                # Draw segment digit
                digit_font = QFont("Courier New", int(digit.size * 0.8 * digit.age))
                digit_font.setBold(True)
                painter.setFont(digit_font)
                painter.setPen(segment_color)
                painter.drawText(
                    QRectF(
                        x - digit.size / 2,
                        segment_y - digit.size / 2,
                        digit.size,
                        digit.size,
                    ),
                    Qt.AlignmentFlag.AlignCenter,
                    str(segment["value"]),
                )

            # Now draw the main digit
            # Glow effect based on sine wave
            glow_factor = abs(math.sin(digit.glow_amount * math.pi))

            # Main color is bright green for the lead digit
            main_color = QColor()

            # Main digit brightness changes with glow - ensure all values are within valid range
            brightness = max(
                0.0,
                min(
                    1.0,
                    digit.value_prop
                    * digit.brightness_factor
                    * (0.8 + 0.2 * glow_factor),
                ),
            )
            main_color.setHsvF(
                max(0.0, min(1.0, digit.hue)),
                max(0.0, min(1.0, digit.saturation)),
                brightness,
                max(0.0, min(1.0, digit.alpha)),
            )

            # Draw the main digit
            digit_font = QFont("Courier New", int(digit.size * digit.age))
            digit_font.setBold(True)
            painter.setFont(digit_font)
            painter.setPen(main_color)
            painter.drawText(
                QRectF(x - digit.size / 2, y - digit.size / 2, digit.size, digit.size),
                Qt.AlignmentFlag.AlignCenter,
                str(digit.value),
            )

            # Add a subtle glow for the lead digit when it's glowing
            if glow_factor > 0.5:
                glow_alpha = max(0.0, min(1.0, 0.4 * (glow_factor - 0.5) * 2.0))
                glow_color = QColor(main_color)
                glow_color.setAlphaF(glow_alpha)
                painter.setPen(glow_color)

                # Slightly larger font for glow
                glow_font = QFont("Courier New", int(digit.size * digit.age * 1.1))
                glow_font.setBold(True)
                painter.setFont(glow_font)

                painter.drawText(
                    QRectF(
                        x - digit.size / 2, y - digit.size / 2, digit.size, digit.size
                    ),
                    Qt.AlignmentFlag.AlignCenter,
                    str(digit.value),
                )


class TQTab(QWidget):
    """Main tab for the TQ pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the TQ tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager

        # Set layout first
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        # Initialize matrix canvas
        self.matrix_canvas = MatrixCanvas(self)

        self._init_ui()
        logger.debug("TQTab initialized")

    def resizeEvent(self, event) -> None:
        """Called when the tab is resized."""
        super().resizeEvent(event)

        # Resize the matrix canvas to match the tab size
        if hasattr(self, "matrix_canvas") and hasattr(self, "stacked_widget"):
            self.matrix_canvas.resize(self.stacked_widget.size())
            self.matrix_canvas.raise_()  # Keep it on top

    def showEvent(self, event) -> None:
        """Called when the tab is shown."""
        super().showEvent(event)

        # Ensure canvas is visible when tab is shown
        if hasattr(self, "matrix_canvas"):
            self.matrix_canvas.setVisible(True)
            self.matrix_canvas.raise_()

    def _ensure_canvas_on_top(self) -> None:
        """Make sure the matrix canvas is visible and on top."""
        self.matrix_canvas.setVisible(True)
        self.matrix_canvas.raise_()
        self.update()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Create a stacked widget to hold both content and canvas
        self.stacked_widget = QWidget(self)
        self.layout().addWidget(self.stacked_widget)

        # Stack layout for stacked_widget
        stack_layout = QVBoxLayout(self.stacked_widget)
        stack_layout.setContentsMargins(0, 0, 0, 0)
        stack_layout.setSpacing(0)

        # Content container with completely transparent background
        content_container = QWidget()
        content_container.setObjectName("tq_content")
        content_container.setStyleSheet(
            """
            QWidget#tq_content {
                background-color: transparent;
            }
        """
        )
        content_layout = QVBoxLayout(content_container)

        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        # TQ Grid button
        grid_btn = QPushButton("TQ Grid")
        grid_btn.setToolTip("Open TQ Grid Explorer")
        grid_btn.clicked.connect(self._open_tq_grid)
        button_layout.addWidget(grid_btn)

        # Elemental Analysis button
        elemental_btn = QPushButton("Elemental Analysis")
        elemental_btn.setToolTip("Analyze elemental components")
        elemental_btn.clicked.connect(self._open_cosmic_force_analysis)
        button_layout.addWidget(elemental_btn)

        # Chart Creator button
        chart_btn = QPushButton("Chart Creator")
        chart_btn.setToolTip("Create and save TQ charts")
        chart_btn.clicked.connect(self._open_planar_expansion)
        button_layout.addWidget(chart_btn)

        # Ternary Visualizer button
        visualizer_btn = QPushButton("Ternary Visualizer")
        visualizer_btn.setToolTip("Visualize and transform ternary numbers")
        visualizer_btn.clicked.connect(self._open_ternary_visualizer)
        button_layout.addWidget(visualizer_btn)

        # Ternary Transition button
        transition_btn = QPushButton("Ternary Transition")
        transition_btn.setToolTip("Calculate transitions between ternary numbers")
        transition_btn.clicked.connect(self._open_ternary_transition)
        button_layout.addWidget(transition_btn)

        # Series Transition button
        series_btn = QPushButton("Series Transition")
        series_btn.setToolTip("Calculate transitions between series of numbers")
        series_btn.clicked.connect(self._open_series_transition)
        button_layout.addWidget(series_btn)

        # Pair Finder button
        pair_finder_btn = QPushButton("Pair Finder")
        pair_finder_btn.setToolTip("Find pairs of numbers with specific properties")
        pair_finder_btn.clicked.connect(self._open_pair_finder)
        button_layout.addWidget(pair_finder_btn)

        # Kamea of Maut button
        kamea_btn = QPushButton("Kamea of Maut")
        kamea_btn.setToolTip("Explore the 27×27 ternary fractal Kamea")
        kamea_btn.clicked.connect(self._open_kamea_of_maut)
        button_layout.addWidget(kamea_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show TQ help")
        help_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        # help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        # Add button bar to content layout
        content_layout.addWidget(button_bar)

        # Create card for welcome content with Matrix-inspired styling
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet(
            """
            #welcomeCard {
                background-color: rgba(0, 15, 0, 0.7);
                border-radius: 8px;
                border: 1px solid #00ff00;
                padding: 15px;
                margin: 20px 40px;
                min-width: 500px;
                max-width: 800px;
                min-height: 200px;
            }
        """
        )
        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(15, 15, 15, 15)
        welcome_layout.setSpacing(10)

        # Title and welcome message with Matrix-inspired styling
        title = QLabel("TQ Analysis")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00;")

        welcome = QLabel(
            "Welcome to the Trigammaton Qabalah (TQ) pillar. Here you can explore the mathematical "
            "and metaphysical relationships between ternary numbers and geometric structures."
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("font-size: 14px; color: #aaffaa;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description with more details
        description = QLabel(
            "Trigammaton Qabalah uses a base-3 (ternary) number system where the digits 0, 1, and 2 "
            "represent Tao/Void, Yang/Active, and Yin/Receptive forces. The system maps ternary numbers "
            "to geometric elements (vertices, edges, faces) in multi-dimensional space, with the number "
            "of 0-digits (Tao lines) determining the geometric role."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #88cc88; margin-top: 10px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add content to welcome card
        welcome_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(description)

        # Add welcome card to content layout
        content_layout.addWidget(welcome_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add Leo image below welcome card
        leo_container = QFrame()
        leo_container.setObjectName("leoImageContainer")
        leo_container.setStyleSheet(
            """
            #leoImageContainer {
                background-color: transparent;
                margin: 10px 40px 20px 40px;
            }
        """
        )
        leo_layout = QVBoxLayout(leo_container)

        # Create image label
        leo_image_label = QLabel()
        leo_pixmap = QPixmap("assets/tab_images/leo.png")

        if not leo_pixmap.isNull():
            # Scale the image to a reasonable size while maintaining aspect ratio
            scaled_pixmap = leo_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            leo_image_label.setPixmap(scaled_pixmap)
            leo_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add caption with specified text and Matrix-inspired styling
            caption = QLabel("Omega Logion, Founder of Trigrammaton QBLH")
            caption.setStyleSheet(
                "font-size: 12px; color: #00ff00; font-style: italic;"
            )
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

            leo_layout.addWidget(
                leo_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            leo_layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add the image container to the content layout
            content_layout.addWidget(
                leo_container, alignment=Qt.AlignmentFlag.AlignCenter
            )
        else:
            logger.error("Failed to load Leo image from assets/tab_images/leo.png")

        content_layout.addStretch()

        # Add content container to stack layout
        stack_layout.addWidget(content_container)

        # Set up the matrix canvas
        self.matrix_canvas.setParent(self.stacked_widget)
        self.matrix_canvas.resize(self.stacked_widget.size())

        # Place canvas behind the content
        self.matrix_canvas.stackUnder(content_container)

        # Make sure canvas doesn't intercept mouse events
        self.matrix_canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Ensure the canvas is on top after a short delay
        QTimer.singleShot(200, self._ensure_canvas_on_top)

    def _open_tq_grid(self) -> None:
        """Open the TQ Grid panel in a new window."""
        # Use the analysis service instead of directly creating the panel
        tq_analysis_service.get_instance().open_quadset_analysis(
            0
        )  # Start with 0 as default

    def open_quadset_analysis(self, number: int) -> None:
        """Open the TQ Grid panel with a specific number for analysis.

        This is a public method that can be called from other parts of the
        application to launch the TQ Grid with a pre-populated number.

        Args:
            number: The decimal number to analyze
        """
        tq_analysis_service.get_instance().open_quadset_analysis(number)

    def _open_planar_expansion(self) -> None:
        """Open the planar expansion visualizer panel in a new window."""
        panel = PlanarExpansionVisualizer()
        self.window_manager.open_multi_window(
            "tq_planar_expansion", panel, "Planar Expansion Visualizer", (800, 600)
        )

    def _open_ternary_transition(self) -> None:
        """Open the ternary transition calculator in a new window."""
        from tq.ui.dialogs.ternary_transition_window import TernaryTransitionWindow

        # Create instance with window manager
        window_content = TernaryTransitionWindow(window_manager=self.window_manager)

        # Open as multi-window to allow multiple instances
        self.window_manager.open_multi_window(
            "tq_ternary_transition",
            window_content,
            "Ternary Transition Calculator",
            (800, 600),
        )

    def _open_cosmic_force_analysis(self) -> None:
        """Open the Cosmic Force Analysis panel in a new window."""
        panel = TernaryDimensionalAnalysisPanel()
        self.window_manager.open_window("ternary_analysis", panel)
        panel.setWindowTitle("Ternary Dimensional Analysis")

    def _open_series_transition(self) -> None:
        """Open the series transition calculator in a new window."""
        from tq.ui.dialogs.series_transition_window import SeriesTransitionWindow

        # Create instance with parent
        window_content = SeriesTransitionWindow(parent=self)

        # Open as multi-window to allow multiple instances
        self.window_manager.open_multi_window(
            "tq_series_transition",
            window_content,
            "Series Transition Analysis",
            (800, 600),
        )

    def _open_pair_finder(self) -> None:
        """Open the Pair Finder panel in a new window."""
        panel = PairFinderPanel()
        self.window_manager.open_multi_window(
            "tq_pair_finder", panel, "TQ Pair Finder", (800, 600)
        )

    def _open_ternary_visualizer(self) -> None:
        """Open the ternary digit visualizer panel in a new window."""
        panel = TernaryVisualizerPanel()
        self.window_manager.open_multi_window(
            "tq_ternary_visualizer", panel, "Ternary Digit Visualizer", (400, 600)
        )

    def _open_kamea_of_maut(self) -> None:
        """Open the Kamea of Maut panel in a new window."""
        panel = KameaOfMautPanel()
        self.window_manager.open_multi_window(
            "tq_kamea_of_maut", panel, "Kamea of Maut Explorer", (1500, 1100)
        )
