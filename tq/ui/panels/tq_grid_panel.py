"""
Purpose: Provides a panel for displaying TQ Grid with base numbers and their transformations

This file is part of the tq pillar and serves as a UI component.
It is responsible for visualizing decimal numbers, their ternary representations,
and transformations including conrune and ternary digit reversal.

Key components:
- TQGridPanel: Main panel for the TQ Grid visualization
- TQNumberDisplay: Widget for displaying a number in different formats

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary
- tq.utils.ternary_transition: For applying transformations like conrune
- tq.ui.widgets.ternary_visualizer: For visualizing ternary digits
- tq.ui.panels.number_properties_panel: For displaying detailed number properties
- shared.services.number_properties_service: For analyzing number properties
- tq.services.tq_grid_service: For managing TQ Grid display numbers

Related files:
- tq/ui/tq_tab.py: Main tab that hosts this panel
- tq/ui/widgets/ternary_visualizer.py: Widget for visualizing ternary numbers
- tq/ui/panels/number_properties_panel.py: Panel for displaying number properties
"""


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from shared.services.number_properties_service import NumberPropertiesService
from tq.services.tq_grid_service import TQGridService
from tq.ui.panels.number_properties_panel import NumberPropertiesPanel
from tq.ui.widgets.ternary_visualizer import TernaryDigitVisualizer
from tq.utils.ternary_converter import (
    decimal_to_ternary,
    format_ternary,
    ternary_to_decimal,
)
from tq.utils.ternary_transition import TernaryTransition


