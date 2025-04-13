"""
Dialog for managing astrological events database, including calculation and caching of 
planetary aspects, moon phases, and other astronomical events.
"""

import os
import sqlite3
import logging
from threading import Thread
from datetime import datetime, timedelta

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer, QDate
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QLabel, QPushButton, QSpinBox, QProgressBar, 
                            QGridLayout, QMessageBox, QTabWidget, QFormLayout, 
                            QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QWidget)

import swisseph as swe

from astrology.repositories.astrological_events_repository import AstrologicalEventsRepository
from astrology.services.astrological_event_calculator import AstrologicalEventCalculator
from shared.repositories.database import Database
from shared.services.notification_service import NotificationService

# Configure logging
logger = logging.getLogger(__name__)

class CalculatorThread(QObject, Thread):
    """Thread for calculating astrological events in the background."""
    
    progress_updated = pyqtSignal(float, str)
    finished = pyqtSignal(bool)
    
    def __init__(self, start_year: int, end_year: int, repository: AstrologicalEventsRepository):
        """Initialize the calculator thread.
        
        Args:
            start_year: First year to calculate
            end_year: Last year to calculate
            repository: Repository for storing events
        """
        QObject.__init__(self)
        Thread.__init__(self)
        self.daemon = True
        
        self.start_year = start_year
        self.end_year = end_year
        self.repository = repository
        
    def run(self):
        """Run the calculation thread."""
        try:
            calculator = AstrologicalEventCalculator(self.repository)
            calculator.set_progress_callback(self._progress_callback)
            
            success = calculator.calculate_range(self.start_year, self.end_year)
            self.finished.emit(success)
            
        except Exception as e:
            logger.error(f"Calculation thread error: {e}", exc_info=True)
            self.finished.emit(False)
    
    def _progress_callback(self, percentage: float, message: str):
        """Handle progress updates from calculator.
        
        Args:
            percentage: Progress percentage
            message: Progress message
        """
        # Emit signal for UI updates
        self.progress_updated.emit(percentage, message)


