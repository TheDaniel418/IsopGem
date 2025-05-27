"""
Defines the EphemerisDateDialog for selecting a date for ephemeris calculations.

Author: IsopGemini
Created: 2024-07-30
Last Modified: 2024-07-30
Dependencies: PyQt6
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDateEdit, QDialogButtonBox
from PyQt6.QtCore import QDate, pyqtSignal

class EphemerisDateDialog(QDialog):
    """
    A dialog to allow the user to select a calendar date.

    Signals:
        date_selected (QDate): Emitted when the user clicks OK with a valid date.
    """
    date_selected = pyqtSignal(QDate)

    def __init__(self, parent=None, initial_date: QDate = None):
        """
        Initializes the EphemerisDateDialog.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            initial_date (QDate, optional): The date to initially display. 
                                            Defaults to the current date.
        """
        super().__init__(parent)
        self.setWindowTitle("Select Ephemeris Date")

        self.layout = QVBoxLayout(self)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        if initial_date:
            self.date_edit.setDate(initial_date)
        else:
            self.date_edit.setDate(QDate.currentDate())
        # Set a reasonable date range, e.g., from year 1 to year 9999
        self.date_edit.setMinimumDate(QDate(1, 1, 1))
        self.date_edit.setMaximumDate(QDate(9999, 12, 31))
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.layout.addWidget(self.date_edit)

        # Standard OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def accept(self):
        """
        Handles the OK button click. Emits the date_selected signal if date is valid.
        """
        selected_qdate = self.date_edit.date()
        # Basic validation (QDateEdit usually handles internal validity)
        if selected_qdate.isValid():
            self.date_selected.emit(selected_qdate)
            super().accept() # Closes the dialog with QDialog.Accepted
        else:
            # Should ideally show an error message to the user
            # For now, just reject if somehow invalid, though QDateEdit tries to prevent this
            super().reject() 

    def get_selected_date(self) -> QDate | None:
        """
        Static method to conveniently show the dialog and get the date.
        Returns the selected QDate if OK was clicked, otherwise None.
        """
        dialog = EphemerisDateDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.date_edit.date() # Access directly after accepted signal has been processed
        return None

# Example Usage:
if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QPushButton, QWidget
    
    app = QApplication(sys.argv)
    
    main_window = QWidget()
    def open_dialog():
        print("Opening ephemeris date dialog...")
        # Using the static method for convenience in this example
        selected_date = EphemerisDateDialog.get_selected_date()
        if selected_date:
            print(f"Date selected: {selected_date.toString('yyyy-MM-dd')}")
        else:
            print("Dialog was cancelled.")
            
    btn = QPushButton("Open Date Dialog", main_window)
    btn.clicked.connect(open_dialog)
    main_window.show()
    
    sys.exit(app.exec()) 