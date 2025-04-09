"""
Cosmic Force Widget.

This widget allows users to enter a decimal number and view its ternary representation
along with a cosmic force interpretation, providing insights into the number's
energetic qualities and patterns.
"""

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tq.services.cosmic_force_interpreter import CosmicForceInterpreter
from tq.services.ternary_utils import decimal_to_ternary


class CosmicForceWidget(QWidget):
    """Widget for interpreting decimal numbers as cosmic forces through ternary conversion."""

    def __init__(self, parent=None):
        """Initialize the cosmic force widget."""
        super().__init__(parent)

        self.interpreter = CosmicForceInterpreter()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Title
        title_label = QLabel("Cosmic Force Interpreter")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # Description
        description_label = QLabel(
            "Enter a decimal number to see its ternary representation "
            "and cosmic force interpretation."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description_label)

        # Input area
        input_layout = QHBoxLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter decimal number")
        self.number_input.returnPressed.connect(self.on_interpret_clicked)

        self.interpret_button = QPushButton("Interpret")
        self.interpret_button.clicked.connect(self.on_interpret_clicked)

        input_layout.addWidget(QLabel("Number:"))
        input_layout.addWidget(self.number_input)
        input_layout.addWidget(self.interpret_button)

        main_layout.addLayout(input_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # Results area (scrollable)
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)

        # Ternary representation section
        self.ternary_section = QWidget()
        self.ternary_layout = QVBoxLayout(self.ternary_section)

        self.ternary_title = QLabel("Ternary Representation")
        title_font = QFont()
        title_font.setBold(True)
        self.ternary_title.setFont(title_font)
        self.ternary_layout.addWidget(self.ternary_title)

        self.ternary_display = QLabel()
        self.ternary_layout.addWidget(self.ternary_display)

        # Digit meanings section
        self.digits_grid = QGridLayout()
        self.digits_grid.setColumnStretch(1, 1)  # Make the description column stretch
        self.ternary_layout.addLayout(self.digits_grid)

        # Summary section
        self.summary_section = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_section)

        self.summary_title = QLabel("Cosmic Force Summary")
        self.summary_title.setFont(title_font)
        self.summary_layout.addWidget(self.summary_title)

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_layout.addWidget(self.summary_text)

        # Add sections to results
        self.results_layout.addWidget(self.ternary_section)
        self.results_layout.addWidget(self.summary_section)
        self.results_layout.addStretch()

        self.results_area.setWidget(self.results_widget)
        main_layout.addWidget(self.results_area)

        # Set layout
        self.setLayout(main_layout)

        # Hide results initially
        self.ternary_section.hide()
        self.summary_section.hide()

    @pyqtSlot()
    def on_interpret_clicked(self):
        """Handle the interpret button click."""
        input_text = self.number_input.text().strip()

        # Validate input
        try:
            decimal_number = int(input_text)
            if decimal_number < 0:
                raise ValueError("Number must be positive")
        except ValueError as e:
            self.show_error(f"Invalid input: {str(e)}")
            return

        # Convert decimal to ternary
        ternary_digits = decimal_to_ternary(decimal_number)

        # Interpret the ternary representation
        interpretation = self.interpreter.analyze_ternary(ternary_digits)

        # Display results
        self.display_results(decimal_number, ternary_digits, interpretation)

    def show_error(self, error_message):
        """Display an error message."""
        self.ternary_section.hide()
        self.summary_section.hide()

        # Clear previous results
        self.clear_grid_layout(self.digits_grid)

        # Show error
        error_label = QLabel(error_message)
        error_label.setStyleSheet("color: red;")
        self.digits_grid.addWidget(error_label, 0, 0, 1, 2)
        self.ternary_section.show()

    def display_results(self, decimal_number, ternary_digits, interpretation):
        """Display the interpretation results."""
        # Clear previous results
        self.clear_grid_layout(self.digits_grid)

        # Show the ternary representation
        ternary_str = "".join(str(d) for d in ternary_digits)
        self.ternary_display.setText(
            f"Decimal {decimal_number} = Ternary {ternary_str}"
        )

        # Show digit interpretations
        self.digits_grid.addWidget(QLabel("Position"), 0, 0)
        self.digits_grid.addWidget(QLabel("Digit"), 0, 1)
        self.digits_grid.addWidget(QLabel("Meaning"), 0, 2)

        for i, digit_info in enumerate(interpretation["digits"]):
            position = len(interpretation["digits"]) - i - 1

            # Position label
            pos_label = QLabel(f"{position} ({digit_info['position']})")
            self.digits_grid.addWidget(pos_label, i + 1, 0)

            # Digit label
            digit = ternary_digits[position]
            digit_label = QLabel(str(digit))
            self.digits_grid.addWidget(digit_label, i + 1, 1)

            # Meaning label
            meaning_label = QLabel(
                f"{digit_info['name']} - {digit_info['description']}"
            )
            self.digits_grid.addWidget(meaning_label, i + 1, 2)

        # Show summary
        summary_html = f"""
        <h3>Overall Force Analysis</h3>
        <p>{interpretation['overall']['summary']}</p>

        <h3>Dominant Force</h3>
        <p>{interpretation['dominant_force']}</p>

        <h3>Balance</h3>
        <p>{interpretation['balance']}</p>
        """

        # Add patterns if any
        if interpretation["patterns"]:
            summary_html += "<h3>Significant Patterns</h3><ul>"
            for pattern in interpretation["patterns"]:
                summary_html += f"<li>Sequence of {pattern['length']} {self.interpreter.DIGIT_MEANINGS[pattern['digit']]['name']} digits: {pattern['meaning']}</li>"
            summary_html += "</ul>"

        self.summary_text.setHtml(summary_html)

        # Show all sections
        self.ternary_section.show()
        self.summary_section.show()

    def clear_grid_layout(self, layout):
        """Clear all widgets from a grid layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
