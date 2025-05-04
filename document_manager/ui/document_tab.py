"""Document Manager tab implementation.

This module provides the main tab for the Document Manager pillar.
"""

import random

from loguru import logger
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import TabManager, WindowManager


class DocumentTab(QWidget):
    """Main tab for the Document Manager pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Document Manager tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager

        # Background properties
        self.parchment_noise = []
        self.generate_parchment_texture()

        # Initialize UI
        self._init_ui()
        logger.debug("DocumentTab initialized")

    def generate_parchment_texture(self):
        """Generate parchment texture pattern."""
        # Generate random noise for parchment texture
        for _ in range(400):  # Doubled for stronger pattern
            x = random.randint(0, 100)  # As percentage of width
            y = random.randint(0, 100)  # As percentage of height
            size = random.uniform(0.5, 4)  # Increased size
            opacity = random.uniform(0.05, 0.15)  # Stronger noise

            # More varied shades of brown
            hue = random.randint(20, 45)  # Wider range of brown-yellow
            saturation = random.randint(30, 70)  # More saturation
            lightness = random.randint(25, 65)  # More contrast

            self.parchment_noise.append(
                {
                    "x": x,
                    "y": y,
                    "size": size,
                    "opacity": opacity,
                    "hue": hue,
                    "saturation": saturation,
                    "lightness": lightness,
                }
            )

        # Add some fibrous horizontal lines for papyrus effect
        for _ in range(30):
            y = random.randint(0, 100)
            length = random.uniform(10, 40)  # Length of fiber
            thickness = random.uniform(0.5, 2)
            fiber_opacity = random.uniform(0.1, 0.2)

            self.parchment_noise.append(
                {
                    "x": random.randint(0, 100 - int(length)),
                    "y": y,
                    "size": thickness,
                    "length": length,
                    "opacity": fiber_opacity,
                    "hue": random.randint(25, 35),
                    "saturation": random.randint(40, 60),
                    "lightness": random.randint(30, 50),
                    "is_fiber": True,
                }
            )

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Content container with background styling
        content_container = QWidget()
        content_container.setObjectName("document_content")
        content_container.setStyleSheet(
            """
            QWidget#document_content {
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

        # Document Browser button
        doc_browser_btn = QPushButton("Document Browser")
        doc_browser_btn.setToolTip("Open Document Browser")
        doc_browser_btn.clicked.connect(self._open_document_browser)
        button_layout.addWidget(doc_browser_btn)

        # Document Analysis button
        analysis_btn = QPushButton("Document Analysis")
        analysis_btn.setToolTip("Analyze documents from a gematric perspective")
        analysis_btn.clicked.connect(self._open_document_analysis)
        button_layout.addWidget(analysis_btn)

        # RTF Editor button
        rtf_btn = QPushButton("RTF Editor")
        rtf_btn.setToolTip("Open Rich Text Editor")
        rtf_btn.clicked.connect(self._open_rtf_editor)
        button_layout.addWidget(rtf_btn)

        # Document Database Manager button
        db_manager_btn = QPushButton("Database Manager")
        db_manager_btn.setToolTip("Manage documents in the database")
        db_manager_btn.clicked.connect(self._open_document_database_manager)
        button_layout.addWidget(db_manager_btn)

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show Document Manager help")
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

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Add button bar to content layout
        content_layout.addWidget(button_bar)

        # Create card for welcome content
        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")
        welcome_card.setStyleSheet(
            """
            #welcomeCard {
                background-color: rgba(255, 255, 235, 0.85);
                border-radius: 8px;
                border: 1px solid #e0d0b0;
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
        title = QLabel("Document Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #795548;")

        welcome = QLabel(
            "Welcome to the Document Manager pillar. Here you can organize, analyze, "
            "and edit documents using various tools and techniques."
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet("font-size: 14px; color: #555;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description with more details
        description = QLabel(
            "The Document Manager provides tools for organizing your research materials, "
            "performing textual analysis on documents, and creating rich-text documents "
            "with embedded references to your gematric findings."
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

        # Add Seshat image below welcome card
        seshat_container = QFrame()
        seshat_container.setObjectName("seshatImageContainer")
        seshat_container.setStyleSheet(
            """
            #seshatImageContainer {
                background-color: rgba(255, 255, 235, 0.7);
                border-radius: 8px;
                margin: 10px 40px 20px 40px;
                padding: 10px;
            }
        """
        )
        seshat_layout = QVBoxLayout(seshat_container)

        # Create image label
        seshat_image_label = QLabel()
        seshat_pixmap = QPixmap("assets/tab_images/sechat.png")

        if not seshat_pixmap.isNull():
            # Scale the image to a reasonable size while maintaining aspect ratio
            scaled_pixmap = seshat_pixmap.scaled(
                400,
                400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            seshat_image_label.setPixmap(scaled_pixmap)
            seshat_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add caption
            caption = QLabel(
                "Seshat - Egyptian goddess of writing, record keeping, and archives"
            )
            caption.setStyleSheet(
                "font-size: 12px; color: #795548; font-style: italic; background-color: rgba(255, 255, 235, 0.8); padding: 4px; border-radius: 4px;"
            )
            caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

            seshat_layout.addWidget(
                seshat_image_label, alignment=Qt.AlignmentFlag.AlignCenter
            )
            seshat_layout.addWidget(caption, alignment=Qt.AlignmentFlag.AlignCenter)

            # Add the image container to the content layout
            content_layout.addWidget(
                seshat_container, alignment=Qt.AlignmentFlag.AlignCenter
            )
        else:
            logger.error(
                "Failed to load Seshat image from assets/tab_images/sechat.png"
            )

        content_layout.addStretch()

        # Add the content container to the main layout
        layout.addWidget(content_container)

    def paintEvent(self, event):
        """Custom paint event to draw the parchment background."""
        # Call the parent class's paintEvent to handle basic widget drawing
        super().paintEvent(event)

        # Create a painter for this widget
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw parchment background
        self._draw_parchment_background(painter)

    def _draw_parchment_background(self, painter):
        """Draw the parchment texture background."""
        # Create a more defined parchment base color with gradient
        gradient = QLinearGradient(QPointF(0, 0), QPointF(self.width(), self.height()))
        gradient.setColorAt(0, QColor(255, 248, 220))  # Light parchment
        gradient.setColorAt(0.3, QColor(250, 240, 210))  # Mid tone
        gradient.setColorAt(0.7, QColor(245, 235, 200))  # Slightly darker
        gradient.setColorAt(1, QColor(240, 230, 190))  # Darker edge

        painter.fillRect(self.rect(), QBrush(gradient))

        # Draw more defined grid lines (like papyrus fibers)
        painter.setPen(QPen(QColor(150, 130, 100, 20), 1, Qt.PenStyle.SolidLine))

        # Horizontal lines (more dense)
        line_spacing = 15  # Decreased spacing
        for y in range(0, self.height(), line_spacing):
            painter.drawLine(0, y, self.width(), y)

        # Add some vertical fibers (less frequent)
        painter.setPen(QPen(QColor(140, 120, 90, 10), 1, Qt.PenStyle.SolidLine))
        line_spacing = 40
        for x in range(0, self.width(), line_spacing):
            # Slightly wavy vertical lines
            path = QPainterPath()
            path.moveTo(x, 0)

            segments = self.height() // 20
            for i in range(1, segments + 1):
                offset = random.uniform(-1.5, 1.5)
                path.lineTo(x + offset, i * 20)

            painter.drawPath(path)

        # Draw noise spots and fibers for texture
        for spot in self.parchment_noise:
            x = int(self.width() * spot["x"] / 100)
            y = int(self.height() * spot["y"] / 100)

            # Create a color with alpha for the noise
            color = QColor()
            color.setHsv(
                spot["hue"],
                spot["saturation"],
                spot["lightness"],
                int(255 * spot["opacity"]),
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))

            if spot.get("is_fiber", False):
                # Draw a horizontal fiber for papyrus texture
                fiber_width = int(self.width() * spot["length"] / 100)
                fiber_height = int(spot["size"])  # Convert to int for drawRect
                painter.drawRect(x, y, fiber_width, fiber_height)
            else:
                # Draw a small ellipse for the noise spot
                painter.drawEllipse(QPointF(x, y), spot["size"], spot["size"])

    def _open_document_browser(self) -> None:
        """Open the Document Browser window."""
        from document_manager.ui.panels.document_manager_panel import (
            DocumentManagerPanel,
        )

        # Create the panel
        panel = DocumentManagerPanel()

        # Create and open the document browser window
        self.window_manager.open_window("document_browser", panel)

        # Set the window title
        panel.setWindowTitle("Document Browser")

        logger.debug("Opened Document Browser window")

    def _open_document_analysis(self) -> None:
        """Open the Document Analysis window."""
        from document_manager.ui.panels.document_analysis_panel import (
            DocumentAnalysisPanel,
        )

        # Create the panel
        panel = DocumentAnalysisPanel()

        # Create and open the document analysis window
        self.window_manager.open_window("document_analysis", panel)

        # Set the window title
        panel.setWindowTitle("Document Analysis")

        logger.debug("Opened Document Analysis window")

    def _open_rtf_editor(self) -> None:
        """Open the RTF Editor window."""
        from loguru import logger

        from shared.ui.widgets.rtf_editor.rtf_editor_window import RTFEditorWindow

        logger.debug("Opening RTF Editor window directly...")

        # Create the RTF editor window
        editor = RTFEditorWindow()

        # Open the window using the window manager
        self.window_manager.open_window("rtf_editor", editor)

        # Set the window title
        editor.setWindowTitle("Rich Text Editor")

        logger.debug("RTF Editor window opened")

    def _open_document_database_manager(self) -> None:
        """Open the Document Database Utility window."""
        from document_manager.ui.panels.document_database_utility_panel import (
            DocumentDatabaseUtilityPanel,
        )

        # Create the panel
        panel = DocumentDatabaseUtilityPanel()

        # Create and open the document database utility window
        self.window_manager.open_window("document_database_utility", panel)

        # Set the window title
        panel.setWindowTitle("Document Database Utility")

        logger.debug("Opened Document Database Utility window")
