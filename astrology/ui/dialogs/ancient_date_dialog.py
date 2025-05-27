"""
Defines a dialog for selecting ancient dates beyond QDateEdit's 1753 limitation.

Author: IsopGemini
Created: 2024-08-06
Last Modified: 2024-08-06
Dependencies: PyQt6, AncientDateSelector
"""

from PyQt6.QtCore import QDate, pyqtSignal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from astrology.ui.widgets.date_selector import AncientDateSelector


class AncientDateDialog(QDialog):
    """
    A dialog for selecting ancient dates beyond the 1753 limitation of QDateEdit.

    Signals:
        dateSelected: Emitted when a date is selected
    """

    dateSelected = pyqtSignal(QDate)

    def __init__(self, parent=None, initial_date=None, title="Select Date"):
        """
        Initialize the AncientDateDialog.

        Args:
            parent: Parent widget
            initial_date: Initial date to display (QDate)
            title: Dialog title
        """
        super().__init__(parent)
        self.setWindowTitle(title)

        # Create layout
        layout = QVBoxLayout(self)

        # Instructions label
        instructions = QLabel(
            "Select a date (supports dates before 1753, including BCE):"
        )
        layout.addWidget(instructions)

        # Create the date selector
        self.date_selector = AncientDateSelector(self)
        if initial_date and initial_date.isValid():
            self.date_selector.set_date(initial_date)
        layout.addWidget(self.date_selector)

        # Standard OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        """Handle the OK button click."""
        selected_date = self.date_selector.date()
        if selected_date.isValid():
            self.dateSelected.emit(selected_date)
            super().accept()
        else:
            # Invalid date - could show error message here if needed
            pass

    def get_date(self):
        """
        Get the selected date.

        Returns:
            QDate: The selected date
        """
        return self.date_selector.date()

    @staticmethod
    def get_date_from_dialog(parent=None, initial_date=None, title="Select Date"):
        """
        Static convenience method to show the dialog and get a date.

        Args:
            parent: Parent widget
            initial_date: Initial date to display
            title: Dialog title

        Returns:
            QDate or None: Selected date if accepted, None if canceled
        """
        dialog = AncientDateDialog(parent, initial_date, title)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_date()
        return None


# Example usage:
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    class TestWindow(QMainWindow):
        """Test window to demonstrate AncientDateDialog usage."""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("Ancient Date Dialog Test")
            self.setGeometry(100, 100, 400, 200)

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Instructions
            instructions = QLabel(
                "This demo shows how to use the AncientDateDialog.\n"
                "It allows selecting dates before 1753, including BCE dates.\n"
                "Click the button below to open the dialog."
            )
            layout.addWidget(instructions)

            # Button to open dialog
            self.open_button = QPushButton("Select Ancient Date")
            self.open_button.clicked.connect(self.open_dialog)
            layout.addWidget(self.open_button)

            # Label to show selected date
            self.date_label = QLabel("No date selected")
            layout.addWidget(self.date_label)

            # Initial date (e.g., 500 BCE)
            self.initial_date = QDate(-500, 1, 1)  # Year -500 = 500 BCE

        def open_dialog(self):
            """Open the ancient date dialog."""
            selected_date = AncientDateDialog.get_date_from_dialog(
                self, initial_date=self.initial_date, title="Select Historical Date"
            )

            if selected_date:
                # Format the date string based on whether it's BCE or CE
                year = selected_date.year()
                if year <= 0:
                    # For BCE dates (astronomical year <= 0)
                    era = "BCE"
                    year_display = abs(year) if year < 0 else 1  # Handle year 0 (1 BCE)
                else:
                    # For CE dates
                    era = "CE"
                    year_display = year

                # Update the label with formatted date
                date_str = f"{year_display} {era}, {selected_date.month()}/{selected_date.day()}"
                self.date_label.setText(f"Selected date: {date_str}")

                # Update initial date for next dialog
                self.initial_date = selected_date
            else:
                self.date_label.setText("No date selected (dialog canceled)")

    # Create application
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
