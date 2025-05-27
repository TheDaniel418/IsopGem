"""
@file encoding_conversion_dialog.py
@description Dialog for bulk text file encoding conversion to UTF-8
@author Assistant
@created 2024-01-20
@lastModified 2024-01-20
@dependencies PyQt6, document_manager.services.document_service
"""

import os
from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from document_manager.services.document_service import DocumentService


class ConversionWorker(QThread):
    """Worker thread for bulk encoding conversion."""

    progress_updated = pyqtSignal(int, str)  # progress, message
    conversion_completed = pyqtSignal(dict)  # results
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, directory_path: str, file_patterns: List[str], recursive: bool):
        super().__init__()
        self.directory_path = directory_path
        self.file_patterns = file_patterns
        self.recursive = recursive
        self.document_service = DocumentService()

    def run(self):
        """Run the bulk conversion process."""
        try:
            results = self.document_service.bulk_convert_text_files_to_utf8(
                self.directory_path, self.file_patterns, self.recursive
            )
            self.conversion_completed.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))


class EncodingConversionDialog(QDialog):
    """Dialog for bulk text file encoding conversion."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Text File Encoding Converter")
        self.setModal(True)
        self.resize(800, 600)

        self.conversion_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Convert Text Files to UTF-8 Encoding")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)

        # Description
        desc_label = QLabel(
            "This tool will detect and convert text files with various encodings "
            "(Windows-1252, ISO-8859-1, etc.) to UTF-8. Original files will be backed up."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 5px 10px;")
        layout.addWidget(desc_label)

        # Directory selection
        dir_group = QGroupBox("Directory Selection")
        dir_layout = QVBoxLayout(dir_group)

        dir_row = QHBoxLayout()
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText(
            "Select directory containing text files..."
        )
        dir_row.addWidget(QLabel("Directory:"))
        dir_row.addWidget(self.directory_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_directory)
        dir_row.addWidget(self.browse_button)

        dir_layout.addLayout(dir_row)

        # Options
        options_row = QHBoxLayout()
        self.recursive_checkbox = QCheckBox("Include subdirectories")
        self.recursive_checkbox.setChecked(True)
        options_row.addWidget(self.recursive_checkbox)
        options_row.addStretch()

        dir_layout.addLayout(options_row)
        layout.addWidget(dir_group)

        # File patterns
        patterns_group = QGroupBox("File Patterns")
        patterns_layout = QVBoxLayout(patterns_group)

        patterns_label = QLabel("File extensions to process (one per line):")
        patterns_layout.addWidget(patterns_label)

        self.patterns_edit = QTextEdit()
        self.patterns_edit.setMaximumHeight(80)
        self.patterns_edit.setPlainText("*.txt\n*.text\n*.asc")
        patterns_layout.addWidget(self.patterns_edit)

        layout.addWidget(patterns_group)

        # Results area
        results_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Progress and status
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)

        progress_layout.addWidget(QLabel("Conversion Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to convert files...")
        self.status_label.setStyleSheet("color: #666;")
        progress_layout.addWidget(self.status_label)

        # Results list
        self.results_list = QListWidget()
        self.results_list.setVisible(False)
        progress_layout.addWidget(self.results_list)

        results_splitter.addWidget(progress_frame)

        # Log area
        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.addWidget(QLabel("Conversion Log:"))

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        results_splitter.addWidget(log_frame)
        results_splitter.setSizes([400, 400])

        layout.addWidget(results_splitter)

        # Buttons
        button_layout = QHBoxLayout()

        self.convert_button = QPushButton("Start Conversion")
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }"
        )

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_conversion)
        self.cancel_button.setEnabled(False)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def browse_directory(self):
        """Open directory browser dialog."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory with Text Files",
            self.directory_edit.text() or os.path.expanduser("~"),
        )

        if directory:
            self.directory_edit.setText(directory)

    def get_file_patterns(self) -> List[str]:
        """Get file patterns from the text edit."""
        patterns_text = self.patterns_edit.toPlainText().strip()
        if not patterns_text:
            return ["*.txt", "*.text", "*.asc"]

        patterns = []
        for line in patterns_text.split("\n"):
            pattern = line.strip()
            if pattern and not pattern.startswith("#"):
                patterns.append(pattern)

        return patterns or ["*.txt", "*.text", "*.asc"]

    def start_conversion(self):
        """Start the bulk conversion process."""
        directory = self.directory_edit.text().strip()
        if not directory:
            QMessageBox.warning(self, "Warning", "Please select a directory first.")
            return

        if not Path(directory).exists():
            QMessageBox.warning(self, "Warning", "Selected directory does not exist.")
            return

        # Get conversion parameters
        file_patterns = self.get_file_patterns()
        recursive = self.recursive_checkbox.isChecked()

        # Update UI for conversion
        self.convert_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_list.setVisible(True)
        self.results_list.clear()
        self.log_text.clear()

        self.status_label.setText("Starting conversion...")
        self.log_text.append(f"🔄 Starting bulk conversion in: {directory}")
        self.log_text.append(f"📁 Recursive: {recursive}")
        self.log_text.append(f"📄 Patterns: {', '.join(file_patterns)}")
        self.log_text.append("")

        # Start worker thread
        self.conversion_worker = ConversionWorker(directory, file_patterns, recursive)
        self.conversion_worker.conversion_completed.connect(
            self.on_conversion_completed
        )
        self.conversion_worker.error_occurred.connect(self.on_conversion_error)
        self.conversion_worker.start()

    def cancel_conversion(self):
        """Cancel the ongoing conversion."""
        if self.conversion_worker and self.conversion_worker.isRunning():
            self.conversion_worker.terminate()
            self.conversion_worker.wait()

        self.reset_ui()
        self.status_label.setText("Conversion cancelled.")
        self.log_text.append("❌ Conversion cancelled by user.")

    def on_conversion_completed(self, results: dict):
        """Handle conversion completion."""
        self.reset_ui()

        # Update status
        total = results["total_files"]
        converted = results["converted_files"]
        already_utf8 = results["already_utf8"]
        failed = results["failed_conversions"]

        self.status_label.setText(
            f"Conversion complete! {converted} converted, {already_utf8} already UTF-8, {failed} failed"
        )

        # Update progress bar
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        # Add results to list
        for detail in results["conversion_details"]:
            item_text = f"{Path(detail['file_path']).name} - {detail['status']}"
            if detail["status"] == "converted":
                item_text += f" (from {detail['original_encoding']})"

            item = QListWidgetItem(item_text)

            # Color code by status
            if detail["status"] == "converted":
                item.setBackground(Qt.GlobalColor.lightGreen)
            elif detail["status"] == "already_utf8":
                item.setBackground(Qt.GlobalColor.lightBlue)
            elif detail["status"] == "failed":
                item.setBackground(Qt.GlobalColor.lightGray)

            self.results_list.addItem(item)

        # Update log
        self.log_text.append("✅ Conversion completed!")
        self.log_text.append("📊 Summary:")
        self.log_text.append(f"   Total files: {total}")
        self.log_text.append(f"   Converted: {converted}")
        self.log_text.append(f"   Already UTF-8: {already_utf8}")
        self.log_text.append(f"   Failed: {failed}")

        if results["errors"]:
            self.log_text.append("\n❌ Errors:")
            for error in results["errors"]:
                self.log_text.append(f"   {error}")

        # Show completion message
        if failed == 0:
            QMessageBox.information(
                self,
                "Success",
                f"Successfully processed {total} files!\n"
                f"Converted: {converted}\n"
                f"Already UTF-8: {already_utf8}",
            )
        else:
            QMessageBox.warning(
                self,
                "Partial Success",
                f"Processed {total} files with {failed} failures.\n"
                f"Converted: {converted}\n"
                f"Already UTF-8: {already_utf8}\n"
                f"Failed: {failed}\n\n"
                f"Check the log for details.",
            )

    def on_conversion_error(self, error_message: str):
        """Handle conversion error."""
        self.reset_ui()
        self.status_label.setText("Conversion failed!")
        self.log_text.append(f"❌ Error: {error_message}")

        QMessageBox.critical(
            self,
            "Conversion Error",
            f"An error occurred during conversion:\n\n{error_message}",
        )

    def reset_ui(self):
        """Reset UI to initial state."""
        self.convert_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.conversion_worker and self.conversion_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Conversion in Progress",
                "A conversion is currently running. Do you want to cancel it and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.cancel_conversion()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
