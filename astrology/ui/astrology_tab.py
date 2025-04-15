"""Astrology tab implementation.

This module provides the main tab for the Astrology pillar.
"""

import random

from loguru import logger
from PyQt6.QtCore import QPointF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from astrology.ui.dialogs.astrological_database_manager import (
    AstrologicalDatabaseManager,
)
from astrology.ui.dialogs.birth_chart_window import BirthChartWindow
from astrology.ui.dialogs.cycle_calculator_window import CycleCalculatorWindow
from astrology.ui.dialogs.planner_window import PlannerWindow
from shared.repositories.database import Database
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

    def _open_planner(self):
        """Open the astrological planner window."""
        # Create the planner window
        planner_window = PlannerWindow()

        # Set the window title
        planner_window.setWindowTitle("Astrological Planner")

        # Connect chart requested signal
        planner_window.chart_requested.connect(self._on_chart_requested_from_planner)

        # Open it in a window
        self.window_manager.open_window("astro_planner", planner_window)

    def _on_chart_requested_from_planner(self, chart):
        """Handle chart request from the planner.

        Args:
            chart: Chart to display
        """
        # Create a birth chart window with the chart
        birth_chart_window = BirthChartWindow()
        birth_chart_window.set_chart(chart)

        # Set the window title
        birth_chart_window.setWindowTitle(f"Chart: {chart.name}")

        # Open it in a window
        self.window_manager.open_window("planner_chart", birth_chart_window)

    def _open_cycle_calculator(self):
        """Open the cosmic cycle calculator window."""
        # Create the cycle calculator window
        cycle_calculator_window = CycleCalculatorWindow()

        # Set the window title
        cycle_calculator_window.setWindowTitle("Cosmic Cycle Calculator")

        # Connect chart requested signal
        cycle_calculator_window.chart_requested.connect(
            self._on_chart_requested_from_cycle_calculator
        )

        # Open it in a window
        self.window_manager.open_window("cycle_calculator", cycle_calculator_window)

    def _on_chart_requested_from_cycle_calculator(self, chart):
        """Handle chart request from the cycle calculator.

        Args:
            chart: Chart to display
        """
        # Create a birth chart window with the chart
        birth_chart_window = BirthChartWindow()
        birth_chart_window.set_chart(chart)

        # Set the window title
        birth_chart_window.setWindowTitle(f"Chart: {chart.name}")

        # Open it in a window
        self.window_manager.open_window("cycle_chart", birth_chart_window)

    def _open_database_manager(self):
        """Open the astrological database manager dialog."""
        try:
            # Get the database instance
            database = Database.get_instance()

            # Create the database manager dialog
            db_manager = AstrologicalDatabaseManager(database, self)

            # Show the dialog
            db_manager.exec()
        except Exception as e:
            logger.error(f"Error opening database manager: {e}", exc_info=True)
            # Show error message to user
            QMessageBox.critical(
                self,
                "Database Manager Error",
                f"Could not open database manager: {str(e)}",
            )

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

        # Cycle Calculator button (renamed from Transit Calculator)
        cycle_btn = QPushButton("Cycle Calculator")
        cycle_btn.setToolTip("Search for cosmic cycles and planetary patterns")
        cycle_btn.clicked.connect(self._open_cycle_calculator)
        button_layout.addWidget(cycle_btn)

        # Zodiac Explorer button
        zodiac_btn = QPushButton("Zodiac Explorer")
        zodiac_btn.setToolTip("Explore zodiac signs and their meanings")
        # zodiac_btn.clicked.connect(lambda: self._open_zodiac_explorer())
        button_layout.addWidget(zodiac_btn)

        # Planner button
        planner_btn = QPushButton("Planner")
        planner_btn.setToolTip("Open the astrological daily planner")
        planner_btn.clicked.connect(self._open_planner)
        button_layout.addWidget(planner_btn)

        # Database Manager button
        db_manager_btn = QPushButton("Database Manager")
        db_manager_btn.setToolTip("Manage the astrological events database")
        db_manager_btn.clicked.connect(self._open_database_manager)
        button_layout.addWidget(db_manager_btn)

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
