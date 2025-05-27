"""
Number Dictionary Window for the Gematria module.

This window provides a comprehensive interface for exploring numbers with:
- Note-taking capabilities with rich text editing
- Number properties display with enhanced formatting
- Quadset analysis showing related numbers
- Database entries showing all calculations for the number
- Number navigation and linking system
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gematria.services.number_dictionary_service import NumberDictionaryService
from gematria.ui.widgets.note_tab_widget import NoteTabWidget
from gematria.ui.widgets.properties_tab_widget import PropertiesTabWidget
from gematria.ui.widgets.quadset_tab_widget import QuadsetTabWidget
from gematria.ui.widgets.database_entries_tab_widget import DatabaseEntriesTabWidget
from shared.ui.window_management import AuxiliaryWindow

class NumberDictionaryWindow(AuxiliaryWindow):
    """Window for exploring numbers with notes, properties, and quadset analysis."""
    
    # Signal emitted when user wants to navigate to a different number
    number_requested = pyqtSignal(int)
    
    def __init__(self, initial_number: int = 1, parent=None):
        super().__init__(f"Number Dictionary - {initial_number}", parent)
        self.current_number = initial_number
        self.service = NumberDictionaryService()
        
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._connect_signals()
        self._load_number(initial_number)
    
    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Number input section
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("Number:"))
        
        self.number_input = QLineEdit()
        self.number_input.setValidator(QIntValidator(1, 999999))
        self.number_input.setText(str(self.current_number))
        self.number_input.setMaximumWidth(100)
        input_layout.addWidget(self.number_input)
        
        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.prev_button.setMaximumWidth(80)
        input_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next")
        self.next_button.setMaximumWidth(80)
        input_layout.addWidget(self.next_button)
        
        input_layout.addStretch()
        
        # Save and Delete buttons
        self.save_button = QPushButton("Save Note")
        self.save_button.setMaximumWidth(100)
        input_layout.addWidget(self.save_button)
        
        self.delete_button = QPushButton("Delete Note")
        self.delete_button.setMaximumWidth(100)
        input_layout.addWidget(self.delete_button)
        
        layout.addLayout(input_layout)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Note tab
        self.note_tab = NoteTabWidget()
        self.tab_widget.addTab(self.note_tab, "Notes")
        
        # Properties tab - back to original implementation
        self.properties_tab = PropertiesTabWidget()
        self.tab_widget.addTab(self.properties_tab, "Properties")
        
        # Quadset tab
        self.quadset_tab = QuadsetTabWidget()
        self.tab_widget.addTab(self.quadset_tab, "Quadset Analysis")
        
        # Database entries tab
        self.database_entries_tab = DatabaseEntriesTabWidget()
        self.tab_widget.addTab(self.database_entries_tab, "Database Entries")
        
        layout.addWidget(self.tab_widget)
    
    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        self.number_input.returnPressed.connect(self._on_number_input_changed)
        self.prev_button.clicked.connect(self._go_to_previous)
        self.next_button.clicked.connect(self._go_to_next)
        self.save_button.clicked.connect(self._save_note)
        self.delete_button.clicked.connect(self._delete_note)
        
        # Connect note tab signals - use the correct signal name
        self.note_tab.number_link_requested.connect(self._navigate_to_number)
        
        # Connect quadset tab signals - use the correct signal name
        self.quadset_tab.number_link_requested.connect(self._navigate_to_number)
    
    def _on_number_input_changed(self):
        """Handle when the number input changes."""
        try:
            number = int(self.number_input.text())
            if number > 0:
                self._load_number(number)
        except ValueError:
            # Reset to current number if invalid input
            self.number_input.setText(str(self.current_number))
    
    def _go_to_previous(self):
        """Navigate to the previous number."""
        if self.current_number > 1:
            self._load_number(self.current_number - 1)
    
    def _go_to_next(self):
        """Navigate to the next number."""
        self._load_number(self.current_number + 1)
    
    def _navigate_to_number(self, number: int):
        """Navigate to a specific number."""
        self._load_number(number)
    
    def _load_number(self, number: int):
        """Load a specific number and update all tabs."""
        try:
            self.current_number = number
            self.number_input.setText(str(number))
            self.setWindowTitle(f"Number Dictionary - {number}")
            
            # Update note tab
            note = self.service.get_or_create_note(number)
            self.note_tab.load_note(note)
            
            # Update properties tab
            self.properties_tab.load_number(number)
            
            # Update quadset tab - use the correct method name
            self.quadset_tab.load_number(number)
            
            # Update database entries tab
            self.database_entries_tab.load_number(number)
            
            # Update button states
            self.prev_button.setEnabled(number > 1)
            self.delete_button.setEnabled(note is not None and note.id is not None)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load number {number}:\n{str(e)}"
            )
    
    def _save_note(self):
        """Save the current note."""
        try:
            note = self.note_tab.get_note()
            note.number = self.current_number
            self.service.save_note(note)
            QMessageBox.information(self, "Success", f"Note saved for number {self.current_number}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving note: {e}")
    
    def _delete_note(self):
        """Delete the current note."""
        try:
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the note for number {self.current_number}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.service.delete_note(self.current_number)
                # Reload to show empty note
                self._load_number(self.current_number)
                QMessageBox.information(self, "Success", f"Note deleted for number {self.current_number}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deleting note: {e}")
    
    def set_number(self, number: int):
        """Set the number to display (external interface)."""
        self._load_number(number)
        
        # Bring window to front
        self.raise_()
        self.activateWindow()


def main():
    """Main function for testing the Number Dictionary window."""
    import sys
    
    app = QApplication(sys.argv)
    
    # Get initial number from command line or use default
    initial_number = 1
    if len(sys.argv) > 1:
        try:
            initial_number = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default: 1")
    
    window = NumberDictionaryWindow(initial_number)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 