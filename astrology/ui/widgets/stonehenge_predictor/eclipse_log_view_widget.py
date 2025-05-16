"""
Defines the EclipseLogViewWidget for the Stonehenge Eclipse Predictor.

This widget displays log messages, primarily for eclipse predictions.

Author: IsopGemini
Created: 2024-07-30
Last Modified: 2024-07-30
Dependencies: PyQt6
"""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QSizePolicy, QTextEdit, QVBoxLayout, QWidget


class EclipseLogViewWidget(QWidget):
    """
    A widget to display log messages, especially for eclipse predictions.
    It uses a QTextEdit for displaying formatted text.
    """

    def __init__(self, parent=None):
        """
        Initializes the EclipseLogViewWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """
        Initializes the UI components of the log view.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Compact layout

        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setFont(QFont("monospace", 9))
        self.log_text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # Optionally set a minimum height or use stretch factors in the parent layout
        self.log_text_edit.setMinimumHeight(100)

        layout.addWidget(self.log_text_edit)
        self.setLayout(layout)

    def add_log_message(self, message: str):
        """
        Appends a new message to the log.
        The message can contain HTML for basic formatting if desired.

        Args:
            message (str): The message string to add.
        """
        self.log_text_edit.append(message)  # append handles scrolling to the end

    def clear_log(self):
        """
        Clears all messages from the log.
        """
        self.log_text_edit.clear()


# Example usage for testing this widget directly
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication, QPushButton

    app = QApplication(sys.argv)

    main_window = QWidget()
    main_layout = QVBoxLayout(main_window)

    log_view = EclipseLogViewWidget()

    # Test buttons
    def add_test_message():
        log_view.add_log_message(
            "This is a <b>test</b> message with <font color='blue'>HTML</font>."
        )
        log_view.add_log_message("Another normal message.")

    def clear_test_log():
        log_view.clear_log()
        log_view.add_log_message("Log cleared.")

    add_button = QPushButton("Add Message")
    add_button.clicked.connect(add_test_message)
    clear_button = QPushButton("Clear Log")
    clear_button.clicked.connect(clear_test_log)

    main_layout.addWidget(log_view)
    main_layout.addWidget(add_button)
    main_layout.addWidget(clear_button)

    main_window.setWindowTitle("Eclipse Log View Test")
    main_window.setGeometry(300, 300, 500, 300)
    main_window.show()

    log_view.add_log_message("Log view initialized.")

    sys.exit(app.exec())
