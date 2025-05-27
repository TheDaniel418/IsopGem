"""
Properties Tab Widget for the Number Dictionary.

This widget displays comprehensive properties of a number using the
NumberPropertiesService to show mathematical and numerical characteristics.
"""

from typing import Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from shared.services.number_properties_service import NumberPropertiesService


class PropertyDisplayWidget(QWidget):
    """Widget for displaying a single property with label and value."""
    
    def __init__(self, label: str, value: str, parent=None):
        """Initialize the property display widget.
        
        Args:
            label: The property label
            value: The property value
            parent: Parent widget
        """
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setMinimumWidth(150)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label_widget.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(label_widget)
        
        # Value
        value_widget = QLabel(str(value))
        value_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_widget.setWordWrap(True)
        value_widget.setStyleSheet("color: #666; padding-left: 10px;")
        layout.addWidget(value_widget, 1)


class PropertyGroupWidget(QGroupBox):
    """Widget for displaying a group of related properties."""
    
    def __init__(self, title: str, properties: Dict[str, Any], parent=None):
        """Initialize the property group widget.
        
        Args:
            title: The group title
            properties: Dictionary of properties to display
            parent: Parent widget
        """
        super().__init__(title, parent)
        
        layout = QVBoxLayout(self)
        
        # Add properties with enhanced formatting
        for key, value in properties.items():
            display_key = self._format_key(key)
            formatted_value = self._format_value(key, value, properties)
            
            property_widget = PropertyDisplayWidget(display_key, formatted_value)
            layout.addWidget(property_widget)
        
        layout.addStretch()
    
    def _format_key(self, key: str) -> str:
        """Format a property key for display.
        
        Args:
            key: The property key
            
        Returns:
            Formatted key string
        """
        # Convert snake_case to Title Case
        return key.replace('_', ' ').title()
    
    def _format_value(self, key: str, value: Any, all_properties: Dict[str, Any]) -> str:
        """Format a property value for display with enhanced formatting.
        
        Args:
            key: The property key
            value: The property value
            all_properties: All properties for context
            
        Returns:
            Formatted value string
        """
        # Handle boolean values
        if isinstance(value, bool):
            if value:
                # For True values, check if we need to add additional info
                if key == "is_prime" and "prime_ordinal" in all_properties:
                    prime_ordinal = all_properties["prime_ordinal"]
                    if prime_ordinal is not None:
                        return f"Yes (#{prime_ordinal})"
                
                # Handle abundant/deficient numbers - use 'number' key instead of 'value'
                if key == "is_abundant" and "aliquot_sum" in all_properties and "number" in all_properties:
                    aliquot_sum = all_properties["aliquot_sum"]
                    number_value = all_properties["number"]
                    if aliquot_sum is not None and number_value is not None:
                        abundance = aliquot_sum - number_value
                        return f"Yes (abundant by {abundance})"
                
                if key == "is_deficient" and "aliquot_sum" in all_properties and "number" in all_properties:
                    aliquot_sum = all_properties["aliquot_sum"]
                    number_value = all_properties["number"]
                    if aliquot_sum is not None and number_value is not None:
                        deficiency = number_value - aliquot_sum
                        return f"Yes (deficient by {deficiency})"
                
                return "Yes"
            else:
                return "No"
        
        # Handle list/tuple values
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        
        # Handle nested dictionaries
        if isinstance(value, dict):
            return self._format_dict(value)
        
        # Default string conversion
        return str(value)
    
    def _format_dict(self, d: Dict[str, Any]) -> str:
        """Format a dictionary for display.
        
        Args:
            d: Dictionary to format
            
        Returns:
            Formatted string representation
        """
        items = []
        for k, v in d.items():
            formatted_key = self._format_key(k)
            items.append(f"{formatted_key}: {v}")
        return "; ".join(items)


class PropertiesTabWidget(QWidget):
    """Tab widget for displaying number properties."""
    
    def __init__(self, parent=None):
        """Initialize the properties tab widget."""
        super().__init__(parent)
        
        self.properties_service = NumberPropertiesService.get_instance()
        self.current_number = 0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel("Number Properties")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.header_label)
        
        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
        # Initially show placeholder
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder content when no number is loaded."""
        self.header_label.setText("Number Properties")
        
        # Clear existing content
        self._clear_content()
        
        placeholder = QLabel("Select a number to view its properties")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #7f8c8d;
                padding: 50px;
            }
        """)
        self.content_layout.addWidget(placeholder)
    
    def _clear_content(self):
        """Clear all content from the layout."""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def load_number(self, number: int):
        """Load properties for a specific number.
        
        Args:
            number: The number to analyze
        """
        self.current_number = number
        self.header_label.setText(f"Properties of {number}")
        
        try:
            # Get comprehensive properties
            properties = self.properties_service.get_number_properties(number)
            
            # Clear existing content
            self._clear_content()
            
            # Create property groups
            self._create_property_groups(properties)
            
        except Exception as e:
            self._show_error(f"Error loading properties: {str(e)}")
    
    def _create_property_groups(self, properties: Dict[str, Any]):
        """Create property group widgets from the properties dictionary.
        
        Args:
            properties: Dictionary of number properties
        """
        # Define property groups and their order
        group_definitions = [
            ("Basic Properties", [
                "number", "value", "is_prime", "is_perfect", "is_abundant", "is_deficient",
                "is_triangular", "is_square", "is_pentagonal", "is_hexagonal", "aliquot_sum"
            ]),
            ("Divisibility", [
                "divisors", "proper_divisors", "divisor_count", "sum_of_divisors",
                "sum_of_proper_divisors", "aliquot_sum"
            ]),
            ("Prime Factorization", [
                "prime_factors", "prime_factorization", "distinct_prime_factors",
                "omega", "big_omega"
            ]),
            ("Digital Properties", [
                "digital_root", "digit_sum", "digit_count", "digits",
                "is_palindrome", "reverse_number"
            ]),
            ("Special Numbers", [
                "fibonacci_index", "lucas_index", "catalan_index",
                "is_fibonacci", "is_lucas", "is_catalan"
            ]),
            ("Geometric Properties", [
                "is_triangular", "triangular_index", "is_square", "square_root",
                "is_pentagonal", "pentagonal_index", "is_hexagonal", "hexagonal_index"
            ]),
            ("Arithmetic Functions", [
                "euler_totient", "mobius", "liouville", "carmichael_lambda"
            ])
        ]
        
        # Create groups
        for group_title, property_keys in group_definitions:
            group_properties = {}
            
            # Collect properties for this group
            for key in property_keys:
                if key in properties:
                    group_properties[key] = properties[key]
            
            # Only create group if it has properties
            if group_properties:
                group_widget = PropertyGroupWidget(group_title, group_properties)
                self.content_layout.addWidget(group_widget)
        
        # Add any remaining properties that weren't categorized
        remaining_properties = {}
        all_categorized_keys = set()
        for _, keys in group_definitions:
            all_categorized_keys.update(keys)
        
        for key, value in properties.items():
            if key not in all_categorized_keys:
                remaining_properties[key] = value
        
        if remaining_properties:
            group_widget = PropertyGroupWidget("Other Properties", remaining_properties)
            self.content_layout.addWidget(group_widget)
        
        # Add stretch at the end
        self.content_layout.addStretch()
    
    def _show_error(self, error_message: str):
        """Show an error message.
        
        Args:
            error_message: The error message to display
        """
        self._clear_content()
        
        error_label = QLabel(error_message)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #e74c3c;
                padding: 50px;
            }
        """)
        self.content_layout.addWidget(error_label) 