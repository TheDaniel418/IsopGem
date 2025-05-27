"""
Unit tests for the AncientDateSelector widget.

Author: IsopGemini
Created: 2024-08-06
Last Modified: 2024-08-06
Dependencies: PyQt6, pytest
"""

import pytest
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QApplication
import sys

from astrology.ui.widgets.date_selector import AncientDateSelector
from astrology.ui.dialogs.ancient_date_dialog import AncientDateDialog

# Create QApplication instance for the tests
@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_ancient_date_selector_creation(app):
    """Test that the AncientDateSelector can be created."""
    selector = AncientDateSelector()
    assert selector is not None

def test_ancient_date_selector_default_date(app):
    """Test that the AncientDateSelector has a valid default date."""
    selector = AncientDateSelector()
    assert selector.date().isValid()

def test_ancient_date_selector_set_date(app):
    """Test setting a date on the AncientDateSelector."""
    selector = AncientDateSelector()
    date = QDate(2000, 1, 1)
    selector.set_date(date)
    assert selector.date() == date

def test_ancient_date_selector_bce_date(app):
    """Test setting a BCE date on the AncientDateSelector."""
    selector = AncientDateSelector()
    
    # Set a BCE date via the year spinbox
    selector.year_spinbox.setValue(-500)  # 500 BCE
    selector.month_combo.setCurrentIndex(0)  # January
    selector.day_spinbox.setValue(1)  # 1st
    
    # Check the date
    date = selector.date()
    assert date.year() == -500
    assert date.month() == 1
    assert date.day() == 1
    
    # Check that BCE checkbox is checked
    assert selector.bce_checkbox.isChecked()

def test_ancient_date_selector_toggle_bce(app):
    """Test toggling BCE on the AncientDateSelector."""
    selector = AncientDateSelector()
    
    # Set a CE date
    selector.year_spinbox.setValue(500)  # 500 CE
    selector.month_combo.setCurrentIndex(0)  # January
    selector.day_spinbox.setValue(1)  # 1st
    
    # Toggle BCE
    selector.bce_checkbox.setChecked(True)
    
    # Check if year is negative now
    assert selector.year_spinbox.value() < 0
    
    # Toggle back to CE
    selector.bce_checkbox.setChecked(False)
    
    # Check if year is positive again
    assert selector.year_spinbox.value() > 0

def test_ancient_date_selector_days_in_month(app):
    """Test that the days in month are correct for different months and leap years."""
    selector = AncientDateSelector()
    
    # Test February in a non-leap year
    selector.year_spinbox.setValue(2023)
    selector.month_combo.setCurrentIndex(1)  # February (0-indexed)
    assert selector.day_spinbox.maximum() == 28
    
    # Test February in a leap year
    selector.year_spinbox.setValue(2024)
    selector.month_combo.setCurrentIndex(1)  # February
    assert selector.day_spinbox.maximum() == 29
    
    # Test February in a non-leap century year
    selector.year_spinbox.setValue(1900)
    selector.month_combo.setCurrentIndex(1)  # February
    assert selector.day_spinbox.maximum() == 28
    
    # Test February in a leap century year
    selector.year_spinbox.setValue(2000)
    selector.month_combo.setCurrentIndex(1)  # February
    assert selector.day_spinbox.maximum() == 29
    
    # Test a 31-day month
    selector.month_combo.setCurrentIndex(0)  # January
    assert selector.day_spinbox.maximum() == 31
    
    # Test a 30-day month
    selector.month_combo.setCurrentIndex(3)  # April
    assert selector.day_spinbox.maximum() == 30

def test_ancient_date_selector_very_old_date(app):
    """Test setting a very old date on the AncientDateSelector."""
    selector = AncientDateSelector()
    
    # Set a date well before the 1753 limitation
    selector.year_spinbox.setValue(-5000)  # 5000 BCE
    selector.month_combo.setCurrentIndex(5)  # June
    selector.day_spinbox.setValue(15)  # 15th
    
    # Check the date
    date = selector.date()
    assert date.year() == -5000
    assert date.month() == 6
    assert date.day() == 15

def test_ancient_date_selector_leap_year_bce(app):
    """Test leap year handling for BCE dates."""
    selector = AncientDateSelector()
    
    # 5 BCE should be a leap year (using astronomical year -4)
    selector.year_spinbox.setValue(-5)
    selector.bce_checkbox.setChecked(True)
    selector.month_combo.setCurrentIndex(1)  # February
    
    # Should have 29 days
    assert selector.day_spinbox.maximum() == 29
    
    # 100 BCE should not be a leap year (using astronomical year -99)
    selector.year_spinbox.setValue(-100)
    selector.month_combo.setCurrentIndex(1)  # February
    
    # Should have 28 days
    assert selector.day_spinbox.maximum() == 28 