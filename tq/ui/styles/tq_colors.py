"""
Purpose: Provides color schemes and styling utilities for TQ components

This file is part of the tq pillar and serves as a styling utility.
It defines color schemes, gradients, and styling constants used across
the TQ pillar UI components for visual consistency.

Key components:
- TQColors: Class with color constants for TQ components
- get_element_color: Function to get colors for ternary elements
- apply_tq_styles: Function to apply TQ styling to widgets

Dependencies:
- PyQt6: For QColor and styling components
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QWidget


class TQColors:
    """Color constants for TQ components."""
    
    # Main theme colors
    PRIMARY = "#3F51B5"  # Indigo
    PRIMARY_LIGHT = "#7986CB"
    PRIMARY_DARK = "#303F9F"
    
    SECONDARY = "#FF4081"  # Pink
    SECONDARY_LIGHT = "#FF80AB"
    SECONDARY_DARK = "#F50057"
    
    ACCENT = "#009688"  # Teal
    ACCENT_LIGHT = "#4DB6AC"
    ACCENT_DARK = "#00796B"
    
    # Background colors
    BACKGROUND_LIGHT = "#F5F5F5"
    BACKGROUND_MEDIUM = "#E0E0E0"
    BACKGROUND_DARK = "#424242"
    
    # Text colors
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_LIGHT = "#FFFFFF"
    
    # Element colors (Aperture, Surge, Lattice)
    APERTURE = "#2196F3"  # Blue
    APERTURE_LIGHT = "#90CAF9"
    APERTURE_DARK = "#1976D2"
    
    SURGE = "#FF9800"  # Orange
    SURGE_LIGHT = "#FFCC80"
    SURGE_DARK = "#F57C00"
    
    LATTICE = "#4CAF50"  # Green
    LATTICE_LIGHT = "#A5D6A7"
    LATTICE_DARK = "#388E3C"
    
    # Status colors
    SUCCESS = "#4CAF50"  # Green
    WARNING = "#FFC107"  # Amber
    ERROR = "#F44336"  # Red
    INFO = "#2196F3"  # Blue
    
    # Grid colors
    GRID_HEADER = "#E3F2FD"  # Light blue
    GRID_ALTERNATE = "#F5F5F5"  # Light grey
    GRID_BORDER = "#BDBDBD"  # Medium grey
    
    # Quadset specific colors
    BASE_NUMBER = "#3F51B5"  # Indigo
    CONRUNE = "#009688"  # Teal
    REVERSAL = "#FF4081"  # Pink
    REVERSAL_CONRUNE = "#FF9800"  # Orange
    
    # Quadset analysis colors
    DIFFERENCE_BG = "#E8F5E9"  # Light green
    SUM_BG = "#FFF8E1"  # Light amber


def get_element_color(element: int, light: bool = False) -> str:
    """Get the color for a ternary element.
    
    Args:
        element: The ternary element (0, 1, or 2)
        light: Whether to use the light version of the color
        
    Returns:
        The color as a hex string
    """
    if element == 0:  # Aperture
        return TQColors.APERTURE_LIGHT if light else TQColors.APERTURE
    elif element == 1:  # Surge
        return TQColors.SURGE_LIGHT if light else TQColors.SURGE
    elif element == 2:  # Lattice
        return TQColors.LATTICE_LIGHT if light else TQColors.LATTICE
    else:
        return TQColors.TEXT_SECONDARY


def apply_tq_styles(widget: QWidget, is_dark: bool = False) -> None:
    """Apply TQ styling to a widget.
    
    Args:
        widget: The widget to style
        is_dark: Whether to use dark mode styling
    """
    # Set base palette
    palette = QPalette()
    
    if is_dark:
        # Dark mode
        palette.setColor(QPalette.ColorRole.Window, QColor(TQColors.BACKGROUND_DARK))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(TQColors.TEXT_LIGHT))
        palette.setColor(QPalette.ColorRole.Base, QColor("#303030"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3A3A3A"))
        palette.setColor(QPalette.ColorRole.Text, QColor(TQColors.TEXT_LIGHT))
        palette.setColor(QPalette.ColorRole.Button, QColor(TQColors.PRIMARY_DARK))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(TQColors.TEXT_LIGHT))
        palette.setColor(QPalette.ColorRole.Link, QColor(TQColors.PRIMARY_LIGHT))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(TQColors.PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(TQColors.TEXT_LIGHT))
    else:
        # Light mode
        palette.setColor(QPalette.ColorRole.Window, QColor(TQColors.BACKGROUND_LIGHT))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(TQColors.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(TQColors.BACKGROUND_MEDIUM))
        palette.setColor(QPalette.ColorRole.Text, QColor(TQColors.TEXT_PRIMARY))
        palette.setColor(QPalette.ColorRole.Button, QColor(TQColors.PRIMARY))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(TQColors.TEXT_LIGHT))
        palette.setColor(QPalette.ColorRole.Link, QColor(TQColors.PRIMARY_DARK))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(TQColors.PRIMARY))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(TQColors.TEXT_LIGHT))
    
    widget.setPalette(palette)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    widget.setFont(font)
    
    # Apply stylesheet
    widget.setStyleSheet(f"""
        QFrame {{
            border-radius: 6px;
            background-color: white;
            border: 1px solid {TQColors.GRID_BORDER};
        }}
        
        QLabel[isTitle="true"] {{
            font-size: 14pt;
            font-weight: bold;
            color: {TQColors.PRIMARY_DARK};
            padding: 8px;
        }}
        
        QLabel[isSubtitle="true"] {{
            font-size: 12pt;
            font-weight: bold;
            color: {TQColors.PRIMARY};
            padding: 6px;
        }}
        
        QLabel[isHeader="true"] {{
            font-weight: bold;
            color: {TQColors.TEXT_PRIMARY};
            background-color: {TQColors.GRID_HEADER};
            padding: 6px;
            border-radius: 4px;
        }}
        
        QLabel[isValue="true"] {{
            font-family: 'Courier New';
            padding: 6px;
            background-color: {TQColors.BACKGROUND_LIGHT};
            border: 1px solid {TQColors.GRID_BORDER};
            border-radius: 4px;
        }}
        
        QPushButton {{
            background-color: {TQColors.PRIMARY};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: {TQColors.PRIMARY_DARK};
        }}
        
        QPushButton:pressed {{
            background-color: {TQColors.PRIMARY_DARK};
        }}
        
        QLineEdit {{
            padding: 8px;
            border: 1px solid {TQColors.GRID_BORDER};
            border-radius: 4px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {TQColors.PRIMARY};
        }}
    """)
