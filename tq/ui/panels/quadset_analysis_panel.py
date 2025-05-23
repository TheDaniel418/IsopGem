"""
Purpose: Provides a panel for analyzing relationships between numbers in a quadset

This file is part of the tq pillar and serves as a UI component.
It is responsible for displaying mathematical relationships between the four numbers
in a TQ Grid quadset, including absolute differences and sums of pairs.

Key components:
- QuadsetAnalysisPanel: Panel for displaying quadset analysis

Dependencies:
- PyQt6: For the user interface components
- tq.services.tq_grid_service: For accessing the current quadset values

Related files:
- tq/ui/panels/tq_grid_panel.py: Main panel that hosts this analysis panel
- tq/services/tq_grid_service.py: Service that provides the quadset data
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QApplication,
)

from tq.services.tq_grid_service import TQGridService
from tq.ui.styles.tq_colors import TQColors, apply_tq_styles


class QuadsetAnalysisPanel(QFrame):
    """Panel for displaying mathematical relationships between quadset numbers."""

    def __init__(self, parent=None):
        """Initialize the quadset analysis panel.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Apply TQ styling
        apply_tq_styles(self)

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Create title
        title_label = QLabel("Quadset Analysis")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setProperty("isTitle", "true")
        self.layout.addWidget(title_label)

        # Create scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(15)

        # Create sections for different analyses
        self.create_word_equivalents_section()
        self.create_differences_section()
        self.create_sums_section()

        # Set the content widget to the scroll area
        scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(scroll_area, 1)  # Give it stretch factor of 1

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(300)  # Set minimum width to match the 2:3:2 ratio

        # Get the grid service and register for updates
        self.grid_service = TQGridService.get_instance()
        self.grid_service.register_callback(self.update_analysis)

        # Initialize with current grid values
        self.update_analysis()

    def create_differences_section(self):
        """Create the section for displaying absolute differences."""
        # Create a frame for the differences section
        diff_frame = QFrame()
        diff_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        diff_frame.setStyleSheet(
            f"background-color: {TQColors.DIFFERENCE_BG}; border-radius: 6px; padding: 5px;"
        )
        diff_layout = QVBoxLayout(diff_frame)

        # Section header
        diff_header = QLabel("Absolute Differences")
        diff_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        diff_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diff_header.setProperty("isSubtitle", "true")
        diff_header.setStyleSheet(
            f"color: {TQColors.PRIMARY_DARK}; background-color: transparent;"
        )
        diff_layout.addWidget(diff_header)

        # Create grid for differences
        diff_grid = QGridLayout()
        diff_grid.setContentsMargins(15, 15, 15, 15)
        diff_grid.setSpacing(12)

        # Headers for the grid with colors
        headers = ["", "Base", "Conrune", "Reversal", "Rev. Conrune"]
        header_colors = [
            "",  # Empty cell
            TQColors.BASE_NUMBER,
            TQColors.CONRUNE,
            TQColors.REVERSAL,
            TQColors.REVERSAL_CONRUNE,
        ]

        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setProperty("isHeader", "true")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(100)  # Set minimum width for better spacing
            if i > 0:  # Skip the empty cell
                label.setStyleSheet(
                    f"background-color: {header_colors[i]}; color: white; border-radius: 4px;"
                )
            diff_grid.addWidget(label, 0, i)

        # Row headers with colors
        for i, header in enumerate(headers[1:], 1):
            label = QLabel(header)
            label.setProperty("isHeader", "true")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(100)  # Set minimum width for better spacing
            label.setStyleSheet(
                f"background-color: {header_colors[i]}; color: white; border-radius: 4px;"
            )
            diff_grid.addWidget(label, i, 0)

        # Create value labels for the differences
        self.diff_labels = {}
        for row in range(1, 5):
            for col in range(1, 5):
                if row == col:
                    # Diagonal (same number) - display 0
                    label = QLabel("0")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setProperty("isValue", "true")
                    label.setStyleSheet("background-color: #E0E0E0; font-weight: bold;")
                    label.setMinimumWidth(100)  # Set minimum width for better spacing
                    diff_grid.addWidget(label, row, col)
                else:
                    # Create a label for the difference
                    label = QLabel("--")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setProperty("isValue", "true")
                    label.setMinimumWidth(100)  # Set minimum width for better spacing
                    diff_grid.addWidget(label, row, col)
                    # Store the label for later updates
                    self.diff_labels[(row, col)] = label

        # Add the grid to the frame layout
        diff_layout.addLayout(diff_grid)

        # Add the frame to the content layout
        self.content_layout.addWidget(diff_frame)

    def create_sums_section(self):
        """Create the section for displaying sums of pairs."""
        # Create a frame for the sums section
        sums_frame = QFrame()
        sums_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        sums_frame.setStyleSheet(
            f"background-color: {TQColors.SUM_BG}; border-radius: 6px; padding: 5px;"
        )
        sums_layout = QVBoxLayout(sums_frame)

        # Section header
        sums_header = QLabel("Sums of Pairs")
        sums_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        sums_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sums_header.setProperty("isSubtitle", "true")
        sums_header.setStyleSheet(
            f"color: {TQColors.PRIMARY_DARK}; background-color: transparent;"
        )
        sums_layout.addWidget(sums_header)

        # Create grid for sums
        sums_grid = QGridLayout()
        sums_grid.setContentsMargins(15, 15, 15, 15)
        sums_grid.setSpacing(12)

        # Headers for the grid with colors
        headers = ["", "Base", "Conrune", "Reversal", "Rev. Conrune"]
        header_colors = [
            "",  # Empty cell
            TQColors.BASE_NUMBER,
            TQColors.CONRUNE,
            TQColors.REVERSAL,
            TQColors.REVERSAL_CONRUNE,
        ]

        for i, header in enumerate(headers):
            label = QLabel(header)
            label.setProperty("isHeader", "true")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(100)  # Set minimum width for better spacing
            if i > 0:  # Skip the empty cell
                label.setStyleSheet(
                    f"background-color: {header_colors[i]}; color: white; border-radius: 4px;"
                )
            sums_grid.addWidget(label, 0, i)

        # Row headers with colors
        for i, header in enumerate(headers[1:], 1):
            label = QLabel(header)
            label.setProperty("isHeader", "true")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumWidth(100)  # Set minimum width for better spacing
            label.setStyleSheet(
                f"background-color: {header_colors[i]}; color: white; border-radius: 4px;"
            )
            sums_grid.addWidget(label, i, 0)

        # Create value labels for the sums
        self.sum_labels = {}
        for row in range(1, 5):
            for col in range(1, 5):
                if row == col:
                    # Diagonal (same number) - display the number doubled
                    label = QLabel("--")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setProperty("isValue", "true")
                    label.setStyleSheet("background-color: #E0E0E0; font-weight: bold;")
                    label.setMinimumWidth(100)  # Set minimum width for better spacing
                    sums_grid.addWidget(label, row, col)
                    # Store the label for later updates
                    self.sum_labels[(row, col)] = label
                elif row < col:
                    # Only show upper triangle to avoid duplication
                    label = QLabel("--")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setProperty("isValue", "true")
                    label.setMinimumWidth(100)  # Set minimum width for better spacing
                    sums_grid.addWidget(label, row, col)
                    # Store the label for later updates
                    self.sum_labels[(row, col)] = label
                else:
                    # Lower triangle - display "Same as above"
                    label = QLabel("↑")
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setProperty("isValue", "true")
                    label.setStyleSheet(
                        "background-color: #F0F0F0; font-style: italic; color: #757575;"
                    )
                    label.setMinimumWidth(100)  # Set minimum width for better spacing
                    sums_grid.addWidget(label, row, col)

        # Add the grid to the frame layout
        sums_layout.addLayout(sums_grid)

        # Add the frame to the content layout
        self.content_layout.addWidget(sums_frame)

    def create_word_equivalents_section(self):
        """Create the section for displaying word equivalents."""
        # Create a frame for the word equivalents section
        word_frame = QFrame()
        word_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        word_frame.setStyleSheet(
            f"background-color: {TQColors.WORD_EQUIV_BG}; border-radius: 6px; padding: 5px;"
        )
        word_layout = QVBoxLayout(word_frame)

        # Section header
        word_header = QLabel("Word Equivalents")
        word_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        word_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        word_header.setProperty("isSubtitle", "true")
        word_header.setStyleSheet(
            f"color: {TQColors.PRIMARY_DARK}; background-color: transparent;"
        )
        word_layout.addWidget(word_header)

        # Create grid for word equivalents
        word_grid = QGridLayout()
        word_grid.setContentsMargins(15, 15, 15, 15)
        word_grid.setSpacing(12)

        # Headers for the grid with colors
        headers = ["Base", "Conrune", "Reversal", "Rev. Conrune"]
        header_colors = [
            TQColors.BASE_NUMBER,
            TQColors.CONRUNE,
            TQColors.REVERSAL,
            TQColors.REVERSAL_CONRUNE,
        ]

        # Create value labels and buttons for each number
        self.value_labels = {}
        self.word_buttons = {}

        for i, header in enumerate(headers):
            # Create container for each number
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(5, 5, 5, 5)
            container_layout.setSpacing(5)

            # Header label
            header_label = QLabel(header)
            header_label.setProperty("isHeader", "true")
            header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_label.setStyleSheet(
                f"background-color: {header_colors[i]}; color: white; border-radius: 4px; padding: 4px;"
            )
            container_layout.addWidget(header_label)

            # Value label
            value_label = QLabel("--")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setProperty("isValue", "true")
            value_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            container_layout.addWidget(value_label)
            self.value_labels[i] = value_label

            # Find Words button
            find_button = QPushButton("Find Words with this Value")
            find_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2472a4;
                }
                """
            )
            find_button.clicked.connect(lambda _, idx=i: self._find_words_with_value(idx))
            container_layout.addWidget(find_button)
            self.word_buttons[i] = find_button

            # Add to grid
            word_grid.addWidget(container, 0, i)

        # Add the grid to the frame layout
        word_layout.addLayout(word_grid)

        # Add the frame to the content layout
        self.content_layout.addWidget(word_frame)

    # Class variable to keep references to search windows
    _search_windows = []
    
    def _find_words_with_value(self, index):
        """
        Send the selected value to the Gematria Search panel and perform the search.

        This method enables cross-pillar communication by sending a quadset value
        (Base, Conrune, Reversal, or Rev. Conrune) directly to the Gematria Search panel.
        It always locates the main application window by iterating over QApplication.topLevelWidgets(),
        ensuring robust operation regardless of whether this panel is hosted in the main window,
        an auxiliary window, or a dialog. This guarantees that the real, fully-featured search panel
        is used for all 'send to search' actions, matching the cross-pillar communication pattern
        used elsewhere in the application.

        Args:
            index (int): Index of the value to search for (0=base, 1=conrune, 2=reversal, 3=rev. conrune)
        """
        from PyQt6.QtWidgets import QApplication
        grid = self.grid_service.get_current_grid()
        values = [grid.base_number, grid.conrune, grid.reversal, grid.reversal_conrune]
        value = values[index]

        # Always get the real main window with gematria_tab
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, "gematria_tab"):
                widget.gematria_tab.open_search_panel_with_value(value)
                return

        from loguru import logger
        logger.error("No main window with gematria_tab found. Cannot send value to search panel.")

    def closeEvent(self, event):
        """Handle the panel being closed.

        Args:
            event: The close event
        """
        # Unregister the callback when the panel is closed
        self.grid_service.unregister_callback(self.update_analysis)

        super().closeEvent(event)

    def update_analysis(self):
        """Update the analysis with current quadset values."""
        # Get the current grid values
        grid = self.grid_service.get_current_grid()

        # Extract the values
        values = [grid.base_number, grid.conrune, grid.reversal, grid.reversal_conrune]

        # Update the word equivalents section
        for i, value in enumerate(values):
            self.value_labels[i].setText(str(value))

        # Update the differences
        for row in range(1, 5):
            for col in range(1, 5):
                if row != col:
                    # Calculate absolute difference
                    diff = abs(values[row - 1] - values[col - 1])

                    # Update the label
                    label = self.diff_labels[(row, col)]
                    label.setText(str(diff))

                    # Add visual cue based on the magnitude of the difference
                    # Larger differences get darker background
                    intensity = min(255, max(220, 255 - int(diff * 0.1)))
                    bg_color = f"rgb({intensity}, {intensity}, 255)"
                    label.setStyleSheet(
                        f"background-color: {bg_color}; font-weight: bold;"
                    )

        # Update the sums
        for row in range(1, 5):
            for col in range(1, 5):
                if row <= col:
                    # Calculate sum
                    sum_value = values[row - 1] + values[col - 1]

                    # Update the label
                    label = self.sum_labels[(row, col)]
                    label.setText(str(sum_value))

                    # Add visual cue based on the magnitude of the sum
                    # Larger sums get darker background
                    intensity = min(255, max(220, 255 - int(sum_value * 0.05)))
                    bg_color = f"rgb(255, {intensity}, {intensity})"
                    label.setStyleSheet(
                        f"background-color: {bg_color}; font-weight: bold;"
                    )
