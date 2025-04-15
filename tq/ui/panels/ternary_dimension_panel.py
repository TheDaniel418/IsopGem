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
- tq.services.ternary_dimension_interpreter: For interpreting ternary numbers

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

from tq.services.ternary_dimension_interpreter import TernaryDimensionInterpreter
from tq.utils.ternary_converter import decimal_to_ternary


class TernaryDimensionalAnalysisPanel(QWidget):
    """Panel for analyzing ternary numbers through dimensional interpretation."""

    def __init__(self, parent=None):
        """Initialize the Ternary Dimensional Analysis panel.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Create interpreter
        self.interpreter = TernaryDimensionInterpreter()

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

        # Overall pattern analysis
        self.pattern_group = QGroupBox("Pattern Interpretation")
        pattern_layout = QVBoxLayout(self.pattern_group)
        self.pattern_text = QTextEdit()
        self.pattern_text.setReadOnly(True)
        self.pattern_text.setMinimumHeight(250)
        pattern_layout.addWidget(self.pattern_text)
        self.results_layout.addWidget(self.pattern_group)

        # Add results to scroll area
        scroll_area.setWidget(self.results_container)
        main_layout.addWidget(scroll_area, 1)  # Give it stretch

        # Set the position group and pattern group initially hidden
        self.position_group.setVisible(False)
        self.pattern_group.setVisible(False)

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
        self._display_pattern_analysis(ternary_str)

        # Show the results sections
        self.position_group.setVisible(True)
        self.pattern_group.setVisible(True)

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

    def _show_help_dialog(self):
        """Show a dialog with detailed explanation of the calculation methods."""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Ternary Dimensional Analysis - Framework")
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
        # Ternary Dimensional Analysis Overview

        This tool analyzes ternary numbers (base-3 numbers consisting of digits 0, 1, and 2)
        through a dimensional interpretive framework. In this system, each ternary digit represents
        a specific element in the dimensional structure:

        - **0 (Aperture)**: Represents openings, potential, receptivity, and the unmanifest.
        - **1 (Surge)**: Represents transformation, change, dynamic flow, and becoming.
        - **2 (Lattice)**: Represents structure, pattern, stability, and being.

        The analysis interprets patterns within ternary numbers to reveal interactions between these
        elements across various dimensions and scales. The resulting insights offer perspectives
        on transformational dynamics, structural patterns, and dimensional resonances.

        ## Key Analysis Components

        - **Dimensional Analysis**: Interprets each digit based on its dimensional position (1-9)
        - **Triad Framework**: Groups dimensions into Potential (1-3), Process (4-6), and Emergence (7-9)
        - **Pattern Recognition**: Identifies significant patterns within and across triads
        - **Element Interactions**: Examines how different elements influence each other
        - **Dimensional Geometry**: Explores symmetry, directionality, and transformational dynamics
        """
        )
        overview_layout.addWidget(overview_text)
        tab_widget.addTab(overview_tab, "Overview")

        # Elements tab
        elements_tab = QWidget()
        elements_layout = QVBoxLayout(elements_tab)
        elements_text = QTextEdit()
        elements_text.setReadOnly(True)
        elements_text.setMarkdown(
            """
        # The Three Elements

        The foundation of this system consists of three fundamental elements that represent distinct modes of existence and transformation:

        ## Aperture (0)

        An opening of possibility; the space through which potential emerges.

        **Nature**: Non-directed openness; a space of pure potential
        **Movement**: Radial expansion or contraction; creates space for emergence
        **Relation to Time**: Exists beyond temporality; holds all possibilities simultaneously
        **Manifestation**: Appears as gaps, pauses, spaces of opportunity, or undefined regions
        **When Dominant**: Indicates deep potential, awaiting conditions for activation

        ## Surge (1)

        A flowing current of change; the active principle of transformation.

        **Nature**: Directed energy; an active principle of transformation
        **Movement**: Vectored, flowing in specific directions or along paths of least resistance
        **Relation to Time**: Engages with temporal processes; the principle of becoming
        **Manifestation**: Appears as growth, change, evolution, energy transfer, or active transformation
        **When Dominant**: Indicates dynamic systems undergoing significant transformation or exchange

        ## Lattice (2)

        A crystallized pattern; the structure that gives form to possibility.

        **Nature**: Patterned structure; a coherent arrangement of relationships
        **Movement**: Geometric organization; creates stable networks and frameworks
        **Relation to Time**: Persists through time; embodies remembered patterns
        **Manifestation**: Appears as form, structure, organization, or defined boundaries
        **When Dominant**: Indicates crystallized patterns resistant to change but rich in complexity
        """
        )
        elements_layout.addWidget(elements_text)
        tab_widget.addTab(elements_tab, "Elements")

        # Dimensions tab
        dimensions_tab = QWidget()
        dimensions_layout = QVBoxLayout(dimensions_tab)
        dimensions_text = QTextEdit()
        dimensions_text.setReadOnly(True)
        dimensions_text.setMarkdown(
            """
        # The Nine Dimensions

        The system uses 9 positions, organized as three triads, each representing a distinct domain of experience:

        ## Dimensions of Potential (Positions 1-3)
        *These dimensions describe the foundational qualities and inner dynamics of a system.*

        1. **Seed** - The generative core or initial impulse
        2. **Resonance** - The internal vibratory pattern and self-relation
        3. **Echo** - The ripple effect; how the core pattern reverberates outward

        ## Dimensions of Process (Positions 4-6)
        *These dimensions describe how systems interact, transform, and develop over time.*

        4. **Weave** - The interconnection pattern; how elements join and separate
        5. **Pulse** - The rhythm and timing; the temporal aspect of transformation
        6. **Flow** - The directional movement; how energy or information is channeled

        ## Dimensions of Emergence (Positions 7-9)
        *These dimensions describe how systems culminate, transcend, and transform completely.*

        7. **Nexus** - The point of convergence; where multiple patterns meet and intensify
        8. **Horizon** - The edge of perception; the boundary between known and unknown
        9. **Nova** - The point of complete transformation; fundamental shift of the entire system

        ## Scale-Based Categorization

        The magnitude of a ternary number determines which triads are activated:

        - **Potential Numbers** (1-3 digits, 001-222): Focus solely on foundational qualities
        - **Process Numbers** (4-6 digits, 1000-222222): Include both potential and developmental aspects
        - **Emergence Numbers** (7-9 digits, 1000000-222222222): Represent the complete picture
        """
        )
        dimensions_layout.addWidget(dimensions_text)
        tab_widget.addTab(dimensions_tab, "Dimensions")

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
