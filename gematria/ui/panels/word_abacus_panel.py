"""Gematria Word Abacus panel.

This module provides a panel implementation of the Gematria Word Abacus
for calculating gematria values.
"""

from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QPushButton,
    QHBoxLayout,
    QDialog,
    QLabel,
)
from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType
from gematria.ui.widgets.word_abacus_widget import WordAbacusWidget
from gematria.models.custom_cipher_config import CustomCipherConfig
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.gematria_service import GematriaService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.history_service import HistoryService

# Import the actual dialog classes - we use these in type annotations and code
from gematria.ui.dialogs.gematria_help_dialog import GematriaHelpDialog
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog
from gematria.ui.dialogs.save_calculation_dialog import SaveCalculationDialog
from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog


class WordAbacusPanel(QWidget):
    """Panel for Word Abacus calculations."""

    # Signal emitted when a calculation is performed
    calculation_performed = pyqtSignal(CalculationResult)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the word abacus panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize services
        self._gematria_service = GematriaService()
        self._custom_cipher_service = CustomCipherService()
        self._history_service = HistoryService()
        self._db_service = CalculationDatabaseService()

        # Track the current calculation
        self._current_calculation: Optional[CalculationResult] = None

        # Initialize UI components
        self._help_dialog: Optional[GematriaHelpDialog] = None
        self._custom_cipher_dialog: Optional[CustomCipherDialog] = None
        self._import_dialog: Optional[ImportWordListDialog] = None
        self._save_button: Optional[QPushButton] = None

        # Initialize UI
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Create the main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create the header
        header = QLabel("Word Abacus")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Create a button area
        button_area = QWidget()
        button_layout = QHBoxLayout(button_area)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Save button - used to save current calculation
        self._save_button = QPushButton("Save Calculation")
        self._save_button.setEnabled(False)  # Disabled until a calculation is performed
        self._save_button.clicked.connect(self._show_save_dialog)
        button_layout.addWidget(self._save_button)

        # Custom cipher button
        custom_button = QPushButton("Custom Ciphers")
        custom_button.clicked.connect(self._show_custom_cipher_dialog)
        button_layout.addWidget(custom_button)

        # Import word list button
        import_button = QPushButton("Import Word/Phrase List")
        import_button.clicked.connect(self._show_import_dialog)
        button_layout.addWidget(import_button)

        # Help button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self._show_help_dialog)
        button_layout.addWidget(help_button)

        # Add button area to main layout
        layout.addWidget(button_area)

        # Create a scroll area to allow scrolling if the widget gets too large
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Create the Word Abacus widget
        self.word_abacus_widget = WordAbacusWidget(
            calculation_service=self._gematria_service,
            custom_cipher_service=self._custom_cipher_service,
            history_service=self._history_service,
        )

        # Set the widget as the scroll area's widget
        scroll_area.setWidget(self.word_abacus_widget)

        # Add the scroll area to the layout
        layout.addWidget(scroll_area)

        # Connect signals
        self.word_abacus_widget.calculation_performed.connect(
            self._on_calculation_performed
        )

        self.setLayout(layout)

    def _on_calculation_performed(self, result: CalculationResult) -> None:
        """Handle when a calculation is performed.

        Args:
            result: The calculation result
        """
        # Store the current calculation
        self._current_calculation = result

        # Enable the save button
        if self._save_button:
            self._save_button.setEnabled(True)

        # Re-emit the signal
        self.calculation_performed.emit(result)

    def _show_help_dialog(self) -> None:
        """Show the gematria help dialog."""
        # Create the dialog if it doesn't exist yet
        if self._help_dialog is None:
            self._help_dialog = GematriaHelpDialog(self)

        # Show the dialog if it's not already visible
        if self._help_dialog and not self._help_dialog.isVisible():
            self._help_dialog.show()
        # If it's already showing, bring it to the front
        elif self._help_dialog:
            self._help_dialog.raise_()
            self._help_dialog.activateWindow()

    def _show_custom_cipher_dialog(self) -> None:
        """Show the custom cipher manager dialog."""
        # Create the dialog if it doesn't exist yet
        if self._custom_cipher_dialog is None:
            self._custom_cipher_dialog = CustomCipherDialog(self)

            # Connect the cipher updated signal to refresh the widget
            if self._custom_cipher_dialog and hasattr(
                self.word_abacus_widget, "_on_custom_cipher_updated"
            ):
                self._custom_cipher_dialog.cipher_updated.connect(
                    self.word_abacus_widget._on_custom_cipher_updated
                )

        # Show the dialog if it's not already visible
        if self._custom_cipher_dialog and not self._custom_cipher_dialog.isVisible():
            self._custom_cipher_dialog.show()
        # If it's already showing, bring it to the front
        elif self._custom_cipher_dialog:
            self._custom_cipher_dialog.raise_()
            self._custom_cipher_dialog.activateWindow()

    def _show_save_dialog(self) -> None:
        """Show the save calculation dialog."""
        if not self._current_calculation:
            logger.warning("No calculation to save")
            return

        # Get calculation details
        value = self._current_calculation.result_value
        text = self._current_calculation.input_text

        # Get method name
        if self._current_calculation.custom_method_name:
            method_name = self._current_calculation.custom_method_name
        else:
            calc_type = self._current_calculation.calculation_type
            if calc_type:
                # Handle both string and CalculationType objects
                if isinstance(calc_type, str):
                    method_name = calc_type.replace("_", " ").title()
                else:
                    method_name = calc_type.name.replace("_", " ").title()
            else:
                method_name = "Unknown Method"

        # Create and show the dialog
        save_dialog = SaveCalculationDialog(value, text, method_name, self)

        if save_dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the data from the dialog
            tags = save_dialog.selected_tags
            notes = save_dialog.notes
            favorite = save_dialog.is_favorite

            # Save to database
            self._gematria_service.calculate_and_save(
                text=text,
                calculation_type=self._current_calculation.calculation_type,
                notes=notes,
                tags=tags,
                favorite=favorite,
            )

            logger.debug(f"Saved calculation: {text} = {value}")

    def _show_import_dialog(self) -> None:
        """Show the import word list dialog."""
        # Create the dialog if it doesn't exist yet
        if self._import_dialog is None:
            self._import_dialog = ImportWordListDialog(self)

            # Connect the import complete signal to refresh the UI if needed
            self._import_dialog.import_complete.connect(self._on_import_complete)

        # Show the dialog if it's not already visible
        if self._import_dialog and not self._import_dialog.isVisible():
            self._import_dialog.show()
        # If it's already showing, bring it to the front
        elif self._import_dialog:
            self._import_dialog.raise_()
            self._import_dialog.activateWindow()

    def _on_import_complete(self, count: int) -> None:
        """Handle completion of word list import.

        Args:
            count: Number of words imported
        """
        # Log the import completion
        logger.info(f"Imported {count} words/phrases")

        # You could refresh any relevant UI components here if needed
        # For example, if there's a history component that should be updated

    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.word_abacus_widget.clear_history()

        # Disable the save button
        if self._save_button:
            self._save_button.setEnabled(False)
        self._current_calculation = None

    def reset_calculator(self) -> None:
        """Reset the calculator to its initial state."""
        self.word_abacus_widget.reset_calculator()

        # Disable the save button
        if self._save_button:
            self._save_button.setEnabled(False)
        self._current_calculation = None

    def closeEvent(self, event):
        """Handle panel close event.

        Ensures help dialog and custom cipher dialog are closed when panel is closed.

        Args:
            event: Close event
        """
        # Close help dialog if it exists and is visible
        if self._help_dialog is not None and self._help_dialog.isVisible():
            self._help_dialog.close()

        # Close custom cipher dialog if it exists and is visible
        if (
            self._custom_cipher_dialog is not None
            and self._custom_cipher_dialog.isVisible()
        ):
            self._custom_cipher_dialog.close()

        # Close import dialog if it exists and is visible
        if self._import_dialog is not None and self._import_dialog.isVisible():
            self._import_dialog.close()

        # Continue with normal close event
        super().closeEvent(event)
