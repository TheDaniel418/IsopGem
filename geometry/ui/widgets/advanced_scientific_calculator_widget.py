"""
Advanced Scientific Calculator Widget for IsopGem's Geometry module.

This module provides the UI widget for the Advanced Scientific Calculator,
implementing a comprehensive calculator interface with a wide range of
mathematical functions for use in geometry and general calculations.
"""

import math
from typing import Dict, Optional, List, Tuple, Union, Any

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QKeyEvent
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.advanced_scientific_calculator import AdvancedScientificCalculator


class CalculatorButton(QPushButton):
    """Custom button class for calculator buttons."""
    
    def __init__(self, text: str, category: str = "default", parent=None):
        """Initialize a calculator button.
        
        Args:
            text: Text to display on the button
            category: Button category determines styling
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(40, 40)
        
        # Apply styling based on category
        self._apply_styling(category)
        
    def _apply_styling(self, category: str) -> None:
        """Apply styling based on button category.
        
        Args:
            category: Button category
        """
        base_style = """
            QPushButton {
                border: 1px solid #bbb;
                border-radius: 4px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #ddd;
            }
        """
        
        category_styles = {
            "number": """
                background-color: #ffffff;
                color: #000000;
            """,
            "operator": """
                background-color: #f0f0f0;
                color: #0000cc;
            """,
            "function": """
                background-color: #e0e0e0;
                color: #008800;
            """,
            "memory": """
                background-color: #e8e8ff;
                color: #880000;
            """,
            "constant": """
                background-color: #fff0e0;
                color: #885500;
            """,
            "clear": """
                background-color: #ffeeee;
                color: #cc0000;
            """,
            "equals": """
                background-color: #d0e8ff;
                color: #0000cc;
                font-size: 14px;
                font-weight: bold;
            """
        }
        
        # Apply the base style plus category-specific style
        style = base_style
        if category in category_styles:
            style += category_styles[category]
        else:
            # Default style if category not found
            style += """
                background-color: #f8f8f8;
                color: #333333;
            """
            
        self.setStyleSheet(style)


class AdvancedScientificCalculatorWidget(QWidget):
    """Widget implementing the Advanced Scientific Calculator UI."""
    
    # Signal emitted when calculation is performed
    calculation_performed = pyqtSignal(str, float)
    
    def __init__(self, parent=None):
        """Initialize the calculator widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create calculator backend
        self.calculator = AdvancedScientificCalculator()
        
        # Calculator state
        self.current_input = ""
        self.result = 0.0
        self.memory = 0.0
        self.calculation_history: List[str] = []
        self.in_calculation_mode = False
        self.last_button_was_operator = False
        self.angle_mode = "DEG"  # DEG, RAD, GRAD
        
        # Initialize the UI
        self._init_ui()
        
        # Allow the widget to receive keyboard focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus() # Optionally set focus immediately
        
        logger.debug("AdvancedScientificCalculatorWidget initialized")
        
    def _init_ui(self) -> None:
        """Initialize the calculator UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        
        # Display area
        self._setup_display_area(main_layout)
        
        # Tab widget for different calculator modes
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self._setup_basic_tab()
        self._setup_scientific_tab()
        self._setup_matrix_tab()
        self._setup_constants_tab()
        self._setup_conversion_tab()
        
        # History and memory panel at bottom
        self._setup_history_panel(main_layout)
        
    def _setup_display_area(self, layout: QVBoxLayout) -> None:
        """Set up the calculator display area.
        
        Args:
            layout: Layout to add the display area to
        """
        # Group for display
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout(display_group)
        
        # Expression display (shows current calculation)
        self.expression_display = QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.expression_display.setStyleSheet("""
            QLineEdit {
                background-color: #f8f8ff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
                color: #555;
            }
        """)
        display_layout.addWidget(self.expression_display)
        
        # Result display
        self.result_display = QLineEdit("0")
        self.result_display.setReadOnly(True)
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        font = QFont("Arial", 18, QFont.Weight.Bold)
        self.result_display.setFont(font)
        self.result_display.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #bbb;
                border-radius: 4px;
                padding: 10px;
                color: #000;
            }
        """)
        display_layout.addWidget(self.result_display)
        
        # Mode indicators (horizontal layout)
        mode_layout = QHBoxLayout()
        
        # Angle mode group
        self.angle_mode_group = QButtonGroup(self)
        
        # Degree mode (default)
        self.deg_radio = QRadioButton("DEG")
        self.deg_radio.setChecked(True)
        self.deg_radio.toggled.connect(lambda: self._set_angle_mode("DEG"))
        self.angle_mode_group.addButton(self.deg_radio)
        mode_layout.addWidget(self.deg_radio)
        
        # Radian mode
        self.rad_radio = QRadioButton("RAD")
        self.rad_radio.toggled.connect(lambda: self._set_angle_mode("RAD"))
        self.angle_mode_group.addButton(self.rad_radio)
        mode_layout.addWidget(self.rad_radio)
        
        # Gradian mode
        self.grad_radio = QRadioButton("GRAD")
        self.grad_radio.toggled.connect(lambda: self._set_angle_mode("GRAD"))
        self.angle_mode_group.addButton(self.grad_radio)
        mode_layout.addWidget(self.grad_radio)
        
        # Add stretch to push other elements to the right
        mode_layout.addStretch()
        
        # Add memory indicator
        self.memory_indicator = QLabel("M: 0")
        self.memory_indicator.setStyleSheet("color: #990000;")
        mode_layout.addWidget(self.memory_indicator)
        
        # Add mode layout to display layout
        display_layout.addLayout(mode_layout)
        
        # Add display group to main layout
        layout.addWidget(display_group)
        
    def _setup_basic_tab(self) -> None:
        """Set up the basic calculator tab."""
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Button grid
        button_grid = QGridLayout()
        button_grid.setSpacing(5)
        
        # Row 0
        button_grid.addWidget(CalculatorButton("C", "clear"), 0, 0)
        button_grid.addWidget(CalculatorButton("CE", "clear"), 0, 1)
        button_grid.addWidget(CalculatorButton("⌫", "clear"), 0, 2)
        button_grid.addWidget(CalculatorButton("÷", "operator"), 0, 3)
        
        # Row 1
        button_grid.addWidget(CalculatorButton("7", "number"), 1, 0)
        button_grid.addWidget(CalculatorButton("8", "number"), 1, 1)
        button_grid.addWidget(CalculatorButton("9", "number"), 1, 2)
        button_grid.addWidget(CalculatorButton("×", "operator"), 1, 3)
        
        # Row 2
        button_grid.addWidget(CalculatorButton("4", "number"), 2, 0)
        button_grid.addWidget(CalculatorButton("5", "number"), 2, 1)
        button_grid.addWidget(CalculatorButton("6", "number"), 2, 2)
        button_grid.addWidget(CalculatorButton("-", "operator"), 2, 3)
        
        # Row 3
        button_grid.addWidget(CalculatorButton("1", "number"), 3, 0)
        button_grid.addWidget(CalculatorButton("2", "number"), 3, 1)
        button_grid.addWidget(CalculatorButton("3", "number"), 3, 2)
        button_grid.addWidget(CalculatorButton("+", "operator"), 3, 3)
        
        # Row 4
        button_grid.addWidget(CalculatorButton("±", "operator"), 4, 0)
        button_grid.addWidget(CalculatorButton("0", "number"), 4, 1)
        button_grid.addWidget(CalculatorButton(".", "number"), 4, 2)
        button_grid.addWidget(CalculatorButton("=", "equals"), 4, 3)
        
        # Memory buttons
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(CalculatorButton("MC", "memory"))  # Memory Clear
        memory_layout.addWidget(CalculatorButton("MR", "memory"))  # Memory Recall
        memory_layout.addWidget(CalculatorButton("M+", "memory"))  # Memory Add
        memory_layout.addWidget(CalculatorButton("M-", "memory"))  # Memory Subtract
        memory_layout.addWidget(CalculatorButton("MS", "memory"))  # Memory Store
        
        # Add layouts to basic tab
        basic_layout.addLayout(button_grid)
        basic_layout.addLayout(memory_layout)
        
        # Connect buttons to handlers
        self._connect_number_buttons(basic_tab)
        self._connect_operator_buttons(basic_tab)
        self._connect_function_buttons(basic_tab)
        self._connect_memory_buttons(basic_tab)
        
        # Add tab to tab widget
        self.tab_widget.addTab(basic_tab, "Basic")
        
    def _setup_scientific_tab(self) -> None:
        """Set up the scientific calculator tab."""
        scientific_tab = QWidget()
        scientific_layout = QVBoxLayout(scientific_tab)
        
        # Button grid for scientific functions
        sci_grid = QGridLayout()
        sci_grid.setSpacing(5)
        
        # Row 0
        sci_grid.addWidget(CalculatorButton("x²", "function"), 0, 0)
        sci_grid.addWidget(CalculatorButton("x³", "function"), 0, 1)
        sci_grid.addWidget(CalculatorButton("xʸ", "function"), 0, 2)
        sci_grid.addWidget(CalculatorButton("ex", "function"), 0, 3)
        sci_grid.addWidget(CalculatorButton("10x", "function"), 0, 4)
        
        # Row 1
        sci_grid.addWidget(CalculatorButton("√", "function"), 1, 0)
        sci_grid.addWidget(CalculatorButton("∛", "function"), 1, 1)
        sci_grid.addWidget(CalculatorButton("y√x", "function"), 1, 2)
        sci_grid.addWidget(CalculatorButton("ln", "function"), 1, 3)
        sci_grid.addWidget(CalculatorButton("log", "function"), 1, 4)
        
        # Row 2
        sci_grid.addWidget(CalculatorButton("sin", "function"), 2, 0)
        sci_grid.addWidget(CalculatorButton("cos", "function"), 2, 1)
        sci_grid.addWidget(CalculatorButton("tan", "function"), 2, 2)
        sci_grid.addWidget(CalculatorButton("sec", "function"), 2, 3)
        sci_grid.addWidget(CalculatorButton("csc", "function"), 2, 4)
        
        # Row 3
        sci_grid.addWidget(CalculatorButton("sin⁻¹", "function"), 3, 0)
        sci_grid.addWidget(CalculatorButton("cos⁻¹", "function"), 3, 1)
        sci_grid.addWidget(CalculatorButton("tan⁻¹", "function"), 3, 2)
        sci_grid.addWidget(CalculatorButton("sinh", "function"), 3, 3)
        sci_grid.addWidget(CalculatorButton("cosh", "function"), 3, 4)
        
        # Row 4
        sci_grid.addWidget(CalculatorButton("tanh", "function"), 4, 0)
        sci_grid.addWidget(CalculatorButton("π", "constant"), 4, 1)
        sci_grid.addWidget(CalculatorButton("e", "constant"), 4, 2)
        sci_grid.addWidget(CalculatorButton("φ", "constant"), 4, 3)  # Golden ratio
        sci_grid.addWidget(CalculatorButton("γ", "constant"), 4, 4)  # Euler–Mascheroni constant
        
        # Row 5
        sci_grid.addWidget(CalculatorButton("(", "operator"), 5, 0)
        sci_grid.addWidget(CalculatorButton(")", "operator"), 5, 1)
        sci_grid.addWidget(CalculatorButton("n!", "function"), 5, 2)
        sci_grid.addWidget(CalculatorButton("%", "operator"), 5, 3)
        sci_grid.addWidget(CalculatorButton("mod", "operator"), 5, 4)
        
        # Add to layout
        scientific_layout.addLayout(sci_grid)
        
        # Connect scientific buttons
        self._connect_scientific_buttons(scientific_tab)
        
        # Add tab to tab widget
        self.tab_widget.addTab(scientific_tab, "Scientific")
        
    def _setup_matrix_tab(self) -> None:
        """Set up the matrix and vector calculator tab."""
        matrix_tab = QWidget()
        matrix_layout = QVBoxLayout(matrix_tab)
        
        # Matrix size selection
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Matrix Size: "))
        
        self.matrix_size_combo = QComboBox()
        self.matrix_size_combo.addItems(["2x2", "3x3", "4x4"])
        self.matrix_size_combo.currentTextChanged.connect(self._update_matrix_size)
        size_layout.addWidget(self.matrix_size_combo)
        
        # Matrix input area (stacked widget for different sizes)
        self.matrix_stack = QStackedWidget()
        
        # Create widgets for different matrix sizes
        for size in ["2x2", "3x3", "4x4"]:
            matrix_widget = self._create_matrix_input(size)
            self.matrix_stack.addWidget(matrix_widget)
        
        # Matrix operations
        op_layout = QHBoxLayout()
        op_layout.addWidget(CalculatorButton("Determinant", "function"))
        op_layout.addWidget(CalculatorButton("Inverse", "function"))
        op_layout.addWidget(CalculatorButton("Transpose", "function"))
        
        # Vector operations
        vec_layout = QHBoxLayout()
        vec_layout.addWidget(CalculatorButton("Dot Product", "function"))
        vec_layout.addWidget(CalculatorButton("Cross Product", "function"))
        vec_layout.addWidget(CalculatorButton("Magnitude", "function"))
        
        # Add to layout
        matrix_layout.addLayout(size_layout)
        matrix_layout.addWidget(self.matrix_stack)
        matrix_layout.addLayout(op_layout)
        matrix_layout.addLayout(vec_layout)
        
        # Connect matrix/vector buttons
        self._connect_matrix_vector_buttons(matrix_tab)
        
        # Add tab to tab widget
        self.tab_widget.addTab(matrix_tab, "Matrix/Vector")
        
    def _create_matrix_input(self, size: str) -> QWidget:
        """Create matrix input grid for the specified size.
        
        Args:
            size: Matrix size string (e.g. "2x2")
            
        Returns:
            Widget containing the matrix input grid
        """
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Parse size
        dim = int(size[0])
        
        # Create grid of input fields
        self.matrix_inputs = []
        for i in range(dim):
            row_inputs = []
            for j in range(dim):
                input_field = QLineEdit("0")
                input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
                input_field.setFixedWidth(60)
                layout.addWidget(input_field, i, j)
                row_inputs.append(input_field)
            self.matrix_inputs.append(row_inputs)
        
        return widget
        
    def _update_matrix_size(self, size: str) -> None:
        """Update matrix input area when size changes.
        
        Args:
            size: Matrix size string (e.g. "2x2")
        """
        # Set the appropriate widget in the stack
        if size == "2x2":
            self.matrix_stack.setCurrentIndex(0)
        elif size == "3x3":
            self.matrix_stack.setCurrentIndex(1)
        elif size == "4x4":
            self.matrix_stack.setCurrentIndex(2)
            
    def _setup_constants_tab(self) -> None:
        """Set up the constants and unit conversion tab."""
        constants_tab = QWidget()
        constants_layout = QVBoxLayout(constants_tab)
        
        # Constants scroll area
        constants_scroll = QScrollArea()
        constants_scroll.setWidgetResizable(True)
        constants_widget = QWidget()
        constants_grid = QGridLayout(constants_widget)
        
        # Add constants buttons
        constants = [
            ("π (Pi)", "π"), 
            ("e (Euler's number)", "e"), 
            ("φ (Golden ratio)", "φ"), 
            ("γ (Euler-Mascheroni)", "γ"),
            ("c (Speed of light)", "c"),
            ("G (Gravitation)", "G"),
            ("h (Planck)", "h"),
            ("ℏ (Reduced Planck)", "ℏ"),
            ("ε₀ (Electric const.)", "ε0"),
            ("μ₀ (Magnetic const.)", "μ0"),
            ("k (Boltzmann)", "k"),
            ("Nₐ (Avogadro)", "NA"),
            ("R (Gas constant)", "R")
        ]
        
        row = 0
        col = 0
        for name, symbol in constants:
            const_btn = QPushButton(f"{name}")
            const_btn.setToolTip(f"Insert {symbol} constant")
            const_btn.clicked.connect(lambda _, s=symbol: self._insert_constant(s))
            constants_grid.addWidget(const_btn, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        constants_scroll.setWidget(constants_widget)
        constants_layout.addWidget(constants_scroll)
        
        # Add tab to tab widget
        self.tab_widget.addTab(constants_tab, "Constants")
        
    def _setup_conversion_tab(self) -> None:
        """Set up the unit conversion tab."""
        conversion_tab = QWidget()
        conversion_layout = QVBoxLayout(conversion_tab)
        
        # Conversion types
        conv_type_layout = QHBoxLayout()
        conv_type_layout.addWidget(QLabel("Conversion Type: "))
        
        self.conversion_type_combo = QComboBox()
        self.conversion_type_combo.addItems(["Length", "Area", "Volume", "Mass", "Temperature", "Angle"])
        self.conversion_type_combo.currentTextChanged.connect(self._update_conversion_units)
        conv_type_layout.addWidget(self.conversion_type_combo)
        
        # Conversion direction
        from_to_layout = QGridLayout()
        from_to_layout.addWidget(QLabel("From:"), 0, 0)
        self.from_unit_combo = QComboBox()
        from_to_layout.addWidget(self.from_unit_combo, 0, 1)
        
        from_to_layout.addWidget(QLabel("To:"), 1, 0)
        self.to_unit_combo = QComboBox()
        from_to_layout.addWidget(self.to_unit_combo, 1, 1)
        
        # Value inputs
        value_layout = QGridLayout()
        value_layout.addWidget(QLabel("Input Value:"), 0, 0)
        self.conversion_input = QLineEdit("0")
        value_layout.addWidget(self.conversion_input, 0, 1)
        
        value_layout.addWidget(QLabel("Result:"), 1, 0)
        self.conversion_result = QLineEdit()
        self.conversion_result.setReadOnly(True)
        value_layout.addWidget(self.conversion_result, 1, 1)
        
        # Convert button
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self._perform_conversion)
        
        # Add all layouts
        conversion_layout.addLayout(conv_type_layout)
        conversion_layout.addLayout(from_to_layout)
        conversion_layout.addLayout(value_layout)
        conversion_layout.addWidget(convert_btn)
        conversion_layout.addStretch()
        
        # Initialize conversion units
        self._update_conversion_units("Length")
        
        # Add tab to tab widget
        self.tab_widget.addTab(conversion_tab, "Conversions")
        
    def _update_conversion_units(self, conversion_type: str) -> None:
        """Update conversion units based on selected conversion type.
        
        Args:
            conversion_type: Type of conversion (Length, Area, etc.)
        """
        self.from_unit_combo.clear()
        self.to_unit_combo.clear()
        
        # Define units for each conversion type
        if conversion_type == "Length":
            units = ["m", "cm", "mm", "km", "in", "ft", "yd", "mi"]
        elif conversion_type == "Area":
            units = ["m²", "cm²", "km²", "in²", "ft²", "acre", "hectare"]
        elif conversion_type == "Volume":
            units = ["m³", "cm³", "mm³", "L", "mL", "gal (US)", "gal (UK)"]
        elif conversion_type == "Mass":
            units = ["kg", "g", "mg", "lb", "oz", "stone", "ton"]
        elif conversion_type == "Temperature":
            units = ["°C", "°F", "K"]
        elif conversion_type == "Angle":
            units = ["degree", "radian", "gradian"]
        else:
            units = []
            
        self.from_unit_combo.addItems(units)
        self.to_unit_combo.addItems(units)
        
        # Default to different units for from and to
        if len(units) > 1:
            self.to_unit_combo.setCurrentIndex(1)
            
    def _perform_conversion(self) -> None:
        """Perform unit conversion based on current selections."""
        try:
            # Get input value
            value = float(self.conversion_input.text())
            
            # Get unit conversion type, from unit, and to unit
            conv_type = self.conversion_type_combo.currentText()
            from_unit = self.from_unit_combo.currentText()
            to_unit = self.to_unit_combo.currentText()
            
            # Perform conversion using backend calculator
            result = self._convert_unit(value, from_unit, to_unit, conv_type)
            
            # Display result
            self.conversion_result.setText(str(result))
            
            # Add to calculation history
            history_entry = f"{value} {from_unit} = {result} {to_unit}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
        except (ValueError, ZeroDivisionError) as e:
            # Handle errors in conversion
            self.conversion_result.setText(f"Error: {str(e)}")
            
    def _convert_unit(self, value: float, from_unit: str, to_unit: str, 
                     conv_type: str) -> float:
        """Convert a value between units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            conv_type: Conversion category
            
        Returns:
            Converted value
        """
        # Use the backend calculator to perform conversions
        # For simplicity in this implementation, we'll handle a few cases directly
        if from_unit == to_unit:
            return value
            
        # This is simplified - a complete implementation would use the 
        # unit conversion functionality from AdvancedScientificCalculator
        
        # Example conversion factor lookups
        if conv_type == "Length":
            # Convert to meters first
            meters = value
            if from_unit == "cm":
                meters = value / 100
            elif from_unit == "mm":
                meters = value / 1000
            elif from_unit == "km":
                meters = value * 1000
            elif from_unit == "in":
                meters = value * 0.0254
            elif from_unit == "ft":
                meters = value * 0.3048
            elif from_unit == "yd":
                meters = value * 0.9144
            elif from_unit == "mi":
                meters = value * 1609.344
                
            # Convert from meters to target unit
            if to_unit == "m":
                return meters
            elif to_unit == "cm":
                return meters * 100
            elif to_unit == "mm":
                return meters * 1000
            elif to_unit == "km":
                return meters / 1000
            elif to_unit == "in":
                return meters / 0.0254
            elif to_unit == "ft":
                return meters / 0.3048
            elif to_unit == "yd":
                return meters / 0.9144
            elif to_unit == "mi":
                return meters / 1609.344
                
        # Handle temperature as a special case
        if conv_type == "Temperature":
            if from_unit == "°C":
                if to_unit == "°F":
                    return (value * 9/5) + 32
                elif to_unit == "K":
                    return value + 273.15
            elif from_unit == "°F":
                if to_unit == "°C":
                    return (value - 32) * 5/9
                elif to_unit == "K":
                    return (value - 32) * 5/9 + 273.15
            elif from_unit == "K":
                if to_unit == "°C":
                    return value - 273.15
                elif to_unit == "°F":
                    return (value - 273.15) * 9/5 + 32
                    
        # For now, just return the input value for unimplemented conversions
        return value
    
    def _setup_history_panel(self, layout: QVBoxLayout) -> None:
        """Set up the calculation history panel.
        
        Args:
            layout: Layout to add the history panel to
        """
        # Create history group
        history_group = QGroupBox("Calculation History")
        history_layout = QVBoxLayout(history_group)
        
        # History display
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMaximumHeight(100)
        history_layout.addWidget(self.history_display)
        
        # Add to main layout
        layout.addWidget(history_group)
        
    def _connect_number_buttons(self, parent: QWidget) -> None:
        """Connect number button signals to handlers.
        
        Args:
            parent: Parent widget containing buttons
        """
        for btn in parent.findChildren(QPushButton):
            if btn.text() in "0123456789.":
                btn.clicked.connect(lambda _, digit=btn.text(): self._on_digit_clicked(digit))
                
    def _connect_operator_buttons(self, parent: QWidget) -> None:
        """Connect operator button signals to handlers.
        
        Args:
            parent: Parent widget containing buttons
        """
        operator_map = {
            "+": self._on_add_clicked,
            "-": self._on_subtract_clicked,
            "×": self._on_multiply_clicked,
            "÷": self._on_divide_clicked,
            "=": self._on_equals_clicked,
            "%": self._on_percent_clicked,
            "±": self._on_negate_clicked,
            "(": lambda: self._on_parenthesis_clicked("("),
            ")": lambda: self._on_parenthesis_clicked(")"),
            "mod": self._on_mod_clicked,
        }
        
        for btn in parent.findChildren(QPushButton):
            if btn.text() in operator_map:
                btn.clicked.connect(operator_map[btn.text()])
                
    def _connect_function_buttons(self, parent: QWidget) -> None:
        """Connect function button signals to handlers.
        
        Args:
            parent: Parent widget containing buttons
        """
        # Map button text to handler methods
        function_map = {
            "C": self._on_clear_clicked,
            "CE": self._on_clear_entry_clicked,
            "⌫": self._on_backspace_clicked,
        }
        
        for btn in parent.findChildren(QPushButton):
            if btn.text() in function_map:
                btn.clicked.connect(function_map[btn.text()])
                
    def _connect_memory_buttons(self, parent: QWidget) -> None:
        """Connect memory button signals to handlers.
        
        Args:
            parent: Parent widget containing buttons
        """
        # Map button text to handler methods
        memory_map = {
            "MC": self._on_memory_clear_clicked,
            "MR": self._on_memory_recall_clicked,
            "M+": self._on_memory_add_clicked,
            "M-": self._on_memory_subtract_clicked,
            "MS": self._on_memory_store_clicked,
        }
        
        for btn in parent.findChildren(QPushButton):
            if btn.text() in memory_map:
                btn.clicked.connect(memory_map[btn.text()])
                
    def _connect_scientific_buttons(self, parent: QWidget) -> None:
        """Connect scientific function button signals to handlers.
        
        Args:
            parent: Parent widget containing buttons
        """
        # Map button text to handler methods
        scientific_map = {
            "x²": self._on_square_clicked,
            "x³": self._on_cube_clicked,
            "xʸ": self._on_power_clicked,
            "ex": self._on_exp_clicked,
            "10x": self._on_ten_power_clicked,
            "√": self._on_sqrt_clicked,
            "∛": self._on_cbrt_clicked,
            "y√x": self._on_nth_root_clicked,
            "ln": self._on_ln_clicked,
            "log": self._on_log10_clicked,
            "sin": self._on_sin_clicked,
            "cos": self._on_cos_clicked,
            "tan": self._on_tan_clicked,
            "sec": self._on_sec_clicked,
            "csc": self._on_csc_clicked,
            "sin⁻¹": self._on_asin_clicked,
            "cos⁻¹": self._on_acos_clicked,
            "tan⁻¹": self._on_atan_clicked,
            "sinh": self._on_sinh_clicked,
            "cosh": self._on_cosh_clicked,
            "tanh": self._on_tanh_clicked,
            "π": lambda: self._insert_constant("π"),
            "e": lambda: self._insert_constant("e"),
            "φ": lambda: self._insert_constant("φ"),
            "γ": lambda: self._insert_constant("γ"),
            "n!": self._on_factorial_clicked,
        }
        
        for btn in parent.findChildren(QPushButton):
            if btn.text() in scientific_map:
                btn.clicked.connect(scientific_map[btn.text()])
    
    def _set_angle_mode(self, mode: str) -> None:
        """Set the angle mode for trigonometric calculations.
        
        Args:
            mode: Angle mode ("DEG", "RAD", or "GRAD")
        """
        self.angle_mode = mode
        logger.debug(f"Angle mode set to {mode}")
        
    def _on_digit_clicked(self, digit: str) -> None:
        """Handle digit button click.
        
        Args:
            digit: Digit character clicked
        """
        # Only clear the input if we've just completed a calculation AND we're not after an operator
        # This prevents clearing when entering the second number after an operator
        if self.in_calculation_mode and not self.last_button_was_operator and not self.current_input.endswith(' '):
            self.current_input = ""
            self.in_calculation_mode = False
            
        # Handle decimal point logic
        if digit == '.':
            # Don't add multiple decimal points
            if '.' in self.current_input.split(' ')[-1]:
                return
            
            # If the current input is empty or ends with an operator, add "0."
            if not self.current_input or self.current_input[-1] in "+-×÷" or self.current_input.endswith(' '):
                digit = "0."
        
        # Add digit to input
        self.current_input += digit
        self._update_display()
        self.last_button_was_operator = False
        
    def _on_add_clicked(self) -> None:
        """Handle addition operator click."""
        self._append_operator("+")
        
    def _on_subtract_clicked(self) -> None:
        """Handle subtraction operator click."""
        self._append_operator("-")
        
    def _on_multiply_clicked(self) -> None:
        """Handle multiplication operator click."""
        self._append_operator("×")
        
    def _on_divide_clicked(self) -> None:
        """Handle division operator click."""
        self._append_operator("÷")
        
    def _on_equals_clicked(self) -> None:
        """Handle equals button click."""
        if not self.current_input:
            return
            
        try:
            # Save the expression for history
            expression = self.current_input
            
            # Calculate result
            result = self._evaluate_expression()
            
            # Update displays
            self.result = result
            self.result_display.setText(str(result))
            self.expression_display.setText(f"{expression} =")
            
            # Reset for next calculation but keep result
            self.current_input = str(result)
            self.in_calculation_mode = True
            
            # Add to history
            history_entry = f"{expression} = {result}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            # Emit calculation performed signal
            self.calculation_performed.emit(expression, result)
            
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Calculation error: {str(e)}")
        
        self.last_button_was_operator = False
        
    def _on_percent_clicked(self) -> None:
        """Handle percent button click."""
        if not self.current_input:
            return
            
        try:
            # Get current value
            current_value = float(self._evaluate_expression())
            
            # Calculate percentage (current value / 100)
            result = current_value / 100
            
            # Update input and display
            self.current_input = str(result)
            self._update_display()
            
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Percent calculation error: {str(e)}")
            
        self.last_button_was_operator = False
        
    def _on_negate_clicked(self) -> None:
        """Handle number negation (±) button click."""
        if not self.current_input:
            return
            
        try:
            # Parse current expression to find the last number
            parts = self.current_input.split(' ')
            
            if parts:
                # Check if there's a number to negate
                if parts[-1].replace('.', '', 1).replace('-', '', 1).isdigit():
                    # If it's a number, negate it
                    if parts[-1].startswith('-'):
                        parts[-1] = parts[-1][1:]  # Remove the negative sign
                    else:
                        parts[-1] = '-' + parts[-1]  # Add a negative sign
                    
                    # Reassemble the expression
                    self.current_input = ' '.join(parts)
                    self._update_display()
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Negation error: {str(e)}")
            logger.error(f"Negation error: {str(e)}")
            
        self.last_button_was_operator = False
        
    def _on_parenthesis_clicked(self, parenthesis: str) -> None:
        """Handle parenthesis button click.
        
        Args:
            parenthesis: Parenthesis character ("(" or ")")
        """
        if self.in_calculation_mode and not self.last_button_was_operator:
            self.current_input = ""
            self.in_calculation_mode = False
            
        # Add space before parenthesis if needed
        if self.current_input and self.current_input[-1].isdigit() and parenthesis == "(":
            self.current_input += " × " + parenthesis
        else:
            # Make sure we have proper spacing around operators
            if self.current_input and self.current_input[-1] not in " (":
                self.current_input += " " + parenthesis
            else:
                self.current_input += parenthesis
                
        self._update_display()
        self.last_button_was_operator = False
        
    def _on_mod_clicked(self) -> None:
        """Handle modulo operator click."""
        self._append_operator("mod")
        
    def _on_clear_clicked(self) -> None:
        """Handle clear button click."""
        self.current_input = ""
        self.result = 0.0
        self._update_display()
        self.in_calculation_mode = False
        self.last_button_was_operator = False
        
    def _on_clear_entry_clicked(self) -> None:
        """Handle clear entry button click."""
        # Remove the last entry (number or operator)
        parts = self.current_input.split(' ')
        if parts:
            parts.pop()
        self.current_input = ' '.join(parts)
        self._update_display()
        
    def _on_backspace_clicked(self) -> None:
        """Handle backspace button click."""
        if self.current_input:
            # If the last character is a space, remove the operator or function
            # with its surrounding spaces
            if self.current_input.endswith(" "):
                # Find the last operator with its spaces
                parts = self.current_input.rstrip().split(" ")
                if len(parts) > 1:
                    self.current_input = " ".join(parts[:-1]) + " "
                else:
                    self.current_input = ""
            else:
                # Just remove the last character
                self.current_input = self.current_input[:-1]
                
            self._update_display()
            
    def _on_memory_clear_clicked(self) -> None:
        """Handle memory clear button click."""
        self.memory = 0.0
        self._update_memory_display()
        
    def _on_memory_recall_clicked(self) -> None:
        """Handle memory recall button click."""
        self.current_input = str(self.memory)
        self._update_display()
        
    def _on_memory_add_clicked(self) -> None:
        """Handle memory add button click."""
        try:
            current_value = float(self._evaluate_expression())
            self.memory += current_value
            self._update_memory_display()
        except Exception as e:
            logger.error(f"Memory add error: {str(e)}")
            
    def _on_memory_subtract_clicked(self) -> None:
        """Handle memory subtract button click."""
        try:
            current_value = float(self._evaluate_expression())
            self.memory -= current_value
            self._update_memory_display()
        except Exception as e:
            logger.error(f"Memory subtract error: {str(e)}")
            
    def _on_memory_store_clicked(self) -> None:
        """Handle memory store button click."""
        try:
            self.memory = float(self._evaluate_expression())
            self._update_memory_display()
        except Exception as e:
            logger.error(f"Memory store error: {str(e)}")
            
    def _on_square_clicked(self) -> None:
        """Handle x² button click."""
        if not self.current_input:
            return
            
        try:
            # Get the current value
            value = self._evaluate_expression()
            # Square it
            result = value ** 2
            
            # Add to history
            self.calculation_history.append(f"{value}² = {result}")
            
            # Update display
            self.current_input = str(result)
            self._update_display()
            self._update_history_display()
            
            self.in_calculation_mode = True
            self.last_button_was_operator = False
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Square calculation error: {str(e)}")
        
    def _on_cube_clicked(self) -> None:
        """Handle x³ button click."""
        if not self.current_input:
            return
            
        try:
            # Get the current value
            value = self._evaluate_expression()
            # Cube it
            result = value ** 3
            
            # Add to history
            self.calculation_history.append(f"{value}³ = {result}")
            
            # Update display
            self.current_input = str(result)
            self._update_display()
            self._update_history_display()
            
            self.in_calculation_mode = True
            self.last_button_was_operator = False
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Cube calculation error: {str(e)}")
        
    def _on_power_clicked(self) -> None:
        """Handle xʸ button click."""
        self._append_operator("^")
        
    def _on_exp_clicked(self) -> None:
        """Handle eˣ button click."""
        self._apply_function('exp')
        
    def _on_ten_power_clicked(self) -> None:
        """Handle 10ˣ button click."""
        self._apply_function('10^')
        
    def _on_sqrt_clicked(self) -> None:
        """Handle square root button click."""
        self._apply_function('sqrt')
        
    def _on_cbrt_clicked(self) -> None:
        """Handle cube root button click."""
        self._apply_function('cbrt')
        
    def _on_nth_root_clicked(self) -> None:
        """Handle y√x button click."""
        self._append_operator("root")
        
    def _on_ln_clicked(self) -> None:
        """Handle natural logarithm button click."""
        self._apply_function('ln')
        
    def _on_log10_clicked(self) -> None:
        """Handle base-10 logarithm button click."""
        self._apply_function('log')
        
    def _on_sin_clicked(self) -> None:
        """Handle sine button click."""
        self._apply_function('sin')
        
    def _on_cos_clicked(self) -> None:
        """Handle cosine button click."""
        self._apply_function('cos')
        
    def _on_tan_clicked(self) -> None:
        """Handle tangent button click."""
        self._apply_function('tan')
        
    def _on_sec_clicked(self) -> None:
        """Handle secant button click."""
        self._apply_function('sec')
        
    def _on_csc_clicked(self) -> None:
        """Handle cosecant button click."""
        self._apply_function('csc')
        
    def _on_asin_clicked(self) -> None:
        """Handle arcsine button click."""
        self._apply_function('asin')
        
    def _on_acos_clicked(self) -> None:
        """Handle arccosine button click."""
        self._apply_function('acos')
        
    def _on_atan_clicked(self) -> None:
        """Handle arctangent button click."""
        self._apply_function('atan')
        
    def _on_sinh_clicked(self) -> None:
        """Handle hyperbolic sine button click."""
        self._apply_function('sinh')
        
    def _on_cosh_clicked(self) -> None:
        """Handle hyperbolic cosine button click."""
        self._apply_function('cosh')
        
    def _on_tanh_clicked(self) -> None:
        """Handle hyperbolic tangent button click."""
        self._apply_function('tanh')
        
    def _on_factorial_clicked(self) -> None:
        """Handle factorial button click."""
        self._apply_function('factorial')
        
    def _insert_constant(self, constant: str) -> None:
        """Insert a constant into the expression.
        
        Args:
            constant: Constant symbol to insert
        """
        # If starting a new calculation after completing one
        if self.in_calculation_mode and not self.last_button_was_operator:
            self.current_input = ""
            self.in_calculation_mode = False
            
        # If current input is not empty and does not end with an operator or open parenthesis,
        # add a multiplication operator before inserting the constant.
        if self.current_input and not self.current_input.endswith(tuple(" +-×÷^(")):
            self.current_input += " × "
            
        # Add the constant
        self.current_input += constant
        self._update_display()
        self.last_button_was_operator = False
        
    def _append_operator(self, operator: str) -> None:
        """Append an operator to the current expression.
        
        Args:
            operator: Operator to append
        """
        if not self.current_input and operator != "-":
            # Cannot start with an operator except minus
            return
            
        # If the last character is already an operator, replace it
        if self.current_input:
            if self.current_input[-1] in "+-×÷^":
                self.current_input = self.current_input[:-1] + operator
                self._update_display()
                return
                
        # Add operator to input with spaces
        self.current_input += f" {operator} "
        self._update_display()
        
        # Just mark that the last button was an operator, don't set calculation mode
        # Calculation mode should only be set after equals is pressed
        self.last_button_was_operator = True
        
    def _apply_function(self, func_name: str) -> None:
        """Apply a mathematical function to the current value.
        
        Args:
            func_name: Name of function to apply
        """
        if not self.current_input:
            return
            
        try:
            # Get current value
            current_value = float(self._evaluate_expression())
            
            # Apply function using the calculator backend
            if func_name == 'square':
                result = self.calculator.power(current_value, 2)
            elif func_name == 'cube':
                result = self.calculator.power(current_value, 3)
            elif func_name == 'exp':
                result = self.calculator.exp(current_value)
            elif func_name == '10^':
                result = self.calculator.power(10, current_value)
            elif func_name == 'sqrt':
                result = self.calculator.square_root(current_value)
            elif func_name == 'cbrt':
                result = self.calculator.cbrt(current_value)
            elif func_name == 'ln':
                result = self.calculator.ln(current_value)
            elif func_name == 'log':
                result = self.calculator.log10(current_value)
            elif func_name == 'sin':
                result = self._calculate_trig_function(self.calculator.sin, current_value)
            elif func_name == 'cos':
                result = self._calculate_trig_function(self.calculator.cos, current_value)
            elif func_name == 'tan':
                result = self._calculate_trig_function(self.calculator.tan, current_value)
            elif func_name == 'sec':
                result = self._calculate_trig_function(self.calculator.sec, current_value)
            elif func_name == 'csc':
                result = self._calculate_trig_function(self.calculator.csc, current_value)
            elif func_name == 'asin':
                result = self.calculator.asin(current_value)
            elif func_name == 'acos':
                result = self.calculator.acos(current_value)
            elif func_name == 'atan':
                result = self.calculator.atan(current_value)
            elif func_name == 'sinh':
                result = self.calculator.sinh(current_value)
            elif func_name == 'cosh':
                result = self.calculator.cosh(current_value)
            elif func_name == 'tanh':
                result = self.calculator.tanh(current_value)
            elif func_name == 'factorial':
                result = self.calculator.factorial(int(current_value))
            else:
                raise ValueError(f"Unknown function: {func_name}")
                
            # Add operation to history
            operation = f"{func_name}({current_value})"
            history_entry = f"{operation} = {result}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            # Update current input with result
            self.current_input = str(result)
            self._update_display()
            
        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")
            logger.error(f"Function error ({func_name}): {str(e)}")
            
    def _calculate_trig_function(self, func: callable, value: float) -> float:
        """Calculate trigonometric function based on current angle mode.
        
        Args:
            func: Trigonometric function to apply
            value: Input value
            
        Returns:
            Result of the calculation
        """
        # Convert value to radians if needed
        if self.angle_mode == "DEG":
            radians = math.radians(value)
        elif self.angle_mode == "GRAD":
            radians = (value * math.pi) / 200
        else:  # RAD mode
            radians = value
            
        return func(radians)
        
    def _evaluate_expression(self) -> float:
        """Evaluate the current expression.
        
        Returns:
            Result of the expression evaluation
        """
        # Replace UI operators with Python operators
        expression = self.current_input
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        expression = expression.replace('^', '**')
        expression = expression.replace('mod', '%')
        
        # Replace constants with their values
        expression = expression.replace('π', str(math.pi))
        expression = expression.replace('e', str(math.e))
        expression = expression.replace('φ', str((1 + math.sqrt(5)) / 2))
        expression = expression.replace('γ', str(0.57721566490153286))
        # Add replacements for other scientific constants
        # Using values from scipy.constants (or define manually if scipy not available)
        expression = expression.replace('c', str(299792458.0))  # Speed of light
        expression = expression.replace('G', str(6.67430e-11)) # Gravitational constant
        expression = expression.replace('h', str(6.62607015e-34)) # Planck constant
        expression = expression.replace('ℏ', str(1.054571817e-34)) # Reduced Planck constant (hbar)
        expression = expression.replace('ε0', str(8.8541878128e-12)) # Electric constant (epsilon_0)
        expression = expression.replace('μ0', str(1.25663706212e-6)) # Magnetic constant (mu_0)
        expression = expression.replace('k', str(1.380649e-23))    # Boltzmann constant
        expression = expression.replace('NA', str(6.02214076e+23)) # Avogadro constant
        expression = expression.replace('R', str(8.314462618))   # Gas constant

        # Clean up the expression before evaluation
        expression = expression.strip()  # Remove leading/trailing whitespace
        # Remove trailing operators if any
        while expression and expression[-1] in '+-*/%':
            expression = expression[:-1].strip()
            
        # Ensure expression is not empty after cleanup
        if not expression:
            return 0.0  # Return 0 for empty/invalid expressions after cleanup
            
        try:
            # Use eval for basic expressions (with security considerations)
            # In a production environment, use a safer expression evaluator
            result = eval(expression)
            return result
        except Exception as e:
            logger.error(f"Expression evaluation error: {str(e)}")
            raise
            
    def _update_display(self) -> None:
        """Update the calculator displays."""
        # Update expression display
        self.expression_display.setText(self.current_input)
        
        # Try to evaluate and update result display
        if self.current_input:
            try:
                result = self._evaluate_expression()
                self.result = result
                self.result_display.setText(str(result))
            except SyntaxError:
                # Display Syntax Error for invalid expressions
                self.result_display.setText("Syntax Error")
            except Exception as e:
                # Handle other evaluation errors (e.g., division by zero)
                self.result_display.setText(f"Error: {e}")
                logger.warning(f"Evaluation error in display update: {e}")
        else:
            # Clear result if input is empty
            self.result = 0.0
            self.result_display.setText("0")
            
    def _update_memory_display(self) -> None:
        """Update the memory indicator display."""
        self.memory_indicator.setText(f"M: {self.memory}")
        
    def _update_history_display(self) -> None:
        """Update the calculation history display."""
        # Show the most recent calculations (limited to last 10)
        history_text = "\n".join(self.calculation_history[-10:])
        self.history_display.setText(history_text)
        
        # Scroll to the bottom to show latest entries
        self.history_display.verticalScrollBar().setValue(
            self.history_display.verticalScrollBar().maximum()
        )

    # --- Keyboard Handling ---
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle keyboard input for calculator operations."""
        key = event.key()
        text = event.text()

        # Numbers (0-9) from main keyboard or numpad
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            self._on_digit_clicked(text)
            return

        # Decimal point
        if key == Qt.Key.Key_Period:
            self._on_digit_clicked('.')
            return

        # Basic Operators
        if key == Qt.Key.Key_Plus:
            self._on_add_clicked()
            return
        if key == Qt.Key.Key_Minus:
            self._on_subtract_clicked()
            return
        if key == Qt.Key.Key_Asterisk:  # Numpad multiply often uses asterisk
            self._on_multiply_clicked()
            return
        if text == '*': # Handle shift+8 for multiply
            self._on_multiply_clicked()
            return
        if key == Qt.Key.Key_Slash: # Numpad divide
            self._on_divide_clicked()
            return
        if text == '/': # Handle main keyboard divide
            self._on_divide_clicked()
            return

        # Equals (Enter/Return)
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_equals_clicked()
            return

        # Backspace
        if key == Qt.Key.Key_Backspace:
            self._on_backspace_clicked()
            return

        # Clear (Escape)
        if key == Qt.Key.Key_Escape:
            self._on_clear_clicked()
            return
        
        # Parentheses
        if text == '(':
            self._on_parenthesis_clicked('(')
            return
        if text == ')':
            self._on_parenthesis_clicked(')')
            return
        
        # Percent
        if text == '%':
            self._on_percent_clicked()
            return
            
        # Power (^)
        if text == '^':
            self._on_power_clicked()
            return

        # Allow other key events (like tab navigation) to pass through
        super().keyPressEvent(event)

    # --- Matrix/Vector Helpers ---
    def _get_matrix_from_inputs(self) -> Optional[List[List[float]]]:
        """Retrieve the matrix values from the current input fields."""
        current_widget = self.matrix_stack.currentWidget()
        if not current_widget:
            logger.error("No current matrix widget found.")
            return None
            
        matrix: List[List[float]] = []
        layout = current_widget.layout()
        if not isinstance(layout, QGridLayout):
            logger.error("Matrix widget layout is not QGridLayout.")
            return None

        rows = layout.rowCount()
        cols = layout.columnCount()

        try:
            for i in range(rows):
                row_values: List[float] = []
                for j in range(cols):
                    item = layout.itemAtPosition(i, j)
                    if item and isinstance(item.widget(), QLineEdit):
                        input_field = item.widget()
                        value = float(input_field.text())
                        row_values.append(value)
                    else:
                        # Handle potential empty spots or non-QLineEdit widgets if any
                        logger.warning(f"No QLineEdit found at matrix position ({i},{j})")
                        # Depending on requirements, might return None or use a default value
                        row_values.append(0.0) # Defaulting to 0.0 for now
                matrix.append(row_values)
            return matrix
        except ValueError as e:
            logger.error(f"Invalid input in matrix: {e}")
            self.result_display.setText("Invalid Matrix Input")
            return None

    # --- Matrix/Vector Handlers ---
    def _connect_matrix_vector_buttons(self, parent: QWidget) -> None:
        """Connect matrix/vector button signals to handlers."""
        button_map = {
            "Determinant": self._on_determinant_clicked,
            "Inverse": self._on_inverse_clicked,
            "Transpose": self._on_transpose_clicked,
            "Dot Product": self._on_dot_product_clicked,
            "Cross Product": self._on_cross_product_clicked,
            "Magnitude": self._on_magnitude_clicked
        }
        for btn in parent.findChildren(QPushButton):
            if btn.text() in button_map:
                btn.clicked.connect(button_map[btn.text()])

    def _on_determinant_clicked(self) -> None:
        """Handle determinant button click."""
        matrix = self._get_matrix_from_inputs()
        if matrix is None:
            return # Error handled in helper

        try:
            determinant = self.calculator.matrix_determinant(matrix)
            result_str = str(determinant)
            
            # Update display and history
            self.result_display.setText(result_str)
            self.result = determinant # Store float result if needed elsewhere
            self.current_input = f"det({matrix})" # Represent operation in input
            self.expression_display.setText(self.current_input)
            
            history_entry = f"det({matrix}) = {result_str}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            logger.debug(f"Calculated determinant: {determinant}")
            
        except Exception as e:
            error_msg = f"Determinant Error: {e}"
            logger.error(error_msg)
            self.result_display.setText(error_msg)
            self.expression_display.setText("Error")

    def _on_inverse_clicked(self) -> None:
        """Handle matrix inverse button click."""
        matrix = self._get_matrix_from_inputs()
        if matrix is None:
            return

        try:
            inverse_matrix = self.calculator.matrix_inverse(matrix)
            if inverse_matrix is None: # Backend might return None for non-invertible
                result_str = "Matrix not invertible"
                inverse_matrix_float_or_list = [] # Or some other appropriate default
            else:
                result_str = str(inverse_matrix)
                inverse_matrix_float_or_list = inverse_matrix

            self.result_display.setText(result_str)
            # Storing a list of lists (matrix) in self.result might need type adjustment
            # For now, let's assume self.result can handle it or we primarily use text display
            self.result = inverse_matrix_float_or_list 
            self.current_input = f"inv({matrix})"
            self.expression_display.setText(self.current_input)
            
            history_entry = f"inv({matrix}) = {result_str}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            logger.debug(f"Calculated inverse: {result_str}")

        except Exception as e:
            error_msg = f"Inverse Error: {e}"
            logger.error(error_msg)
            self.result_display.setText(error_msg)
            self.expression_display.setText("Error")

    def _on_transpose_clicked(self) -> None:
        """Handle matrix transpose button click."""
        matrix = self._get_matrix_from_inputs()
        if matrix is None:
            return

        try:
            transpose_matrix = self.calculator.matrix_transpose(matrix)
            result_str = str(transpose_matrix)

            self.result_display.setText(result_str)
            self.result = transpose_matrix # Store the list of lists
            self.current_input = f"transpose({matrix})"
            self.expression_display.setText(self.current_input)
            
            history_entry = f"transpose({matrix}) = {result_str}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            logger.debug(f"Calculated transpose: {result_str}")

        except Exception as e:
            error_msg = f"Transpose Error: {e}"
            logger.error(error_msg)
            self.result_display.setText(error_msg)
            self.expression_display.setText("Error")

    def _on_dot_product_clicked(self) -> None:
        """Handle vector dot product button click.
        Assumes vectors are the first two rows of the current matrix input.
        """
        matrix = self._get_matrix_from_inputs()
        if matrix is None or len(matrix) < 2:
            self.result_display.setText("Matrix with at least 2 rows required")
            return
            
        vector1 = matrix[0]
        vector2 = matrix[1]

        if len(vector1) != len(vector2):
            self.result_display.setText("Vectors must have same dimension")
            return

        try:
            dot_product = self.calculator.vector_dot(vector1, vector2)
            result_str = str(dot_product)

            self.result_display.setText(result_str)
            self.result = dot_product
            self.current_input = f"dot({vector1}, {vector2})"
            self.expression_display.setText(self.current_input)
            
            history_entry = f"dot({vector1}, {vector2}) = {result_str}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            logger.debug(f"Calculated dot product: {result_str}")

        except Exception as e:
            error_msg = f"Dot Product Error: {e}"
            logger.error(error_msg)
            self.result_display.setText(error_msg)
            self.expression_display.setText("Error")

    def _on_cross_product_clicked(self) -> None:
        """Handle vector cross product button click.
        Assumes vectors are the first two rows (must be 3D) of the current matrix input.
        """
        matrix = self._get_matrix_from_inputs()
        if matrix is None or len(matrix) < 2:
            self.result_display.setText("Matrix with at least 2 rows required")
            return
            
        vector1 = matrix[0]
        vector2 = matrix[1]

        if len(vector1) != 3 or len(vector2) != 3:
            self.result_display.setText("Cross product requires 3D vectors")
            return

        try:
            cross_product = self.calculator.vector_cross(vector1, vector2)
            result_str = str(cross_product) # Result is a vector (list)

            self.result_display.setText(result_str)
            self.result = cross_product # Store the resulting vector
            self.current_input = f"cross({vector1}, {vector2})"
            self.expression_display.setText(self.current_input)
            
            history_entry = f"cross({vector1}, {vector2}) = {result_str}"
            self.calculation_history.append(history_entry)
            self._update_history_display()
            
            logger.debug(f"Calculated cross product: {result_str}")

        except Exception as e:
            error_msg = f"Cross Product Error: {e}"
            logger.error(error_msg)
            self.result_display.setText(error_msg)
            self.expression_display.setText("Error")

    def _on_magnitude_clicked(self) -> None:
        """Handle vector magnitude button click."""
        logger.info("Magnitude button clicked - not yet implemented")
        # TODO: Implement logic
        pass
