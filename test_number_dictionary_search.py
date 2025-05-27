#!/usr/bin/env python3
"""
Test script for the Number Dictionary search functionality.

This script tests the search window and creates some sample notes to search through.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from gematria.ui.windows.number_dictionary_search_window import NumberDictionarySearchWindow
from gematria.services.number_dictionary_service import NumberDictionaryService
from gematria.models.number_note import NumberNote


def create_sample_notes():
    """Create some sample notes for testing."""
    print("📝 Creating sample notes for testing...")
    
    service = NumberDictionaryService()
    
    # Sample notes with different content
    sample_notes = [
        NumberNote(
            number=7,
            title="The Sacred Seven",
            content="Seven is considered a sacred number in many traditions. It represents completion, perfection, and spiritual awakening. Found in the seven days of creation, seven chakras, seven heavens."
        ),
        NumberNote(
            number=12,
            title="Cosmic Order",
            content="Twelve represents cosmic order and completeness. Twelve zodiac signs, twelve apostles, twelve tribes of Israel. This number appears frequently in religious and mystical contexts."
        ),
        NumberNote(
            number=42,
            title="Answer to Everything",
            content="According to Douglas Adams, 42 is the answer to the ultimate question of life, the universe, and everything. In gematria, this number has interesting properties and connections."
        ),
        NumberNote(
            number=108,
            title="Sacred Hindu Number",
            content="108 is a sacred number in Hinduism and Buddhism. There are 108 beads on a mala, 108 Upanishads, and 108 marma points in Ayurveda. The number has deep spiritual significance."
        ),
        NumberNote(
            number=666,
            title="Number of the Beast",
            content="666 is known as the number of the beast in Christian tradition. However, in gematria, it has other meanings and can represent the sun, material world, and human consciousness."
        ),
        NumberNote(
            number=777,
            title="Divine Perfection",
            content="777 represents divine perfection and completion. It's considered a highly spiritual number, often associated with divine intervention and spiritual awakening."
        )
    ]
    
    # Save the sample notes
    for note in sample_notes:
        saved_note = service.save_note(note)
        print(f"✅ Created note for number {saved_note.number}: {saved_note.title}")
    
    print(f"📚 Created {len(sample_notes)} sample notes")


def test_search_window():
    """Test the Number Dictionary search window."""
    print("🔍 Testing Number Dictionary Search Window...")
    
    app = QApplication(sys.argv)
    
    # Create sample notes first
    create_sample_notes()
    
    # Create and show the search window
    search_window = NumberDictionarySearchWindow()
    search_window.show()
    
    # Connect the signal to print when a number is requested
    def on_number_requested(number):
        print(f"🎯 User requested to open Number Dictionary for number: {number}")
    
    search_window.open_number_requested.connect(on_number_requested)
    
    print("✅ Number Dictionary search window created successfully!")
    print("💡 You can now:")
    print("   - Search for terms like 'sacred', 'divine', 'spiritual'")
    print("   - Browse all notes by clicking 'Show All'")
    print("   - Preview note content in the right panel")
    print("   - Double-click or use 'Open in Dictionary' to open a number")
    print("   - Try searching for specific numbers like '42' or '777'")
    
    return app.exec()


if __name__ == "__main__":
    test_search_window() 