#!/usr/bin/env python3
"""
Test script for the Database Entries tab in the Number Dictionary window.

This script tests the new Database Entries tab functionality, including:
- Creating test calculation entries
- Loading entries for specific numbers
- Double-click functionality to open calculation details
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.windows.number_dictionary_window import NumberDictionaryWindow


def create_test_calculations():
    """Create test calculation entries for testing."""
    try:
        from shared.services.service_locator import ServiceLocator
        calc_db_service = ServiceLocator.get(CalculationDatabaseService)
        
        print("📝 Creating test calculations...")
        
        # Test calculations for number 42
        test_calculations = [
            CalculationResult(
                input_text="life",
                result_value=42,
                calculation_type=CalculationType.ENGLISH_TQ_STANDARD_VALUE,
                timestamp=datetime.now(),
                notes="The answer to life, the universe, and everything",
                favorite=True
            ),
            CalculationResult(
                input_text="world",
                result_value=42,
                calculation_type=CalculationType.ENGLISH_TQ_REDUCED_VALUE,
                timestamp=datetime.now(),
                notes="Another word that equals 42"
            ),
            CalculationResult(
                input_text="אמת",  # Hebrew for "truth"
                result_value=42,
                calculation_type=CalculationType.HEBREW_STANDARD_VALUE,
                timestamp=datetime.now(),
                notes="Hebrew word for truth"
            ),
        ]
        
        # Save test calculations
        for calc in test_calculations:
            if calc_db_service.save_calculation(calc):
                print(f"  ✅ Saved: '{calc.input_text}' = {calc.result_value}")
            else:
                print(f"  ❌ Failed to save: '{calc.input_text}' = {calc.result_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test calculations: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_entries_tab():
    """Test the Database Entries tab functionality."""
    app = QApplication(sys.argv)
    
    print("🧪 Testing Database Entries Tab")
    print("=" * 50)
    
    try:
        # Register the CalculationDatabaseService in ServiceLocator
        print("🔧 Registering services...")
        from shared.services.service_locator import ServiceLocator
        
        # Create and register the calculation database service with data directory
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        calc_db_service = CalculationDatabaseService(data_dir=data_dir)
        ServiceLocator.register(CalculationDatabaseService, calc_db_service)
        
        # Create test calculations first
        if not create_test_calculations():
            print("❌ Failed to create test calculations")
            return False
            
        print("✅ Test calculations created successfully")
        
        # Create Number Dictionary windows for testing
        print("\n🪟 Creating Number Dictionary windows...")
        
        # Test with number 42 (should have entries)
        window_42 = NumberDictionaryWindow()
        window_42.set_number(42)
        window_42.setWindowTitle("Number Dictionary - 42 (with entries)")
        window_42.show()
        
        # Test with number 100 (should have no entries)
        window_100 = NumberDictionaryWindow()
        window_100.set_number(100)
        window_100.setWindowTitle("Number Dictionary - 100 (no entries)")
        window_100.show()
        
        print("✅ Number Dictionary windows created")
        print("\n📋 Instructions:")
        print("1. Check the 'Database Entries' tab in both windows")
        print("2. Window for 42 should show calculation entries")
        print("3. Window for 100 should show 'No entries found'")
        print("4. Double-click any entry in the 42 window to test calculation details")
        print("5. Close windows when done testing")
        
        # Keep windows open for testing
        app.exec()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_database_entries_tab() 