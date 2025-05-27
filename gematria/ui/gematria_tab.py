"""Gematria tab implementation.

This module provides the main tab for the Gematria pillar.
"""

import math
import random

from loguru import logger
from PyQt6.QtCore import QRectF, Qt, QTime, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap, QRadialGradient
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import TabManager, WindowManager


class HebrewLetter:
    """A Hebrew letter with animation and visual properties."""

    def __init__(self):
        # Hebrew letters with their numerical values (for standard gematria)
        self.hebrew_letters = {
            # Alef to Tet (1-9)
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            # Yod to Tsadi (10-90)
            "י": 10,
            "כ": 20,
            "ל": 30,
            "מ": 40,
            "נ": 50,
            "ס": 60,
            "ע": 70,
            "פ": 80,
            "צ": 90,
            # Qof to Tav (100-400)
            "ק": 100,
            "ר": 200,
            "ש": 300,
            "ת": 400,
            # Final forms
            "ך": 20,
            "ם": 40,
            "ן": 50,
            "ף": 80,
            "ץ": 90,
        }

        # Position (as percentage of width/height)
        self.x = random.uniform(5, 95)
        self.y = random.uniform(5, 95)

        # Choose a random letter
        self.letter = random.choice(list(self.hebrew_letters.keys()))
        self.value = self.hebrew_letters[self.letter]

        # For morphing effect - target letter to transform into
        self.target_letter = self.letter
        self.morph_progress = (
            1.0  # Start fully formed (1.0 = current letter, 0.0 = fully target letter)
        )
        self.morph_speed = 0  # Not morphing initially
        self.target_value = self.value  # Initialize target value

        # Size (based on numerical value)
        # Higher values get bigger size, but capped for aesthetics
        self.size = min(80, max(30, self.value * 0.1 + 20))  # Smaller overall

        # Movement
        self.dx = random.uniform(-0.05, 0.05)  # Much slower movement
        self.dy = random.uniform(-0.05, 0.05)

        # Visual properties - ensure all values stay in 0-1 range
        self.hue = random.uniform(0.1, 0.9)  # Avoid extremes for better safety
        self.target_hue = self.hue

        # Higher values get more saturated colors - clamped to 0-1 range
        saturation_base = min(0.8, max(0.2, self.value / 400 * 0.3 + 0.3))
        self.saturation = random.uniform(saturation_base, 0.8)

        # Higher values get brighter - clamped to 0-1 range
        value_base = min(0.8, max(0.2, self.value / 400 * 0.2 + 0.5))
        self.value_prop = random.uniform(value_base, 0.8)

        # Transparency based on numerical value
        # Higher values more visible, but still translucent
        self.alpha = min(0.7, max(0.3, self.value / 400 * 0.3 + 0.3))

        # Animation properties
        self.pulse_offset = random.uniform(0, math.pi * 2)  # Random starting phase
        self.pulse_speed = random.uniform(0.01, 0.02)  # Slower pulsation
        self.pulse_amount = random.uniform(0.05, 0.1)  # Very small pulsation
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-0.1, 0.1)  # Slower rotation

        # Color transition
        self.color_progress = 0.0
        self.color_speed = random.uniform(0.001, 0.002)  # Much slower color changes

        # Connection properties
        self.connect_to = None  # Will store reference to another letter to connect to
        self.connection_alpha = 0.0  # Opacity of connection line
        self.connection_target_alpha = 0.0  # Target opacity
        self.connection_speed = 0.005  # Speed of connection fade in/out

        # Morph timer
        self.time_until_morph = random.uniform(3.0, 8.0)  # Random time until next morph

    def start_morphing(self):
        """Begin morphing into a new letter."""
        # Choose a new random letter that's different from the current one
        letter_options = [l for l in self.hebrew_letters.keys() if l != self.letter]
        self.target_letter = random.choice(letter_options)

        # New target value based on the letter
        self.target_value = self.hebrew_letters[self.target_letter]

        # Reset morph progress
        self.morph_progress = 1.0  # Start fully as current letter

        # Set morph speed (complete in about 1.5-2.5 seconds)
        self.morph_speed = random.uniform(0.008, 0.012)

        # Set new target hue based on the new letter
        self.target_hue = random.uniform(0.1, 0.9)  # Avoid extremes

        # Reset morph timer for next morph
        self.time_until_morph = random.uniform(3.0, 8.0)


