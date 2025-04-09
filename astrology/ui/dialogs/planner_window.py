"""
Purpose: Astrological planner window.

This file is part of the astrology pillar and serves as a UI component.
It provides a window for the astrological daily planner, including
monthly calendar view and day view.
"""

from datetime import datetime
from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QFrame, QSizePolicy,
    QDialog, QMessageBox
)
from PyQt6.QtGui import QColor, QPalette, QFont

from astrology.services.planner_service import PlannerService
from astrology.services.chart_service import ChartService
from astrology.models.chart import Chart
from astrology.ui.widgets.planner.monthly_calendar_widget import MonthlyCalendarWidget
from astrology.ui.widgets.planner.day_view_widget import DayViewWidget


class PlannerWindow(QWidget):
    """Window for the astrological daily planner."""
    
    # Signal emitted when a chart is requested
    chart_requested = pyqtSignal(Chart)
    
    def __init__(self, parent=None):
        """Initialize the planner window.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Get the planner service
        self.planner_service = PlannerService.get_instance()
        
        # Get the chart service
        self.chart_service = ChartService.get_instance()
        
        # Initialize UI
        self._init_ui()
        
        logger.debug("PlannerWindow initialized")
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("Astrological Planner")
        self.resize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Add tabs
        self._add_month_tab()
        self._add_day_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Set default tab based on settings
        settings = self.planner_service.get_settings()
        if settings.default_view == "day":
            self.tabs.setCurrentIndex(1)
    
    def _add_month_tab(self):
        """Add the month tab."""
        # Create tab widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add monthly calendar widget
        self.month_widget = MonthlyCalendarWidget()
        self.month_widget.day_selected.connect(self._on_day_selected)
        layout.addWidget(self.month_widget)
        
        # Add tab
        self.tabs.addTab(tab, "Month")
    
    def _add_day_tab(self):
        """Add the day tab."""
        # Create tab widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Add day view widget
        self.day_widget = DayViewWidget()
        self.day_widget.date_changed.connect(self._on_date_changed)
        self.day_widget.chart_requested.connect(self._on_chart_requested)
        layout.addWidget(self.day_widget)
        
        # Add tab
        self.tabs.addTab(tab, "Day")
    
    def _on_day_selected(self, date: QDate):
        """Handle day selection from the monthly calendar.
        
        Args:
            date: Selected date
        """
        # Switch to day tab
        self.tabs.setCurrentIndex(1)
        
        # Update day view
        self.day_widget.set_date(date)
    
    def _on_date_changed(self, date: QDate):
        """Handle date change from the day view.
        
        Args:
            date: New date
        """
        # Update monthly calendar
        self.month_widget.set_date(date)
    
    def _on_chart_requested(self, chart: Chart):
        """Handle chart request from the day view.
        
        Args:
            chart: Chart to display
        """
        # Emit signal to parent
        self.chart_requested.emit(chart)
    
    def set_date(self, date: QDate):
        """Set the current date.
        
        Args:
            date: Date to set
        """
        # Update both views
        self.month_widget.set_date(date)
        self.day_widget.set_date(date)
