"""
Purpose: Provides a panel for analyzing the cosmic forces in ternary numbers

This file is part of the tq pillar and serves as a UI component.
It is responsible for interpreting ternary numbers in terms of their
force dynamics, positional values, and cosmic energetic patterns.

Key components:
- CosmicForceAnalysisPanel: Main panel for analyzing cosmic forces in ternary numbers
- CosmicForceInterpreter: Service class that generates force interpretations

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary

Related files:
- tq/ui/tq_tab.py: Main tab that opens this panel
"""

from typing import Dict, List, Tuple, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGridLayout, QGroupBox, QScrollArea,
    QSizePolicy, QSpacerItem, QTextEdit, QTabWidget, QDialog
)
from PyQt6.QtGui import QIntValidator, QFont, QColor, QPalette
from PyQt6.QtCore import Qt

from tq.utils.ternary_converter import decimal_to_ternary


class CosmicForceInterpreter:
    """Interpreter for cosmic forces in ternary numbers."""
    
    POSITION_NAMES = {
        1: "Immediate Force",
        2: "Daily Force",
        3: "Lunar Force",
        4: "Annual Force",
        5: "Life Phase Force",
        6: "Life Path Force",
        7: "Generational Force",
        8: "Collective Force",
        9: "Universal Force"
    }
    
    FORCE_MEANINGS = {
        0: {
            "name": "The Void State",
            "description": "Pure equilibrium; neither expanding nor contracting. The primordial state of undifferentiated potential."
        },
        1: {
            "name": "The Expansive Force",
            "description": "Active outward movement; the principle of differentiation and separation. The cosmic impulse that breaks symmetry."
        },
        2: {
            "name": "The Contractive Force",
            "description": "Inward movement and concentration; the principle of attraction and densification. The force that gathers energy into coherent structures."
        }
    }
    
    def interpret_digit(self, digit: int, position: int) -> Dict:
        """Generate an interpretation for a digit at a specific position.
        
        Args:
            digit: The ternary digit (0, 1, or 2)
            position: The position of the digit (1-9, with 1 being the rightmost)
            
        Returns:
            Dictionary containing the interpretation
        """
        position_name = self.POSITION_NAMES.get(position, f"Position {position}")
        force_info = self.FORCE_MEANINGS.get(digit, {"name": "Unknown", "description": "Unknown force"})
        
        # Build specific interpretation based on digit and position
        if digit == 0:
            specific = f"The Void Force in the {position_name.lower()} position creates equilibrium and balance. "
            if position > 7:
                specific += "At this cosmic level, it establishes fundamental stability in the highest realms of force dynamics."
            elif position > 4:
                specific += "This creates a stabilizing influence in the intermediate force structure."
            else:
                specific += "This grounds the system with balance at the foundational level."
        elif digit == 1:
            specific = f"The Expansive Force in the {position_name.lower()} position generates outward movement and growth. "
            if position > 7:
                specific += "At this cosmic level, it creates primary differentiation and breaks universal symmetry."
            elif position > 4:
                specific += "This introduces dynamic expansion in the intermediate force structure."
            else:
                specific += "This pushes energy outward at the foundational level."
        else:  # digit == 2
            specific = f"The Contractive Force in the {position_name.lower()} position pulls energy inward and concentrates it. "
            if position > 7:
                specific += "At this cosmic level, it creates fundamental attraction and cosmic cohesion."
            elif position > 4:
                specific += "This introduces consolidation and density in the intermediate force structure."
            else:
                specific += "This gathers and concentrates energy at the foundational level."
        
        return {
            "position": position,
            "position_name": position_name,
            "position_value": 3**(position-1),
            "digit": digit,
            "force_name": force_info["name"],
            "force_description": force_info["description"],
            "specific_interpretation": specific
        }
    
    def analyze_pattern(self, ternary_str: str) -> Dict:
        """Analyze the overall pattern in a ternary number.
        
        Args:
            ternary_str: The ternary string to analyze
            
        Returns:
            Dictionary containing pattern analysis
        """
        # Count occurrences of each digit
        counts = {
            0: ternary_str.count('0'),
            1: ternary_str.count('1'),
            2: ternary_str.count('2')
        }
        
        # Calculate digital root
        decimal_value = sum(int(digit) * (3 ** i) for i, digit in enumerate(reversed(ternary_str)))
        digital_root = (decimal_value - 1) % 9 + 1 if decimal_value > 0 else 0
        
        # Analyze distribution
        total_digits = len(ternary_str)
        void_ratio = counts[0] / total_digits if total_digits > 0 else 0
        expansive_ratio = counts[1] / total_digits if total_digits > 0 else 0
        contractive_ratio = counts[2] / total_digits if total_digits > 0 else 0
        
        # Determine dominant force
        dominant_force = max(counts, key=counts.get)
        
        # Check for balance between expansion and contraction
        is_balanced = counts[1] == counts[2]
        
        # Generate pattern analysis
        analysis = {
            "force_counts": counts,
            "digital_root": digital_root,
            "dominant_force": dominant_force,
            "dominant_force_name": self.FORCE_MEANINGS[dominant_force]["name"],
            "is_balanced": is_balanced,
            "void_ratio": void_ratio,
            "expansive_ratio": expansive_ratio,
            "contractive_ratio": contractive_ratio
        }
        
        # Generate textual analysis
        pattern_text = self._generate_pattern_text(ternary_str, analysis)
        analysis["pattern_text"] = pattern_text
        
        return analysis
    
    def _generate_pattern_text(self, ternary_str: str, analysis: Dict) -> str:
        """Generate a textual analysis of the ternary pattern.
        
        Args:
            ternary_str: The ternary string
            analysis: The pattern analysis dictionary
            
        Returns:
            Textual analysis of the pattern
        """
        counts = analysis["force_counts"]
        
        text = "### Force Distribution\n"
        text += f"- Void Force (0): {counts[0]} appearances\n"
        text += f"- Expansive Force (1): {counts[1]} appearances\n"
        text += f"- Contractive Force (2): {counts[2]} appearances\n\n"
        
        text += "### Numerical Force Balance\n"
        if analysis["is_balanced"]:
            text += "The Expansive and Contractive forces exist in perfect equilibrium, creating a harmonious cosmic structure.\n\n"
        elif counts[1] > counts[2]:
            text += "The Expansive forces predominate, creating a cosmic structure tending toward growth and outward movement.\n\n"
        else:
            text += "The Contractive forces predominate, creating a cosmic structure tending toward consolidation and inward movement.\n\n"
        
        text += "### Vibrational Signature\n"
        # Enhanced vibrational analysis with more detail
        text += f"The pattern of forces ({ternary_str}) manifests a multi-dimensional cosmic wave function with the following properties:\n\n"
        
        # Base frequency
        total_digits = len(ternary_str)
        # Scale the base frequency to be within human hearing range (20 Hz - 20,000 Hz)
        # Using logarithmic scaling to create more meaningful distribution
        raw_ratio = sum(int(d) for d in ternary_str) / (total_digits * 2)  # Normalize to 0-1 range
        base_frequency = 20 * (1000 ** raw_ratio)  # Exponential scaling from 20 Hz to 20 kHz
        text += f"**Base Frequency:** {base_frequency:.2f} Hz - "
        
        if base_frequency < 100:
            text += "A deep foundational tone in the sub-bass range, resonating with physical structures and earth energies.\n"
        elif base_frequency < 500:
            text += "A bass frequency that connects to bodily rhythms and fundamental life processes.\n"
        elif base_frequency < 2000:
            text += "A mid-range frequency that aligns with heart rhythms and emotional resonance patterns.\n"
        elif base_frequency < 8000:
            text += "A high-mid frequency that stimulates mental clarity and spiritual awareness.\n"
        else:
            text += "A high frequency that activates subtle energy fields and higher dimensional connections.\n"
        
        # Wave pattern
        text += "\n**Wave Morphology:** "
        if counts[0] > counts[1] + counts[2]:
            text += "This waveform exhibits extended periods of null-state equilibrium, punctuated by significant peaks of active force manifestation. "
            text += "The void-dominant pattern creates a cosmic field that serves as a gestation matrix for potential realities.\n"
        elif counts[0] == 0:
            text += "This waveform oscillates continuously between expansive and contractive poles without passing through neutral states. "
            text += "This creates an intense, dynamic cosmic field that catalyzes rapid manifestation cycles.\n"
        else:
            text += "This waveform displays a complex rhythmic structure alternating between all three force states. "
            text += "The resulting interference patterns generate a rich harmonic field capable of sustaining multi-dimensional phenomena.\n"
        
        # Harmonic structure
        harmonic_index = (counts[1] * 1.5 + counts[2] * 2.0 + counts[0] * 0.5) / total_digits
        text += f"\n**Harmonic Index:** {harmonic_index:.3f} - "
        if harmonic_index < 1.0:
            text += "Sub-harmonic frequencies dominate, creating receptive fields and introspective spaces.\n"
        elif harmonic_index < 1.5:
            text += "Balanced harmonics create stabilized fields suitable for sustained manifestation processes.\n"
        else:
            text += "Super-harmonic frequencies predominate, generating expansive, transformative energy fields.\n"
        
        # Resonance patterns
        digit_pairs = []
        for i in range(len(ternary_str)-1):
            digit_pairs.append(ternary_str[i:i+2])
            
        unique_pairs = len(set(digit_pairs))
        pattern_complexity = unique_pairs / len(digit_pairs) if len(digit_pairs) > 0 else 0
        
        text += f"\n**Pattern Complexity:** {pattern_complexity:.3f} - "
        if pattern_complexity < 0.4:
            text += "Highly repetitive patterns create strong resonant fields with focused, specific effects.\n"
        elif pattern_complexity < 0.7:
            text += "Moderate complexity generates balanced fields that support diverse manifestation potentials.\n"
        else:
            text += "High complexity produces chaotic-harmonic fields capable of quantum-level transformations.\n"
        
        # Vibrational nodes
        transitions = 0
        for i in range(len(ternary_str)-1):
            if ternary_str[i] != ternary_str[i+1]:
                transitions += 1
                
        transition_rate = transitions / (len(ternary_str)-1) if len(ternary_str) > 1 else 0
        
        text += f"\n**Transition Density:** {transition_rate:.3f} - "
        if transition_rate < 0.3:
            text += "Low transition density creates sustained vibrational states with profound depth of influence.\n"
        elif transition_rate < 0.7:
            text += "Moderate transition density establishes rhythmic oscillations that facilitate balanced energetic exchange.\n"
        else:
            text += "High transition density generates rapid vibrational shifts that catalyze transformation and transcendence.\n"
        
        # Cosmic resonance
        text += "\n**Cosmic Resonance:** This vibrational signature "
        
        if analysis["digital_root"] in [3, 6, 9]:
            text += f"harmonizes with the fundamental cosmic triad through its digital root of {analysis['digital_root']}. "
            text += "This creates direct channels to primary creative forces."
        elif analysis["digital_root"] in [1, 4, 7]:
            text += f"connects to initiatory cosmic principles through its digital root of {analysis['digital_root']}. "
            text += "This establishes pathways for new beginnings and breakthrough insights."
        else:  # 2, 5, 8
            text += f"aligns with stabilizing cosmic influences through its digital root of {analysis['digital_root']}. "
            text += "This grounds energy into constructive manifestation patterns."
        
        text += "\n"
        
        # Dimensional Resonance - new section
        text += "\n**Dimensional Resonance:** "
        
        # Calculate dimensional coefficients
        sequence_uniqueness = len(set(ternary_str)) / 3.0  # How many of the possible digits are used
        sequence_pattern = ""
        
        # Detect repeating patterns
        for pattern_length in range(1, len(ternary_str)//2 + 1):
            pattern = ternary_str[:pattern_length]
            pattern_count = 0
            
            for i in range(0, len(ternary_str) - pattern_length + 1, pattern_length):
                if ternary_str[i:i+pattern_length] == pattern:
                    pattern_count += 1
            
            if pattern_count > 1 and pattern_count * pattern_length > len(ternary_str) * 0.5:
                sequence_pattern = f"repeating pattern '{pattern}' detected"
                break
        
        # Golden ratio approximation check
        if counts[0] > 0 and counts[1] > 0:
            ratio_1_0 = counts[1] / counts[0] if counts[0] > 0 else 0
            golden_proximity = abs(ratio_1_0 - 1.618) / 1.618
            if golden_proximity < 0.1:
                text += "This pattern approximates the Golden Ratio (φ ≈ 1.618) in its relationship between Expansive and Void forces. "
                text += "This creates a naturally harmonious structure that resonates with fundamental growth patterns in the universe. "
        
        # Fibonacci sequence check
        fib_present = False
        if len(ternary_str) >= 5:
            runs = []
            current_digit = ternary_str[0]
            current_run = 1
            
            for i in range(1, len(ternary_str)):
                if ternary_str[i] == current_digit:
                    current_run += 1
                else:
                    runs.append(current_run)
                    current_digit = ternary_str[i]
                    current_run = 1
            
            runs.append(current_run)
            
            # Check for Fibonacci-like sequence in the run lengths
            if len(runs) >= 3:
                fib_like = 0
                for i in range(2, len(runs)):
                    if abs(runs[i] - (runs[i-1] + runs[i-2])) <= 1:  # Allow small variance
                        fib_like += 1
                
                if fib_like >= (len(runs) - 2) * 0.5:  # If at least half are Fibonacci-like
                    fib_present = True
        
        # Dimensional resonance text based on calculations
        if sequence_pattern:
            text += f"The {sequence_pattern}, establishing a strong connection to the fourth dimension through its cyclical nature. "
            text += "This creates temporal resonance that amplifies its effects across multiple timelines.\n"
        elif fib_present:
            text += "This pattern contains segments that follow Fibonacci-like progression, connecting it to the spiral growth patterns "
            text += "found throughout nature. This creates a multi-dimensional resonance that facilitates natural evolution and transformation.\n"
        elif sequence_uniqueness < 0.5:
            text += "The limited variety of force states creates a concentrated frequency that penetrates deeply into the first and second dimensions. "
            text += "This generates powerful but narrowly focused effects within the material plane.\n"
        elif analysis["is_balanced"] and transition_rate > 0.5:
            text += "The balanced forces combined with frequent transitions create a fifth-dimensional resonance pattern. "
            text += "This establishes connection points across multiple reality streams and facilitates quantum possibility convergence.\n"
        else:
            text += "This pattern creates a stable third-dimensional resonance field that anchors cosmic forces into physical manifestation. "
            text += "The interaction between dimensions is smooth and supports gradual transformation processes.\n"

        # Force Geometry Analysis - new section
        text += "\n**Force Geometry:** "
        
        # Calculate geometry coefficients
        force_succession = []
        for i in range(len(ternary_str)-1):
            force_succession.append(int(ternary_str[i+1]) - int(ternary_str[i]))
        
        # Convert to directional movements
        directions = []
        for change in force_succession:
            if change == 0:
                directions.append("stable")
            elif change in [1, -2]:  # Increasing force (0->1, 1->2, or 2->0 with wraparound)
                directions.append("clockwise")
            else:  # change in [-1, 2] - Decreasing force (1->0, 2->1, or 0->2 with wraparound)
                directions.append("counterclockwise")
        
        # Count directional changes
        clockwise_count = directions.count("clockwise")
        counterclockwise_count = directions.count("counterclockwise")
        stable_count = directions.count("stable")
        
        # Calculate angular momentum
        angular_momentum = (clockwise_count - counterclockwise_count) / len(directions) if len(directions) > 0 else 0
        
        # Calculate symmetry markers
        symmetry_score = 0
        if len(ternary_str) >= 4:
            # Check for palindrome-like patterns
            for i in range(len(ternary_str) // 2):
                if ternary_str[i] == ternary_str[-(i+1)]:
                    symmetry_score += 1
            symmetry_score = symmetry_score / (len(ternary_str) // 2) if len(ternary_str) // 2 > 0 else 0
        
        # Generate force geometry description
        if abs(angular_momentum) > 0.6:
            text += f"This pattern exhibits strong {'clockwise' if angular_momentum > 0 else 'counterclockwise'} rotational momentum "
            text += f"with an angular coefficient of {abs(angular_momentum):.2f}. "
            if angular_momentum > 0:
                text += "The predominant clockwise movement creates accelerating manifestation currents that bring potentials into form. "
            else:
                text += "The predominant counterclockwise movement creates dissolving currents that return forms to potential states. "
        elif abs(angular_momentum) > 0.2:
            text += f"This pattern shows moderate {'clockwise' if angular_momentum > 0 else 'counterclockwise'} motion "
            text += f"with an angular coefficient of {abs(angular_momentum):.2f}. "
            text += "This creates balanced cycles of manifestation and dissolution. "
        else:
            text += "This pattern exhibits balanced bidirectional movement, creating complex vortex structures "
            text += "that simultaneously manifest and dissolve forms across multiple dimensions. "
        
        if symmetry_score > 0.7:
            text += f"\nThe pattern displays remarkable symmetry (coefficient: {symmetry_score:.2f}), creating a stable geometric framework "
            text += "that resonates with universal mirror principles. This amplifies its effects through harmonic reinforcement."
        elif symmetry_score > 0.3:
            text += f"\nThe pattern contains elements of symmetry (coefficient: {symmetry_score:.2f}), establishing anchor points "
            text += "that create predictable nodes of manifestation within an otherwise dynamic system."
        
        if stable_count / len(directions) > 0.3 if len(directions) > 0 else 0:
            text += f"\nThe sequence contains {stable_count} stable transitions, creating focal points of concentrated force "
            text += "that serve as nucleation sites for crystallizing specific manifestation outcomes."
        
        text += "\n"
        
        text += "### Cosmic Mathematics\n"
        text += f"The digital root is {analysis['digital_root']}, "
        
        if analysis['digital_root'] == 3:
            text += "representing the trinity principle and fundamental creative forces."
        elif analysis['digital_root'] == 6:
            text += "representing harmony and balance between opposing cosmic forces."
        elif analysis['digital_root'] == 9:
            text += "representing cosmic completion and the culmination of a force cycle."
        else:
            text += f"which resonates with the numerical vibration of {analysis['digital_root']} in cosmic mathematics."
        
        text += "\n\n"
        
        text += "### Force Dynamics\n"
        text += "This ternary structure reveals a cosmic system where:\n\n"
        
        if counts[0] > 0:
            text += f"1. Equilibrium forces provide {counts[0]/len(ternary_str)*100:.1f}% of the overall structure\n"
        
        if counts[1] > 0:
            text += f"2. Expansive forces create outward movement across {counts[1]/len(ternary_str)*100:.1f}% of the system\n"
        
        if counts[2] > 0:
            text += f"3. Contractive forces balance with inward movement in {counts[2]/len(ternary_str)*100:.1f}% of positions\n"
        
        if analysis["is_balanced"] and counts[1] > 0:
            text += "4. The overall system maintains perfect balance between expansion and contraction\n"
        
        return text


class CosmicForceAnalysisPanel(QWidget):
    """Panel for analyzing cosmic forces in ternary numbers."""
    
    def __init__(self, parent=None):
        """Initialize the Cosmic Force Analysis panel.
        
        Args:
            parent: The parent widget
        """
        super().__init__(parent)
        
        # Create interpreter
        self.interpreter = CosmicForceInterpreter()
        
        # Initialize the UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title = QLabel("Cosmic Force Analysis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # Description
        description = QLabel(
            "This tool analyzes the cosmic force dynamics in ternary numbers. "
            "Enter a decimal number to see how it manifests as a pattern of "
            "Void (0), Expansive (1), and Contractive (2) forces across different cosmic positions."
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
        self.analyze_button = QPushButton("Analyze Cosmic Forces")
        self.analyze_button.clicked.connect(self._analyze_number)
        input_layout.addWidget(self.analyze_button, 0, 2)
        
        # Help button
        self.help_button = QPushButton("?")
        self.help_button.setToolTip("Learn about calculation methods")
        self.help_button.setFixedSize(30, 30)  # Make it a small circular button
        self.help_button.setStyleSheet("""
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
        """)
        self.help_button.clicked.connect(self._show_help_dialog)
        input_layout.addWidget(self.help_button, 0, 3)
        
        # Ternary display
        input_layout.addWidget(QLabel("Ternary Form:"), 1, 0)
        self.ternary_display = QLabel("")
        self.ternary_display.setStyleSheet("font-family: monospace; font-weight: bold; font-size: 14px;")
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
        self.position_group = QGroupBox("Force Analysis by Position")
        position_layout = QVBoxLayout(self.position_group)
        self.position_layout = position_layout
        self.results_layout.addWidget(self.position_group)
        
        # Overall pattern analysis
        self.pattern_group = QGroupBox("Cosmic Pattern Analysis")
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
        """Analyze the input number and display cosmic force interpretation."""
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
        """Display the position-by-position force analysis.
        
        Args:
            ternary_str: The ternary string to analyze
        """
        # Clear previous content
        for i in reversed(range(self.position_layout.count())): 
            widget = self.position_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Create position frames in reverse order (from highest position to lowest)
        for position in range(len(ternary_str), 0, -1):
            # Index from the right (lowest position)
            index = len(ternary_str) - position
            digit = int(ternary_str[index])
            
            interpretation = self.interpreter.interpret_digit(digit, position)
            
            # Create frame for this position
            position_frame = QFrame()
            position_frame.setFrameShape(QFrame.Shape.StyledPanel)
            position_frame.setFrameShadow(QFrame.Shadow.Raised)
            
            # Color code based on digit
            if digit == 0:
                position_frame.setStyleSheet("background-color: #E6F3FF; border: 1px solid #99CCFF;")  # Light blue for Void
            elif digit == 1:
                position_frame.setStyleSheet("background-color: #FFF0E6; border: 1px solid #FFCC99;")  # Light orange for Expansive
            else:  # digit == 2
                position_frame.setStyleSheet("background-color: #E6FFE6; border: 1px solid #99FF99;")  # Light green for Contractive
            
            frame_layout = QVBoxLayout(position_frame)
            
            # Position header
            header = QLabel(f"Position {position}: {interpretation['position_name']} (3^{position-1} = {interpretation['position_value']})")
            header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            frame_layout.addWidget(header)
            
            # Force info
            force_info = QLabel(f"Force: {digit} - {interpretation['force_name']}")
            force_info.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            frame_layout.addWidget(force_info)
            
            # Force description
            description = QLabel(interpretation['force_description'])
            description.setWordWrap(True)
            frame_layout.addWidget(description)
            
            # Specific interpretation
            specific = QLabel(interpretation['specific_interpretation'])
            specific.setWordWrap(True)
            frame_layout.addWidget(specific)
            
            self.position_layout.addWidget(position_frame)
    
    def _display_pattern_analysis(self, ternary_str: str):
        """Display the overall pattern analysis.
        
        Args:
            ternary_str: The ternary string to analyze
        """
        analysis = self.interpreter.analyze_pattern(ternary_str)
        self.pattern_text.setMarkdown(analysis["pattern_text"])
    
    def _show_help_dialog(self):
        """Show a dialog with detailed explanation of the calculation methods."""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Cosmic Force Analysis - Calculation Methods")
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
        overview_text.setMarkdown("""
        # Cosmic Force Analysis Overview
        
        This tool analyzes ternary numbers (base-3 numbers consisting of digits 0, 1, and 2) 
        through the lens of cosmic force theory. In this system, each ternary digit represents 
        a specific force state:
        
        - **0 (Void Force)**: Represents equilibrium, neutrality, and undifferentiated potential.
        - **1 (Expansive Force)**: Represents outward movement, growth, and differentiation.
        - **2 (Contractive Force)**: Represents inward movement, concentration, and densification.
        
        The analysis interprets patterns within ternary numbers to reveal the interplay of these 
        cosmic forces across various dimensions and scales. The resulting insights offer perspectives 
        on energy dynamics, manifestation patterns, and cosmic resonance.
        
        ## Key Analysis Components
        
        - **Position Analysis**: Interprets each digit based on its position value (3^n)
        - **Vibrational Signature**: Analyzes the wave-like properties of the number
        - **Dimensional Resonance**: Identifies connections to different dimensional planes
        - **Force Geometry**: Examines rotational dynamics and symmetry patterns
        - **Cosmic Mathematics**: Relates the number to universal mathematical principles
        """)
        overview_layout.addWidget(overview_text)
        tab_widget.addTab(overview_tab, "Overview")
        
        # Vibrational Analysis tab
        vibration_tab = QWidget()
        vibration_layout = QVBoxLayout(vibration_tab)
        vibration_text = QTextEdit()
        vibration_text.setReadOnly(True)
        vibration_text.setMarkdown("""
        # Vibrational Signature Calculations
        
        The Vibrational Signature section analyzes the wave-like properties of the ternary number. 
        Each calculation provides insight into different aspects of the cosmic vibration.
        
        ## Base Frequency
        
        **Formula**: `base_frequency = (sum of digits / total digits) * 3.0`
        
        This calculation determines the fundamental vibrational tone of the number. The multiplication 
        by 3.0 scales the result to correspond with the ternary number system. The base frequency 
        indicates the overall energetic intensity of the number and its resonance level.
        
        ## Harmonic Index
        
        **Formula**: `harmonic_index = (counts[1] * 1.5 + counts[2] * 2.0 + counts[0] * 0.5) / total_digits`
        
        This weighted average assigns different values to each force type:
        - Void (0) = 0.5 (sub-harmonic)
        - Expansive (1) = 1.5 (intermediate harmonic)
        - Contractive (2) = 2.0 (super-harmonic)
        
        The resulting index indicates whether the pattern tends toward sub-harmonic (receptive), 
        balanced harmonic, or super-harmonic (transformative) frequencies.
        
        ## Pattern Complexity
        
        **Formula**: `complexity = unique_digit_pairs / total_digit_pairs`
        
        This calculation examines all adjacent digit pairs in the sequence and determines the ratio 
        of unique pairs to total pairs. Higher values indicate more complex patterns with less 
        repetition, while lower values suggest more repetitive structures.
        
        ## Transition Density
        
        **Formula**: `transition_rate = transitions / (length - 1)`
        
        This measures how frequently the digits change throughout the sequence. A higher transition 
        rate indicates a more dynamic pattern with rapid shifts between force states, while a lower 
        rate suggests longer periods of consistent force expression.
        """)
        vibration_layout.addWidget(vibration_text)
        tab_widget.addTab(vibration_tab, "Vibrational Analysis")
        
        # Dimensional Resonance tab
        dimension_tab = QWidget()
        dimension_layout = QVBoxLayout(dimension_tab)
        dimension_text = QTextEdit()
        dimension_text.setReadOnly(True)
        dimension_text.setMarkdown("""
        # Dimensional Resonance Calculations
        
        The Dimensional Resonance section analyzes how the ternary pattern connects to and 
        influences different dimensional planes.
        
        ## Sequence Uniqueness
        
        **Formula**: `sequence_uniqueness = distinct_digits_used / 3.0`
        
        This calculation determines how many of the possible ternary digits (0, 1, 2) appear 
        in the number. Lower uniqueness values indicate more concentrated energy patterns that 
        tend to affect lower dimensions more powerfully.
        
        ## Repeating Pattern Detection
        
        The analysis searches for repeating sub-patterns within the ternary sequence. When a 
        repeating pattern constitutes more than 50% of the sequence, it's identified as cyclical. 
        Cyclical patterns create resonance with the 4th dimension (time) and can influence 
        temporal dynamics.
        
        ## Golden Ratio Proximity
        
        **Formula**: `golden_proximity = |ratio_of_1_to_0 - 1.618| / 1.618`
        
        This calculation checks if the ratio between Expansive (1) and Void (0) forces approximates 
        the golden ratio (φ ≈ 1.618). Patterns matching this ratio resonate with natural growth and 
        universal harmonic systems.
        
        ## Fibonacci Sequence Detection
        
        The analysis checks if the sequence contains Fibonacci-like patterns by examining the runs 
        of identical digits. When consecutive runs follow a pattern where each run approximately equals 
        the sum of the two previous runs, it creates a spiral-like energy pattern that facilitates 
        evolution and transformation.
        """)
        dimension_layout.addWidget(dimension_text)
        tab_widget.addTab(dimension_tab, "Dimensional Resonance")
        
        # Force Geometry tab
        geometry_tab = QWidget()
        geometry_layout = QVBoxLayout(geometry_tab)
        geometry_text = QTextEdit()
        geometry_text.setReadOnly(True)
        geometry_text.setMarkdown("""
        # Force Geometry Calculations
        
        The Force Geometry section analyzes the directional flow and structural properties of the 
        cosmic forces within the ternary pattern.
        
        ## Force Succession
        
        The analysis tracks the change between consecutive digits in the sequence:
        
        **Formula**: `succession = ternary_digit[i+1] - ternary_digit[i]`
        
        These successions are then classified as:
        - **Stable**: No change (0)
        - **Clockwise**: Increasing force (0→1, 1→2, or 2→0 with wraparound)
        - **Counterclockwise**: Decreasing force (1→0, 2→1, or 0→2 with wraparound)
        
        ## Angular Momentum
        
        **Formula**: `angular_momentum = (clockwise_count - counterclockwise_count) / total_directions`
        
        This calculation determines the overall rotational tendency of the force pattern. 
        Positive values indicate clockwise momentum (increasing manifestation), negative values 
        indicate counterclockwise momentum (dissolution), and values near zero indicate balanced 
        bidirectional movement.
        
        ## Symmetry Score
        
        **Formula**: `symmetry_score = matching_positions / (length / 2)`
        
        This calculation checks for palindromic patterns by comparing digits equidistant from the center. 
        Higher symmetry scores indicate more mirrored patterns, which create stable geometric frameworks 
        and harmonic reinforcement fields.
        
        ## Stable Transitions
        
        The analysis counts transitions where the digit remains unchanged ("stable" successions). 
        These stable points create focal regions of concentrated force, serving as anchors within 
        the overall pattern. A high proportion of stable transitions creates stronger manifestation 
        outcomes in specific areas.
        """)
        geometry_layout.addWidget(geometry_text)
        tab_widget.addTab(geometry_tab, "Force Geometry")
        
        # Cosmic Mathematics tab
        mathematics_tab = QWidget()
        mathematics_layout = QVBoxLayout(mathematics_tab)
        mathematics_text = QTextEdit()
        mathematics_text.setReadOnly(True)
        mathematics_text.setMarkdown("""
        # Cosmic Mathematics Calculations
        
        The Cosmic Mathematics section relates the ternary pattern to universal numerical principles.
        
        ## Digital Root
        
        **Formula**: `digital_root = (decimal_value - 1) % 9 + 1` (if decimal_value > 0, else 0)
        
        The digital root is calculated by first converting the ternary number to its decimal equivalent,
        then applying the standard digital root formula (recursive digit sum until a single digit remains).
        
        The digital root reveals the fundamental numerical essence of the pattern:
        
        - **Digital Roots 3, 6, 9**: Connect to the cosmic triad principles, representing creation, 
          balance, and completion respectively.
        - **Digital Roots 1, 4, 7**: Connect to initiatory principles, representing beginnings, 
          foundations, and spiritual insights respectively.
        - **Digital Roots 2, 5, 8**: Connect to stabilizing principles, representing duality, 
          change, and material manifestation respectively.
        
        ## Force Distribution
        
        **Formula**: `force_percentage = (count_of_digit / total_digits) * 100`
        
        This calculation determines the percentage composition of each force type within the pattern.
        The relative proportions reveal the pattern's overall tendencies and dominant influences.
        
        ## Balance Assessment
        
        The analysis checks if the Expansive (1) and Contractive (2) forces exist in equal numbers.
        Perfect balance creates harmonious systems that can sustain complex interactions without 
        collapsing toward either extreme.
        """)
        mathematics_layout.addWidget(mathematics_text)
        tab_widget.addTab(mathematics_tab, "Cosmic Mathematics")
        
        # Position Analysis tab
        position_tab = QWidget()
        position_layout = QVBoxLayout(position_tab)
        position_text = QTextEdit()
        position_text.setReadOnly(True)
        position_text.setMarkdown("""
        # Position Analysis Calculations
        
        The Position Analysis examines each digit in context of its position within the ternary number.
        
        ## Position Value
        
        **Formula**: `position_value = 3^(position-1)`
        
        Each position in a ternary number has a mathematical value based on powers of 3. These 
        values correspond to different scales of cosmic influence:
        
        - **Position 1** (3^0 = 1): Immediate Force - affecting current, direct experiences
        - **Position 2** (3^1 = 3): Daily Force - affecting short-term patterns
        - **Position 3** (3^2 = 9): Lunar Force - affecting monthly cycles
        - **Position 4** (3^3 = 27): Annual Force - affecting yearly patterns
        - **Position 5** (3^4 = 81): Life Phase Force - affecting multi-year periods
        - **Position 6** (3^5 = 243): Life Path Force - affecting lifetime arcs
        - **Position 7** (3^6 = 729): Generational Force - affecting multi-generational patterns
        - **Position 8** (3^7 = 2187): Collective Force - affecting societal patterns
        - **Position 9** (3^8 = 6561): Universal Force - affecting cosmic cycles
        
        ## Force Interpretation
        
        Each position contains a specific force type (0, 1, or 2), which is interpreted based on:
        
        1. The inherent quality of the force (Void, Expansive, or Contractive)
        2. The position's scale of influence (positions 1-3 affect foundational levels, 4-6 affect 
           intermediate levels, and 7-9 affect cosmic levels)
        3. The interaction between the force type and position level
        
        The combined interpretation reveals how cosmic forces manifest across multiple scales of 
        reality simultaneously, creating a holographic system where each part contains aspects of 
        the whole pattern.
        """)
        position_layout.addWidget(position_text)
        tab_widget.addTab(position_tab, "Position Analysis")
        
        # Add the tab widget to the main layout
        main_layout.addWidget(tab_widget)
        
        # Show the dialog
        help_dialog.exec()


if __name__ == "__main__":
    """Simple demonstration of the Cosmic Force Analysis panel."""
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = CosmicForceAnalysisPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec()) 