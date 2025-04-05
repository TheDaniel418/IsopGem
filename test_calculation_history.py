"""Test script for checking the calculation history panel functionality."""

import os
import sys
import shutil
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from gematria.repositories.tag_repository import TagRepository
from gematria.repositories.calculation_repository import CalculationRepository
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.gematria_service import GematriaService
from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel


class TestWindow(QMainWindow):
    """Test window for displaying the calculation history panel."""
    
    def __init__(self, test_dir):
        super().__init__()
        self.setWindowTitle("Calculation History Test")
        self.setGeometry(100, 100, 1000, 700)
        self.test_dir = test_dir
        
        # Setup test data directory
        os.makedirs(test_dir, exist_ok=True)
        
        # Initialize service with test directory
        self.db_service = CalculationDatabaseService(str(test_dir))
        
        # Create the gematria service and set its db_service attribute to our test db_service
        self.gematria_service = GematriaService()
        # Replace the default db_service with our test one
        self.gematria_service.db_service = self.db_service
        
        # Create some test data
        self._create_test_data()
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QVBoxLayout(central)
        
        # Create and add the calculation history panel
        self.history_panel = CalculationHistoryPanel()
        layout.addWidget(self.history_panel)
        
        # Refresh to load the test data
        self.history_panel.refresh()

    def _create_test_data(self):
        """Create some test calculations and tags for the test."""
        # Sample Hebrew values to test
        test_values = [
            ("אלהים", CalculationType.MISPAR_HECHRACHI, "The Hebrew word for God (Elohim)"),
            ("יהוה", CalculationType.MISPAR_HECHRACHI, "The Tetragrammaton (YHVH)"),
            ("אדם", CalculationType.MISPAR_HECHRACHI, "The Hebrew word for Man (Adam)"),
            ("תורה", CalculationType.MISPAR_HECHRACHI, "The Hebrew word for Torah"),
            ("ישראל", CalculationType.MISPAR_HECHRACHI, "The Hebrew word for Israel"),
            ("אמת", CalculationType.MISPAR_GADOL, "The Hebrew word for Truth (Emet)"),
            ("שלום", CalculationType.MISPAR_GADOL, "The Hebrew word for Peace (Shalom)"),
            ("משיח", CalculationType.MISPAR_KATAN, "The Hebrew word for Messiah (Mashiach)"),
            ("חיים", CalculationType.MISPAR_KATAN, "The Hebrew word for Life (Chaim)"),
            ("אחד", CalculationType.MISPAR_SIDURI, "The Hebrew word for One (Echad)")
        ]
        
        # Get the default tags
        tags = self.db_service.get_all_tags()
        
        # Create the test calculations
        for i, (text, method, note) in enumerate(test_values):
            # Calculate and save
            if i < 5:  # Make half of them favorites
                is_favorite = True
            else:
                is_favorite = False
                
            # Calculate with different tag combinations
            tag_ids = []
            if i % 3 == 0:  # Every 3rd item gets the first tag
                tag_ids.append(tags[0].id)
            if i % 2 == 0:  # Every 2nd item gets the second tag
                tag_ids.append(tags[1].id)
            if i % 5 == 0:  # Every 5th item gets the third tag
                tag_ids.append(tags[2].id)
                
            # Calculate the value
            value = self.gematria_service.calculate(text, method)
            
            # Create the calculation result
            calc = CalculationResult(
                input_text=text,
                calculation_type=method,
                result_value=value,
                notes=note,
                tags=tag_ids,
                favorite=is_favorite
            )
            
            # Save it
            self.db_service.save_calculation(calc)
            
        print(f"Created {len(test_values)} test calculations")


def main():
    """Main function to run the test."""
    # Create a test directory
    test_dir = Path("./test_history_data")
    
    try:
        # Create test application
        app = QApplication(sys.argv)
        
        # Create and show the test window
        window = TestWindow(test_dir)
        window.show()
        
        print("\nTest UI launched. Please interact with the calculation history panel.")
        print("Close the window when finished testing.\n")
        
        # Run the application
        sys.exit(app.exec())
        
    finally:
        # Clean up the test directory when done
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("Test cleanup completed")


if __name__ == "__main__":
    main() 