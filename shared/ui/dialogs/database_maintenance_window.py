"""
Purpose: Provides interface for database maintenance operations

This file is part of the shared utilities and serves as a UI component.
It is responsible for providing a user interface for performing database
maintenance operations such as cleansing, optimization, and removing duplicates.

Key components:
- DatabaseMaintenanceWindow: Main window for database maintenance operations

Dependencies:
- PyQt6: For building the graphical user interface
- gematria.services.calculation_database_service: For accessing the database
- shared.repositories: For direct repository operations
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from loguru import logger
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gematria.services.calculation_database_service import CalculationDatabaseService


class DatabaseMaintenanceWindow(QWidget):
    """Window for database maintenance operations."""

    def __init__(self, parent=None):
        """Initialize the database maintenance window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize the database service and repositories
        self.db_service = CalculationDatabaseService()

        # Initialize UI
        self._init_ui()

        # Update statistics
        self._update_stats()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Database Maintenance")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Statistics group
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_group)

        # Maintenance Tasks group
        tasks_group = QGroupBox("Maintenance Tasks")
        tasks_layout = QVBoxLayout(tasks_group)

        # Clean Database
        clean_layout = QHBoxLayout()
        clean_btn = QPushButton("Clean Database")
        clean_btn.setToolTip("Remove all entries from the database")
        clean_btn.clicked.connect(self._clean_database)
        clean_layout.addWidget(clean_btn)
        clean_layout.addWidget(
            QLabel("Permanently delete all calculations and/or tags")
        )
        clean_layout.addStretch()
        tasks_layout.addLayout(clean_layout)

        # Find Duplicates
        duplicates_layout = QHBoxLayout()
        duplicates_btn = QPushButton("Find Duplicates")
        duplicates_btn.setToolTip("Find and optionally remove duplicate calculations")
        duplicates_btn.clicked.connect(self._find_duplicates)
        duplicates_layout.addWidget(duplicates_btn)
        duplicates_layout.addWidget(QLabel("Find and manage duplicate calculations"))
        duplicates_layout.addStretch()
        tasks_layout.addLayout(duplicates_layout)

        # Optimize Database
        optimize_layout = QHBoxLayout()
        optimize_btn = QPushButton("Optimize Database")
        optimize_btn.setToolTip("Compact and optimize the database files")
        optimize_btn.clicked.connect(self._optimize_database)
        optimize_layout.addWidget(optimize_btn)
        optimize_layout.addWidget(
            QLabel("Compact and reorganize data for better performance")
        )
        optimize_layout.addStretch()
        tasks_layout.addLayout(optimize_layout)

        # Backup Database
        backup_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Database")
        backup_btn.setToolTip("Create a backup of the database files")
        backup_btn.clicked.connect(self._backup_database)
        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(QLabel("Create a backup of all database files"))
        backup_layout.addStretch()
        tasks_layout.addLayout(backup_layout)

        # Restore Database
        restore_layout = QHBoxLayout()
        restore_btn = QPushButton("Restore Database")
        restore_btn.setToolTip("Restore database from a backup")
        restore_btn.clicked.connect(self._restore_database)
        restore_layout.addWidget(restore_btn)
        restore_layout.addWidget(QLabel("Restore database from a previous backup"))
        restore_layout.addStretch()
        tasks_layout.addLayout(restore_layout)

        layout.addWidget(tasks_group)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Add stretch to push everything to the top
        layout.addStretch()

    def _update_stats(self):
        """Update the statistics display."""
        # Get counts
        num_calculations = len(self.db_service.get_all_calculations())
        favorite_calculations = len(self.db_service.find_favorites())
        num_tags = len(self.db_service.get_all_tags())

        # Calculate database size
        db_file_size = 0

        # For SQLite, both calculations and tags are in the same database file
        db_path = self.db_service.calculation_repo.db._db_file

        if os.path.exists(db_path):
            # Convert to KB as an integer for type safety
            db_file_size = int(os.path.getsize(db_path) / 1024)  # KB

        # Get unique values
        unique_values = len(self.db_service.get_unique_values())

        # Update status
        self.stats_label.setText(
            f"<b>Calculations:</b> {num_calculations} total, {favorite_calculations} favorites, {unique_values} unique values<br>"
            f"<b>Tags:</b> {num_tags} total<br>"
            f"<b>Database Size:</b> {db_file_size} KB"
        )

    def _clean_database(self):
        """Clean the database by removing all entries."""
        # Ask the user which parts to clean
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Clean Database")
        msg_box.setText("Which database components would you like to clean?")
        msg_box.setIcon(QMessageBox.Icon.Question)

        # Add buttons for different options
        calculations_btn = msg_box.addButton(
            "Calculations Only", QMessageBox.ButtonRole.ActionRole
        )
        tags_btn = msg_box.addButton("Tags Only", QMessageBox.ButtonRole.ActionRole)
        all_btn = msg_box.addButton("All Data", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == calculations_btn:
            self._clean_calculations()
        elif clicked_button == tags_btn:
            self._clean_tags()
        elif clicked_button == all_btn:
            self._clean_all()
        # If cancel, do nothing

    def _clean_calculations(self):
        """Clean all calculations from the database."""
        # Confirm action
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete ALL calculations? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Execute a SQL statement to delete all calculations
                self.db_service.calculation_repo.db.execute("DELETE FROM calculations")

                self.status_label.setText("All calculations have been deleted.")
                self._update_stats()

                logger.info("All calculations deleted during database maintenance")

            except Exception as e:
                logger.error(f"Error cleaning calculations: {e}")
                self.status_label.setText(f"Error cleaning calculations: {str(e)}")

    def _clean_tags(self):
        """Clean all tags from the database."""
        # Confirm action
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete ALL tags? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Execute a SQL statement to delete all tags
                self.db_service.tag_repo.db.execute("DELETE FROM tags")

                # Create default tags
                self.db_service.tag_repo.create_default_tags()

                self.status_label.setText(
                    "All tags have been deleted and default tags created."
                )
                self._update_stats()

                logger.info("All tags deleted during database maintenance")

            except Exception as e:
                logger.error(f"Error cleaning tags: {e}")
                self.status_label.setText(f"Error cleaning tags: {str(e)}")

    def _clean_all(self):
        """Clean all data from the database (both calculations and tags)."""
        # Confirm action
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete ALL data (calculations and tags)? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Execute SQL statements to delete all data
                self.db_service.calculation_repo.db.execute("DELETE FROM calculations")
                self.db_service.tag_repo.db.execute("DELETE FROM tags")

                # Create default tags
                self.db_service.tag_repo.create_default_tags()

                self.status_label.setText(
                    "All data has been deleted and default tags created."
                )
                self._update_stats()

                logger.info("All database data deleted during maintenance")

            except Exception as e:
                logger.error(f"Error cleaning database: {e}")
                self.status_label.setText(f"Error cleaning database: {str(e)}")

    def _find_duplicates(self):
        """Find duplicate calculations in the database."""
        try:
            # Use SQL to find duplicates based on input text and calculation type
            query = """
            SELECT input_text, calculation_type, COUNT(*) as count
            FROM calculations
            GROUP BY input_text, calculation_type
            HAVING COUNT(*) > 1
            """

            # Execute the query and fetch results manually since fetch is not a parameter
            cursor = self.db_service.calculation_repo.db.execute(query)
            result = cursor.fetchall() if cursor else []

            if not result:
                self.status_label.setText("No duplicate calculations found.")
                return

            # Count duplicates
            total_dupes = sum(row[2] - 1 for row in result)

            # Ask if the user wants to remove duplicates
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Duplicate Calculations")
            msg_box.setText(
                f"Found {total_dupes} duplicate calculations for {len(result)} unique inputs."
            )
            msg_box.setInformativeText("Do you want to remove these duplicates?")
            msg_box.setIcon(QMessageBox.Icon.Question)
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            result_btn = msg_box.exec()

            if result_btn == QMessageBox.StandardButton.Yes:
                # For each group of duplicates, keep the newest one and delete the rest
                removed_count = 0

                for row in result:
                    input_text, calculation_type = row[0], row[1]

                    # Get all calculations with this input and type, ordered by date
                    duplicates_query = """
                    SELECT id FROM calculations
                    WHERE input_text = ? AND calculation_type = ?
                    ORDER BY created_at DESC
                    """

                    # Execute the query and fetch results manually
                    cursor = self.db_service.calculation_repo.db.execute(
                        duplicates_query, (input_text, calculation_type)
                    )
                    dupe_ids = cursor.fetchall() if cursor else []

                    # Keep the first one (newest), delete the rest
                    if len(dupe_ids) > 1:
                        for i in range(1, len(dupe_ids)):
                            if self.db_service.delete_calculation(dupe_ids[i][0]):
                                removed_count += 1

                self.status_label.setText(
                    f"Removed {removed_count} duplicate calculations."
                )
                self._update_stats()

                logger.info(
                    f"Removed {removed_count} duplicate calculations during maintenance"
                )
            else:
                self.status_label.setText(
                    f"Found {total_dupes} duplicate calculations. No changes made."
                )

        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            self.status_label.setText(f"Error finding duplicates: {str(e)}")

    def _optimize_database(self):
        """Optimize the database files."""
        try:
            # Use VACUUM to rebuild the database, reclaiming unused space
            self.db_service.calculation_repo.db.execute("VACUUM")

            # Run ANALYZE to update statistics
            self.db_service.calculation_repo.db.execute("ANALYZE")

            self.status_label.setText("Database optimized successfully.")
            self._update_stats()

            logger.info("Database optimized during maintenance")

        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            self.status_label.setText(f"Error optimizing database: {str(e)}")

    def _backup_database(self):
        """Backup the database files."""
        try:
            # Create a backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_dir = Path(self.db_service.calculation_repo.db._db_file).parent
            backup_dir = data_dir / f"backup_{timestamp}"
            os.makedirs(backup_dir, exist_ok=True)

            # Copy the SQLite database file
            db_file = self.db_service.calculation_repo.db._db_file
            if os.path.exists(db_file):
                shutil.copy2(db_file, backup_dir / "isopgem.db")

            self.status_label.setText(
                f"Database backed up successfully to {backup_dir}"
            )

            logger.info(f"Database backed up to {backup_dir}")

        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            self.status_label.setText(f"Error backing up database: {str(e)}")

    def _restore_database(self):
        """Restore the database from a backup."""
        try:
            # Get data directory
            data_dir = Path(self.db_service.calculation_repo.db._db_file).parent

            # Find backup directories
            backup_dirs = [
                d
                for d in data_dir.iterdir()
                if d.is_dir() and d.name.startswith("backup_")
            ]

            if not backup_dirs:
                self.status_label.setText("No backups found to restore.")
                return

            # Sort backups by name (newest first)
            backup_dirs.sort(reverse=True)

            # Let user select a backup
            backup_dir_names = [d.name for d in backup_dirs]

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Restore Database")
            msg_box.setText("Select a backup to restore:")
            msg_box.setIcon(QMessageBox.Icon.Question)

            # Add buttons for each backup
            buttons = []
            for name in backup_dir_names[:5]:  # Show only the 5 most recent backups
                # Convert backup name to a more readable format
                if name.startswith("backup_"):
                    date_str = name[7:]  # Remove "backup_" prefix
                    date_str = date_str.replace("_", " ")
                    btn = msg_box.addButton(date_str, QMessageBox.ButtonRole.ActionRole)
                    buttons.append((btn, name))

            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

            msg_box.exec()

            clicked_button = msg_box.clickedButton()

            if clicked_button == cancel_btn:
                return

            # Find which backup was selected
            selected_backup_name = None
            for btn, name in buttons:
                if clicked_button == btn:
                    selected_backup_name = name
                    break

            if not selected_backup_name:
                return

            # Find the backup directory
            selected_backup = None
            for d in backup_dirs:
                if d.name == selected_backup_name:
                    selected_backup = d
                    break

            if not selected_backup:
                self.status_label.setText("Selected backup not found.")
                return

            # Confirm restore
            confirm = QMessageBox.question(
                self,
                "Confirm Restore",
                f"Are you sure you want to restore the database from backup {selected_backup_name}? This will overwrite your current data.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                # Close current database connections
                self.db_service.calculation_repo.db.close()

                # Create backup of current database before restoring
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                current_backup_dir = data_dir / f"pre_restore_backup_{timestamp}"
                os.makedirs(current_backup_dir, exist_ok=True)

                db_file = self.db_service.calculation_repo.db._db_file
                if os.path.exists(db_file):
                    shutil.copy2(db_file, current_backup_dir / "isopgem.db")

                # Restore from backup
                backup_db_file = selected_backup / "isopgem.db"
                if os.path.exists(backup_db_file):
                    # We need to copy the file and then reopen the connection
                    shutil.copy2(backup_db_file, db_file)

                    # Reinitialize the database connections
                    # This is a bit of a hack; in a more robust implementation we would
                    # have a method to reopen the connections or recreate the service
                    self.db_service = CalculationDatabaseService()

                    self.status_label.setText(
                        f"Database restored successfully from {selected_backup_name}"
                    )
                    self._update_stats()

                    logger.info(f"Database restored from backup {selected_backup_name}")
                else:
                    self.status_label.setText("Backup database file not found.")
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            self.status_label.setText(f"Error restoring database: {str(e)}")
