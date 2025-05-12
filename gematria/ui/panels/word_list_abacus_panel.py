"""
Purpose: Provides a panel for Gematria Word List Abacus functionality.

This file is part of the gematria pillar and serves as a UI component.
It provides a container panel for the Word List Abacus widget,
allowing users to perform gematria calculations on lists of words.

Key components:
- WordListAbacusPanel: Panel for Word List Abacus calculations

Dependencies:
- PyQt6: For UI components
- gematria.ui.widgets.word_list_abacus_widget: For the core Word List Abacus widget
- gematria.services.gematria_service: For gematria calculation service
- gematria.services.custom_cipher_service: For custom cipher management
- gematria.services.history_service: For calculation history management
"""

from loguru import logger
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService
from gematria.services.history_service import HistoryService
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog
from gematria.ui.dialogs.import_word_list_dialog import ImportWordListDialog
from gematria.ui.dialogs.save_calculation_dialog import SaveCalculationDialog
from gematria.ui.widgets.word_list_abacus_widget import WordListAbacusWidget


class WordListAbacusPanel(QWidget):
    """Panel for Word List Abacus calculations."""

    # Signal emitted when a calculation is performed
    calculation_performed = pyqtSignal(CalculationResult)

    def __init__(self, parent=None, window_manager=None) -> None:
        """Initialize the Word List Abacus panel.

        Args:
            parent: Parent widget
            window_manager: Window manager instance
        """
        super().__init__(parent)

        # Store the window manager
        self.window_manager = window_manager

        # Initialize services
        self._gematria_service = GematriaService()
        self._custom_cipher_service = CustomCipherService()
        self._history_service = HistoryService()

        # Initialize dialog references to None
        self._help_dialog = None
        self._custom_cipher_dialog = None
        self._save_dialog = None
        self._import_dialog = None

        # Current calculation result (for saving)
        self._current_calculation = None

        # Initialize UI
        self._init_ui()

        logger.debug("WordListAbacusPanel initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Create the main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create the header
        header = QLabel("Word List Abacus")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Create a button area
        button_area = QWidget()
        button_layout = QHBoxLayout(button_area)
        button_layout.setContentsMargins(0, 0, 0, 0)

        # Save button - used to save current calculations
        self._save_button = QPushButton("Save Calculations")
        self._save_button.setEnabled(False)  # Disabled until a calculation is performed
        self._save_button.clicked.connect(self._show_save_dialog)
        button_layout.addWidget(self._save_button)

        # Group & Chain button - used to open the word group chain window
        self._group_chain_button = QPushButton("Word Groups & Chains")
        self._group_chain_button.setEnabled(
            False
        )  # Disabled until a calculation is performed
        self._group_chain_button.clicked.connect(self._show_group_chain_window)
        self._group_chain_button.setToolTip(
            "Organize words into groups and create calculation chains"
        )
        button_layout.addWidget(self._group_chain_button)

        # Custom cipher button
        custom_button = QPushButton("Custom Ciphers")
        custom_button.clicked.connect(self._show_custom_cipher_dialog)
        button_layout.addWidget(custom_button)

        # Import word list button
        import_button = QPushButton("Import Word/Phrase List")
        import_button.clicked.connect(self._show_import_dialog)
        button_layout.addWidget(import_button)

        # Export results button
        export_button = QPushButton("Export Results")
        export_button.clicked.connect(self._export_results)
        export_button.setEnabled(False)  # Disabled until calculations are performed
        self._export_button = export_button
        button_layout.addWidget(export_button)

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

        # Create the Word List Abacus widget
        # Pass our services to ensure we're using the same instances
        self.word_list_abacus_widget = WordListAbacusWidget(
            calculation_service=self._gematria_service,
            custom_cipher_service=self._custom_cipher_service,
            history_service=self._history_service,
        )

        # Set the widget as the scroll area's widget
        scroll_area.setWidget(self.word_list_abacus_widget)

        # Add the scroll area to the layout
        layout.addWidget(scroll_area)

        # Connect signals
        self.word_list_abacus_widget.calculations_performed.connect(
            self._on_calculations_performed
        )

        self.setLayout(layout)

    def _on_calculations_performed(self, results) -> None:
        """Handle when calculations are performed.

        Args:
            results: The list of calculation results
        """
        logger.debug(f"WordListAbacusPanel received {len(results)} calculation results")

        # Store the current calculations
        self._current_calculations = results

        # Enable buttons
        self._save_button.setEnabled(True)
        self._export_button.setEnabled(True)
        self._group_chain_button.setEnabled(True)  # Enable the Group Chain button

        # If we have any results, emit the first one for display compatibility
        if results:
            self.calculation_performed.emit(results[0])

    def _show_help_dialog(self) -> None:
        """Show the gematria help dialog."""
        from gematria.ui.dialogs.gematria_help_dialog import GematriaHelpDialog

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
        """Show the custom cipher dialog."""
        # Create the dialog if it doesn't exist yet
        if self._custom_cipher_dialog is None:
            self._custom_cipher_dialog = CustomCipherDialog(self)
            self._custom_cipher_dialog.cipher_updated.connect(
                self.word_list_abacus_widget.refresh_methods
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
        # Only show if we have a calculation result
        if not hasattr(self, "_current_calculations") or not self._current_calculations:
            return

        # Create a save dialog with the current calculation
        self._save_dialog = SaveCalculationDialog(
            self._current_calculations[0], parent=self
        )
        self._save_dialog.calculation_saved.connect(self._on_calculation_saved)
        self._save_dialog.exec()

    def _on_calculation_saved(self) -> None:
        """Handle when a calculation is saved."""
        logger.info("Calculation saved to history")

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

        # Forward to the widget to update the word list
        self.word_list_abacus_widget.update_word_list()

    def _export_results(self) -> None:
        """Export the calculation results to a file."""
        # Forward to the widget
        self.word_list_abacus_widget.export_results()

    def reset(self) -> None:
        """Reset the Word List Abacus to its initial state."""
        self.word_list_abacus_widget.reset()

        # Disable buttons
        self._save_button.setEnabled(False)
        self._export_button.setEnabled(False)

        # Clear current calculations
        self._current_calculations = None

    def _show_group_chain_window(self) -> None:
        """Open the Word Group Chain window for organizing and chaining words."""
        from gematria.ui.windows.word_group_chain_window import WordGroupChainWindow

        # Create a new window instance
        window = WordGroupChainWindow()

        # Use the window manager instance
        if self.window_manager is None:
            # Try to get the window manager from the parent hierarchy if not provided
            parent = self
            while parent is not None:
                if hasattr(parent, "window_manager"):
                    self.window_manager = parent.window_manager
                    break
                parent = parent.parent()

            # If still not found, create a new window directly
            if self.window_manager is None:
                window.show()
                window.raise_()
                logger.warning(
                    "WindowManager not found. Opening window without proper management."
                )
                return

        # Open the window through the window manager with a unique ID
        window_id = "word_group_chain_window"
        self.window_manager.open_window(window_id, window)

        # Show window
        window.show()
        window.raise_()

        # If we have calculation results, offer to import them
        if self._current_calculations:
            response = QMessageBox.question(
                self,
                "Import Results",
                "Would you like to import the current calculation results into the Word Group Chain?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )

            if response == QMessageBox.StandardButton.Yes:
                window.import_calculation_results(self._current_calculations)

        logger.debug("Opened Word Group Chain window")

    def _on_calculation_complete(self) -> None:
        """Handle completion of calculations."""
        # Enable the save button
        self._save_button.setEnabled(True)

        # Enable the group chain button
        self._group_chain_button.setEnabled(True)

        # Store calculation results
        self._current_calculations = []

        # Generate calculation results from the model
        for i in range(self._result_model.rowCount()):
            row_idx = self._result_model.index(i, 0)
            result = self._result_model.data(row_idx, Qt.ItemDataRole.UserRole)
            if result:
                self._current_calculations.append(result)

        self._widget.set_calculating(False)
        logger.debug("Calculation completed")
