"""
Calendar Visualization Widget for the Kamea Cosmic Calendar.

This widget provides a circular calendar visualization that displays the relationship
between calendar days and the mathematical structure of the Kamea system.
"""

import csv
import math
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFrame,
    QFormLayout,
    QSplitter,
    QTextEdit,
    QGraphicsDropShadowEffect,
)

from shared.utils.config import get_config

# Setup module logger
logger = logging.getLogger(__name__)

class CalendarVisualizationWidget(QWidget):
    """Widget for visualizing the Kamea Cosmic Calendar."""

    def __init__(self, parent=None):
        """Initialize the calendar visualization widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize instance variables
        self.selected_differential = None
        self.day_markers = {}
        self.calendar_data = []
        self.quadsets_data = []
        self.conrune_reversal_map = {}
        self.recursive_pairs = set()
        self.factors = [2, 3, 4, 5, 6, 8, 9, 10, 12]
        self.geometric_factor_map = {}
        self.differential_map = {}
        self.zodiacal_map = {}
        self.zodiac_sign_map = {
            'A': 'Aries',
            'B': 'Taurus',
            'C': 'Gemini',
            'D': 'Cancer',
            'E': 'Leo',
            'F': 'Virgo',
            'G': 'Libra',
            'H': 'Scorpio',
            'I': 'Sagittarius',
            'J': 'Capricorn',
            'K': 'Aquarius',
            'L': 'Pisces'
        }
        
        # Initialize UI components
        self._init_ui()

        # Load data
        self._load_calendar_data()
        self._load_quadsets_data()
        
        # Build the maps (order matters)
        self._build_lookup_maps()
        self._build_conrune_reversal_map_from_quadsets()
        self._build_geometric_factor_maps()
        
        # Create initial visualization
        self._update_visualization()
        
    def _format_zodiacal_position(self, zodiacal_text):
        """Format zodiacal position to show sign name instead of letter.
        
        Args:
            zodiacal_text: The raw zodiacal position text (e.g. "11 B")
            
        Returns:
            Formatted zodiacal position (e.g. "11° Taurus")
        """
        if not zodiacal_text or zodiacal_text == "XXXX":
            return zodiacal_text
            
        parts = zodiacal_text.strip().split()
        if len(parts) < 2:
            return zodiacal_text
            
        if parts[-1] in self.zodiac_sign_map:
            degree = parts[0]
            sign_letter = parts[-1]
            sign_name = self.zodiac_sign_map.get(sign_letter, f"Sign {sign_letter}")
            return f"{degree}° {sign_name}"
        
        return zodiacal_text

    def _init_ui(self):
        """Initialize the UI components."""
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the scene and view
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setStyleSheet("background-color: white;")
        
        # Create info panel for connected pairs
        self.info_panel = QTextEdit()
        self.info_panel.setReadOnly(True)
        self.info_panel.setMinimumWidth(300)
        self.info_panel.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                font-family: Arial, sans-serif;
            }
        """)
        
        # Create horizontal splitter for visualization and info panel
        viz_splitter = QSplitter(Qt.Orientation.Horizontal)
        viz_splitter.addWidget(self.view)
        viz_splitter.addWidget(self.info_panel)
        viz_splitter.setSizes([700, 300])  # Initial sizes
        
        # Create controls frame
        controls_frame = QFrame()
        controls_frame.setFrameShape(QFrame.Shape.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Create form layout for controls
        form_layout = QFormLayout()
        
        # Create control for differential selection
        self.differential_spin = QSpinBox()
        self.differential_spin.setRange(0, 364)
        self.differential_spin.setValue(self.selected_differential or 0)
        self.differential_spin.valueChanged.connect(self._differential_changed)
        form_layout.addRow("Selected Differential:", self.differential_spin)
        
        # Create lookup box
        self.lookup_entry = QLineEdit()
        self.lookup_entry.setPlaceholderText("Enter date (e.g., '25 March') or differential")
        self.lookup_entry.returnPressed.connect(self._lookup_entry)
        form_layout.addRow("Lookup:", self.lookup_entry)
        
        # Create lookup label
        self.lookup_result_label = QLabel("")
        self.lookup_result_label.setWordWrap(True)
        
        # Create checkboxes for interaction options
        top_controls_layout = QHBoxLayout()
        
        # Create "Show Factors" checkbox
        self.show_factors_checkbox = QCheckBox("Show Factors")
        self.show_factors_checkbox.setChecked(True)
        self.show_factors_checkbox.stateChanged.connect(self._update_visualization)
        top_controls_layout.addWidget(self.show_factors_checkbox)
        
        # Create "Show Reversals" checkbox
        self.show_reversals_checkbox = QCheckBox("Show Reversal Connections")
        self.show_reversals_checkbox.setChecked(False)
        self.show_reversals_checkbox.stateChanged.connect(self._update_visualization)
        top_controls_layout.addWidget(self.show_reversals_checkbox)
        
        # Create a second row for additional checkboxes
        bottom_controls_layout = QHBoxLayout()
        
        # Add "Radial Visualization" checkbox
        self.radial_mode_checkbox = QCheckBox("Radial Visualization")
        self.radial_mode_checkbox.setChecked(False)
        self.radial_mode_checkbox.stateChanged.connect(self._update_visualization)
        self.radial_mode_checkbox.setToolTip(
            "When checked, connections will radiate from the center.\n"
            "When unchecked, connections will be direct between differentials."
        )
        bottom_controls_layout.addWidget(self.radial_mode_checkbox)
        
        # Create layout for factor checkboxes
        self.factor_checkboxes = []
        factors_layout = QHBoxLayout()
        factors_frame = QFrame()
        factors_layout_inner = QHBoxLayout(factors_frame)
        factors_layout_inner.setContentsMargins(0, 0, 0, 0)
        
        # Add checkboxes for each factor
        for factor in self.factors:
            checkbox = QCheckBox(f"{factor}")
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(self._update_visualization)
            self.factor_checkboxes.append(checkbox)
            factors_layout_inner.addWidget(checkbox)
        
        factors_layout.addWidget(QLabel("Factors:"))
        factors_layout.addWidget(factors_frame)
        factors_layout.addStretch()
        
        # Add info label at the bottom
        self.info_label = QLabel("Hover over a day marker to view details")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("padding: 5px; background-color: #f8f8f8; border-radius: 3px;")
        
        # Add all components to the layout
        controls_layout.addLayout(form_layout)
        controls_layout.addWidget(self.lookup_result_label)
        controls_layout.addLayout(top_controls_layout)
        controls_layout.addLayout(bottom_controls_layout)
        controls_layout.addLayout(factors_layout)
        
        # Main layout with splitter for resizing
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(viz_splitter)
        main_splitter.addWidget(controls_frame)
        main_splitter.setSizes([700, 300])  # Initial sizes
        
        layout.addWidget(main_splitter)
        layout.addWidget(self.info_label)
        
        # Install event filter to capture mouse events
        self.view.viewport().installEventFilter(self)
        
        # Initialize data
        self.selected_differential = None
        
        # Initially create the visualization
        self._update_visualization()

    def _build_lookup_maps(self):
        """Build lookup maps for quick access to calendar entries."""
        # Map for zodiacal position lookups
        self.zodiacal_map = {}
        # Map for differential lookups
        self.differential_map = {}
        # Map for conrune pair-to-pair relationships
        self.conrune_reversal_map = {}
        # Map for recursive pairs
        self.recursive_pairs = set()
        # Map for differential-to-differential relationships by geometric factors
        self.geometric_factor_map = {}
        
        # Map zodiac letters to sign names
        self.zodiac_sign_map = {
            'A': 'Aries',
            'B': 'Taurus',
            'C': 'Gemini',
            'D': 'Cancer',
            'E': 'Leo',
            'F': 'Virgo',
            'G': 'Libra',
            'H': 'Scorpio',
            'I': 'Sagittarius',
            'J': 'Capricorn',
            'K': 'Aquarius',
            'L': 'Pisces'
        }
        
        # Map sign names back to letters for lookup
        self.sign_letter_map = {v: k for k, v in self.zodiac_sign_map.items()}
        
        # First pass: Build basic lookup maps
        for entry in self.calendar_data:
            # Add to differential map
            diff = entry.get('Differential', '')
            if diff and diff != "XXXX":
                self.differential_map[diff] = entry
            
            # Add to zodiacal map
            zodiacal = entry.get('Zodiacal', '')
            if zodiacal and zodiacal != "XXXX":
                parts = zodiacal.split()
                if len(parts) > 1 and parts[-1] in "ABCDEFGHIJKL":
                    degree = int(parts[0])
                    sign_letter = parts[-1]
                    sign_name = self.zodiac_sign_map.get(sign_letter, '')
                    if sign_name:
                        key = f"{sign_name}_{degree}"
                        self.zodiacal_map[key] = entry
        
        # Build conrune reversal map from quadsets data
        self._build_conrune_reversal_map_from_quadsets()
        
        # Build geometric factor maps
        self._build_geometric_factor_maps()
        
        logger.debug(f"Built lookup maps with {len(self.differential_map)} differentials and {len(self.zodiacal_map)} zodiacal positions")

    def _build_conrune_reversal_map_from_quadsets(self):
        """Build the conrune reversal map based on the quadsets_for_app.csv file."""
        # Reset the maps
        self.conrune_reversal_map = {}
        self.recursive_pairs = set()
        
        # Process regular quadsets
        for entry in self.quadsets_data:
            # Skip rows without quadset data
            if 'QuadSet' not in entry or not entry['QuadSet']:
                continue
                
            # Check if this is a regular quadset or recursive pair
            if entry['QuadSet'].startswith('RP'):
                # This is a recursive pair
                try:
                    a_diff = entry.get('A', '')
                    if a_diff and a_diff.isdigit():
                        # Only add valid differentials (0-359)
                        a_diff_int = int(a_diff)
                        if 0 <= a_diff_int < 360:
                            self.recursive_pairs.add(a_diff)
                        else:
                            logger.warning(f"Skipping out-of-range recursive pair differential: {a_diff}")
                except Exception as e:
                    logger.error(f"Error processing recursive pair {entry.get('QuadSet', '')}: {e}")
                    continue  # Skip to next entry on error
            else:
                # This is a regular quadset - extract AB and CD differentials
                try:
                    ab_diff = entry.get('A-B', '')
                    cd_diff = entry.get('C-D', '')
                    
                    # Skip quickly if either value is missing or not numeric
                    if not ab_diff or not ab_diff.isdigit() or not cd_diff or not cd_diff.isdigit():
                        continue
                
                    # Validate both differentials are in valid range
                    ab_diff_int = int(ab_diff)
                    cd_diff_int = int(cd_diff)
                    
                    # Check if both are in the valid range (0-359) 
                    if not (0 <= ab_diff_int < 360 and 0 <= cd_diff_int < 360):
                        continue
                            
                    # Always store from smaller to larger differential for consistency
                    if ab_diff_int < cd_diff_int:
                        self.conrune_reversal_map[ab_diff] = cd_diff
                    else:
                        self.conrune_reversal_map[cd_diff] = ab_diff
                except Exception as e:
                    logger.error(f"Error processing quadset {entry.get('QuadSet', '')}: {e}")
                    continue  # Skip to next entry on error
            
        logger.info(f"Built conrune reversal map with {len(self.conrune_reversal_map)} pairs")
        logger.info(f"Identified {len(self.recursive_pairs)} recursive pairs")
            
    def _build_geometric_factor_maps(self):
        """Build maps for geometric factor relationships using precise zodiacal calculations."""
        # These connect differentials that are related through factors of 360
        factors = [2, 3, 4, 5, 6, 8, 9, 10, 12]
        
        # Initialize the geometric factor map
        self.geometric_factor_map = {}
        for factor in factors:
            self.geometric_factor_map[factor] = {}
        
        # Collect all valid differential values and build zodiacal position mapping
        valid_differentials = [diff for diff in self.differential_map.keys() if diff and diff.isdigit()]
        
        # Create direct mapping between differential and exact zodiacal degree
        diff_to_zodiacal_degree = {}
        zodiacal_degree_to_diff = {}
        
        for diff in valid_differentials:
            entry = self.differential_map[diff]
            zodiacal_text = entry.get('Zodiacal', '')
            
            # Skip entries without valid zodiacal position
            if not zodiacal_text or zodiacal_text == "XXXX":
                continue
                
            try:
                # Parse the zodiacal position to get exact degree
                parts = zodiacal_text.strip().split()
                if len(parts) >= 2 and parts[-1] in "ABCDEFGHIJKL":
                    degree = int(parts[0])
                    sign_letter = parts[-1]
                    
                    # Calculate absolute zodiacal degree (0-359)
                    sign_index = "ABCDEFGHIJKL".index(sign_letter)
                    absolute_degree = (sign_index * 30) + degree
                    
                    # Store the mapping both ways
                    diff_to_zodiacal_degree[diff] = absolute_degree
                    zodiacal_degree_to_diff[absolute_degree] = diff
            except (ValueError, IndexError):
                continue
        
        # For each differential, find factor connections based on exact zodiacal degrees
        for diff in valid_differentials:
            # Skip if we don't have zodiacal data for this differential
            if diff not in diff_to_zodiacal_degree:
                continue
                
            zodiacal_degree = diff_to_zodiacal_degree[diff]
            
            for factor in factors:
                # Calculate exact factor points around the zodiacal circle
                related_diffs = []
                
                # For each factor point, find the corresponding differential
                for i in range(1, factor):
                    # Calculate exact zodiacal degree for this factor point
                    related_zodiacal_degree = (zodiacal_degree + (i * 360 / factor)) % 360
                    
                    # Find the exact differential at this zodiacal degree
                    if related_zodiacal_degree in zodiacal_degree_to_diff:
                        related_diff = zodiacal_degree_to_diff[related_zodiacal_degree]
                        related_diffs.append(related_diff)
                    else:
                        # If exact match not found, look for the closest degree
                        closest_degree = None
                        min_difference = 3  # Allow up to 3 degree difference
                        
                        for degree in zodiacal_degree_to_diff:
                            difference = abs(degree - related_zodiacal_degree)
                            # Consider wrap-around at 0/360 degrees
                            if difference > 180:
                                difference = 360 - difference
                                
                            if difference < min_difference:
                                min_difference = difference
                                closest_degree = degree
                        
                        if closest_degree is not None:
                            related_diff = zodiacal_degree_to_diff[closest_degree]
                            related_diffs.append(related_diff)
                
                # Store in the factor map (only if we found related differentials)
                if related_diffs:
                    self.geometric_factor_map[factor][diff] = sorted(related_diffs, key=int)
        
        # Log statistics about geometric factor map
        total_connections = 0
        for factor, factor_map in self.geometric_factor_map.items():
            factor_connections = sum(len(diffs) for diffs in factor_map.values())
            total_connections += factor_connections
            logger.debug(f"Factor {factor}: {len(factor_map)} sources with {factor_connections} connections")
            
        logger.info(f"Built geometric factor maps with {total_connections} total connections")
        
        # If debugging, check some expected factor relationships
        if logger.isEnabledFor(logging.DEBUG):
            for test_diff in ["42", "162", "222", "282"]:
                if test_diff in diff_to_zodiacal_degree:
                    degree = diff_to_zodiacal_degree[test_diff]
                    sign_idx = degree // 30
                    sign_degree = degree % 30
                    sign_letter = "ABCDEFGHIJKL"[sign_idx]
                    logger.debug(f"Differential {test_diff} is at absolute degree {degree} ({sign_degree}° {self.zodiac_sign_map[sign_letter]})")
            
            # Check factor 2 and 3 connections for differential 42
            if "42" in self.geometric_factor_map.get(2, {}):
                logger.debug(f"Factor 2 connections for diff 42: {self.geometric_factor_map[2]['42']}")
            if "42" in self.geometric_factor_map.get(3, {}):
                logger.debug(f"Factor 3 connections for diff 42: {self.geometric_factor_map[3]['42']}")

    def _load_calendar_data(self):
        """Load the calendar data from the CSV file.
        
        Returns:
            List of dictionaries with calendar data
        """
        # Get the data file path using relative path from project root
        csv_file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                'assets', 'cvs', 'day_count.csv'
            )
            
        entries = []
        
        # Load data from CSV file
        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    entries.append(row)
                
            logger.info(f"Loaded {len(entries)} calendar entries from {csv_file_path}")
            
            # Store the data in the instance variable
            self.calendar_data = entries
            
            return entries
        except Exception as e:
            logger.error(f"Error loading calendar data: {e}")
            return []

    def _load_quadsets_data(self):
        """Load the quadsets data from the CSV file.
        
        Returns:
            List of dictionaries with quadsets data
        """
        # Get the data file path using relative path from project root
        csv_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            'assets', 'cvs', 'quadsets_for_app.csv'
        )
        
        entries = []
        
        # Load data from CSV file
        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    entries.append(row)
                
            logger.info(f"Loaded {len(entries)} quadset entries from {csv_file_path}")
            
            # Store the data in the instance variable
            self.quadsets_data = entries
            
            return entries
        except Exception as e:
            logger.error(f"Error loading quadsets data: {e}")
            return []

    def _lookup_by_zodiacal(self):
        """Lookup entry by zodiacal position (sign and degree)."""
        sign_name = self.sign_selector.currentText()
        degree = self.degree_input.value()
        
        # Create lookup key
        key = f"{sign_name}_{degree}"
        
        if key in self.zodiacal_map:
            entry = self.zodiacal_map[key]
            
            # Format result
            self.lookup_result_label.setText(
                f"Zodiacal Position: {degree}° {sign_name} | "
                f"Differential: {entry.get('Differential', '')} | "
                f"Ditrune: {entry.get('Ditrune', '')} | "
                f"Conrune: {entry.get('Conrune', '')}"
            )
            self.lookup_result_label.setStyleSheet(
                "padding: 10px; background-color: #e6f7e6; border-radius: 5px; margin-top: 5px;"
            )
            
            # Set the selected differential
            differential = entry.get('Differential', '')
            if differential and differential != "XXXX":
                self.selected_differential = differential
                
                # Clear existing highlights and connections
                self._clear_highlights()
                self._update_visualization()
                
        else:
            self.lookup_result_label.setText(
                f"No entry found for {degree}° {sign_name}"
            )
            self.lookup_result_label.setStyleSheet(
                "padding: 10px; background-color: #ffebeb; border-radius: 5px; margin-top: 5px;"
            )
            # Clear selection
            self.selected_differential = None
            self._clear_highlights()
            self._update_visualization()

    def _lookup_by_differential(self):
        """Lookup entry by differential value."""
        differential = str(self.diff_input.value())
        
        if differential in self.differential_map:
            entry = self.differential_map[differential]
            
            # Format zodiacal position for display
            zodiacal = entry.get('Zodiacal', '').strip()
            formatted_zodiacal = zodiacal
            
            if zodiacal != "XXXX" and len(zodiacal.split()) > 1:
                parts = zodiacal.split()
                if parts[-1] in "ABCDEFGHIJKL":
                    degree = parts[0]
                    sign_letter = parts[-1]
                    sign_name = self.zodiac_sign_map.get(sign_letter, f"Sign {sign_letter}")
                    formatted_zodiacal = f"{degree}° {sign_name}"
            
            # Format result
            self.lookup_result_label.setText(
                f"Differential: {differential} | "
                f"Zodiacal Position: {formatted_zodiacal} | "
                f"Ditrune: {entry.get('Ditrune', '')} | "
                f"Conrune: {entry.get('Conrune', '')}"
            )
            self.lookup_result_label.setStyleSheet(
                "padding: 10px; background-color: #e6f7e6; border-radius: 5px; margin-top: 5px;"
            )
            
            # Set the selected differential
            if differential and differential != "XXXX":
                self.selected_differential = differential
                
                # Clear existing highlights and connections
                self._clear_highlights()
                self._update_visualization()
                
        else:
            self.lookup_result_label.setText(
                f"No entry found for differential {differential}"
            )
            self.lookup_result_label.setStyleSheet(
                "padding: 10px; background-color: #ffebeb; border-radius: 5px; margin-top: 5px;"
            )
            # Clear selection
            self.selected_differential = None
            self._clear_highlights()
            self._update_visualization()

    def _highlight_day_in_visualization(self, entry):
        """Highlight the specified day in the current visualization and its connections.
        
        Args:
            entry: The calendar entry to highlight
        """
        # Clear any existing highlights
        self._clear_highlights()
        
        # Find and highlight the corresponding item
        day_to_find = entry.get('Day', '')
        differential = entry.get('Differential', '')
        
        # Highlight the day marker
        for item in self.scene.items():
            if hasattr(item, 'data') and item.data(0) and item.data(0).get('Day') == day_to_find:
                # Store original appearance
                item.originalBrush = item.brush()
                # Set highlight appearance
                highlight_brush = QBrush(QColor(255, 255, 0, 220))  # Brighter yellow highlight
                item.setBrush(highlight_brush)
                item.isHighlighted = True
                
                # Ensure it's visible in the view
                self.view.ensureVisible(item)
                break
        
        # If this day has a differential, highlight its connections too
        if differential and differential != "XXXX":
            # Get the positions of all markers
            marker_positions = {}
            for diff, marker in self.day_markers.items():
                pos = marker.scenePos()
                marker_positions[diff] = (pos.x(), pos.y())
                
            # Get the selected differential position
            if differential in marker_positions:
                # Store the selected differential
                selected = differential
                x1, y1 = marker_positions[differential]
                
                # Check for reversal connections
                if self.show_reversals_checkbox.isChecked():
                    # First check if it's a recursive pair
                    if differential in self.recursive_pairs:
                        # Highlight the recursive pair indicator
                        for item in self.scene.items():
                            if (hasattr(item, 'data') and item.data(0) and 
                                isinstance(item.data(0), dict) and item.data(0).get('type') == 'recursive' and
                                item.data(0).get('differential') == differential):
                                item.originalPen = item.pen()
                                item.setPen(QPen(QColor(255, 0, 255, 255), 3.0))  # Bright magenta, very thick
                    
                    # Then check for reversal connections
                    elif differential in self.conrune_reversal_map:
                        reversal_diff = self.conrune_reversal_map[differential]
                        
                        # Highlight reversal connection line
                        for item in self.scene.items():
                            if (hasattr(item, 'data') and item.data(0) and 
                                isinstance(item.data(0), dict) and 
                                item.data(0).get('type') == 'reversal' and 
                                ((item.data(0).get('from') == differential and item.data(0).get('to') == reversal_diff) or
                                (item.data(0).get('from') == reversal_diff and item.data(0).get('to') == differential))):
                                
                                # Highlight connection
                                item.originalPen = item.pen()
                                item.setPen(QPen(QColor(255, 0, 255, 255), 3.0))  # Bright magenta, very thick
                                item.isHighlighted = True
                                
                                # Also highlight the reversal marker
                                if reversal_diff in self.day_markers:
                                    marker = self.day_markers[reversal_diff]
                                    marker.originalBrush = marker.brush()
                                    marker.setBrush(QBrush(QColor(255, 105, 180, 220)))  # Brighter pink
                                    marker.isHighlighted = True
                        
                        # If we're the target of a reversal connection, highlight that too
                        for diff, rev_diff in self.conrune_reversal_map.items():
                            if rev_diff == differential:
                                # Highlight connection line
                                for item in self.scene.items():
                                    if (hasattr(item, 'data') and item.data(0) and 
                                        isinstance(item.data(0), dict) and 
                                        item.data(0).get('type') == 'reversal' and 
                                        ((item.data(0).get('from') == diff and item.data(0).get('to') == differential) or
                                        (item.data(0).get('from') == differential and item.data(0).get('to') == diff))):
                                        
                                        # Highlight connection
                                        item.originalPen = item.pen()
                                        item.setPen(QPen(QColor(255, 0, 255, 255), 3.0))  # Bright magenta, very thick
                                        item.isHighlighted = True
                                        
                                        # Also highlight the source marker
                                        if diff in self.day_markers:
                                            marker = self.day_markers[diff]
                                            marker.originalBrush = marker.brush()
                                            marker.setBrush(QBrush(QColor(255, 105, 180, 220)))  # Brighter pink
                                            marker.isHighlighted = True

    def _clear_highlights(self):
        """Clear any existing highlights in the visualization."""
        # Remove any existing highlights (lines and special markers)
        items_to_remove = []
        
        for item in self.scene.items():
            if hasattr(item, 'data') and item.data(0) and isinstance(item.data(0), dict):
                data = item.data(0)
                if isinstance(data, dict) and data.get('type') in ['reversal', 'factor', 'recursive']:
                    items_to_remove.append(item)
        
        # Remove identified items
        for item in items_to_remove:
            self.scene.removeItem(item)

    def _update_visualization(self):
        """Update the visualization based on the current settings."""
        # Track update start time for performance monitoring
        import time
        start_time = time.time()
        
        # Clear the scene
        self.scene.clear()
        self.day_markers.clear()
        
        # Create the positions for all the points on the circle
        center_x = 400
        center_y = 400
        radius = 350
        
        # Store the center point for radial visualization
        self.center_point = (center_x, center_y)
        
        # Generate positions for all markers
        marker_positions = {}
        
        # First pass: Calculate positions (this is quick)
        for entry in self.calendar_data:
            # Skip rows without differential
            differential = entry.get('Differential', '')
            if not differential or differential == "XXXX":
                continue
                
            try:
                # Convert the differential to an angle (degrees)
                diff_int = int(differential)
                # Use 360 instead of 365 - each differential is directly a zodiacal degree
                angle_degrees = diff_int  # No conversion needed if differential is already 0-359
                
                # Convert the angle to radians
                angle_radians = math.radians(angle_degrees)
                
                # Calculate the position on the circle
                x = center_x + radius * math.cos(angle_radians)
                y = center_y + radius * math.sin(angle_radians)
                
                # Store this position for this differential
                marker_positions[differential] = (x, y)
            except (ValueError, TypeError) as e:
                continue  # Skip invalid differentials
        
        # Second pass: Create markers (also quick)
        for differential, (x, y) in marker_positions.items():
            try:
                # Find the calendar entry for this differential
                entry = next((e for e in self.calendar_data if e.get('Differential') == differential), None)
                if not entry:
                    continue
                    
                # Create a marker at this position
                marker = self.scene.addEllipse(
                    x - 5, y - 5, 10, 10,
                    QPen(Qt.GlobalColor.black),
                    QBrush(QColor("#3498db"))  # Blue color
                )
                
                # Highlight the selected differential if it matches
                if self.selected_differential and differential == str(self.selected_differential):
                    # Create a larger highlight circle around the marker
                    highlight = self.scene.addEllipse(
                        x - 10, y - 10, 20, 20,
                        QPen(QColor(255, 165, 0, 200), 2),  # Orange outline
                        QBrush(QColor(255, 165, 0, 50))    # Semi-transparent orange fill
                    )
                    highlight.setZValue(-1)  # Make sure it's behind the marker
                
                # Store the calendar entry data with the marker
                marker.setData(0, entry)
                
                # Create tooltip with the date information
                marker.setToolTip(
                    f"Date: {entry.get('Day', '')}\n"
                    f"Differential: {differential}\n"
                    f"Zodiacal: {entry.get('Zodiacal', '')}\n"
                    f"Ditrune: {entry.get('Ditrune', '')}\n"
                    f"Conrune: {entry.get('Conrune', '')}"
                )
                
                # Store reference to this marker
                self.day_markers[differential] = marker
            except Exception as e:
                logger.error(f"Error creating marker for differential {differential}: {e}")
        
        # IMPORTANT: Draw the center-to-differential line BEFORE drawing factor/reversal connections
        # This ensures it won't be obscured by other elements
        if self.radial_mode_checkbox.isChecked() and self.selected_differential:
            selected = str(self.selected_differential)
            if selected in marker_positions:
                x, y = marker_positions[selected]
                
                # Log that we're drawing the line (for debugging)
                logger.debug(f"Drawing center line to differential {selected} at coordinates ({x}, {y})")
                
                # Draw a distinctive line from center to the selected differential
                # Make it VERY prominent - bright green, extra thick, and solid
                center_line = self.scene.addLine(
                    center_x, center_y, x, y,
                    QPen(QColor(0, 255, 0, 255), 4.0)  # Bright green, extra thick
                )
                
                # Add a center point marker for visibility
                center_marker = self.scene.addEllipse(
                    center_x - 5, center_y - 5, 10, 10,
                    QPen(QColor(255, 0, 0)),
                    QBrush(QColor(255, 0, 0))  # Bright red
                )
                center_marker.setZValue(20)  # Above everything
                
                # Ensure this line is drawn on top of other connections
                center_line.setZValue(15)  # Very high z-index
                
                # Store data for identification
                center_line.setData(0, {
                    "type": "selected_differential_line",
                    "differential": selected
                })
                
                center_line.setToolTip(f"Selected Differential: {selected}")
                
                # Log that we created the line (for debugging)
                logger.debug(f"Created center line for differential {selected}")
        else:
            logger.debug(f"Not creating center line. Radial mode: {self.radial_mode_checkbox.isChecked()}, Selected diff: {self.selected_differential}")
        
        # Draw factors if enabled and there's a selected differential
        factor_start_time = time.time()
        if self.show_factors_checkbox.isChecked() and self.selected_differential:
            # Get the enabled factors
            enabled_factors = []
            for i, checkbox in enumerate(self.factor_checkboxes):
                if checkbox.isChecked():
                    enabled_factors.append(self.factors[i])
            
            # Draw connections for enabled factors based on visualization mode
            is_radial = self.radial_mode_checkbox.isChecked()
            
            for factor in enabled_factors:
                if is_radial:
                    self._draw_selected_factor_connections_radial(factor, marker_positions)
                else:
                    self._draw_selected_factor_connections(factor, marker_positions)
                    
            factor_end_time = time.time()
            logger.debug(f"Drawing factor connections took {factor_end_time - factor_start_time:.2f} seconds")
        
        # Draw reversal connections if enabled and there's a selected differential
        reversal_start_time = time.time()
        if self.show_reversals_checkbox.isChecked() and self.selected_differential:
            is_radial = self.radial_mode_checkbox.isChecked()
            
            if is_radial:
                self._draw_selected_reversal_connections_radial(marker_positions)
            else:
                self._draw_selected_reversal_connections(marker_positions)
                
            reversal_end_time = time.time()
            logger.debug(f"Drawing reversal connections took {reversal_end_time - reversal_start_time:.2f} seconds")
        
        # Adjust the scene rect to fit all content
        self.scene.setSceneRect(self.scene.sceneRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
        # Update the info panel with the current differential's connections
        if self.selected_differential:
            self._update_info_panel()
        
        end_time = time.time()
        logger.debug(f"Total visualization update took {end_time - start_time:.2f} seconds")

    def _draw_selected_factor_connections_radial(self, factor, marker_positions):
        """Draw factor connections in radial mode for the selected differential.
        
        Args:
            factor: The factor to draw connections for
            marker_positions: Dictionary mapping differentials to marker positions (x, y)
        """
        if not self.selected_differential or factor not in self.geometric_factor_map:
            return
            
        # Convert to string since our map keys are strings
        selected = str(self.selected_differential)
        
        # Get center coordinates
        center_x, center_y = self.center_point
        
        # Use bright colors for better visibility
        connection_color = QColor(0, 200, 0, 200)  # Brighter green with transparency
        
        # Add a center point marker for the selected differential
        center_marker = self.scene.addEllipse(
            center_x - 8, center_y - 8, 16, 16,
            QPen(QColor(255, 165, 0, 200), 2),  # Orange outline
            QBrush(QColor(255, 255, 255, 200))  # White fill with transparency
        )
        center_marker.setToolTip(f"Center: Factor {factor} connections for differential {selected}")
        center_marker.setZValue(5)  # Make sure it's on top
        
        # Find factor connections involving this differential
        if selected in self.geometric_factor_map[factor]:
            # This differential is a source in the factor map
            related_diffs = self.geometric_factor_map[factor][selected]
            
            # Draw each connection (max 12 for visual clarity)
            for i, related_diff in enumerate(related_diffs[:12]):
                try:
                    if related_diff in marker_positions:
                        x2, y2 = marker_positions[related_diff]
                        
                        # Draw line from center to the related differential
                        connection_line = self.scene.addLine(
                            center_x, center_y, x2, y2,
                            QPen(connection_color, 2.0)  # Thicker line for visibility
                        )
                        
                        # Store data and add helpful tooltip
                        connection_line.setData(0, {
                            "type": "factor_radial",
                            "factor": factor,
                            "from": selected, 
                            "to": related_diff
                        })
                        
                        connection_line.setToolTip(
                            f"Factor {factor}: {selected} ↔ {related_diff}"
                        )
                        
                        # Set z-value to ensure visibility (below reversal lines)
                        connection_line.setZValue(2)
                        
                        # Highlight the connected differential
                        if related_diff in self.day_markers:
                            connected_x, connected_y = marker_positions[related_diff]
                            highlight = self.scene.addEllipse(
                                connected_x - 8, connected_y - 8, 16, 16,
                                QPen(connection_color, 1.5),
                                QBrush(QColor(0, 200, 0, 50))  # Semi-transparent green
                            )
                            highlight.setZValue(1)
                            highlight.setToolTip(f"Factor {factor} connection from {selected}")
                except Exception as e:
                    logger.error(f"Error drawing factor radial connection between {selected} and {related_diff}: {e}")
        
        # Also check if this differential is a target in any factor relationships
        for source_diff, related_diffs in self.geometric_factor_map.get(factor, {}).items():
            if selected in related_diffs:
                try:
                    if source_diff in marker_positions:
                        x2, y2 = marker_positions[source_diff]
                        
                        # Draw line from center to the source differential
                        connection_line = self.scene.addLine(
                            center_x, center_y, x2, y2,
                            QPen(QColor(100, 200, 100, 200), 2.0)  # Lighter green
                        )
                        
                        # Store data and add tooltip
                        connection_line.setData(0, {
                            "type": "factor_radial",
                            "factor": factor,
                            "from": source_diff, 
                            "to": selected
                        })
                        
                        connection_line.setToolTip(
                            f"Factor {factor}: {source_diff} ↔ {selected}"
                        )
                        
                        # Set z-value
                        connection_line.setZValue(2)
                        
                        # Highlight the source differential
                        highlight = self.scene.addEllipse(
                            x2 - 8, y2 - 8, 16, 16, 
                            QPen(QColor(100, 200, 100, 200), 1.5),
                            QBrush(QColor(100, 200, 100, 50))
                        )
                        highlight.setZValue(1)
                        highlight.setToolTip(f"Factor {factor} source for {selected}")
                except Exception as e:
                    logger.error(f"Error drawing factor radial connection between {source_diff} and {selected}: {e}")

    def _draw_selected_reversal_connections_radial(self, marker_positions):
        """Draw reversal connections in radial mode for the selected differential.
        
        Args:
            marker_positions: Dictionary mapping differentials to marker positions (x, y)
        """
        if not self.selected_differential:
            return
        
        # Convert to string since our map keys are strings
        selected = str(self.selected_differential)
        
        # Get center coordinates
        center_x, center_y = self.center_point
        
        # Check if this is a recursive pair
        is_recursive = selected in self.recursive_pairs
        
        # Add a center point marker
        center_marker = self.scene.addEllipse(
            center_x - 8, center_y - 8, 16, 16,
            QPen(QColor(255, 0, 0, 180), 2),  # Red outline
            QBrush(QColor(255, 255, 255, 200))  # White fill with transparency
        )
        center_marker.setToolTip(f"Center: Reversal connections for differential {selected}")
        center_marker.setZValue(5)  # Make sure it's on top
        
        # Use bright colors for better visibility
        connection_color = QColor(255, 0, 0, 220)  # Brighter red
        
        if is_recursive:
            # Mark the selected differential as recursive
            if selected in marker_positions:
                x, y = marker_positions[selected]
                
                # Draw a line from center to the recursive differential
                connection_line = self.scene.addLine(
                    center_x, center_y, x, y,
                    QPen(QColor(128, 0, 128, 220), 3.0)  # Bright purple, thick
                )
                
                # Store data about this recursive pair
                connection_line.setData(0, {
                    "type": "recursive_radial",
                    "differential": selected
                })
                
                # Add tooltip
                connection_line.setToolTip(
                    f"Recursive Pair: Differential {selected}\n"
                    f"This is a special case with no reversal differential."
                )
                
                # Set z-value for visibility
                connection_line.setZValue(3)
                
                # Highlight the recursive differential
                highlight = self.scene.addEllipse(
                    x - 12, y - 12, 24, 24,
                    QPen(QColor(128, 0, 128, 220), 2),  # Purple outline
                    QBrush(QColor(128, 0, 128, 80))  # Semi-transparent purple fill
                )
                highlight.setZValue(2)
                highlight.setToolTip(f"Recursive Pair: Differential {selected}")
        else:
            # Find reversal pairs involving this differential
            reversal_pairs = []
            
            # Check if this differential is a key in the map
            if selected in self.conrune_reversal_map:
                reversal_pairs.append(self.conrune_reversal_map[selected])
            
            # Check if this differential is a value in the map
            for key, value in self.conrune_reversal_map.items():
                if value == selected:
                    reversal_pairs.append(key)
            
            # Draw radial line to each reversal pair
            for rev_diff in sorted(set(reversal_pairs), key=int):  # Ensure uniqueness and sorting
                try:
                    if rev_diff in marker_positions:
                        x, y = marker_positions[rev_diff]
                        
                        # Draw a line from center to the reversal differential
                        connection_line = self.scene.addLine(
                            center_x, center_y, x, y,
                            QPen(connection_color, 3.0)  # Thick red line
                        )
                        
                        # Store data
                        connection_line.setData(0, {
                            "type": "reversal_radial",
                            "from": selected, 
                            "to": rev_diff
                        })
                        
                        # Add tooltip
                        connection_line.setToolTip(
                            f"Conrune Reversal: {selected} ↔ {rev_diff}"
                        )
                        
                        # Set z-value for visibility
                        connection_line.setZValue(3)
                        
                        # Highlight the reversal differential
                        highlight = self.scene.addEllipse(
                            x - 10, y - 10, 20, 20,
                            QPen(connection_color, 2),
                            QBrush(QColor(255, 0, 0, 80))  # Semi-transparent red
                        )
                        highlight.setZValue(2)
                        highlight.setToolTip(f"Reversal pair for {selected}: {rev_diff}")
                except Exception as e:
                    logger.error(f"Error drawing radial reversal connection between {selected} and {rev_diff}: {e}")

    def _go_to_today(self):
        """Focus the visualization on today's date."""
        import datetime
        
        today = datetime.datetime.now().strftime("%-d-%b")
        
        # Find today's entry in the calendar data
        today_entry = None
        for entry in self.calendar_data:
            if entry.get('Day', '') == today:
                today_entry = entry
                break
        
        if today_entry:
            # Display today's information
            self.info_label.setText(
                f"Today ({today}): Differential {today_entry.get('Differential', '')}, "
                f"Zodiacal {today_entry.get('Zodiacal', '')}"
            )
            
            # Set as selected differential if valid
            differential = today_entry.get('Differential', '')
            if differential and differential != "XXXX":
                self.selected_differential = differential
                
                # Clear existing highlights and redraw
                self._clear_highlights()
                self._update_visualization()
        else:
            self.info_label.setText(f"Today ({today}) not found in calendar data")

    def resizeEvent(self, event):
        """Handle resize events for the widget.
        
        Args:
            event: The resize event
        """
        super().resizeEvent(event)
        
        # Adjust the view to maintain the visualization's aspect ratio
        if hasattr(self, 'scene') and hasattr(self, 'view'):
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def eventFilter(self, obj, event):
        """Event filter to handle mouse movement and clicks over the visualization.
        
        Args:
            obj: The object that triggered the event
            event: The event
            
        Returns:
            True if the event was handled, False otherwise
        """
        if obj == self.view.viewport():
            # Handle mouse move events (hover)
            if event.type() == event.Type.MouseMove:
                # Convert the mouse position to scene coordinates
                scene_pos = self.view.mapToScene(event.position().toPoint())
                
                # Find items under the mouse
                items = self.scene.items(scene_pos)
                
                # Look for day markers with data
                for item in items:
                    if hasattr(item, 'data') and item.data(0):
                        entry = item.data(0)
                        
                        # Format zodiacal position for display
                        formatted_zodiacal = self._format_zodiacal_position(entry.get('Zodiacal', ''))
                        
                        # Update info label
                        self.info_label.setText(
                            f"Date: {entry.get('Day', '')} | "
                            f"Differential: {entry.get('Differential', '')} | "
                            f"Zodiacal: {formatted_zodiacal} | "
                            f"Ditrune: {entry.get('Ditrune', '')} | "
                            f"Conrune: {entry.get('Conrune', '')}"
                        )
                        return True
                
                # Reset label if no item found
                self.info_label.setText("Hover over a day marker to view details")
                return True  # Still handled the event
            
            # Handle mouse click events
            elif event.type() == event.Type.MouseButtonPress:
                # Convert the mouse position to scene coordinates
                scene_pos = self.view.mapToScene(event.position().toPoint())
                
                # Find items under the mouse
                items = self.scene.items(scene_pos)
                
                # Look for day markers with data
                for item in items:
                    if hasattr(item, 'data') and item.data(0):
                        entry = item.data(0)
                        differential = entry.get('Differential', '')
                        
                        # Set as selected differential if valid
                        if differential and differential != "XXXX":
                            self.selected_differential = differential
                            
                            # Clear existing highlights and redraw
                            self._clear_highlights()
                            self._update_visualization()
                            
                            # Also update the lookup result label
                            formatted_zodiacal = self._format_zodiacal_position(entry.get('Zodiacal', ''))
                            
                            self.lookup_result_label.setText(
                                f"Selected: {entry.get('Day', '')} | "
                                f"Differential: {differential} | "
                                f"Zodiacal: {formatted_zodiacal} | "
                                f"Ditrune: {entry.get('Ditrune', '')} | "
                                f"Conrune: {entry.get('Conrune', '')}"
                            )
                            self.lookup_result_label.setStyleSheet(
                                "padding: 10px; background-color: #e6f7e6; border-radius: 5px; margin-top: 5px;"
                            )
                            return True
                
                return True  # Handled the event even if no marker was clicked
                
        # Pass the event on to the object
        return False

    def _differential_changed(self, value):
        """Handle changes to the selected differential.
        
        Args:
            value: The new differential value
        """
        # Store the new selected differential
        self.selected_differential = value
        
        # Update the visualization
        self._clear_highlights()
        self._update_visualization()
        
        # Find the entry for this differential
        for entry in self.calendar_data:
            if entry.get('Differential', '') == str(value):
                # Format zodiacal position for display using the helper method
                formatted_zodiacal = self._format_zodiacal_position(entry.get('Zodiacal', ''))
                
                # Update the lookup result label
                self.lookup_result_label.setText(
                    f"Selected: {entry.get('Day', '')} | "
                    f"Differential: {value} | "
                    f"Zodiacal: {formatted_zodiacal} | "
                    f"Ditrune: {entry.get('Ditrune', '')} | "
                    f"Conrune: {entry.get('Conrune', '')}"
                )
                self.lookup_result_label.setStyleSheet(
                    "padding: 10px; background-color: #e6f7e6; border-radius: 5px; margin-top: 5px;"
                )
                
                # Update the info panel
                self._update_info_panel()
                break

    def _lookup_entry(self):
        """Handle lookup from the entry field."""
        query = self.lookup_entry.text().strip()
        if not query:
            return
            
        # First try to interpret as differential
        if query.isdigit():
            diff = int(query)
            if 0 <= diff <= 364:
                self.differential_spin.setValue(diff)
                return
        
        # Then try to interpret as a date
        for entry in self.calendar_data:
            day = entry.get('Day', '').lower()
            if query.lower() in day:
                differential = entry.get('Differential', '')
                if differential and differential.isdigit():
                    self.differential_spin.setValue(int(differential))
                    return
        
        # If we get here, no match was found
        self.lookup_result_label.setText(f"No matching entry found for: {query}")
        self.lookup_result_label.setStyleSheet(
            "padding: 10px; background-color: #ffebeb; border-radius: 5px; margin-top: 5px;"
        )

    def _update_info_panel(self):
        """Update the information panel with details about connected pairs."""
        if not self.selected_differential:
            self.info_panel.setHtml("<p>No differential selected</p>")
            return
            
        selected = str(self.selected_differential)
        
        # Get the entry for this differential
        selected_entry = None
        for entry in self.calendar_data:
            if entry.get('Differential', '') == selected:
                selected_entry = entry
                break
                
        if not selected_entry:
            self.info_panel.setHtml("<p>No data available for this differential</p>")
            return
            
        # Format zodiacal position
        formatted_zodiacal = self._format_zodiacal_position(selected_entry.get('Zodiacal', ''))
            
        # Build HTML content
        html_content = [
            f"<h3>Differential {selected} - {selected_entry.get('Day', '')}</h3>",
            f"<p><b>Zodiacal:</b> {formatted_zodiacal}</p>",
            f"<p><b>Ditrune:</b> {selected_entry.get('Ditrune', '')}</p>",
            f"<p><b>Conrune:</b> {selected_entry.get('Conrune', '')}</p>",
            "<hr>"
        ]
        
        # Check for reversal connections if enabled
        if self.show_reversals_checkbox.isChecked():
            html_content.append("<h4>Reversal Connections</h4>")
            
            # Check if this is a recursive pair
            is_recursive = selected in self.recursive_pairs
            if is_recursive:
                html_content.append("<p><b>Recursive Pair</b> - This differential has no reversal pair</p>")
            else:
                # Find reversal pairs
                reversal_pairs = []
                
                # Check if this differential is a key in the map
                if selected in self.conrune_reversal_map:
                    reversal_pairs.append(self.conrune_reversal_map[selected])
                
                # Check if this differential is a value in the map
                for key, value in self.conrune_reversal_map.items():
                    if value == selected:
                        reversal_pairs.append(key)
                
                if reversal_pairs:
                    for rev_diff in sorted(set(reversal_pairs), key=int):  # Ensure uniqueness and sorting
                        # Find the calendar entry for this differential
                        rev_entry = None
                        for entry in self.calendar_data:
                            if entry.get('Differential', '') == rev_diff:
                                rev_entry = entry
                                break
                                
                        if rev_entry:
                            # Format zodiacal position
                            rev_zodiacal = self._format_zodiacal_position(rev_entry.get('Zodiacal', ''))
                            
                            html_content.append(
                                f"<p><b>Reversal Pair:</b> Differential {rev_diff} - {rev_entry.get('Day', '')}</p>"
                                f"<ul>"
                                f"<li>Zodiacal: {rev_zodiacal}</li>"
                                f"<li>Ditrune: {rev_entry.get('Ditrune', '')}</li>"
                                f"<li>Conrune: {rev_entry.get('Conrune', '')}</li>"
                                f"</ul>"
                            )
                        else:
                            html_content.append(f"<p><b>Reversal Pair:</b> Differential {rev_diff} (No additional data)</p>")
                else:
                    html_content.append("<p>No reversal connections found</p>")
            
            html_content.append("<hr>")
        
        # Check for factor connections if enabled
        if self.show_factors_checkbox.isChecked():
            html_content.append("<h4>Factor Connections</h4>")
            
            # Get the enabled factors
            enabled_factors = []
            for i, checkbox in enumerate(self.factor_checkboxes):
                if checkbox.isChecked():
                    enabled_factors.append(self.factors[i])
            
            factor_connections_found = False
            
            # Create a master list of all connections to avoid duplicates
            all_connections = set()
            
            # Loop through each enabled factor
            for factor in enabled_factors:
                if not factor_connections_found:
                    factor_connections = []
                    
                    # Check if this differential is a source in the factor map
                    if factor in self.geometric_factor_map and selected in self.geometric_factor_map[factor]:
                        # Add connections that aren't already in all_connections
                        for diff in self.geometric_factor_map[factor][selected]:
                            if diff not in all_connections:
                                factor_connections.append(diff)
                                all_connections.add(diff)
                    
                    # Check if this differential is a target in any factor relationships
                    for source_diff, related_diffs in self.geometric_factor_map.get(factor, {}).items():
                        if selected in related_diffs and source_diff not in all_connections:
                            factor_connections.append(source_diff)
                            all_connections.add(source_diff)
                    
                    # If we found connections for this factor, add them to the content
                    if factor_connections:
                        factor_connections_found = True
                        html_content.append(f"<p><b>Factor {factor} connections:</b></p><ul>")
                        
                        # Sort connections for consistency
                        factor_connections.sort(key=int)
                        
                        # Add each connection's details
                        for diff in factor_connections:
                            # Find the calendar entry for this differential
                            factor_entry = None
                            for entry in self.calendar_data:
                                if entry.get('Differential', '') == diff:
                                    factor_entry = entry
                                    break
                                    
                            if factor_entry:
                                # Format zodiacal position
                                factor_zodiacal = self._format_zodiacal_position(factor_entry.get('Zodiacal', ''))
                                
                                html_content.append(
                                    f"<li><b>Differential {diff}</b> - {factor_entry.get('Day', '')}<br>"
                                    f"Zodiacal: {factor_zodiacal}, "
                                    f"Ditrune: {factor_entry.get('Ditrune', '')}, "
                                    f"Conrune: {factor_entry.get('Conrune', '')}</li>"
                                )
                            else:
                                html_content.append(f"<li><b>Differential {diff}</b> (No additional data)</li>")
                        
                        html_content.append("</ul>")
            
            if not factor_connections_found:
                html_content.append("<p>No factor connections found</p>")
        
        # Set the HTML content
        self.info_panel.setHtml("".join(html_content))

    def _draw_selected_factor_connections(self, factor, marker_positions):
        """Draw factor connections in point-to-point mode for the selected differential.
        
        Args:
            factor: The factor to draw connections for
            marker_positions: Dictionary mapping differentials to marker positions (x, y)
        """
        if not self.selected_differential or factor not in self.geometric_factor_map:
            return
            
        # Convert to string since our map keys are strings
        selected = str(self.selected_differential)
        
        # Use bright colors for better visibility
        connection_color = QColor(0, 200, 0, 200)  # Brighter green with transparency
        
        # Find factor connections involving this differential
        if selected in self.geometric_factor_map[factor]:
            # This differential is a source in the factor map
            related_diffs = self.geometric_factor_map[factor][selected]
            
            # Get the position of the selected differential
            if selected not in marker_positions:
                return
                
            x1, y1 = marker_positions[selected]
            
            # Draw each connection (max 12 for visual clarity)
            for i, related_diff in enumerate(related_diffs[:12]):
                try:
                    if related_diff in marker_positions:
                        x2, y2 = marker_positions[related_diff]
                        
                        # Draw line from selected to the related differential
                        connection_line = self.scene.addLine(
                            x1, y1, x2, y2,
                            QPen(connection_color, 2.0)  # Thicker line for visibility
                        )
                        
                        # Store data and add helpful tooltip
                        connection_line.setData(0, {
                            "type": "factor",
                            "factor": factor,
                            "from": selected, 
                            "to": related_diff
                        })
                        
                        connection_line.setToolTip(
                            f"Factor {factor}: {selected} ↔ {related_diff}"
                        )
                        
                        # Set z-value to ensure visibility (below reversal lines)
                        connection_line.setZValue(2)
                        
                        # Highlight the connected differential
                        if related_diff in self.day_markers:
                            connected_marker = self.day_markers[related_diff]
                            connected_marker.originalBrush = connected_marker.brush()
                            connected_marker.setBrush(QBrush(QColor(0, 200, 0, 200)))  # Semi-transparent green
                            connected_marker.isHighlighted = True
                except Exception as e:
                    logger.error(f"Error drawing factor connection between {selected} and {related_diff}: {e}")
        
        # Also check if this differential is a target in any factor relationships
        for source_diff, related_diffs in self.geometric_factor_map.get(factor, {}).items():
            if selected in related_diffs:
                try:
                    # Get the positions
                    if source_diff not in marker_positions or selected not in marker_positions:
                        continue
                        
                    x1, y1 = marker_positions[source_diff]
                    x2, y2 = marker_positions[selected]
                    
                    # Draw line from source to selected differential
                    connection_line = self.scene.addLine(
                        x1, y1, x2, y2,
                        QPen(QColor(100, 200, 100, 200), 2.0)  # Lighter green
                    )
                    
                    # Store data and add tooltip
                    connection_line.setData(0, {
                        "type": "factor",
                        "factor": factor,
                        "from": source_diff, 
                        "to": selected
                    })
                    
                    connection_line.setToolTip(
                        f"Factor {factor}: {source_diff} ↔ {selected}"
                    )
                    
                    # Set z-value
                    connection_line.setZValue(2)
                    
                    # Highlight the source differential
                    if source_diff in self.day_markers:
                        source_marker = self.day_markers[source_diff]
                        source_marker.originalBrush = source_marker.brush()
                        source_marker.setBrush(QBrush(QColor(100, 200, 100, 200)))
                        source_marker.isHighlighted = True
                except Exception as e:
                    logger.error(f"Error drawing factor connection between {source_diff} and {selected}: {e}")
                    
    def _draw_selected_reversal_connections(self, marker_positions):
        """Draw reversal connections in point-to-point mode for the selected differential.
        
        Args:
            marker_positions: Dictionary mapping differentials to marker positions (x, y)
        """
        if not self.selected_differential:
            return
        
        # Convert to string since our map keys are strings
        selected = str(self.selected_differential)
        
        # Check if this is a recursive pair
        is_recursive = selected in self.recursive_pairs
        
        # Use bright colors for better visibility
        connection_color = QColor(255, 0, 0, 220)  # Brighter red
        
        # Get the position of the selected differential
        if selected not in marker_positions:
            return
        
        x1, y1 = marker_positions[selected]
        
        if is_recursive:
            # Mark the selected differential as recursive
            recursive_marker = self.scene.addEllipse(
                x1 - 12, y1 - 12, 24, 24,
                QPen(QColor(128, 0, 128, 220), 2),  # Purple outline
                QBrush(QColor(128, 0, 128, 80))  # Semi-transparent purple fill
            )
            recursive_marker.setZValue(1)
            recursive_marker.setToolTip(f"Recursive Pair: Differential {selected}")
            
            # Add special recursive pair indicator (self-loop)
            recursive_path = QPainterPath()
            recursive_path.moveTo(x1, y1 - 8)
            recursive_path.arcTo(x1 - 15, y1 - 15, 30, 30, 60, 240)
            
            recursive_line = self.scene.addPath(
                recursive_path,
                QPen(QColor(128, 0, 128, 220), 3.0)  # Bright purple, thick
            )
            recursive_line.setData(0, {
                "type": "recursive",
                "differential": selected
            })
            recursive_line.setToolTip(f"Recursive Pair: Differential {selected}")
            recursive_line.setZValue(3)
        else:
            # Find reversal pairs involving this differential
            reversal_pairs = []
            
            # Check if this differential is a key in the map
            if selected in self.conrune_reversal_map:
                reversal_pairs.append(self.conrune_reversal_map[selected])
            
            # Check if this differential is a value in the map
            for key, value in self.conrune_reversal_map.items():
                if value == selected:
                    reversal_pairs.append(key)
            
            # Draw line to each reversal pair
            for rev_diff in sorted(set(reversal_pairs), key=int):  # Ensure uniqueness and sorting
                try:
                    if rev_diff in marker_positions:
                        x2, y2 = marker_positions[rev_diff]
                        
                        # Draw a line from selected to the reversal differential
                        connection_line = self.scene.addLine(
                            x1, y1, x2, y2,
                            QPen(connection_color, 3.0)  # Thick red line
                        )
                        
                        # Store data
                        connection_line.setData(0, {
                            "type": "reversal",
                            "from": selected, 
                            "to": rev_diff
                        })
                        
                        # Add tooltip
                        connection_line.setToolTip(
                            f"Conrune Reversal: {selected} ↔ {rev_diff}"
                        )
                        
                        # Set z-value for visibility
                        connection_line.setZValue(3)
                        
                        # Highlight the reversal differential
                        if rev_diff in self.day_markers:
                            rev_marker = self.day_markers[rev_diff]
                            rev_marker.originalBrush = rev_marker.brush()
                            rev_marker.setBrush(QBrush(QColor(255, 0, 0, 200)))  # Semi-transparent red
                            rev_marker.isHighlighted = True
                except Exception as e:
                    logger.error(f"Error drawing reversal connection between {selected} and {rev_diff}: {e}")
                    