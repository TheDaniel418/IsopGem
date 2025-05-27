#!/usr/bin/env python3
"""
Complete Number Dictionary Features Test.

This script demonstrates all the features of the Number Dictionary system:
1. Number Dictionary window with tabbed interface
2. Search functionality across all notes
3. Rich text editing with RTF support
4. Number properties with enhanced formatting
5. Quadset analysis with navigation
6. Cross-linking between numbers
7. Integration with main Gematria tab
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from shared.ui.window_management import WindowManager, TabManager
from gematria.ui.gematria_tab import GematriaTab
from gematria.services.number_dictionary_service import NumberDictionaryService
from gematria.models.number_note import NumberNote


def create_comprehensive_test_data():
    """Create comprehensive test data for all features."""
    print("📚 Creating comprehensive test data...")
    
    service = NumberDictionaryService()
    
    # Test notes with various features
    test_notes = [
        NumberNote(
            number=1,
            title="Unity and Beginning",
            content="The number 1 represents unity, beginning, and the source of all numbers. In many traditions, it symbolizes the divine unity and the starting point of creation. Related numbers: 11, 111, 1111.",
            linked_numbers=[11, 111, 1111]
        ),
        NumberNote(
            number=7,
            title="Sacred Perfection",
            content="Seven is the number of spiritual perfection and completion. Found in seven days of creation, seven chakras, seven heavens. It's considered the most mystical number. Connected to: 14, 21, 77.",
            linked_numbers=[14, 21, 77]
        ),
        NumberNote(
            number=12,
            title="Cosmic Order",
            content="Twelve represents cosmic order and divine government. 12 zodiac signs, 12 apostles, 12 tribes. This number appears in many sacred contexts. See also: 24, 144.",
            linked_numbers=[24, 144]
        ),
        NumberNote(
            number=42,
            title="Answer to Everything",
            content="According to Douglas Adams, 42 is the answer to life, universe, and everything. In gematria, it has fascinating properties. This abundant number connects to 6 and 7 (6×7=42).",
            linked_numbers=[6, 7]
        ),
        NumberNote(
            number=108,
            title="Sacred Hindu Number",
            content="108 is sacred in Hinduism and Buddhism. 108 beads on a mala, 108 Upanishads, 108 marma points. The number has deep spiritual significance across Eastern traditions.",
            linked_numbers=[54, 216]
        ),
        NumberNote(
            number=666,
            title="Solar Number",
            content="While known as the 'number of the beast', 666 is actually a solar number representing the material world and human consciousness. It's the sum of the first 36 numbers.",
            linked_numbers=[36, 216, 1296]
        ),
        NumberNote(
            number=777,
            title="Divine Perfection",
            content="777 represents divine perfection and spiritual completion. It's considered highly spiritual, often associated with divine intervention and awakening.",
            linked_numbers=[111, 222, 333]
        )
    ]
    
    # Save all test notes
    for note in test_notes:
        saved_note = service.save_note(note)
        print(f"✅ Created note for {saved_note.number}: {saved_note.title}")
    
    print(f"📝 Created {len(test_notes)} comprehensive test notes with cross-links")


class ComprehensiveTestWindow(QMainWindow):
    """Test window that demonstrates all Number Dictionary features."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IsopGem - Complete Number Dictionary Feature Test")
        self.setGeometry(50, 50, 1400, 900)
        
        # Create managers
        self.window_manager = WindowManager(self)
        self.tab_manager = TabManager()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create Gematria tab
        self.gematria_tab = GematriaTab(self.tab_manager, self.window_manager)
        layout.addWidget(self.gematria_tab)
        
        print("✅ Comprehensive test window created")


def demonstrate_all_features():
    """Demonstrate all Number Dictionary features systematically."""
    print("🚀 Starting comprehensive feature demonstration...")
    
    app = QApplication(sys.argv)
    
    # Create test data first
    create_comprehensive_test_data()
    
    # Create main window
    main_window = ComprehensiveTestWindow()
    main_window.show()
    
    print("\n🎯 Complete Number Dictionary System Features:")
    print("=" * 60)
    print("📖 CORE FEATURES:")
    print("   • Multi-tab interface (Notes, Properties, Quadset Analysis)")
    print("   • Rich text editing with RTF support")
    print("   • Number navigation with previous/next buttons")
    print("   • Save/delete functionality for notes")
    print("   • Cross-linking between numbers")
    print()
    print("🔍 SEARCH FEATURES:")
    print("   • Full-text search across all notes")
    print("   • Search by title and content")
    print("   • Preview pane with note details")
    print("   • Direct navigation to numbers from search")
    print()
    print("📊 PROPERTIES FEATURES:")
    print("   • Enhanced boolean formatting (Yes/No instead of True/False)")
    print("   • Prime ordinal display (e.g., 'Yes (#4)' for 4th prime)")
    print("   • Abundance/deficiency amounts (e.g., 'Yes (abundant by 4)')")
    print("   • Comprehensive mathematical properties")
    print()
    print("🎲 QUADSET FEATURES:")
    print("   • Base, conrune, reversal, reversal_conrune analysis")
    print("   • Clickable navigation between related numbers")
    print("   • TQ grid integration")
    print()
    print("🔗 INTEGRATION FEATURES:")
    print("   • Seamless integration with main Gematria tab")
    print("   • Multiple window instances supported")
    print("   • Signal-based communication between components")
    print("   • Window management with proper z-ordering")
    
    # Demonstrate features with timed actions
    def demo_step_1():
        print("\n🎬 DEMO STEP 1: Opening Number Dictionary for number 42...")
        main_window.gematria_tab.open_number_dictionary_with_number(42)
    
    def demo_step_2():
        print("🎬 DEMO STEP 2: Opening search window...")
        main_window.gematria_tab._open_number_dictionary_search()
    
    def demo_step_3():
        print("🎬 DEMO STEP 3: Opening another Number Dictionary for number 777...")
        main_window.gematria_tab.open_number_dictionary_with_number(777)
    
    def demo_step_4():
        print("🎬 DEMO STEP 4: Opening Number Dictionary for number 12 (abundant number)...")
        main_window.gematria_tab.open_number_dictionary_with_number(12)
        
    def demo_complete():
        print("\n✨ DEMONSTRATION COMPLETE!")
        print("🎯 You now have multiple windows open demonstrating:")
        print("   • Number Dictionary windows for numbers 42, 777, and 12")
        print("   • Search window for browsing all notes")
        print("   • Cross-linked notes with clickable number references")
        print("   • Enhanced property formatting")
        print("   • Quadset analysis with navigation")
        print("\n💡 Try these interactions:")
        print("   1. Click linked numbers in notes to navigate")
        print("   2. Search for terms like 'sacred', 'divine', 'spiritual'")
        print("   3. Check Properties tab for abundance/deficiency formatting")
        print("   4. Use Quadset Analysis tab to navigate related numbers")
        print("   5. Create new notes and test the rich text editor")
    
    # Schedule demonstrations
    QTimer.singleShot(1000, demo_step_1)
    QTimer.singleShot(3000, demo_step_2)
    QTimer.singleShot(5000, demo_step_3)
    QTimer.singleShot(7000, demo_step_4)
    QTimer.singleShot(9000, demo_complete)
    
    return app.exec()


if __name__ == "__main__":
    demonstrate_all_features() 