"""
Purpose: Provides a widget for displaying house positions in a table format.

This file is part of the astrology pillar and serves as a UI component.
It provides a widget for displaying house positions, signs, and
other information in a tabular format.

Key components:
- NewHousePositionsWidget: Widget for displaying house positions

Dependencies:
- PyQt6: For UI components
- astrology.models: For astrological data models
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtGui import QColor

from loguru import logger

from astrology.models.chart import Chart


class NewHousePositionsWidget(QWidget):
    """Widget for displaying house positions in a table format."""
    
    def __init__(self, parent=None):
        """Initialize the house positions widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Chart data
        self.chart = None
        
        # Initialize UI
        self._init_ui()
        
        logger.debug("NewHousePositionsWidget initialized")
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "House", "Sign", "Cusp Position", "Width", "Planets"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Add table to layout
        layout.addWidget(self.table)
        
        # Add a note about house systems
        note = QLabel("House positions are calculated using the selected house system")
        note.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(note)
    
    def set_chart(self, chart: Chart) -> None:
        """Set the chart to display.
        
        Args:
            chart: The chart to display
        """
        self.chart = chart
        logger.debug(f"NewHousePositionsWidget: Setting chart with {len(chart.houses) if chart and hasattr(chart, 'houses') else 0} houses")
        self._update_table()
    
    def _update_table(self):
        """Update the table with the current chart data."""
        if not self.chart or not hasattr(self.chart, 'houses') or not self.chart.houses:
            logger.warning("No houses data available in chart")
            self.table.setRowCount(0)
            return
        
        # Get the houses
        houses = self.chart.houses
        logger.debug(f"NewHousePositionsWidget: Processing {len(houses)} houses")
        
        # Sort houses by number
        houses = sorted(houses, key=lambda h: h.number if hasattr(h, 'number') else 0)
        
        # Set the number of rows
        self.table.setRowCount(len(houses))
        
        # Fill the table
        for i, house in enumerate(houses):
            try:
                # House number
                house_item = QTableWidgetItem(str(house.number))
                house_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 0, house_item)
                
                # Sign
                if hasattr(house, 'sign') and house.sign:
                    sign_item = QTableWidgetItem(house.sign)
                    sign_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, 1, sign_item)
                else:
                    self.table.setItem(i, 1, QTableWidgetItem(""))
                
                # Cusp Position
                if hasattr(house, 'cusp_degree') and house.cusp_degree is not None:
                    # Format as degrees, minutes, seconds
                    degrees = int(house.cusp_degree)
                    minutes = int((house.cusp_degree - degrees) * 60)
                    seconds = int(((house.cusp_degree - degrees) * 60 - minutes) * 60)
                    
                    position_str = f"{degrees}° {minutes:02d}' {seconds:02d}\""
                    
                    position_item = QTableWidgetItem(position_str)
                    position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, 2, position_item)
                else:
                    self.table.setItem(i, 2, QTableWidgetItem(""))
                
                # Width
                if hasattr(house, 'cusp_degree') and hasattr(house, 'end_degree') and house.cusp_degree is not None and house.end_degree is not None:
                    # Calculate width, handling the case where the house crosses 0°
                    if house.end_degree < house.cusp_degree:
                        width = house.end_degree + 360 - house.cusp_degree
                    else:
                        width = house.end_degree - house.cusp_degree
                    
                    width_str = f"{width:.2f}°"
                    width_item = QTableWidgetItem(width_str)
                    width_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, 3, width_item)
                else:
                    self.table.setItem(i, 3, QTableWidgetItem(""))
                
                # Planets
                if hasattr(house, 'planets') and house.planets:
                    planets_str = ", ".join(house.planets)
                    planets_item = QTableWidgetItem(planets_str)
                    planets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, 4, planets_item)
                else:
                    self.table.setItem(i, 4, QTableWidgetItem(""))
            except Exception as e:
                logger.error(f"Error processing house {i}: {e}")
                # Fill with empty cells
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(""))
    
    def sizeHint(self):
        """Get the suggested size for the widget.
        
        Returns:
            Suggested size
        """
        return QSize(600, 400)
    
    def minimumSizeHint(self):
        """Get the minimum suggested size for the widget.
        
        Returns:
            Minimum suggested size
        """
        return QSize(400, 300)
