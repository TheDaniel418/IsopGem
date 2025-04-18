"""
Purpose: Provides a panel for analyzing ternary numbers through dimensional interpretation

This file is part of the tq pillar and serves as a UI component.
It is responsible for interpreting ternary numbers through the lens of dimensional
aspects, positional values, and element interactions across different scales.

Key components:
- TernaryDimensionalAnalysisPanel: Main panel for analyzing ternary numbers

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary
- tq.services.ternary_dimension_interpreter_new: For interpreting ternary numbers

Related files:
- tq/ui/tq_tab.py: Main tab that opens this panel
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from tq.services.ternary_dimension_interpreter_new import HexagramInterpreter
from tq.utils.ternary_converter import decimal_to_ternary


class TernaryDimensionalAnalysisPanel(QWidget):
    """Panel for analyzing ternary numbers through dimensional interpretation."""

    def __init__(self, parent=None):
        """Initialize the Ternary Dimensional Analysis panel.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Create interpreter (new logic)
        self.interpreter = HexagramInterpreter()

        # Initialize the UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title = QLabel("Ternary Dimensional Analysis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)

        # Description
        description = QLabel(
            "This tool analyzes ternary numbers through a dimensional interpretation framework. "
            "Enter a decimal number to see how it manifests as a pattern of "
            "Aperture (0), Surge (1), and Lattice (2) elements across different dimensional positions."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)

        # Input section
        input_group = QGroupBox("Input Number")
        input_layout = QGridLayout(input_group)

        # Decimal input
        input_layout.addWidget(QLabel("Decimal Number:"), 0, 0)
        self.decimal_input = QLineEdit()
        self.decimal_input.setValidator(QIntValidator(0, 9999999))
        self.decimal_input.setPlaceholderText("Enter decimal number")
        self.decimal_input.setMaximumWidth(200)
        input_layout.addWidget(self.decimal_input, 0, 1)

        # Analyze button
        self.analyze_button = QPushButton("Analyze Dimensional Pattern")
        self.analyze_button.clicked.connect(self._analyze_number)
        input_layout.addWidget(self.analyze_button, 0, 2)

        # Help button
        self.help_button = QPushButton("?")
        self.help_button.setToolTip("Learn about calculation methods")
        self.help_button.setFixedSize(30, 30)  # Make it a small circular button
        self.help_button.setStyleSheet(
            """
            QPushButton {
                background-color: #5E35B1;
                color: white;
                font-weight: bold;
                border-radius: 15px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #7E57C2;
            }
        """
        )
        self.help_button.clicked.connect(self._show_help_dialog)
        input_layout.addWidget(self.help_button, 0, 3)

        # Ternary display
        input_layout.addWidget(QLabel("Ternary Form:"), 1, 0)
        self.ternary_display = QLabel("")
        self.ternary_display.setStyleSheet(
            "font-family: monospace; font-weight: bold; font-size: 14px;"
        )
        input_layout.addWidget(self.ternary_display, 1, 1, 1, 2)

        main_layout.addWidget(input_group)

        # Create scrollable results area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Results container
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(15)

        # Position analysis section
        self.position_group = QGroupBox("Dimensional Element Analysis")
        position_layout = QVBoxLayout(self.position_group)
        self.position_layout = position_layout
        self.results_layout.addWidget(self.position_group)

        # Trigram analysis section
        self.trigram_group = QGroupBox("Trigram Analysis")
        trigram_layout = QVBoxLayout(self.trigram_group)
        self.trigram_text = QTextEdit()
        self.trigram_text.setReadOnly(True)
        self.trigram_text.setMinimumHeight(150)
        trigram_layout.addWidget(self.trigram_text)
        self.results_layout.addWidget(self.trigram_group)

        # Overall pattern analysis
        self.pattern_group = QGroupBox("Pattern Interpretation")
        pattern_layout = QVBoxLayout(self.pattern_group)
        self.pattern_text = QTextEdit()
        self.pattern_text.setReadOnly(True)
        self.pattern_text.setMinimumHeight(250)
        pattern_layout.addWidget(self.pattern_text)
        self.results_layout.addWidget(self.pattern_group)

        # Kamea full interpretation section
        self.kamea_group = QGroupBox("Kamea Full Interpretation")
        kamea_layout = QVBoxLayout(self.kamea_group)
        self.kamea_text = QTextEdit()
        self.kamea_text.setReadOnly(True)
        self.kamea_text.setMinimumHeight(300)
        kamea_layout.addWidget(self.kamea_text)
        self.results_layout.addWidget(self.kamea_group)

        # Add results to scroll area
        scroll_area.setWidget(self.results_container)
        main_layout.addWidget(scroll_area, 1)  # Give it stretch

        # Set all result groups initially hidden
        self.position_group.setVisible(False)
        self.trigram_group.setVisible(False)
        self.pattern_group.setVisible(False)
        self.kamea_group.setVisible(False)

    def _analyze_number(self):
        """Analyze the input number and display dimensional interpretation."""
        # Get decimal value
        try:
            decimal_value = int(self.decimal_input.text() or "0")
        except ValueError:
            self.ternary_display.setText("Invalid input")
            return

        # Convert to ternary
        ternary_str = decimal_to_ternary(decimal_value)

        # Update ternary display
        self.ternary_display.setText(ternary_str)

        # Analyze and display results
        self._display_position_analysis(ternary_str)
        self._display_trigram_analysis(ternary_str)
        self._display_pattern_analysis(ternary_str)
        self._display_kamea_interpretation(ternary_str)

        # Show the results sections
        self.position_group.setVisible(True)
        self.trigram_group.setVisible(True)
        self.pattern_group.setVisible(True)
        self.kamea_group.setVisible(True)

    def _display_position_analysis(self, ternary_str: str):
        """Display the position-by-position dimensional analysis.

        Args:
            ternary_str: The ternary string to analyze
        """
        # Clear previous content
        for i in reversed(range(self.position_layout.count())):
            widget = self.position_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        num_digits = len(ternary_str)

        # Iterate from rightmost digit (index 0, Dimension 1) to leftmost
        # The UI should display frames from top (highest dimension) to bottom (lowest)
        # So we build the interpretations first, then add them in reverse order to the layout.
        position_frames = []
        for index in range(num_digits):
            digit = int(
                ternary_str[num_digits - 1 - index]
            )  # Get digit from right to left
            dimension_number = index + 1  # Dimension number (1-based, right-to-left)

            # Get the enhanced interpretation for the correct index
            interpretation = self.interpreter.interpret_digit(digit, index)

            # Create frame for this position
            position_frame = QFrame()
            position_frame.setFrameShape(QFrame.Shape.StyledPanel)
            position_frame.setFrameShadow(QFrame.Shadow.Raised)

            # Color code based on digit
            if digit == 0:  # Aperture
                position_frame.setStyleSheet(
                    "background-color: #E6F3FF; border: 1px solid #99CCFF;"
                )
            elif digit == 1:  # Surge
                position_frame.setStyleSheet(
                    "background-color: #FFF0E6; border: 1px solid #FFCC99;"
                )
            else:  # Lattice (digit == 2)
                position_frame.setStyleSheet(
                    "background-color: #E6FFE6; border: 1px solid #99FF99;"
                )

            frame_layout = QVBoxLayout(position_frame)

            # Position header - Use dimension_number (1-based, right-to-left)
            header = QLabel(
                f"Dimension {dimension_number}: {interpretation['position_name']} ({interpretation['triad_name']} Triad) - Value: 3^{index} = {interpretation['position_value']}"
            )
            header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            frame_layout.addWidget(header)

            # Element info - Use keys from the updated service response
            element_info = QLabel(
                f"Element: {digit} - {interpretation['name']} ({interpretation['energy']} - {interpretation['quality']})"
            )
            element_info.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            frame_layout.addWidget(element_info)

            # Basic description
            description = QLabel(interpretation["description"])
            description.setWordWrap(True)
            frame_layout.addWidget(description)

            # Detailed dimensional meaning
            dimensional_meaning = QLabel(
                f"<b>Contextual Meaning:</b> {interpretation['dimensional_meaning']}"
            )
            dimensional_meaning.setWordWrap(True)
            frame_layout.addWidget(dimensional_meaning)

            position_frames.append(position_frame)

        # Add frames to layout in reverse order (highest dimension first)
        for frame in reversed(position_frames):
            self.position_layout.addWidget(frame)

    def _display_trigram_analysis(self, ternary_str: str):
        """Display the trigram analysis using the get_trigram_meanings method.

        Args:
            ternary_str: The ternary string to analyze
        """
        # Get trigram meanings
        trigram_meanings = self.interpreter.get_trigram_meanings(ternary_str)

        # Format the trigram analysis for display
        output_md = "## Trigram Analysis\n\n"

        # Upper Trigram
        upper = trigram_meanings["Upper Trigram"]
        output_md += "### Upper Trigram\n\n"
        if upper["trigram"]:
            output_md += f"**Trigram:** {upper['trigram']}\n\n"
            output_md += f"**Name:** {upper['english_name']} ({upper['name']})\n\n"
            output_md += f"**Transliteration:** {upper['transliteration']}\n\n"
            output_md += f"**Interpretation:** {upper['interpretation']}\n\n"
        else:
            output_md += "*Upper trigram not available for numbers with fewer than 6 digits.*\n\n"

        # Lower Trigram
        lower = trigram_meanings["Lower Trigram"]
        output_md += "### Lower Trigram\n\n"
        if lower["trigram"]:
            output_md += f"**Trigram:** {lower['trigram']}\n\n"
            output_md += f"**Name:** {lower['english_name']} ({lower['name']})\n\n"
            output_md += f"**Transliteration:** {lower['transliteration']}\n\n"
            output_md += f"**Interpretation:** {lower['interpretation']}\n\n"
        else:
            output_md += "*Lower trigram not available for numbers with fewer than 3 digits.*\n\n"

        # Set the text in markdown format
        self.trigram_text.setMarkdown(output_md.strip())

    def _display_pattern_analysis(self, ternary_str: str):
        """Display the overall pattern analysis using the enhanced service format."""
        # Convert string to list of integers for the new service
        ternary_digits = [int(digit) for digit in ternary_str]
        if not ternary_digits:
            self.pattern_text.setMarkdown("Please enter a valid number to analyze.")
            return

        # Use the enhanced analyze_ternary method
        analysis = self.interpreter.analyze_ternary(ternary_digits)

        if "error" in analysis:
            self.pattern_text.setMarkdown(f"**Error:** {analysis['error']}")
            return

        # Format the comprehensive analysis for display
        output_md = ""

        # 1. Distribution
        output_md += "## Element Distribution\n\n"
        output_md += (
            f"- Aperture (0): {analysis['distribution']['counts'][0]} appearances\n"
        )
        output_md += (
            f"- Surge (1): {analysis['distribution']['counts'][1]} appearances\n"
        )
        output_md += (
            f"- Lattice (2): {analysis['distribution']['counts'][2]} appearances\n\n"
        )
        output_md += (
            f"- **Dominant Element:** {analysis['distribution']['dominant_element']}\n"
        )
        output_md += f"- **Element Balance:** {analysis['distribution']['balance']}\n\n"

        # Note: Triad Analysis section removed as it's already included in the Core Narrative
        # We'll only keep the cross-triad resonance info if it's not already in the narrative
        if analysis["patterns"]["cross_triad_resonance"] and (
            analysis.get("narrative") is None
            or "Cross-Triad Resonance" not in analysis["narrative"]
        ):
            output_md += "## Cross-Triad Resonance\n\n"
            output_md += (
                "**Resonance Patterns:** "
                + "; ".join(analysis["patterns"]["cross_triad_resonance"])
                + "\n\n"
            )

        # 3. Pattern Recognition Details
        output_md += "## Pattern Details\n\n"  # Renamed section header
        has_patterns = False
        # Repetitions / Absences
        if analysis["patterns"]["repetitions"]:
            has_patterns = True
            output_md += "**Repetitions/Absences:**\n"
            for rep in analysis["patterns"]["repetitions"]:
                if rep.get("absence"):
                    output_md += f"- Absence of {rep['element']}\n"
                else:
                    output_md += f"- {rep['element']} appears {rep['count']} times\n"
            output_md += "\n"
        # Sequences
        if analysis["patterns"]["sequences"]:
            has_patterns = True
            output_md += "**Sequences (3+ consecutive):**\n"
            for seq in analysis["patterns"]["sequences"]:
                output_md += f"- {seq['element']} sequence of length {seq['length']} starting at Dimension {seq['position']}\n"
            output_md += "\n"
        # Symmetry
        if analysis["patterns"]["symmetry"]["score"] > 0.0:
            has_patterns = True
            output_md += (
                f"**Symmetry:** {analysis['patterns']['symmetry']['description']}\n\n"
            )

        if not has_patterns:
            output_md += (
                "No significant repetitions, sequences, or symmetry detected.\n\n"
            )

        # TODO: Display Progression, Oscillation when implemented

        # 4. Core Narrative (Generated by Service)
        if analysis.get("narrative"):
            output_md += analysis["narrative"]  # Use the pre-formatted narrative

        # 5. Holistic Interpretation (if available)
        if analysis.get("holistic"):
            output_md += "\n"  # Add extra space
            output_md += analysis["holistic"]  # Add the holistic interpretation

        # Set the text in markdown format
        self.pattern_text.setMarkdown(output_md.strip())

    def _display_kamea_interpretation(self, ternary_str: str):
        """Display the full Kamea interpretation using the interpret method.

        Args:
            ternary_str: The ternary string to analyze
        """
        # Ensure we have a 6-digit ternary string for the full interpretation
        # Pad with zeros if needed, or truncate if too long
        ditrune = ternary_str.zfill(6)[-6:]

        # Get the full interpretation
        try:
            interpretation = self.interpreter.interpret(ditrune)
        except Exception as e:
            self.kamea_text.setMarkdown(f"**Error:** {str(e)}")
            return

        # Format the interpretation for display
        output_md = "## Kamea Hexagram Interpretation\n\n"

        # Basic information
        output_md += f"**Ditrune:** {interpretation.get('Ditrune', ditrune)}\n\n"
        output_md += (
            f"**Decimal Value:** {interpretation.get('Decimal Value', 'N/A')}\n\n"
        )
        output_md += (
            f"**Kamea Locator:** {interpretation.get('Kamea Locator', 'N/A')}\n\n"
        )
        output_md += f"**Family:** {interpretation.get('Family', 'N/A')}\n\n"
        output_md += f"**Level:** {interpretation.get('Level', 'N/A')}\n\n"
        output_md += (
            f"**Core Essence:** {interpretation.get('CORE ESSENCE', 'N/A')}\n\n"
        )

        # Ditrune type and mythic overlay
        ditrune_type = interpretation.get("ditrune_type", "unknown")
        output_md += f"**Ditrune Type:** {ditrune_type.capitalize()}\n\n"

        # Hierophant (Prime) information
        if "Hierophant" in interpretation and interpretation["Hierophant"]:
            hierophant = interpretation["Hierophant"]
            output_md += "### Hierophant (Prime)\n\n"
            output_md += f"**Name:** {hierophant.get('name', 'N/A')}\n\n"
            output_md += f"**Greek:** {hierophant.get('greek', 'N/A')}\n\n"
            output_md += (
                f"**Mythic Meaning:** {hierophant.get('mythic_meaning', 'N/A')}\n\n"
            )
            output_md += (
                f"**Core Essence:** {hierophant.get('core_essence', 'N/A')}\n\n"
            )

        # Acolyte (Composite) information
        if "Acolyte" in interpretation and interpretation["Acolyte"]:
            acolyte = interpretation["Acolyte"]
            output_md += "### Acolyte (Composite)\n\n"
            output_md += f"**Title:** {acolyte.get('title', 'N/A')}\n\n"
            output_md += f"**Greek:** {acolyte.get('greek', 'N/A')}\n\n"
            output_md += f"**Function:** {acolyte.get('function', 'N/A')}\n\n"
            output_md += f"**Nature:** {acolyte.get('nature', 'N/A')}\n\n"
            output_md += f"**Serves:** {acolyte.get('serves', 'N/A')}\n\n"
            output_md += f"**Influence:** {acolyte.get('influence', 'N/A')}\n\n"

        # Temple (Concurrent) information
        if "Temple" in interpretation and interpretation["Temple"]:
            temple = interpretation["Temple"]
            output_md += "### Temple (Concurrent)\n\n"
            output_md += f"**Full Name:** {temple.get('full_name', 'N/A')}\n\n"
            output_md += f"**Temple Type:** {temple.get('temple_type', 'N/A')} ({temple.get('temple_type_greek', 'N/A')})\n\n"
            output_md += (
                f"**Element Descriptor:** {temple.get('element_descriptor', 'N/A')}\n\n"
            )

        # Dimensional Analysis
        if "Dimensional Analysis" in interpretation:
            output_md += "### Dimensional Analysis\n\n"
            for line in interpretation["Dimensional Analysis"]:
                output_md += f"**Position {line['position']}:** {line['name']} - {line['interpretation'][:100]}...\n\n"

        # Bigram information
        if "Bigrams" in interpretation:
            output_md += "### Bigram Analysis\n\n"
            for bigram in interpretation["Bigrams"]:
                output_md += f"**{bigram['label']}:** {bigram['name']} - {bigram['interpretation']}\n\n"

        # Set the text in markdown format
        self.kamea_text.setMarkdown(output_md.strip())

    def _show_help_dialog(self):
        """Show a dialog with information about the Kamea system."""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Kamea Ternary Analysis System")
        help_dialog.setMinimumSize(800, 600)

        # Main layout
        main_layout = QVBoxLayout(help_dialog)

        # Create tab widget for different sections
        tab_widget = QTabWidget()

        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setMarkdown(
            """
        # Kamea Ternary Analysis System

        This tool analyzes ternary numbers (base-3 numbers consisting of digits 0, 1, and 2)
        through the Kamea interpretive framework. In this system, each ternary digit represents
        a specific element in the dimensional structure:

        - **0 (Aperture)**: Represents openings, potential, receptivity, and the unmanifest.
        - **1 (Surge)**: Represents transformation, change, dynamic flow, and becoming.
        - **2 (Lattice)**: Represents structure, pattern, stability, and being.

        The analysis interprets patterns within ternary numbers to reveal interactions between these
        elements across various dimensions and scales. The resulting insights offer perspectives
        on transformational dynamics, structural patterns, and dimensional resonances.

        ## Key Analysis Components

        - **Dimensional Analysis**: Interprets each digit based on its dimensional position
        - **Trigram Analysis**: Examines upper and lower trigrams for deeper meaning
        - **Pattern Recognition**: Identifies significant patterns and symmetries
        - **Element Distribution**: Analyzes the balance and dominance of elements
        """
        )
        overview_layout.addWidget(overview_text)
        tab_widget.addTab(overview_tab, "Overview")

        main_layout.addWidget(tab_widget)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(help_dialog.accept)
        main_layout.addWidget(close_button)

        help_dialog.exec()


if __name__ == "__main__":
    """Simple demonstration of the Ternary Dimensional Analysis panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = TernaryDimensionalAnalysisPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec())
