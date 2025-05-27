"""Astrology tab implementation.

This module provides the main tab for the Astrology pillar.
"""

import random
from typing import Optional

from loguru import logger
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from astrology.ui.dialogs.birth_chart_window import BirthChartWindow
from astrology.ui.windows.kamea_calendar_window import KameaCalendarWindow
from astrology.ui.widgets.stonehenge_predictor.adyton_window import AdytonWindow
from astrology.ui.widgets.stonehenge_predictor.stonehenge_predictor_window import StonehengePredictorWindow
from astrology.services.stonehenge_simulation_service import StonehengeSimulationService
from shared.ui.window_management import TabManager, WindowManager


class AstrologyTab(QWidget):
    """Main tab for the Astrology pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Astrology tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager

        # Star properties
        self.stars = []
        self.num_stars = 300
        self.generate_stars()

        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.twinkle_stars)
        self.timer.start(
            100
        )  # Update every 100ms (reduced from 50ms for better performance)

        # Instance to hold the StonehengePredictorWindow
        self.stonehenge_window_instance: Optional[StonehengePredictorWindow] = None
        # Instance to hold the AdytonWindow
        self.adyton_window_instance: Optional[AdytonWindow] = None
        
        # Placeholder for simulation service access
        # This needs proper implementation based on service management (e.g., ServiceLocator)
        self._simulation_service_instance: Optional[StonehengeSimulationService] = None

        # Initialize UI
        self._init_ui()
        logger.debug("AstrologyTab initialized")

    def generate_stars(self):
        """Generate random stars for the field."""
        for _ in range(self.num_stars):
            # Generate random position
            x = random.randint(0, 100)  # As percentage of width
            y = random.randint(0, 100)  # As percentage of height

            # Generate random size (1-3 pixels)
            size = random.uniform(0.5, 3)

            # Generate random brightness (0.2-1.0)
            brightness = random.uniform(0.2, 1.0)

            # Generate random color (mostly white/blue, some yellow/red)
            hue = random.choice(
                [
                    random.randint(200, 240),  # Blue
                    random.randint(40, 60),  # Yellow
                    0,  # Red
                    random.randint(0, 360),  # Any color (rare)
                ]
            )
            saturation = random.randint(0, 20)  # Mostly white
            value = int(255 * brightness)

            # Add star to list
            self.stars.append(
                {
                    "x": x,
                    "y": y,
                    "size": size,
                    "brightness": brightness,
                    "hue": hue,
                    "saturation": saturation,
                    "value": value,
                    "twinkle_direction": random.choice([-1, 1]),
                    "twinkle_speed": random.uniform(0.01, 0.03),
                }
            )

    def twinkle_stars(self):
        """Update star brightness for twinkling effect."""
        for star in self.stars:
            # Update brightness
            star["brightness"] += star["twinkle_direction"] * star["twinkle_speed"]

            # Reverse direction if limits reached
            if star["brightness"] > 1.0:
                star["brightness"] = 1.0
                star["twinkle_direction"] = -1
            elif star["brightness"] < 0.2:
                star["brightness"] = 0.2
                star["twinkle_direction"] = 1

            # Update value based on brightness
            star["value"] = int(255 * star["brightness"])

        # Trigger repaint
        self.update()

    def _open_birth_chart(self):
        """Open the birth chart window."""
        # Create the birth chart window
        birth_chart_window = BirthChartWindow()

        # Set the window title
        birth_chart_window.setWindowTitle("Birth Chart")

        # Open it in a window
        self.window_manager.open_window("birth_chart", birth_chart_window)

    def _open_cosmic_calendar(self):
        """Open the Kamea Cosmic Calendar window."""
        # Create the Kamea Cosmic Calendar window
        calendar_window = KameaCalendarWindow()

        # Open it in a window
        self.window_manager.open_window("kamea_cosmic_calendar", calendar_window)
        logger.info("Opened Kamea Cosmic Calendar window")

    def _open_stonehenge_predictor(self):
        """Open the Stonehenge Eclipse Predictor window."""
        # Create the Stonehenge Predictor window
        if self.stonehenge_window_instance is None or not self.stonehenge_window_instance.isVisible():
            logger.info("Creating new StonehengePredictorWindow instance.")
            self.stonehenge_window_instance = StonehengePredictorWindow()
            # Open it in a window using a unique key
            self.window_manager.open_window("stonehenge_eclipse_predictor", self.stonehenge_window_instance)
        else:
            logger.info("StonehengePredictorWindow already exists, bringing to front.")
            self.stonehenge_window_instance.show()
            self.stonehenge_window_instance.activateWindow()
            self.stonehenge_window_instance.raise_()
        
        logger.info("Opened or focused Stonehenge Eclipse Predictor window")

    def _get_simulation_service(self) -> Optional[StonehengeSimulationService]:
        """
        Retrieves or initializes the StonehengeSimulationService for the Adyton.
        This service instance is separate and independent from any used by other 
        components like the Circle of 56 predictor.
        """
        if self._simulation_service_instance is None:
            try:
                logger.info("AstrologyTab: Creating a new, dedicated StonehengeSimulationService instance for Adyton.")
                self._simulation_service_instance = StonehengeSimulationService()

            except Exception as e:
                logger.error(f"AstrologyTab: Failed to create dedicated StonehengeSimulationService for Adyton: {e}")
                return None
        return self._simulation_service_instance

    def _launch_adyton_view(self):
        """Launch the Adyton 3D viewer directly."""
        sim_service = self._get_simulation_service()
        if not sim_service:
            logger.error("Cannot launch Adyton: StonehengeSimulationService not available.")
            return

        if self.adyton_window_instance is None or not self.adyton_window_instance.isVisible():
            logger.info("Creating and showing new AdytonWindow instance.")
            self.adyton_window_instance = AdytonWindow(None) # Create as top-level
            # Use window_manager to open it, ensuring it's tracked (optional, but good practice)
            # The key "adyton_of_the_seven" should be unique.
            self.window_manager.open_window(
                "adyton_of_the_seven", 
                self.adyton_window_instance
            )
        else:
            logger.info("AdytonWindow already exists, bringing to front.")
            self.adyton_window_instance.show()
            self.adyton_window_instance.activateWindow()
            self.adyton_window_instance.raise_()
        
        if self.adyton_window_instance and self.adyton_window_instance.isVisible():
            try:
                marker_positions = sim_service.get_current_marker_positions()
                self.adyton_window_instance.update_marker_positions(marker_positions)
                logger.info("Adyton viewer launched/focused and updated with marker positions.")
            except Exception as e:
                logger.error(f"Error updating Adyton with marker positions: {e}")
        else:
            logger.error("Failed to open or focus Adyton window.")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout for the tab
        layout = QVBoxLayout(self)

        # Button bar with semi-transparent background
        button_bar = QFrame()
        button_bar.setObjectName("astrology_button_bar")
        button_bar.setStyleSheet(
            """
            QFrame#astrology_button_bar {
                background-color: rgba(0, 0, 0, 70);
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton {
                background-color: rgba(40, 80, 120, 180);
                color: white;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(60, 120, 180, 200);
            }
        """
        )
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(10, 5, 10, 5)
        button_layout.setSpacing(10)

        # Birth Chart button
        birth_chart_btn = QPushButton("Birth Chart")
        birth_chart_btn.setToolTip("Create and analyze birth charts")
        birth_chart_btn.clicked.connect(self._open_birth_chart)
        button_layout.addWidget(birth_chart_btn)

        # Cosmic Calendar button
        cosmic_calendar_btn = QPushButton("Cosmic Calendar")
        cosmic_calendar_btn.setToolTip("Visualize the Kamea Cosmic Calendar")
        cosmic_calendar_btn.clicked.connect(self._open_cosmic_calendar)
        button_layout.addWidget(cosmic_calendar_btn)

        # Stonehenge Predictor button
        stonehenge_predictor_btn = QPushButton("Circle of 56")
        stonehenge_predictor_btn.setToolTip("Open the Stonehenge Eclipse Predictor")
        stonehenge_predictor_btn.clicked.connect(self._open_stonehenge_predictor)
        button_layout.addWidget(stonehenge_predictor_btn)

        # Adyton button
        adyton_btn = QPushButton("Adyton")
        adyton_btn.setToolTip("Open the 3D Adyton of the Seven visualization")
        adyton_btn.clicked.connect(self._launch_adyton_view)
        button_layout.addWidget(adyton_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show Astrology help")
        help_btn.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(52, 152, 219, 180);
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(41, 128, 185, 200);
            }
        """
        )
        # help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        # Add button bar to main layout
        layout.addWidget(button_bar)

        # Create card for welcome content
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet(
            """
            #welcomeCard {
                background-color: rgba(255, 255, 255, 180);
                border-radius: 8px;
                border: 1px solid rgba(200, 200, 255, 120);
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

        # Title and welcome message with enhanced styling
        title = QLabel("Astrology")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1565C0;")

        welcome = QLabel(
            "Welcome to the Astrology pillar. Here you can explore planetary positions, "
            "zodiac signs, and their correspondences to numbers and sacred geometry."
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("font-size: 14px; color: #222;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description with more details
        description = QLabel(
            "Astrology is a system that seeks to understand the relationship between celestial "
            "movements and events on Earth. It has been practiced across cultures for thousands "
            "of years and continues to be an influence in many people's lives."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #333; margin-top: 10px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add content to welcome card
        welcome_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(description)

        # Add welcome card to main layout
        layout.addWidget(welcome_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add Urania image below welcome card
        urania_container = QFrame()
        urania_container.setObjectName("uraniaImageContainer")
        urania_container.setStyleSheet(
            """
            #uraniaImageContainer {
                background-color: rgba(255, 255, 255, 100);
                border-radius: 8px;
                margin: 10px 40px 20px 40px;
                padding: 10px;
            }
        """
        )
        urania_layout = QVBoxLayout(urania_container)

        # Create image label
        urania_image_label = QLabel()
        urania_pixmap = QPixmap("assets/tab_images/urania.png")

        if not urania_pixmap.isNull():
            # Scale the image to a reasonable size while maintaining aspect ratio
            scaled_pixmap = urania_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            urania_image_label.setPixmap(scaled_pixmap)
            urania_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add caption
            caption = QLabel("Urania - Muse of Astronomy and Celestial Sciences")
            caption.setStyleSheet(
                "font-size: 12px; color: #1565C0; font-style: italic; background-color: rgba(255, 255, 255, 150); padding: 4px; border-radius: 4px;"
            )
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

            urania_layout.addWidget(
                urania_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            urania_layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add the image container to the main layout
            layout.addWidget(urania_container, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            logger.error(
                "Failed to load Urania image from assets/tab_images/urania.png"
            )

        # Add stretch to push content to top
        layout.addStretch()

    def paintEvent(self, event):
        """Custom paint event to draw the starry background."""
        super().paintEvent(event)  # Draw the widget normally first

        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw dark blue gradient background
        gradient = QRadialGradient(
            QPointF(self.width() / 2, self.height() / 2),
            max(self.width(), self.height()),
        )
        gradient.setColorAt(0, QColor(10, 10, 40))
        gradient.setColorAt(1, QColor(0, 0, 20))
        painter.fillRect(self.rect(), QBrush(gradient))

        # Draw stars
        for star in self.stars:
            # Calculate pixel position
            x = int(self.width() * star["x"] / 100)
            y = int(self.height() * star["y"] / 100)

            # Set color
            color = QColor()
            color.setHsv(star["hue"], star["saturation"], star["value"])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))

            # Draw star (circle with optional glow for brighter stars)
            size = star["size"]
            if star["brightness"] > 0.7:
                # For bright stars, add glow
                glow_gradient = QRadialGradient(QPointF(x, y), size * 3)
                glow_color = QColor(color)
                glow_color.setAlpha(50)
                glow_gradient.setColorAt(0, color)
                glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(glow_gradient))
                painter.drawEllipse(QPointF(x, y), size * 3, size * 3)

                # Draw core
                painter.setBrush(QBrush(color))

            # Draw the star
            painter.drawEllipse(QPointF(x, y), size, size)

            # For really bright stars, add cross spikes
            if star["brightness"] > 0.85:
                painter.setPen(QPen(color, 0.5))
                spike_length = size * 4
                painter.drawLine(
                    QPointF(x - spike_length, y), QPointF(x + spike_length, y)
                )
                painter.drawLine(
                    QPointF(x, y - spike_length), QPointF(x, y + spike_length)
                )