class TQNumberDisplay(QFrame):
    """Widget for displaying a number in decimal, ternary, and visualization formats."""

    def __init__(self, label_text: str, parent=None):
        """Initialize the number display widget.

        Args:
            label_text: The label text for this display
            parent: The parent widget
        """
        super().__init__(parent)

        # Set up the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        # Add label
        self.label = QLabel(label_text)
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        # Info layout for decimal and ternary representation - use horizontal layout to save vertical space
        self.info_layout = QHBoxLayout()

        # Decimal and ternary info in a compact layout
        info_container = QWidget()
        info_grid = QGridLayout(info_container)
        info_grid.setContentsMargins(0, 0, 0, 0)
        info_grid.setSpacing(3)

        # Decimal display
        info_grid.addWidget(QLabel("Decimal:"), 0, 0)
        self.decimal_label = QLabel("0")
        self.decimal_label.setFont(QFont("Courier New", 10))
        info_grid.addWidget(self.decimal_label, 0, 1)

        # Ternary display
        info_grid.addWidget(QLabel("Ternary:"), 1, 0)
        self.ternary_label = QLabel("0")
        self.ternary_label.setFont(QFont("Courier New", 10))
        info_grid.addWidget(self.ternary_label, 1, 1)

        self.info_layout.addWidget(info_container)
        self.layout.addLayout(self.info_layout)

        # Create a scroll area for the visualizer to handle large numbers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Add ternary visualizer
        self.visualizer = TernaryDigitVisualizer()
        self.visualizer.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding
        )

        # Set minimum height for the visualizer based on typical digit count
        self.visualizer.setMinimumHeight(300)

        # Set the visualizer as the widget in the scroll area
        scroll_area.setWidget(self.visualizer)
        self.layout.addWidget(scroll_area, 1)  # Give it a stretch factor of 1 to expand

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            """
        )

    def set_number(self, decimal_value: int, pad_length: int = 6) -> None:
        """Set the number to display.

        Args:
            decimal_value: The decimal value to display
            pad_length: Minimum length to pad the ternary representation
        """
        # Update decimal display
        self.decimal_label.setText(str(decimal_value))

        # Convert to ternary and update display
        ternary_str = decimal_to_ternary(decimal_value)

        # Pad ternary string to at least pad_length
        padded_ternary = format_ternary(ternary_str, pad_length=pad_length)

        # Update ternary display
        self.ternary_label.setText(padded_ternary)

        # Update visualizer
        self.visualizer.set_ternary(padded_ternary)


class TQGridPanel(QFrame):
    """Panel for displaying the TQ Grid with transformations."""

    def __init__(self, parent=None, standalone=False):
        """Initialize the TQ Grid panel.

        Args:
            parent: The parent widget
            standalone: Whether this panel is running standalone (not in main app)
        """
        super().__init__(parent)

        # Store standalone flag
        self.standalone = standalone

        # Initialize the number properties service
        if NumberPropertiesService._instance is None:
            NumberPropertiesService.get_instance()

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Create title
        title_label = QLabel("TQ Grid Viewer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title_label)

        # Create input section
        input_layout = QHBoxLayout()

        # Number input
        input_layout.addWidget(QLabel("Enter decimal number:"))
        self.number_input = QLineEdit()
        self.number_input.setValidator(
            QIntValidator(0, 999999)
        )  # Limit to positive integers
        self.number_input.setText("0")
        self.number_input.setMaximumWidth(150)
        input_layout.addWidget(self.number_input)

        # Process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self._process_number)
        input_layout.addWidget(self.process_button)

        input_layout.addStretch()
        self.layout.addLayout(input_layout)

        # Create main splitter for properties and visualizers
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Number properties panel
        self.properties_panel = NumberPropertiesPanel()
        self.properties_panel.setMinimumWidth(300)

        # Right side - Visualizers
        self.visualizers_container = QWidget()
        self.visualizers_layout = QVBoxLayout(self.visualizers_container)
        self.visualizers_layout.setContentsMargins(0, 0, 0, 0)

        # Create scrollable content area for visualizers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)

        # Create grid layout for the displays
        self.displays_layout = QGridLayout()
        self.displays_layout.setContentsMargins(0, 0, 0, 0)
        self.displays_layout.setHorizontalSpacing(20)
        self.displays_layout.setVerticalSpacing(20)

        # Create the displays
        self.base_display = TQNumberDisplay("Base Number")
        self.displays_layout.addWidget(self.base_display, 0, 0)

        self.conrune_display = TQNumberDisplay("Conrune")
        self.displays_layout.addWidget(self.conrune_display, 0, 1)

        self.reverse_display = TQNumberDisplay("Ternary Reversal")
        self.displays_layout.addWidget(self.reverse_display, 1, 0)

        self.reverse_conrune_display = TQNumberDisplay("Ternary Reversal Conrune")
        self.displays_layout.addWidget(self.reverse_conrune_display, 1, 1)

        self.content_layout.addLayout(self.displays_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        self.visualizers_layout.addWidget(scroll_area)

        # Add components to the splitter
        self.main_splitter.addWidget(self.properties_panel)
        self.main_splitter.addWidget(self.visualizers_container)

        # Set initial splitter sizes - give more space to visualizers
        self.main_splitter.setSizes([300, 700])

        # Add the splitter to the main layout
        self.layout.addWidget(self.main_splitter, 1)  # Give it stretch

        # Create transition utility
        self.transition = TernaryTransition()

        # Set initial values
        self._process_number()

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            """
        )

    def set_number(self, value: int) -> None:
        """Set the number for analysis.

        Args:
            value: The number to analyze
        """
        self.number_input.setText(str(value))
        self._process_number()

    def _process_number(self) -> None:
        """Process the input number and update all displays."""
        try:
            # Get the decimal value
            try:
                decimal_value = int(self.number_input.text() or "0")
            except ValueError:
                decimal_value = 0

            # Get the ternary representation
            ternary_str = decimal_to_ternary(decimal_value)

            # Auto-determine padding length based on ternary length
            # Always use at least 6 digits padding for consistency
            pad_length = max(6, len(ternary_str))

            # Pad the ternary string
            padded_ternary = format_ternary(ternary_str, pad_length=pad_length)

            # Update base number display
            self.base_display.set_number(decimal_value, pad_length)

            # Calculate and update conrune display
            conrune_ternary = self.transition.apply_conrune(padded_ternary)
            conrune_decimal = ternary_to_decimal(conrune_ternary)
            self.conrune_display.decimal_label.setText(str(conrune_decimal))
            self.conrune_display.ternary_label.setText(conrune_ternary)
            self.conrune_display.visualizer.set_ternary(conrune_ternary)

            # Calculate and update reversed ternary display
            reversed_ternary = padded_ternary[::-1]  # Reverse the string
            reversed_decimal = ternary_to_decimal(reversed_ternary)
            self.reverse_display.decimal_label.setText(str(reversed_decimal))
            self.reverse_display.ternary_label.setText(reversed_ternary)
            self.reverse_display.visualizer.set_ternary(reversed_ternary)

            # Calculate and update reversed conrune display
            reversed_conrune = self.transition.apply_conrune(reversed_ternary)
            reversed_conrune_decimal = ternary_to_decimal(reversed_conrune)
            self.reverse_conrune_display.decimal_label.setText(
                str(reversed_conrune_decimal)
            )
            self.reverse_conrune_display.ternary_label.setText(reversed_conrune)
            self.reverse_conrune_display.visualizer.set_ternary(reversed_conrune)

            # Update the TQGridService with current display values
            grid_service = TQGridService.get_instance()
            grid_service.update_grid_display(
                base=decimal_value,
                conrune=conrune_decimal,
                reversal=reversed_decimal,
                reversal_conrune=reversed_conrune_decimal,
            )

            # Update the number properties panel
            self.properties_panel.set_number(decimal_value)

            # Dynamically adjust visualizer minimum heights based on digit count
            digit_height = 40  # Approximate height of each digit in pixels
            min_visualizer_height = max(300, pad_length * digit_height)

            self.base_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.conrune_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.reverse_display.visualizer.setMinimumHeight(min_visualizer_height)
            self.reverse_conrune_display.visualizer.setMinimumHeight(
                min_visualizer_height
            )

            # Adjust window size if this is a standalone window
            if self.standalone or self.parent() is None:
                # Base height plus space for each visualizer
                header_height = 100  # Space for title, input fields
                total_height = (
                    header_height + (min_visualizer_height * 2) + 150
                )  # Add some spacing between rows

                current_size = self.size()
                self.resize(current_size.width(), total_height)

        except KeyError as e:
            # Handle transition map errors
            import logging

            logging.error(f"Transition error: {e}")

            # Update displays with error message
            error_message = f"Error: {e}"
            self.conrune_display.decimal_label.setText("Error")
            self.conrune_display.ternary_label.setText(error_message)
            self.reverse_conrune_display.decimal_label.setText("Error")
            self.reverse_conrune_display.ternary_label.setText(error_message)

            # Update service with error values
            grid_service = TQGridService.get_instance()
            grid_service.update_grid_display(
                base=decimal_value, conrune=0, reversal=0, reversal_conrune=0
            )


if __name__ == "__main__":
    """Simple demonstration of the TQ Grid panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = TQGridPanel(standalone=True)
    panel.resize(1200, 800)  # Larger initial size to accommodate properties panel
    panel.show()
    sys.exit(app.exec())
