"""
Quadset Analysis Tab Widget for the Number Dictionary.

This widget displays quadset analysis using the TQ grid service and provides
links to navigate to other numbers in the quadset.
"""

from typing import Dict, Any, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gematria.services.number_dictionary_service import NumberDictionaryService


class QuadsetNumberWidget(QWidget):
    """Widget for displaying a quadset number with navigation button."""
    
    number_clicked = pyqtSignal(int)
    
    def __init__(self, label: str, number: int, is_current: bool = False, parent=None):
        """Initialize the quadset number widget.
        
        Args:
            label: The label for this number (e.g., "Base", "Conrune")
            number: The number value
            is_current: Whether this is the currently displayed number
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.number = number
        self._setup_ui(label, number, is_current)
    
    def _setup_ui(self, label: str, number: int, is_current: bool):
        """Set up the user interface.
        
        Args:
            label: The label for this number
            number: The number value
            is_current: Whether this is the currently displayed number
        """
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setMinimumWidth(120)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        label_widget.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(label_widget)
        
        # Number display
        number_label = QLabel(str(number))
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setMinimumWidth(80)
        
        if is_current:
            number_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #e74c3c;
                    background-color: #fdf2f2;
                    border: 2px solid #e74c3c;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
        else:
            number_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #2c3e50;
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
        
        layout.addWidget(number_label)
        
        # Navigation button (only if not current)
        if not is_current:
            nav_button = QPushButton("→")
            nav_button.setMaximumWidth(30)
            nav_button.setToolTip(f"Navigate to {number}")
            nav_button.clicked.connect(lambda: self.number_clicked.emit(number))
            nav_button.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            layout.addWidget(nav_button)
        else:
            # Add spacer for current number
            layout.addWidget(QLabel("(Current)"))
        
        layout.addStretch()


class QuadsetAnalysisWidget(QGroupBox):
    """Widget for displaying quadset analysis information."""
    
    def __init__(self, title: str, analysis_data: Dict[str, Any], parent=None):
        """Initialize the quadset analysis widget.
        
        Args:
            title: The group title
            analysis_data: Dictionary containing analysis data
            parent: Parent widget
        """
        super().__init__(title, parent)
        
        layout = QVBoxLayout(self)
        
        # Display analysis data
        for key, value in analysis_data.items():
            if key == "error":
                # Handle error case
                error_label = QLabel(f"Error: {value}")
                error_label.setStyleSheet("color: #e74c3c; font-style: italic;")
                layout.addWidget(error_label)
            else:
                # Format key for display
                display_key = self._format_key(key)
                
                # Create property display
                prop_layout = QHBoxLayout()
                
                key_label = QLabel(f"{display_key}:")
                key_label.setMinimumWidth(150)
                key_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                key_label.setStyleSheet("font-weight: bold; color: #333;")
                prop_layout.addWidget(key_label)
                
                value_label = QLabel(str(value))
                value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                value_label.setWordWrap(True)
                value_label.setStyleSheet("color: #666; padding-left: 10px;")
                prop_layout.addWidget(value_label, 1)
                
                layout.addLayout(prop_layout)
        
        layout.addStretch()
    
    def _format_key(self, key: str) -> str:
        """Format a property key for display.
        
        Args:
            key: The property key
            
        Returns:
            Formatted key string
        """
        return key.replace('_', ' ').title()


class QuadsetTabWidget(QWidget):
    """Tab widget for displaying quadset analysis."""
    
    number_link_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the quadset tab widget."""
        super().__init__(parent)
        
        self.service = NumberDictionaryService()
        self.current_number = 0
        self.current_analysis: Optional[Dict[str, Any]] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        self.header_label = QLabel("Quadset Analysis")
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
        
        # Scroll area for content
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
        self.header_label.setText("Quadset Analysis")
        
        # Clear existing content
        self._clear_content()
        
        placeholder = QLabel("Select a number to view its quadset analysis")
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
        """Load quadset analysis for a specific number.
        
        Args:
            number: The number to analyze
        """
        self.current_number = number
        self.header_label.setText(f"Quadset Analysis for {number}")
        
        try:
            # Get quadset analysis
            self.current_analysis = self.service.get_quadset_analysis(number)
            
            # Clear existing content
            self._clear_content()
            
            # Create analysis display
            self._create_analysis_display()
            
        except Exception as e:
            self._show_error(f"Error loading quadset analysis: {str(e)}")
    
    def _create_analysis_display(self):
        """Create the analysis display from the current analysis data."""
        if not self.current_analysis:
            self._show_error("No analysis data available")
            return
        
        # Check for error in analysis
        if "error" in self.current_analysis:
            self._show_error(self.current_analysis["error"])
            return
        
        # Quadset Numbers Section
        quadset_group = QGroupBox("Quadset Numbers")
        quadset_layout = QVBoxLayout(quadset_group)
        
        # Extract quadset numbers from the analysis
        base_number = self.current_analysis.get("base_number", self.current_number)
        
        # Get quadset properties which contain the actual quadset numbers
        quadset_props = self.current_analysis.get("quadset_properties", {})
        
        # Extract numbers from the nested structure
        # The structure is: {"base": {"number": 42, "ternary": "1120", ...}, ...}
        base_info = quadset_props.get("base", {})
        conrune_info = quadset_props.get("conrune", {})
        reversal_info = quadset_props.get("ternary_reversal", {})
        reversal_conrune_info = quadset_props.get("reversal_conrune", {})
        
        # Extract the actual numbers
        base_num = base_info.get("number") if isinstance(base_info, dict) else base_info
        conrune_num = conrune_info.get("number") if isinstance(conrune_info, dict) else conrune_info
        reversal_num = reversal_info.get("number") if isinstance(reversal_info, dict) else reversal_info
        reversal_conrune_num = reversal_conrune_info.get("number") if isinstance(reversal_conrune_info, dict) else reversal_conrune_info
        
        # Create number widgets for each quadset number
        if isinstance(base_num, int):
            base_widget = QuadsetNumberWidget("Base", base_num, base_num == self.current_number)
            base_widget.number_clicked.connect(self.number_link_requested.emit)
            quadset_layout.addWidget(base_widget)
        
        if isinstance(conrune_num, int):
            conrune_widget = QuadsetNumberWidget("Conrune", conrune_num, conrune_num == self.current_number)
            conrune_widget.number_clicked.connect(self.number_link_requested.emit)
            quadset_layout.addWidget(conrune_widget)
        
        if isinstance(reversal_num, int):
            reversal_widget = QuadsetNumberWidget("Ternary Reversal", reversal_num, reversal_num == self.current_number)
            reversal_widget.number_clicked.connect(self.number_link_requested.emit)
            quadset_layout.addWidget(reversal_widget)
        
        if isinstance(reversal_conrune_num, int):
            reversal_conrune_widget = QuadsetNumberWidget("Reversal Conrune", reversal_conrune_num, reversal_conrune_num == self.current_number)
            reversal_conrune_widget.number_clicked.connect(self.number_link_requested.emit)
            quadset_layout.addWidget(reversal_conrune_widget)
        
        # If no quadset numbers were found, show a message
        if not any(isinstance(x, int) for x in [conrune_num, reversal_num, reversal_conrune_num]):
            no_quadset_label = QLabel("No quadset numbers available for this number")
            no_quadset_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_quadset_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #7f8c8d;
                    padding: 20px;
                    font-style: italic;
                }
            """)
            quadset_layout.addWidget(no_quadset_label)
        
        self.content_layout.addWidget(quadset_group)
        
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