class AstrologicalDatabaseManager(QDialog):
    """Management interface for the astrological events database."""
    
    def __init__(self, database: Database, parent=None):
        """Initialize the database manager.
        
        Args:
            database: Database instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Astrological Database Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        self.database = database
        self.repository = AstrologicalEventsRepository(database)
        self.notification_service = NotificationService()
        
        # Set parent for notification service
        self.notification_service.set_parent(self)
        
        self.calculator_thread = None
        
        self._init_ui()
        self._connect_signals()
        self._update_status()
        self._update_database_stats()
        
        # Update status periodically during calculations
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status_during_calculation)
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.calculation_tab = QWidget()
        self.database_management_tab = QWidget()
        
        self._init_calculation_tab()
        self._init_database_management_tab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.calculation_tab, "Calculation")
        self.tab_widget.addTab(self.database_management_tab, "Database Management")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def _init_calculation_tab(self):
        """Initialize the calculation tab."""
        layout = QVBoxLayout()
        
        # Status Group
        status_group = QGroupBox("Database Status")
        status_layout = QGridLayout()
        
        self.total_events_label = QLabel("Total Events: --")
        self.year_range_label = QLabel("Year Range: --")
        self.last_calculation_label = QLabel("Last Calculation: --")
        
        status_layout.addWidget(QLabel("<b>Status:</b>"), 0, 0)
        status_layout.addWidget(self.total_events_label, 1, 0)
        status_layout.addWidget(self.year_range_label, 1, 1)
        status_layout.addWidget(self.last_calculation_label, 2, 0, 1, 2)
        status_group.setLayout(status_layout)
        
        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        # Initialize Default Range (1900-2100)
        self.init_default_btn = QPushButton("Initialize Default Range (1900-2100)")
        
        # Add Custom Range
        custom_range_layout = QHBoxLayout()
        
        self.start_year_spin = QSpinBox()
        self.start_year_spin.setRange(1800, 2200)
        self.start_year_spin.setValue(1800)
        
        self.end_year_spin = QSpinBox()
        self.end_year_spin.setRange(1800, 2200)
        self.end_year_spin.setValue(1900)
        
        self.calculate_range_btn = QPushButton("Calculate Range")
        
        custom_range_layout.addWidget(QLabel("Start Year:"))
        custom_range_layout.addWidget(self.start_year_spin)
        custom_range_layout.addWidget(QLabel("End Year:"))
        custom_range_layout.addWidget(self.end_year_spin)
        custom_range_layout.addWidget(self.calculate_range_btn)
        
        # Debug button to test aspects calculation directly
        self.test_aspects_btn = QPushButton("Test Aspects Calculation")
        self.test_aspects_btn.setToolTip("Test whether aspects can be calculated with the current Swiss Ephemeris setup")
        
        # Save aspects button
        self.save_aspects_btn = QPushButton("Save Current Aspects to Database")
        self.save_aspects_btn.setToolTip("Calculate current planetary aspects and save them to the database")
        
        # View aspects button
        self.view_aspects_btn = QPushButton("View Aspects in Database")
        self.view_aspects_btn.setToolTip("View and filter planetary aspects stored in the database")
        
        # Progress Section
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        
        actions_layout.addWidget(self.init_default_btn)
        actions_layout.addLayout(custom_range_layout)
        actions_layout.addWidget(self.test_aspects_btn)
        actions_layout.addWidget(self.save_aspects_btn)
        actions_layout.addWidget(self.view_aspects_btn)
        actions_layout.addWidget(self.progress_bar)
        actions_layout.addWidget(self.status_label)
        actions_group.setLayout(actions_layout)
        
        # Add all groups to main layout
        layout.addWidget(status_group)
        layout.addWidget(actions_group)
        
        self.calculation_tab.setLayout(layout)

    def _init_database_management_tab(self):
        """Initialize the database management tab."""
        layout = QVBoxLayout()
        
        # Database Statistics Group
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QGridLayout()
        
        self.db_size_label = QLabel("Database Size: --")
        self.total_tables_label = QLabel("Total Tables: --")
        self.total_indexes_label = QLabel("Total Indexes: --")
        
        # Event counts
        self.aspects_count_label = QLabel("Aspects: --")
        self.lunar_phases_count_label = QLabel("Lunar Phases: --")
        self.planet_phases_count_label = QLabel("Planet Phases: --")
        self.eclipses_count_label = QLabel("Eclipses: --")
        self.solar_events_count_label = QLabel("Solar Events: --")
        
        stats_layout.addWidget(QLabel("<b>General Statistics:</b>"), 0, 0, 1, 2)
        stats_layout.addWidget(self.db_size_label, 1, 0)
        stats_layout.addWidget(self.total_tables_label, 1, 1)
        stats_layout.addWidget(self.total_indexes_label, 2, 0)
        
        stats_layout.addWidget(QLabel("<b>Event Counts:</b>"), 3, 0, 1, 2)
        stats_layout.addWidget(self.aspects_count_label, 4, 0)
        stats_layout.addWidget(self.lunar_phases_count_label, 4, 1)
        stats_layout.addWidget(self.planet_phases_count_label, 5, 0)
        stats_layout.addWidget(self.eclipses_count_label, 5, 1)
        stats_layout.addWidget(self.solar_events_count_label, 6, 0)
        
        stats_group.setLayout(stats_layout)
        
        # Database Maintenance Group
        maintenance_group = QGroupBox("Database Maintenance")
        maintenance_layout = QVBoxLayout()
        
        # Maintenance buttons
        self.find_duplicates_btn = QPushButton("Find and Remove Duplicates")
        self.find_duplicates_btn.setToolTip("Search for and remove duplicate entries in the database")
        self.find_duplicates_btn.clicked.connect(self._handle_find_duplicates)
        
        self.vacuum_db_btn = QPushButton("Vacuum Database")
        self.vacuum_db_btn.setToolTip("Clean and optimize the database")
        self.vacuum_db_btn.clicked.connect(self._handle_vacuum_database)
        
        self.clear_all_btn = QPushButton("Clear All Data")
        self.clear_all_btn.setToolTip("WARNING: This will delete all data from the database")
        self.clear_all_btn.setStyleSheet("QPushButton { color: red; }")
        self.clear_all_btn.clicked.connect(self._handle_clear_database)
        
        maintenance_layout.addWidget(self.find_duplicates_btn)
        maintenance_layout.addWidget(self.vacuum_db_btn)
        maintenance_layout.addWidget(self.clear_all_btn)
        
        maintenance_group.setLayout(maintenance_layout)
        
        # Add groups to layout
        layout.addWidget(stats_group)
        layout.addWidget(maintenance_group)
        layout.addStretch()
        
        self.database_management_tab.setLayout(layout)

    def _update_database_stats(self):
        """Update the database statistics display."""
        try:
            # Use the connection context manager
            with self.database.connection() as conn:
                cursor = conn.cursor()
                
                # Get database file size
                db_path = self.database.get_database_path()
                db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convert to MB
                self.db_size_label.setText(f"Database Size: {db_size:.2f} MB")
                
                # Get table count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                self.total_tables_label.setText(f"Total Tables: {table_count}")
                
                # Get index count
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
                index_count = cursor.fetchone()[0]
                self.total_indexes_label.setText(f"Total Indexes: {index_count}")
                
                # Get event counts
                try:
                    cursor.execute("SELECT COUNT(*) FROM aspects")
                    aspects_count = cursor.fetchone()[0]
                    self.aspects_count_label.setText(f"Aspects: {aspects_count}")
                except sqlite3.Error:
                    self.aspects_count_label.setText("Aspects: Not available")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM lunar_phases")
                    lunar_phases_count = cursor.fetchone()[0]
                    self.lunar_phases_count_label.setText(f"Lunar Phases: {lunar_phases_count}")
                except sqlite3.Error:
                    self.lunar_phases_count_label.setText("Lunar Phases: Not available")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM planet_phases")
                    planet_phases_count = cursor.fetchone()[0]
                    self.planet_phases_count_label.setText(f"Planet Phases: {planet_phases_count}")
                except sqlite3.Error:
                    self.planet_phases_count_label.setText("Planet Phases: Not available")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM eclipses")
                    eclipses_count = cursor.fetchone()[0]
                    self.eclipses_count_label.setText(f"Eclipses: {eclipses_count}")
                except sqlite3.Error:
                    self.eclipses_count_label.setText("Eclipses: Not available")
                
                try:
                    cursor.execute("SELECT COUNT(*) FROM solar_events")
                    solar_events_count = cursor.fetchone()[0]
                    self.solar_events_count_label.setText(f"Solar Events: {solar_events_count}")
                except sqlite3.Error:
                    self.solar_events_count_label.setText("Solar Events: Not available")
                
        except Exception as e:
            logger.error(f"Error updating database statistics: {e}")
            try:
                self.notification_service.show_error(
                    "Statistics Error",
                    f"An error occurred while updating database statistics: {str(e)}"
                )
            except Exception as notification_error:
                logger.error(f"Failed to show error notification: {notification_error}")
                QMessageBox.critical(self, "Statistics Error", f"An error occurred: {str(e)}")

    def _handle_find_duplicates(self):
        """Handle finding and removing duplicate entries in the database."""
        try:
            # Use the connection context manager
            with self.database.connection() as conn:
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute("BEGIN")
                
                all_duplicates = []
                
                # Find duplicates in aspects table
                cursor.execute("""
                    SELECT exact_timestamp, body1_id, body2_id, aspect_type, COUNT(*) as count
                    FROM aspects 
                    GROUP BY exact_timestamp, body1_id, body2_id, aspect_type
                    HAVING count > 1
                """)
                aspect_duplicates = cursor.fetchall()
                if aspect_duplicates:
                    all_duplicates.append(("aspects", aspect_duplicates))
                
                # Find duplicates in lunar_phases table
                cursor.execute("""
                    SELECT timestamp, phase_type, COUNT(*) as count
                    FROM lunar_phases 
                    GROUP BY timestamp, phase_type
                    HAVING count > 1
                """)
                lunar_duplicates = cursor.fetchall()
                if lunar_duplicates:
                    all_duplicates.append(("lunar_phases", lunar_duplicates))
                
                # Find duplicates in planet_phases table
                cursor.execute("""
                    SELECT timestamp, body_id, phase_type, COUNT(*) as count
                    FROM planet_phases 
                    GROUP BY timestamp, body_id, phase_type
                    HAVING count > 1
                """)
                planet_duplicates = cursor.fetchall()
                if planet_duplicates:
                    all_duplicates.append(("planet_phases", planet_duplicates))
                
                # Find duplicates in eclipses table
                cursor.execute("""
                    SELECT timestamp, eclipse_type, COUNT(*) as count
                    FROM eclipses 
                    GROUP BY timestamp, eclipse_type
                    HAVING count > 1
                """)
                eclipse_duplicates = cursor.fetchall()
                if eclipse_duplicates:
                    all_duplicates.append(("eclipses", eclipse_duplicates))
                
                # Find duplicates in solar_events table
                cursor.execute("""
                    SELECT timestamp, event_type, COUNT(*) as count
                    FROM solar_events 
                    GROUP BY timestamp, event_type
                    HAVING count > 1
                """)
                solar_duplicates = cursor.fetchall()
                if solar_duplicates:
                    all_duplicates.append(("solar_events", solar_duplicates))
                
                # Count total duplicates
                total_duplicate_sets = sum(len(dups) for _, dups in all_duplicates)
                
                if not all_duplicates:
                    self.notification_service.show_info(
                        "No Duplicates Found",
                        "No duplicate entries were found in the database."
                    )
                    cursor.execute("ROLLBACK")
                    return
                
                # Ask for confirmation
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f"Found {total_duplicate_sets} sets of duplicate entries across {len(all_duplicates)} tables.")
                msg.setInformativeText("Do you want to remove the duplicates?")
                msg.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                msg.setDefaultButton(QMessageBox.StandardButton.No)
                
                if msg.exec() == QMessageBox.StandardButton.Yes:
                    # Remove duplicates from each table
                    duplicate_removed_count = 0
                    
                    for table_name, duplicates in all_duplicates:
                        if table_name == "aspects":
                            for dup in duplicates:
                                cursor.execute(f"""
                                    DELETE FROM {table_name} 
                                    WHERE exact_timestamp = ? AND body1_id = ? AND body2_id = ? AND aspect_type = ?
                                    AND rowid NOT IN (
                                        SELECT MIN(rowid)
                                        FROM {table_name}
                                        WHERE exact_timestamp = ? AND body1_id = ? AND body2_id = ? AND aspect_type = ?
                                        GROUP BY exact_timestamp, body1_id, body2_id, aspect_type
                                    )
                                """, (dup[0], dup[1], dup[2], dup[3], dup[0], dup[1], dup[2], dup[3]))
                                duplicate_removed_count += cursor.rowcount
                        
                        elif table_name == "lunar_phases":
                            for dup in duplicates:
                                cursor.execute(f"""
                                    DELETE FROM {table_name} 
                                    WHERE timestamp = ? AND phase_type = ?
                                    AND rowid NOT IN (
                                        SELECT MIN(rowid)
                                        FROM {table_name}
                                        WHERE timestamp = ? AND phase_type = ?
                                        GROUP BY timestamp, phase_type
                                    )
                                """, (dup[0], dup[1], dup[0], dup[1]))
                                duplicate_removed_count += cursor.rowcount
                        
                        elif table_name == "planet_phases":
                            for dup in duplicates:
                                cursor.execute(f"""
                                    DELETE FROM {table_name} 
                                    WHERE timestamp = ? AND body_id = ? AND phase_type = ?
                                    AND rowid NOT IN (
                                        SELECT MIN(rowid)
                                        FROM {table_name}
                                        WHERE timestamp = ? AND body_id = ? AND phase_type = ?
                                        GROUP BY timestamp, body_id, phase_type
                                    )
                                """, (dup[0], dup[1], dup[2], dup[0], dup[1], dup[2]))
                                duplicate_removed_count += cursor.rowcount
                        
                        elif table_name == "eclipses":
                            for dup in duplicates:
                                cursor.execute(f"""
                                    DELETE FROM {table_name} 
                                    WHERE timestamp = ? AND eclipse_type = ?
                                    AND rowid NOT IN (
                                        SELECT MIN(rowid)
                                        FROM {table_name}
                                        WHERE timestamp = ? AND eclipse_type = ?
                                        GROUP BY timestamp, eclipse_type
                                    )
                                """, (dup[0], dup[1], dup[0], dup[1]))
                                duplicate_removed_count += cursor.rowcount
                        
                        elif table_name == "solar_events":
                            for dup in duplicates:
                                cursor.execute(f"""
                                    DELETE FROM {table_name} 
                                    WHERE timestamp = ? AND event_type = ?
                                    AND rowid NOT IN (
                                        SELECT MIN(rowid)
                                        FROM {table_name}
                                        WHERE timestamp = ? AND event_type = ?
                                        GROUP BY timestamp, event_type
                                    )
                                """, (dup[0], dup[1], dup[0], dup[1]))
                                duplicate_removed_count += cursor.rowcount
                    
                    # Commit transaction
                    cursor.execute("COMMIT")
                    
                    self.notification_service.show_success(
                        "Duplicates Removed",
                        f"Successfully removed {duplicate_removed_count} duplicate entries from {len(all_duplicates)} tables."
                    )
                    
                    # Update statistics
                    self._update_database_stats()
                else:
                    # Rollback if user cancelled
                    cursor.execute("ROLLBACK")
                    
        except Exception as e:
            logger.error(f"Error finding/removing duplicates: {e}")
            # Ensure we rollback on error using the context manager
            if 'cursor' in locals():
                try:
                    cursor.execute("ROLLBACK")
                except:
                    pass  # If cursor execution fails, just continue
            
            # Show error notification with exception handling
            try:
                self.notification_service.show_error(
                    "Database Error",
                    f"An error occurred while managing duplicates: {str(e)}"
                )
            except Exception as notification_error:
                logger.error(f"Failed to show error notification: {notification_error}")
                # Fallback to message box
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def _handle_vacuum_database(self):
        """Handle vacuuming (optimizing) the database."""
        try:
            # Use the connection context manager
            with self.database.connection() as conn:
                cursor = conn.cursor()
                
                # Run VACUUM command
                cursor.execute("VACUUM")
                
                try:
                    self.notification_service.show_success(
                        "Database Optimized",
                        "Successfully optimized the database."
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to show success notification: {notification_error}")
                    QMessageBox.information(self, "Success", "Database successfully optimized")
                
                # Update statistics
                self._update_database_stats()
                
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            try:
                self.notification_service.show_error(
                    "Database Error",
                    f"An error occurred while optimizing the database: {str(e)}"
                )
            except Exception as notification_error:
                logger.error(f"Failed to show error notification: {notification_error}")
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def _handle_clear_database(self):
        """Clear all data from the database."""
        response = QMessageBox.warning(
            self,
            "Clear Database",
            "WARNING: This will delete ALL data from the database. This action cannot be undone.\n\nAre you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.Yes:
            try:
                # Use the connection context manager
                with self.database.connection() as conn:
                    cursor = conn.cursor()
                    
                    # Start transaction
                    cursor.execute("BEGIN")
                    
                    # Clear all astrological tables
                    tables_to_clear = [
                        "aspects", 
                        "lunar_phases", 
                        "planet_phases", 
                        "eclipses", 
                        "solar_events",
                        "positions",
                        "calculation_metadata"
                    ]
                    
                    for table in tables_to_clear:
                        try:
                            cursor.execute(f"DELETE FROM {table}")
                            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                        except sqlite3.Error as e:
                            logger.warning(f"Table {table} could not be cleared: {e}")
                    
                    # Commit changes
                    cursor.execute("COMMIT")
                    
                    try:
                        self.notification_service.show_success(
                            "Database Cleared",
                            "All astrological events have been removed from the database."
                        )
                    except Exception as notification_error:
                        logger.error(f"Failed to show success notification: {notification_error}")
                        QMessageBox.information(self, "Success", "Database successfully cleared")
                    
                    # Update statistics
                    self._update_database_stats()
                    self._update_status()
                    
            except Exception as e:
                logger.error(f"Error clearing database: {e}")
                try:
                    self.notification_service.show_error(
                        "Database Error",
                        f"An error occurred while clearing the database: {str(e)}"
                    )
                except Exception as notification_error:
                    logger.error(f"Failed to show error notification: {notification_error}")
                    QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def _connect_signals(self):
        """Connect UI signals to slots."""
        self.init_default_btn.clicked.connect(self._handle_init_default)
        self.calculate_range_btn.clicked.connect(self._handle_calculate_range)
        self.test_aspects_btn.clicked.connect(self._handle_test_aspects)
        self.save_aspects_btn.clicked.connect(self._handle_save_aspects)
        self.view_aspects_btn.clicked.connect(self._handle_view_aspects)

    def _handle_init_default(self):
        """Handle initialization of default range."""
        self._start_calculation("Initializing default range (1900-2100)", 1900, 2100)

    def _handle_calculate_range(self):
        """Handle calculation of custom range."""
        start_year = self.start_year_spin.value()
        end_year = self.end_year_spin.value()
        
        if end_year <= start_year:
            QMessageBox.warning(self, "Invalid Range", "End year must be greater than start year")
            return
            
        if end_year - start_year > 200:
            response = QMessageBox.question(
                self, 
                "Large Range", 
                f"Calculating {end_year - start_year} years may take a long time. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if response == QMessageBox.StandardButton.No:
                return
        
        self._start_calculation(f"Calculating range {start_year}-{end_year}", start_year, end_year)

    def _start_calculation(self, message: str, start_year: int, end_year: int):
        """Prepare UI for calculation and start calculation thread.
        
        Args:
            message: Status message
            start_year: First year to calculate
            end_year: Last year to calculate
        """
        # Update UI for calculation
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText(message)
        self.progress_bar.setValue(0)
        
        self.init_default_btn.setEnabled(False)
        self.calculate_range_btn.setEnabled(False)
        self.start_year_spin.setEnabled(False)
        self.end_year_spin.setEnabled(False)
        
        # Start calculation in a separate thread
        self.calculator_thread = CalculatorThread(start_year, end_year, self.repository)
        self.calculator_thread.progress_updated.connect(self._update_progress)
        self.calculator_thread.finished.connect(self._calculation_finished)
        self.calculator_thread.start()
        
        # Start timer for periodic updates
        self.timer.start(2000)  # Update every 2 seconds
        
        # Notify user
        self.notification_service.show_info(f"Started calculating astrological events for {start_year}-{end_year}")
        logger.info(f"Started calculation: {start_year}-{end_year}")

    def _update_progress(self, percentage: float, message: str):
        """Update progress bar and status label.
        
        Args:
            percentage: Progress percentage
            message: Progress message
        """
        self.progress_bar.setValue(int(percentage))
        self.status_label.setText(message)

    def _calculation_finished(self, success: bool):
        """Handle calculation completion.
        
        Args:
            success: Whether calculation was successful
        """
        # Stop timer
        self.timer.stop()
        
        # Update UI
        if success:
            self.status_label.setText("Calculation completed successfully")
            self.notification_service.show_success("Astrological events calculation completed")
            logger.info("Calculation completed successfully")
            
            # Verify aspects were properly stored
            self._verify_aspects_calculation()
        else:
            self.status_label.setText("Calculation failed")
            self.notification_service.show_error("Astrological events calculation failed")
            logger.error("Calculation failed")
        
        # Re-enable controls
        self.init_default_btn.setEnabled(True)
        self.calculate_range_btn.setEnabled(True)
        self.start_year_spin.setEnabled(True)
        self.end_year_spin.setEnabled(True)
        
        # Update status
        self._update_status()

    def _verify_aspects_calculation(self):
        """Verify that aspects were properly calculated and stored in the database."""
        try:
            # Get the years that were last calculated
            stats = self.repository.get_calculation_status()
            
            if stats['calculated_ranges']:
                last_calc = max(stats['calculated_ranges'], key=lambda r: r['calculation_date'])
                start_year = last_calc['start_year']
                end_year = last_calc['end_year']
                
                # For larger ranges, just check a sample
                years_to_check = []
                if end_year - start_year > 10:
                    # Check first, last and a couple in the middle
                    years_to_check = [
                        start_year,
                        start_year + (end_year - start_year) // 3,
                        start_year + 2 * (end_year - start_year) // 3,
                        end_year
                    ]
                else:
                    # Check all years for smaller ranges
                    years_to_check = list(range(start_year, end_year + 1))
                
                # Verify each year
                total_aspects = 0
                for year in years_to_check:
                    logger.debug(f"Verifying aspects for year {year}")
                    results = self.repository.verify_aspects_in_database(year)
                    aspects_in_year = results['total_aspects']
                    total_aspects += aspects_in_year
                    
                    if aspects_in_year == 0:
                        logger.warning(f"No aspects found for year {year}")
                
                # Log the total
                if total_aspects > 0:
                    logger.info(f"Verified {total_aspects} aspects in sample years")
                else:
                    logger.warning("No aspects found in database after calculation")
                    # Show a warning to the user
                    QMessageBox.warning(
                        self,
                        "Aspect Calculation Warning",
                        "No planetary aspects were found in the database after calculation. "
                        "This might indicate a problem with the planetary aspect calculation."
                    )
        except Exception as e:
            logger.error(f"Error verifying aspects: {e}", exc_info=True)

    def _update_status(self):
        """Update all status labels with current database information."""
        try:
            stats = self.repository.get_calculation_status()
            
            # Update status labels
            self.total_events_label.setText(f"Total Events: {stats['total_events']:,}")
            
            # Determine year range
            if stats['calculated_ranges']:
                min_year = min(r['start_year'] for r in stats['calculated_ranges'])
                max_year = max(r['end_year'] for r in stats['calculated_ranges'])
                self.year_range_label.setText(f"Year Range: {min_year}-{max_year}")
            else:
                self.year_range_label.setText("Year Range: Not calculated")
            
            # Last calculation
            if stats['calculated_ranges']:
                last_calc = max(stats['calculated_ranges'], key=lambda r: r['calculation_date'])
                dt = datetime.fromisoformat(last_calc['calculation_date'])
                self.last_calculation_label.setText(f"Last Calculation: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                self.last_calculation_label.setText("Last Calculation: Never")
            
            # Event counts
            if 'event_counts' in stats:
                self.aspects_count_label.setText(f"Aspects: {stats['event_counts'].get('aspects', 0):,}")
                self.lunar_phases_count_label.setText(f"Lunar Phases: {stats['event_counts'].get('lunar_phases', 0):,}")
                self.planet_phases_count_label.setText(f"Planet Phases: {stats['event_counts'].get('planet_phases', 0):,}")
                self.eclipses_count_label.setText(f"Eclipses: {stats['event_counts'].get('eclipses', 0):,}")
                self.solar_events_count_label.setText(f"Solar Events: {stats['event_counts'].get('solar_events', 0):,}")
            
            # Enable/disable default button
            self.init_default_btn.setEnabled(not stats.get('has_default_range', False))
        
        except Exception as e:
            logger.error(f"Error updating status: {e}", exc_info=True)
    
    def _update_status_during_calculation(self):
        """Update status while calculation is running."""
        # Query the database for the latest counts while calculation is in progress
        self._update_status()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.calculator_thread and self.calculator_thread.is_alive():
            response = QMessageBox.question(
                self,
                "Calculation in Progress",
                "A calculation is still running. Close anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # Stop the timer but let the thread run to completion
            self.timer.stop()
            
            # Thread is daemon, so it will be terminated when the application exits
            logger.warning("Closing dialog with calculation still running")
        
        event.accept()

    def _handle_test_aspects(self):
        """
        Test aspect calculations for the current date and display results.
        """
        try:
            # Initialize ephemeris path
            swe.set_ephe_path("sweph")
            
            # Get current Julian day
            date = datetime.now()
            jd = swe.julday(date.year, date.month, date.day, date.hour + date.minute/60.0)
            
            # Get planetary positions
            planet_positions = {}
            planets = {
                swe.SUN: "Sun", 
                swe.MOON: "Moon", 
                swe.MERCURY: "Mercury", 
                swe.VENUS: "Venus", 
                swe.MARS: "Mars", 
                swe.JUPITER: "Jupiter", 
                swe.SATURN: "Saturn", 
                swe.URANUS: "Uranus", 
                swe.NEPTUNE: "Neptune", 
                swe.PLUTO: "Pluto"
            }
            
            for planet_id, planet_name in planets.items():
                result = swe.calc_ut(jd, planet_id)
                # Extract the longitude value (first element of the returned tuple)
                position = result[0] if isinstance(result[0], (int, float)) else result[0][0]
                planet_positions[planet_name] = position
            
            # Check aspects between all planets
            aspects = self._check_all_aspects(planet_positions)
            
            # Display results
            if aspects:
                msg = f"Aspects for {date.strftime('%Y-%m-%d %H:%M')}:\n\n"
                msg += "\n".join(aspects)
                QMessageBox.information(self, "Aspect Test Results", msg)
            else:
                QMessageBox.information(self, "Aspect Test Results", "No significant aspects found.")
                
        except Exception as e:
            logger.error(f"Error testing aspects: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to test aspects: {str(e)}")

    def _check_all_aspects(self, planet_positions):
        """
        Check aspects between all planets based on their positions.
        
        Args:
            planet_positions (dict): Dictionary mapping planet names to their positions in degrees
            
        Returns:
            list: List of aspect descriptions
        """
        try:
            aspects = []
            
            # Import AspectType from moon_phase_calculator
            from astrology.services.moon_phase_calculator import AspectType
            
            # Define major aspects and their orbs using AspectType
            major_aspects = {
                "Conjunction": (AspectType.CONJUNCTION.angle, AspectType.CONJUNCTION.base_orb),
                "Opposition": (AspectType.OPPOSITION.angle, AspectType.OPPOSITION.base_orb),
                "Trine": (AspectType.TRINE.angle, AspectType.TRINE.base_orb),
                "Square": (AspectType.SQUARE.angle, AspectType.SQUARE.base_orb),
                "Sextile": (AspectType.SEXTILE.angle, AspectType.SEXTILE.base_orb)
            }
            
            # Check aspects between each pair of planets
            planets = list(planet_positions.keys())
            for i in range(len(planets)):
                for j in range(i + 1, len(planets)):
                    planet1 = planets[i]
                    planet2 = planets[j]
                    pos1 = planet_positions[planet1]
                    pos2 = planet_positions[planet2]
                    
                    # Normalize angles
                    pos1 = self._normalize_angle(pos1)
                    pos2 = self._normalize_angle(pos2)
                    
                    # Calculate angular difference
                    diff = abs(pos1 - pos2)
                    if diff > 180:
                        diff = 360 - diff
                    
                    # Check for aspects
                    for aspect_name, (aspect_angle, orb) in major_aspects.items():
                        if abs(diff - aspect_angle) <= orb:
                            # Calculate exactness (how close to exact aspect)
                            exactness = abs(diff - aspect_angle)
                            exactness_percentage = round(100 * (1 - exactness / orb))
                            
                            # Format aspect description
                            aspects.append(f"{planet1} {aspect_name} {planet2} - {exactness_percentage}% exact ({round(exactness, 2)}° orb)")
            
            # Sort aspects by exactness (assuming higher percentage is first in the list)
            aspects.sort(reverse=True, key=lambda x: int(x.split(" - ")[1].split("%")[0]))
            
            return aspects
        except Exception as e:
            logger.error(f"Error in _check_all_aspects: {e}")
            return []
            
    def _normalize_angle(self, angle):
        """
        Normalize an angle to be between 0 and 360 degrees.
        
        Args:
            angle: Angle in degrees
            
        Returns:
            Normalized angle (0-360)
        """
        try:
            normalized = float(angle) % 360.0
            if normalized < 0:
                normalized += 360.0
            return normalized
        except (TypeError, ValueError) as e:
            logger.error(f"Error normalizing angle: {e}")
            return 0.0

    def _handle_save_aspects(self):
        """
        Calculate current aspects and save them to the database.
        """
        try:
            # Initialize ephemeris path
            swe.set_ephe_path("sweph")
            
            # Get current Julian day
            date = datetime.now()
            jd = swe.julday(date.year, date.month, date.day, date.hour + date.minute/60.0)
            
            # Get planetary positions
            planet_positions = {}
            planets = {
                swe.SUN: "Sun", 
                swe.MOON: "Moon", 
                swe.MERCURY: "Mercury", 
                swe.VENUS: "Venus", 
                swe.MARS: "Mars", 
                swe.JUPITER: "Jupiter", 
                swe.SATURN: "Saturn", 
                swe.URANUS: "Uranus", 
                swe.NEPTUNE: "Neptune", 
                swe.PLUTO: "Pluto"
            }
            
            for planet_id, planet_name in planets.items():
                result = swe.calc_ut(jd, planet_id)
                # Extract the longitude value (first element of the returned tuple)
                position = result[0] if isinstance(result[0], (int, float)) else result[0][0]
                planet_positions[planet_name] = position
            
            # Check aspects between all planets
            aspects = self._check_all_aspects(planet_positions)
            
            if aspects:
                # Save aspects to database
                self._save_aspects_to_database(date, aspects)
                self.status_label.setText(f"Saved {len(aspects)} aspects for {date.strftime('%Y-%m-%d %H:%M')}")
                QMessageBox.information(self, "Success", f"Saved {len(aspects)} aspects to database.")
            else:
                self.status_label.setText("No aspects found to save.")
                QMessageBox.information(self, "No Aspects", "No significant aspects found to save.")
                
        except Exception as e:
            logger.error(f"Error saving aspects: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save aspects: {str(e)}")

    def _save_aspects_to_database(self, date, aspects):
        """
        Save calculated aspects to SQLite database.
        
        Args:
            date (datetime): The date for which aspects were calculated
            aspects (list): List of aspect descriptions
        """
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              "data", "aspects.db")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Create aspects table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS aspects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                planet1 TEXT,
                planet2 TEXT,
                aspect_type TEXT,
                exactness REAL,
                orb REAL
            )
            ''')
            
            # Create celestial_bodies table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS celestial_bodies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                weight REAL
            )
            ''')
            
            # Parse and insert aspects
            for aspect_text in aspects:
                # Example format: "Sun Conjunction Moon - 95% exact (0.4° orb)"
                parts = aspect_text.split(" - ")
                planets_aspect = parts[0].split(" ")
                
                # Extract data
                planet1 = planets_aspect[0]
                aspect_type = planets_aspect[1]
                planet2 = planets_aspect[2]
                
                # Extract exactness and orb
                exactness_str = parts[1].split(" exact ")[0]
                exactness = float(exactness_str.replace("%", ""))
                
                orb_str = parts[1].split("(")[1].split("°")[0]
                orb = float(orb_str)
                
                # Insert into database using helper method
                self._add_aspect_to_database(cursor, date, planet1, planet2, aspect_type, exactness, orb)
            
            # Commit changes
            conn.commit()
            logger.info(f"Saved {len(aspects)} aspects to database")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()

    def _add_aspect_to_database(self, cursor, date, planet1, planet2, aspect_type, exactness, orb):
        """
        Add a single aspect to the database.
        
        Args:
            cursor: Database cursor
            date: Date of the aspect
            planet1: First planet
            planet2: Second planet
            aspect_type: Type of aspect (Conjunction, Opposition, etc.)
            exactness: Exactness percentage (0-100)
            orb: Orb in degrees
            
        Returns:
            ID of the inserted aspect or None if validation fails
        """
        try:
            # Validate aspect data
            if not self._validate_aspect(date, planet1, planet2, aspect_type, exactness, orb):
                logger.warning(f"Invalid aspect data skipped: {planet1} {aspect_type} {planet2}")
                return None
                
            # Make sure both planets exist in celestial_bodies table
            for planet_name in [planet1, planet2]:
                cursor.execute('SELECT id FROM celestial_bodies WHERE name = ?', (planet_name,))
                if not cursor.fetchone():
                    # Add planet if it doesn't exist
                    cursor.execute(
                        'INSERT INTO celestial_bodies (name, type, weight) VALUES (?, ?, ?)',
                        (planet_name, 'Planet', 1.0)  # Default weight
                    )
            
            # Format date properly
            if isinstance(date, datetime):
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(date)
                
            # Insert aspect
            cursor.execute('''
            INSERT INTO aspects (date, planet1, planet2, aspect_type, exactness, orb)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (date_str, planet1, planet2, aspect_type, exactness, orb))
            
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding aspect to database: {e}")
            return None
            
    def _validate_aspect(self, date, planet1, planet2, aspect_type, exactness, orb):
        """
        Validate aspect data before inserting into database.
        
        Args:
            date: Date of the aspect
            planet1: First planet
            planet2: Second planet
            aspect_type: Type of aspect
            exactness: Exactness percentage
            orb: Orb in degrees
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check for missing values
            if not all([date, planet1, planet2, aspect_type]):
                logger.warning("Missing required aspect data")
                return False
                
            # Check planet names (simple validation)
            valid_planets = [
                "Sun", "Moon", "Mercury", "Venus", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
            ]
            if planet1 not in valid_planets or planet2 not in valid_planets:
                logger.warning(f"Invalid planet name: {planet1}, {planet2}")
                return False
                
            # Check aspect type
            valid_aspects = ["Conjunction", "Opposition", "Trine", "Square", "Sextile"]
            if aspect_type not in valid_aspects:
                logger.warning(f"Invalid aspect type: {aspect_type}")
                return False
                
            # Validate numerical values
            if not isinstance(exactness, (int, float)) or exactness < 0 or exactness > 100:
                logger.warning(f"Invalid exactness value: {exactness}")
                return False
                
            if not isinstance(orb, (int, float)) or orb < 0 or orb > 10:
                logger.warning(f"Invalid orb value: {orb}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Error validating aspect: {e}")
            return False

    def _handle_view_aspects(self):
        """
        View aspects stored in the database for a specific date range.
        """
        try:
            # Simple dialog to get date range
            start_date = QDate.currentDate().addDays(-7)  # Default to last week
            end_date = QDate.currentDate()
            
            dialog = QDialog(self)
            dialog.setWindowTitle("View Aspects")
            layout = QVBoxLayout()
            
            # Date range selection
            date_layout = QFormLayout()
            start_date_edit = QDateEdit(start_date)
            start_date_edit.setCalendarPopup(True)
            end_date_edit = QDateEdit(end_date)
            end_date_edit.setCalendarPopup(True)
            
            date_layout.addRow("Start Date:", start_date_edit)
            date_layout.addRow("End Date:", end_date_edit)
            
            # Planet filters
            filter_layout = QHBoxLayout()
            planet_label = QLabel("Filter by planet:")
            planet_combo = QComboBox()
            planet_combo.addItem("All Planets")
            
            # Add valid planets
            valid_planets = [
                "Sun", "Moon", "Mercury", "Venus", "Mars", 
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"
            ]
            planet_combo.addItems(valid_planets)
            
            filter_layout.addWidget(planet_label)
            filter_layout.addWidget(planet_combo)
            
            # Aspect type filter
            aspect_label = QLabel("Filter by aspect:")
            aspect_combo = QComboBox()
            aspect_combo.addItem("All Aspects")
            
            # Add valid aspects
            valid_aspects = ["Conjunction", "Opposition", "Trine", "Square", "Sextile"]
            aspect_combo.addItems(valid_aspects)
            
            filter_layout.addWidget(aspect_label)
            filter_layout.addWidget(aspect_combo)
            
            # Buttons
            button_layout = QHBoxLayout()
            view_button = QPushButton("View Aspects")
            cancel_button = QPushButton("Cancel")
            
            button_layout.addWidget(view_button)
            button_layout.addWidget(cancel_button)
            
            # Add all layouts to main layout
            layout.addLayout(date_layout)
            layout.addLayout(filter_layout)
            layout.addLayout(button_layout)
            
            # Results table
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["Date", "Planet 1", "Aspect", "Planet 2", "Exactness", "Orb"])
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
            layout.addWidget(table)
            
            dialog.setLayout(layout)
            
            # Connect signals
            cancel_button.clicked.connect(dialog.reject)
            view_button.clicked.connect(lambda: self._load_aspects_to_table(
                table, 
                start_date_edit.date().toString("yyyy-MM-dd"),
                end_date_edit.date().toString("yyyy-MM-dd"),
                planet_combo.currentText() if planet_combo.currentIndex() > 0 else None,
                aspect_combo.currentText() if aspect_combo.currentIndex() > 0 else None
            ))
            
            # Show dialog
            dialog.setMinimumSize(800, 600)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error viewing aspects: {e}")
            QMessageBox.critical(self, "Error", f"Failed to view aspects: {e}")
            
    def _load_aspects_to_table(self, table, start_date, end_date, planet=None, aspect_type=None):
        """
        Load aspects from database and display in table.
        
        Args:
            table: QTableWidget to populate
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            planet: Optional planet to filter by
            aspect_type: Optional aspect type to filter by
        """
        try:
            # Get database path
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              "data", "aspects.db")
                              
            if not os.path.exists(db_path):
                QMessageBox.warning(self, "No Data", "Aspects database not found or no aspects have been saved.")
                return
                
            # Connect to database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Build query based on filters
            query = "SELECT date, planet1, aspect_type, planet2, exactness, orb FROM aspects WHERE date BETWEEN ? AND ?"
            params = [f"{start_date} 00:00:00", f"{end_date} 23:59:59"]
            
            if planet:
                query += " AND (planet1 = ? OR planet2 = ?)"
                params.extend([planet, planet])
                
            if aspect_type:
                query += " AND aspect_type = ?"
                params.append(aspect_type)
                
            query += " ORDER BY date DESC"
            
            # Execute query
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Clear table
            table.setRowCount(0)
            
            # Populate table
            for row_idx, (date, planet1, aspect, planet2, exactness, orb) in enumerate(results):
                table.insertRow(row_idx)
                table.setItem(row_idx, 0, QTableWidgetItem(date))
                table.setItem(row_idx, 1, QTableWidgetItem(planet1))
                table.setItem(row_idx, 2, QTableWidgetItem(aspect))
                table.setItem(row_idx, 3, QTableWidgetItem(planet2))
                table.setItem(row_idx, 4, QTableWidgetItem(f"{exactness:.1f}%"))
                table.setItem(row_idx, 5, QTableWidgetItem(f"{orb:.2f}°"))
                
            # Update status
            if results:
                self.status_label.setText(f"Found {len(results)} aspects matching criteria")
            else:
                self.status_label.setText("No aspects found matching criteria")
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Error loading aspects: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load aspects: {e}")
            self.status_label.setText(f"Error: {e}") 