class HebrewLetterCanvas(QWidget):
    """A canvas widget for drawing animated Hebrew letters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.letters = []
        self.num_letters = 20  # Increased number of letters

        # Initialize letters
        for _ in range(self.num_letters):
            self.letters.append(HebrewLetter())

        # Set up connections between letters with similar values
        self._setup_connections()

        # Make widget transparent for mouse events and backgrounds
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(40)  # ~25 FPS for smoother animation

        # Debug info
        logger.debug(f"HebrewLetterCanvas initialized with {self.num_letters} letters")

    def _setup_connections(self):
        """Set up connections between letters with the same or related values."""
        # Find letters with the same value
        for i, letter1 in enumerate(self.letters):
            for j, letter2 in enumerate(self.letters[i + 1 :], i + 1):
                # Connect letters with the same value
                if letter1.value == letter2.value:
                    # 80% chance to connect same-value letters
                    if random.random() < 0.8:
                        letter1.connect_to = letter2
                        letter1.connection_target_alpha = 0.6  # Increased from 0.4
                        break
                # Connect letters with numerically related values (multiples or factors)
                elif (letter1.value != 0 and letter2.value % letter1.value == 0) or (
                    letter2.value != 0 and letter1.value % letter2.value == 0
                ):
                    # 40% chance to connect related-value letters
                    if random.random() < 0.4:
                        letter1.connect_to = letter2
                        letter1.connection_target_alpha = 0.4  # Increased from 0.2
                        break

    def update_animation(self):
        """Update all letter animations."""
        # Get elapsed time since last update
        current_time = QTime.currentTime().msecsSinceStartOfDay() * 0.001  # To seconds
        if not hasattr(self, "last_update_time"):
            self.last_update_time = current_time

        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        for letter in self.letters:
            # Update letter position
            letter.x += letter.dx
            letter.y += letter.dy

            # Bounce off edges
            if letter.x < 5 or letter.x > 95:
                letter.dx = -letter.dx
            if letter.y < 5 or letter.y > 95:
                letter.dy = -letter.dy

            # Update rotation
            letter.rotation += letter.rotation_speed
            if letter.rotation > 360:
                letter.rotation -= 360

            # Update color transition
            letter.color_progress += letter.color_speed
            if letter.color_progress >= 1.0:
                letter.hue = letter.target_hue
                # Generate a new target hue within safe range
                letter.target_hue = random.uniform(0.1, 0.9)
                letter.color_progress = 0.0

            # Update connection alpha (fade in/out)
            if letter.connect_to is not None:
                if letter.connection_alpha < letter.connection_target_alpha:
                    letter.connection_alpha = min(
                        letter.connection_target_alpha,
                        letter.connection_alpha + letter.connection_speed,
                    )
                elif letter.connection_alpha > letter.connection_target_alpha:
                    letter.connection_alpha = max(
                        letter.connection_target_alpha,
                        letter.connection_alpha - letter.connection_speed,
                    )

            # Update morphing effect
            if letter.morph_speed > 0:
                # Continue morphing
                letter.morph_progress -= letter.morph_speed
                if letter.morph_progress <= 0:
                    # Morphing complete, switch to target letter
                    letter.letter = letter.target_letter
                    letter.value = letter.target_value
                    letter.morph_progress = 1.0
                    letter.morph_speed = 0
            else:
                # Count down to next morph
                letter.time_until_morph -= dt
                if letter.time_until_morph <= 0:
                    letter.start_morphing()

        # Trigger repaint
        self.update()

    def paintEvent(self, event):
        """Paint the Hebrew letters."""
        # Create painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Draw cosmic background
        self._draw_cosmic_background(painter)

        # First draw connections between letters
        self._draw_connections(painter)

        # Then draw the letters
        self._draw_letters(painter)

    def _draw_cosmic_background(self, painter):
        """Draw the cosmic background with stars and nebula effects."""
        # Create a completely transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        # Draw a few subtle stars (tiny dots)
        painter.setPen(QColor(255, 255, 255, 20))
        for _ in range(50):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.uniform(0.5, 1.5)
            painter.drawEllipse(QRectF(x - size / 2, y - size / 2, size, size))

        # Add a very subtle nebula effect in the corners
        painter.setOpacity(0.05)  # Extremely subtle
        for _ in range(3):
            # Position nebulas in corners or edges
            x = random.choice(
                [
                    random.randint(0, self.width() // 4),
                    random.randint(3 * self.width() // 4, self.width()),
                ]
            )
            y = random.choice(
                [
                    random.randint(0, self.height() // 4),
                    random.randint(3 * self.height() // 4, self.height()),
                ]
            )
            radius = random.randint(150, 350)

            # Very gentle blue-purple hues
            nebula_color = QColor()
            nebula_color.setHsvF(
                random.uniform(0.6, 0.8),  # Blue-purple hue
                random.uniform(0.3, 0.5),  # Lower saturation
                random.uniform(0.6, 0.8),  # Medium value
                0.1,  # Very low alpha
            )

            # Draw nebula as a radial gradient
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, nebula_color)
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

        painter.setOpacity(1.0)  # Reset opacity

    def _draw_connections(self, painter):
        """Draw connections between related letters."""
        for letter in self.letters:
            if letter.connect_to is not None and letter.connection_alpha > 0.01:
                # Calculate positions
                x1 = self.width() * letter.x / 100.0
                y1 = self.height() * letter.y / 100.0
                x2 = self.width() * letter.connect_to.x / 100.0
                y2 = self.height() * letter.connect_to.y / 100.0

                # Create a pen for the connection
                pen = QPen()

                # More visible connection colors
                if letter.value == letter.connect_to.value:
                    # Golden connections for identical values
                    connection_color = QColor(
                        255, 225, 155, int(letter.connection_alpha * 120)
                    )
                else:
                    # Blue-white for related
                    connection_color = QColor(
                        170, 210, 255, int(letter.connection_alpha * 100)
                    )

                pen.setColor(connection_color)
                pen.setWidth(1)  # Thinner lines
                painter.setPen(pen)

                # Draw the connection line
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

                # Add a small glow effect for important connections
                if letter.value == letter.connect_to.value:
                    # Only add glow to identical value connections
                    glow_pen = QPen(
                        QColor(255, 225, 155, int(letter.connection_alpha * 60))
                    )
                    glow_pen.setWidth(2)
                    painter.setPen(glow_pen)
                    # Draw a slightly offset line for a subtle glow effect
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def _draw_letters(self, painter):
        """Draw all Hebrew letters."""
        for letter in self.letters:
            # Calculate actual position
            x = self.width() * letter.x / 100.0
            y = self.height() * letter.y / 100.0

            # Calculate pulsating size
            current_time = (
                QTime.currentTime().msecsSinceStartOfDay() * 0.001
            )  # Convert to seconds
            pulse = math.sin(letter.pulse_offset + current_time * letter.pulse_speed)
            size_factor = 1.0 + pulse * letter.pulse_amount
            size = letter.size * size_factor

            # Interpolate between current and target hue
            current_hue = letter.hue
            target_hue = letter.target_hue
            # Ensure we take the shortest path around the color wheel
            if abs(target_hue - current_hue) > 0.5:
                if target_hue > current_hue:
                    current_hue += 1.0
                else:
                    target_hue += 1.0

            interpolated_hue = current_hue + letter.color_progress * (
                target_hue - current_hue
            )
            interpolated_hue %= 1.0  # Keep in 0-1 range

            # For morphing effect - calculate alpha based on morph progress
            morph_alpha_factor = min(1.0, 0.5 + abs(letter.morph_progress - 0.5))

            # Set color with slightly less translucency than before
            letter_color = QColor()
            letter_color.setHsvF(
                interpolated_hue,
                min(0.9, max(0.1, letter.saturation * 0.9)),  # Ensure in 0-1 range
                min(0.9, max(0.1, letter.value_prop)),  # Ensure in 0-1 range
                min(
                    0.9, max(0.1, letter.alpha * 0.9 * morph_alpha_factor)
                ),  # Ensure in 0-1 range
            )

            # Set up the painter for this letter
            painter.save()
            painter.translate(x, y)
            painter.rotate(letter.rotation)

            # Skip the outer glow effects for most letters (only for high-value letters)
            if letter.value > 100:
                # Subtle glow for important letters
                glow_color = QColor(letter_color)
                glow_color.setAlpha(
                    int(min(255, max(0, letter.alpha * 40 * morph_alpha_factor)))
                )
                painter.setBrush(Qt.BrushStyle.NoBrush)

                # Just one subtle glow layer
                glow_pen = QPen(glow_color, 1)
                painter.setPen(glow_pen)
                glow_size = size * 1.2
                painter.drawEllipse(
                    QRectF(-glow_size / 2, -glow_size / 2, glow_size, glow_size)
                )

            # Draw letter itself with proper styling - more elegant font
            letter_font = QFont(
                "Arial", int(size * 0.9)
            )  # Slightly larger size for better visibility
            letter_font.setBold(True)
            painter.setFont(letter_font)

            # Draw the current letter based on morph progress
            if letter.morph_progress < 1.0:
                # If morphing, draw both letters with appropriate opacity
                # Current letter fades out
                current_letter_color = QColor(letter_color)
                current_letter_color.setAlphaF(
                    min(
                        1.0,
                        max(0.0, current_letter_color.alphaF() * letter.morph_progress),
                    )
                )
                painter.setPen(current_letter_color)
                painter.drawText(
                    QRectF(-size / 2, -size / 2, size, size),
                    Qt.AlignmentFlag.AlignCenter,
                    letter.letter,
                )

                # Target letter fades in
                target_letter_color = QColor(letter_color)
                target_letter_color.setAlphaF(
                    min(
                        1.0,
                        max(
                            0.0,
                            target_letter_color.alphaF()
                            * (1.0 - letter.morph_progress),
                        ),
                    )
                )
                painter.setPen(target_letter_color)
                painter.drawText(
                    QRectF(-size / 2, -size / 2, size, size),
                    Qt.AlignmentFlag.AlignCenter,
                    letter.target_letter,
                )
            else:
                # Not morphing, just draw the current letter
                painter.setPen(letter_color)
                painter.drawText(
                    QRectF(-size / 2, -size / 2, size, size),
                    Qt.AlignmentFlag.AlignCenter,
                    letter.letter,
                )

            painter.restore()


class GematriaTab(QWidget):
    """Main tab for the Gematria pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Gematria tab.

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

        # Initialize letter canvas
        self.letter_canvas = HebrewLetterCanvas(self)

        self._init_ui()
        logger.debug("GematriaTab initialized")

    def resizeEvent(self, event) -> None:
        """Called when the tab is resized."""
        super().resizeEvent(event)

        # Resize the letter canvas to match the tab size
        if hasattr(self, "letter_canvas") and hasattr(self, "stacked_widget"):
            self.letter_canvas.resize(self.stacked_widget.size())
            self.letter_canvas.raise_()  # Keep it on top

    def showEvent(self, event) -> None:
        """Called when the tab is shown."""
        super().showEvent(event)

        # Ensure canvas is visible when tab is shown
        if hasattr(self, "letter_canvas"):
            self.letter_canvas.setVisible(True)
            self.letter_canvas.raise_()

    def _ensure_canvas_on_top(self) -> None:
        """Make sure the letter canvas is visible and on top."""
        self.letter_canvas.setVisible(True)
        self.letter_canvas.raise_()
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
        content_container.setObjectName("gematria_content")
        content_container.setStyleSheet(
            """
            QWidget#gematria_content {
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

        # Word Abacus button
        word_abacus_btn = QPushButton("Word Abacus")
        word_abacus_btn.setToolTip("Open Gematria Word Abacus")
        word_abacus_btn.clicked.connect(lambda: self._open_word_abacus_window())
        button_layout.addWidget(word_abacus_btn)

        # Word List Abacus button
        word_list_abacus_btn = QPushButton("Word List Abacus")
        word_list_abacus_btn.setToolTip("Calculate gematria for multiple words at once")
        word_list_abacus_btn.clicked.connect(
            lambda: self._open_word_list_abacus_window()
        )
        button_layout.addWidget(word_list_abacus_btn)

        # Word Group Chain button
        word_group_chain_btn = QPushButton("Word Groups & Chains")
        word_group_chain_btn.setToolTip(
            "Organize words into groups and create calculation chains"
        )
        word_group_chain_btn.clicked.connect(
            lambda: self._open_word_group_chain_window()
        )
        button_layout.addWidget(word_group_chain_btn)

        # Calculation History button
        history_btn = QPushButton("Calculation History")
        history_btn.setToolTip("Open Calculation History")
        history_btn.clicked.connect(lambda: self._open_calculation_history())
        button_layout.addWidget(history_btn)

        # Tag Management button
        tags_btn = QPushButton("Manage Tags")
        tags_btn.setToolTip("Open Tag Management")
        tags_btn.clicked.connect(lambda: self._open_tag_management())
        button_layout.addWidget(tags_btn)

        # Search button (replaces Dictionary button)
        search_btn = QPushButton("Search")
        search_btn.setToolTip("Search Gematria Calculations")
        search_btn.clicked.connect(lambda: self._open_search_panel())
        button_layout.addWidget(search_btn)

        # Number Dictionary button
        number_dict_btn = QPushButton("Number Dictionary")
        number_dict_btn.setToolTip("Open Number Dictionary for exploring numbers and taking notes")
        number_dict_btn.clicked.connect(lambda: self._open_number_dictionary())
        button_layout.addWidget(number_dict_btn)

        # Search Notes button
        search_notes_btn = QPushButton("Search Notes")
        search_notes_btn.setToolTip("Search through Number Dictionary notes")
        search_notes_btn.clicked.connect(lambda: self._open_number_dictionary_search())
        button_layout.addWidget(search_notes_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show Gematria calculation methods help")
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
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        # Add button bar to content layout
        content_layout.addWidget(button_bar)

        # Create card for welcome content
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet(
            """
            #welcomeCard {
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 8px;
                border: 1px solid #e0e0e0;
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
        title = QLabel("Gematria")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #673AB7;")

        welcome = QLabel(
            "Welcome to the Gematria pillar. Here you can perform numerical analysis "
            "of texts using various ancient and modern calculation methods."
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("font-size: 14px; color: #555;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description with more details
        description = QLabel(
            "Gematria is a traditional system for assigning numerical values to words "
            "and phrases. Use the tools above to calculate values, search the database, "
            "or manage your tagged calculations."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #777; margin-top: 10px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add content to welcome card
        welcome_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome)
        welcome_layout.addWidget(description)

        # Add welcome card to content layout
        content_layout.addWidget(welcome_card, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add Thoth image below welcome card
        thoth_container = QFrame()
        thoth_container.setObjectName("thothImageContainer")
        thoth_container.setStyleSheet(
            """
            #thothImageContainer {
                background-color: transparent;
                margin: 10px 40px 20px 40px;
            }
        """
        )
        thoth_layout = QVBoxLayout(thoth_container)

        # Create image label
        thoth_image_label = QLabel()
        thoth_pixmap = QPixmap("assets/tab_images/thoth.png")

        if not thoth_pixmap.isNull():
            # Scale the image to a reasonable size while maintaining aspect ratio
            scaled_pixmap = thoth_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            thoth_image_label.setPixmap(scaled_pixmap)
            thoth_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add caption
            caption = QLabel("Thoth - Egyptian deity of wisdom, writing, and magic")
            caption.setStyleSheet(
                "font-size: 12px; color: #673AB7; font-style: italic;"
            )
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

            thoth_layout.addWidget(
                thoth_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            thoth_layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add the image container to the content layout
            content_layout.addWidget(
                thoth_container, alignment=Qt.AlignmentFlag.AlignCenter
            )
        else:
            logger.error("Failed to load Thoth image from assets/tab_images/thoth.png")

        content_layout.addStretch()

        # Add content container to stack layout
        stack_layout.addWidget(content_container)

        # Set up the letter canvas
        self.letter_canvas.setParent(self.stacked_widget)
        self.letter_canvas.resize(self.stacked_widget.size())

        # Place canvas behind the content
        self.letter_canvas.stackUnder(content_container)

        # Make sure canvas doesn't intercept mouse events
        self.letter_canvas.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Ensure the canvas is on top after a short delay
        QTimer.singleShot(200, self._ensure_canvas_on_top)

    def _open_word_abacus_window(self) -> None:
        """Open the Word Abacus window."""
        from gematria.ui.windows.word_abacus_window import WordAbacusWindow

        self._open_gematria_window(
            "word_abacus",
            WordAbacusWindow,
            "Gematria Word Abacus",
            window_manager=self.window_manager,  # Pass window_manager
            allow_multiple=True,
        )

    def _open_word_list_abacus_window(self) -> None:
        """Open the word list abacus window."""
        from gematria.ui.windows.word_list_abacus_window import WordListAbacusWindow

        # Create a new window instance with the window manager
        window = WordListAbacusWindow(window_manager=self.window_manager)

        # Open the window through the window manager with a unique ID
        window_id = "word_list_abacus_window"
        self.window_manager.open_window(window_id, window)

        # Show the window and bring it to front
        window.show()
        window.raise_()
        logger.debug("Opened Word List Abacus window")

    def _open_word_group_chain_window(self) -> None:
        """Open the word group chain window."""
        from gematria.ui.windows.word_group_chain_window import WordGroupChainWindow

        # Create a new window instance
        window = WordGroupChainWindow()

        # Open the window through the window manager with a unique ID
        window_id = "word_group_chain_window"
        self.window_manager.open_window(window_id, window)

        # Show the window and bring it to front
        window.show()
        window.raise_()
        logger.debug("Opened Word Group Chain window")

    def _open_gematria_window(
        self, window_id: str, window_class, title: str, *args, **kwargs
    ) -> None:
        """Open a Gematria window.

        Args:
            window_id: Unique identifier for the window
            window_class: Window class to instantiate
            title: Window title
            *args: Arguments to pass to the window class
            **kwargs: Keyword arguments to pass to the window class
        """
        # Generate a unique window ID if multiple instances are allowed
        allow_multiple = kwargs.pop("allow_multiple", False)
        if allow_multiple:
            import uuid

            final_window_id = f"{window_id}_{uuid.uuid4().hex[:8]}"
        else:
            final_window_id = window_id

        # Create window instance, passing through relevant kwargs
        # Ensure window_manager is passed if it's in kwargs
        window_args = {}
        if "window_manager" in kwargs:
            window_args["window_manager"] = kwargs.pop("window_manager")

        # Pass any other specific args needed by the window constructor
        # For now, we assume other args are passed via *args
        # and remaining kwargs are for other purposes or not for the constructor.

        window = window_class(*args, **window_args, **kwargs)

        # Apply standard flags for proper window behavior
        window.setWindowFlags(
            window.windowFlags()
            | Qt.WindowType.Window
            | Qt.WindowType.WindowStaysOnTopHint
        )

        # Open the window through the window manager - only pass window_id and content
        self.window_manager.open_window(final_window_id, window)

        # Set the window title
        window.setWindowTitle(title)

        # Ensure proper focus and z-order
        window.raise_()
        window.activateWindow()

        return window

    def _open_calculation_history(self) -> None:
        """Open the Calculation History panel."""
        from gematria.ui.windows.calculation_history_window import (
            CalculationHistoryWindow,
        )

        self._open_gematria_window(
            "calculation_history", CalculationHistoryWindow, "Calculation History"
        )

    def _open_tag_management(self) -> None:
        """Open the Tag Management panel."""
        from gematria.ui.windows.tag_management_window import TagManagementWindow

        self._open_gematria_window(
            "tag_management", TagManagementWindow, "Tag Management"
        )

    def _open_search_panel(self) -> None:
        """Open the Search panel."""
        from loguru import logger

        logger.debug("Opening search panel")

        try:
            from gematria.ui.windows.search_window import SearchWindow

            # Open the window with the search panel
            self._open_gematria_window(
                "search",
                SearchWindow,
                "Gematria Search",
                self.window_manager,
                allow_multiple=True,
            )
        except Exception as e:
            logger.error(f"Error opening search panel: {e}")
            import traceback

            logger.error(traceback.format_exc())

    def _show_help(self) -> None:
        """Show the Gematria help dialog."""
        from gematria.ui.windows.help_window import HelpWindow

        self._open_gematria_window("help", HelpWindow, "Gematria Help")

    def open_search_panel_with_value(self, value: int) -> None:
        """Open the search panel, set the exact value, and perform the search."""
        from gematria.ui.windows.search_window import SearchWindow

        # Open the search window using the standard method
        window = self._open_gematria_window(
            "search",
            SearchWindow,
            "Gematria Search",
            self.window_manager,
            allow_multiple=True,
        )
        # Set the value and perform the search if possible
        if hasattr(window, "set_exact_value"):
            window.set_exact_value(value)
        window.raise_()
        window.activateWindow()

    def _open_number_dictionary(self) -> None:
        """Open the Number Dictionary window."""
        from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow

        # Create a new window instance
        window = NumberDictionaryWindow()

        # Use open_multi_window to allow multiple instances
        self.window_manager.open_multi_window(
            "number_dictionary", 
            window, 
            "Number Dictionary",
            size=(1000, 700)
        )
            
        logger.debug("Opened Number Dictionary window")

    def open_number_dictionary_with_number(self, number: int) -> None:
        """Open the Number Dictionary window with a specific number.
        
        This method can be called from other parts of the application
        to open the Number Dictionary and navigate to a specific number.
        
        Args:
            number: The number to display in the Number Dictionary
        """
        from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow

        # Create a new window instance with the specific number
        window = NumberDictionaryWindow(initial_number=number)

        # Use open_multi_window to allow multiple instances
        self.window_manager.open_multi_window(
            "number_dictionary", 
            window, 
            f"Number Dictionary - {number}",
            size=(1000, 700)
        )
            
        logger.debug(f"Opened Number Dictionary window with number {number}")

    def _open_number_dictionary_search(self) -> None:
        """Open the Number Dictionary search window."""
        from gematria.ui.windows.number_dictionary_search_window import NumberDictionarySearchWindow

        # Create a new window instance
        window = NumberDictionarySearchWindow()

        # Connect the signal to open numbers in the dictionary
        window.open_number_requested.connect(self.open_number_dictionary_with_number)

        # Open the window through the window manager with a unique ID
        window_id = "number_dictionary_search_window"
        self.window_manager.open_window(window_id, window)

        # Show the window and bring it to front
        window.show()
        window.raise_()
        logger.debug("Opened Number Dictionary search window")
