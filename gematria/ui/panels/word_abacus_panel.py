"""Gematria Word Abacus panel.

This module provides a panel implementation of the Gematria Word Abacus
for calculating gematria values.
"""

from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult

# Import Language and CalculationType for batch processing
from gematria.models.calculation_type import CalculationType, Language
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService
from gematria.services.history_service import HistoryService
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog

# Import the actual dialog classes - we use these in type annotations and code
from gematria.ui.dialogs.gematria_help_dialog import GematriaHelpDialog
from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog
from gematria.ui.dialogs.save_calculation_dialog import SaveCalculationDialog
from gematria.ui.widgets.word_abacus_widget import WordAbacusWidget

# Import the repository for TagService
from shared.repositories.sqlite_tag_repository import SQLiteTagRepository

# Import TagService for handling tags during import
from shared.services.tag_service import TagService

# Import WindowManager for type hinting
from shared.ui.window_management import WindowManager

# Import TQAnalysisService
from tq.services.tq_analysis_service import TQAnalysisService


class WordAbacusPanel(QWidget):
    """Panel for Word Abacus calculations."""

    # Signal emitted when a calculation is performed
    calculation_performed = pyqtSignal(CalculationResult)

    def __init__(
        self, window_manager: WindowManager, parent: Optional[QWidget] = None
    ) -> None:
        """Initialize the word abacus panel.

        Args:
            window_manager: The application window manager.
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize services
        self._gematria_service = GematriaService()
        self._custom_cipher_service = CustomCipherService()
        self._history_service = HistoryService()
        self._db_service = CalculationDatabaseService()
        # Instantiate the repository first
        tag_repo = SQLiteTagRepository()
        self._tag_service = TagService(tag_repository=tag_repo)
        self.tq_analysis_service = TQAnalysisService(
            window_manager=window_manager
        )  # Pass window_manager

        # Track the current calculation
        self._current_calculation: Optional[CalculationResult] = None

        # Initialize UI components
        self._help_dialog: Optional[GematriaHelpDialog] = None
        self._custom_cipher_dialog: Optional[CustomCipherDialog] = None
        self._import_dialog: Optional[ImportWordListDialog] = None
        self._save_button: Optional[QPushButton] = None
        self._send_to_quadset_button: Optional[
            QPushButton
        ] = None  # Add button attribute

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

        # Send to Quadset Analysis button
        self._send_to_quadset_button = QPushButton("Send to Quadset Analysis")
        self._send_to_quadset_button.setEnabled(
            False
        )  # Disabled until a calculation is performed
        self._send_to_quadset_button.clicked.connect(self._send_to_quadset_analysis)
        button_layout.addWidget(self._send_to_quadset_button)

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
        # Pass our history service to ensure we're using the same instance
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
        from loguru import logger

        logger.debug(
            f"WordAbacusPanel._on_calculation_performed called with result ID: {result.id}"
        )

        # Store the current calculation
        self._current_calculation = result

        # Enable the save button
        if self._save_button:
            self._save_button.setEnabled(True)

        # Enable the send to quadset button
        if self._send_to_quadset_button:
            self._send_to_quadset_button.setEnabled(True)

        # Re-emit the signal to notify parent components
        # This is needed for the MainPanel to switch to the history tab
        logger.debug(
            f"Re-emitting calculation_performed signal with result ID: {result.id}"
        )
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
            from loguru import logger

            # Check if this is a custom cipher calculation
            if (
                hasattr(self._current_calculation, "custom_method_name")
                and self._current_calculation.custom_method_name
            ):
                logger.debug(
                    f"Saving custom cipher calculation with method: {self._current_calculation.custom_method_name}"
                )

                # For custom ciphers, we need to pass the custom_method_name
                # Get the custom method name, removing 'Custom: ' prefix if present
                custom_method_name = self._current_calculation.custom_method_name
                if custom_method_name.startswith("Custom: "):
                    custom_method_name = custom_method_name[8:]

                logger.debug(f"Saving with custom method name: {custom_method_name}")

                self._gematria_service.calculate_and_save(
                    text=text,
                    calculation_type="CUSTOM_CIPHER",  # Use the special string identifier
                    notes=notes,
                    tags=tags,
                    favorite=favorite,
                    value=value,  # Pass the pre-calculated value
                    custom_method_name=custom_method_name,  # Pass the clean custom method name
                )
            else:
                # For standard calculation types
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
        if self._import_dialog is None:
            self._import_dialog = ImportWordListDialog(self)
            self._import_dialog.import_complete.connect(self._on_import_complete)

        if self._import_dialog and not self._import_dialog.isVisible():
            self._import_dialog.show()
        elif self._import_dialog:
            self._import_dialog.raise_()
            self._import_dialog.activateWindow()

    def _on_import_complete(
        self, imported_items: List[dict], language: Language, count: int
    ) -> None:
        """Handle completion of word list import.

        Args:
            imported_items: List of dictionaries, each with 'word', 'notes', 'tags'.
            language: The language selected for the imported words.
            count: The total number of words imported.
        """
        if not imported_items:
            QMessageBox.information(self, "Import Complete", "No items were imported.")
            return

        progress_dialog = QProgressDialog(
            f"Calculating and saving {count} items...", "Cancel", 0, count, self
        )
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(0)  # Show immediately
        progress_dialog.setValue(0)
        progress_dialog.show()

        # Determine applicable calculation methods for the selected language
        applicable_methods = CalculationType.get_types_for_language(language)
        if not applicable_methods:
            QMessageBox.warning(
                self,
                "No Methods",
                f"No calculation methods found for language: {language.value}. Cannot process import.",
            )
            progress_dialog.close()
            return

        total_calculations = len(imported_items) * len(applicable_methods)
        progress_dialog.setMaximum(total_calculations)
        calculation_count = 0

        for i, item_data in enumerate(imported_items):
            word = item_data.get("word")
            notes = item_data.get("notes")
            tag_names = item_data.get("tags", [])  # Default to empty list

            if not word:
                logger.warning(
                    f"Skipping item at index {i} due to missing 'word'. Data: {item_data}"
                )
                # Adjust progress for skipped word across all methods
                calculation_count += len(applicable_methods)
                progress_dialog.setValue(calculation_count)
                continue

            # Resolve tag names to tag IDs
            tag_ids: List[str] = []
            if tag_names:
                for tag_name in tag_names:
                    if not tag_name.strip():  # Skip empty tag names
                        continue
                    tag_obj = self._tag_service.get_tag_by_name(tag_name.strip())
                    if tag_obj:
                        tag_ids.append(tag_obj.id)
                    else:
                        try:
                            new_tag = self._tag_service.create_tag(tag_name.strip())
                            if new_tag:
                                tag_ids.append(new_tag.id)
                            else:
                                logger.warning(
                                    f"Failed to create tag: {tag_name.strip()}"
                                )
                        except Exception as e:
                            logger.error(
                                f"Error creating tag '{tag_name.strip()}': {e}"
                            )

            for calc_type in applicable_methods:
                if progress_dialog.wasCanceled():
                    logger.info("Import and calculation process canceled by user.")
                    QMessageBox.information(
                        self, "Canceled", "Import process was canceled."
                    )
                    return

                try:
                    logger.debug(
                        f"Calculating {calc_type.name} for word: '{word}', notes: '{notes}', tags: {tag_ids}"
                    )
                    self._gematria_service.calculate_and_save(
                        text=word,
                        calculation_type=calc_type,
                        notes=notes,
                        tags=tag_ids,
                        favorite=False,  # Default, or make this configurable from import?
                    )
                    # We could emit calculation_performed here if needed for each saved item
                    # self.calculation_performed.emit(result_obj)
                except Exception as e:
                    logger.error(
                        f"Error calculating/saving '{calc_type.name}' for '{word}': {e}"
                    )
                    # Optionally, inform user about specific errors but continue batch

                calculation_count += 1
                progress_dialog.setValue(calculation_count)

            # Brief pause to allow UI to update, especially if many methods per word
            # QApplication.processEvents() # Can be risky, use with caution

        progress_dialog.setValue(total_calculations)
        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully processed and saved calculations for {len(imported_items)} words/phrases.",
        )
        logger.info("Import and batch calculation complete.")

    def _send_to_quadset_analysis(self) -> None:
        """Send the current calculation result to Quadset Analysis."""
        if (
            not self._current_calculation
            or self._current_calculation.result_value is None
        ):
            QMessageBox.warning(
                self,
                "No Result",
                "No calculation result available to send to Quadset Analysis.",
            )
            return

        try:
            value_to_send = int(self._current_calculation.result_value)
            self.tq_analysis_service.open_quadset_analysis(number=value_to_send)
            logger.info(f"Sent value {value_to_send} to Quadset Analysis.")
        except ValueError:
            QMessageBox.critical(
                self,
                "Invalid Value",
                f"The result value '{self._current_calculation.result_value}' is not a valid integer for Quadset Analysis.",
            )
            logger.error(
                f"Failed to send to Quadset Analysis: result value {self._current_calculation.result_value} is not an integer."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open Quadset Analysis: {e}")
            logger.error(f"Error opening Quadset Analysis: {e}")

    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.word_abacus_widget.clear_history()

        # Disable the save button
        if self._save_button:
            self._save_button.setEnabled(False)
        # Disable the send to quadset button
        if self._send_to_quadset_button:
            self._send_to_quadset_button.setEnabled(False)
        self._current_calculation = None

    def reset_calculator(self) -> None:
        """Reset the calculator to its initial state."""
        self.word_abacus_widget.reset_calculator()

        # Disable the save button
        if self._save_button:
            self._save_button.setEnabled(False)
        # Disable the send to quadset button
        if self._send_to_quadset_button:
            self._send_to_quadset_button.setEnabled(False)
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
