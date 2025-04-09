"""
Purpose: Provides a widget for searching and selecting locations.

This file is part of the astrology pillar and serves as a UI component.
It provides a widget for searching locations by name and selecting them
for use in birth chart calculations.

Key components:
- LocationSearchWidget: Widget for searching and selecting locations

Dependencies:
- PyQt6: For UI components
- astrology.services: For location service
"""

from typing import List, Optional, Callable

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QWidget, QSplitter, QGroupBox,
    QFormLayout, QCheckBox, QTabWidget
)
from PyQt6.QtGui import QFont

from loguru import logger

from astrology.services.location_service import LocationService, Location


class LocationSearchWidget(QWidget):
    """Widget for searching and selecting locations."""
    
    # Signal emitted when a location is selected
    location_selected = pyqtSignal(Location)
    
    def __init__(self, parent=None):
        """Initialize the location search widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Get the location service
        self.location_service = LocationService.get_instance()
        
        # Current search results
        self.search_results = []
        
        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        # Initialize UI
        self._init_ui()
        
        logger.debug("LocationSearchWidget initialized")
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Search tab
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        
        # Search input
        search_input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter location name (city, state, country)")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        search_input_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)
        search_input_layout.addWidget(self.search_button)
        
        search_layout.addLayout(search_input_layout)
        
        # Search results
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_result_double_clicked)
        search_layout.addWidget(self.results_list)
        
        # Location details
        details_group = QGroupBox("Location Details")
        details_layout = QFormLayout()
        
        self.name_label = QLabel("")
        details_layout.addRow("Name:", self.name_label)
        
        self.latitude_label = QLabel("")
        details_layout.addRow("Latitude:", self.latitude_label)
        
        self.longitude_label = QLabel("")
        details_layout.addRow("Longitude:", self.longitude_label)
        
        self.country_label = QLabel("")
        details_layout.addRow("Country:", self.country_label)
        
        self.state_label = QLabel("")
        details_layout.addRow("State/Province:", self.state_label)
        
        self.city_label = QLabel("")
        details_layout.addRow("City:", self.city_label)
        
        details_group.setLayout(details_layout)
        search_layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("Select Location")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)
        
        self.favorite_button = QPushButton("Add to Favorites")
        self.favorite_button.clicked.connect(self._on_favorite_clicked)
        self.favorite_button.setEnabled(False)
        button_layout.addWidget(self.favorite_button)
        
        search_layout.addLayout(button_layout)
        
        # Add search tab
        self.tabs.addTab(search_tab, "Search")
        
        # Favorites tab
        favorites_tab = QWidget()
        favorites_layout = QVBoxLayout(favorites_tab)
        
        # Favorites list
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self._on_favorite_double_clicked)
        favorites_layout.addWidget(self.favorites_list)
        
        # Buttons
        favorites_button_layout = QHBoxLayout()
        
        self.select_favorite_button = QPushButton("Select Location")
        self.select_favorite_button.clicked.connect(self._on_select_favorite_clicked)
        self.select_favorite_button.setEnabled(False)
        favorites_button_layout.addWidget(self.select_favorite_button)
        
        self.remove_favorite_button = QPushButton("Remove from Favorites")
        self.remove_favorite_button.clicked.connect(self._on_remove_favorite_clicked)
        self.remove_favorite_button.setEnabled(False)
        favorites_button_layout.addWidget(self.remove_favorite_button)
        
        favorites_layout.addLayout(favorites_button_layout)
        
        # Add favorites tab
        self.tabs.addTab(favorites_tab, "Favorites")
        
        # Coordinates tab
        coordinates_tab = QWidget()
        coordinates_layout = QVBoxLayout(coordinates_tab)
        
        # Coordinates input
        coordinates_group = QGroupBox("Enter Coordinates")
        coordinates_form = QFormLayout()
        
        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("e.g., 40.7128 (North is positive)")
        coordinates_form.addRow("Latitude:", self.latitude_input)
        
        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("e.g., -74.0060 (East is positive)")
        coordinates_form.addRow("Longitude:", self.longitude_input)
        
        self.lookup_button = QPushButton("Lookup Location")
        self.lookup_button.clicked.connect(self._on_lookup_clicked)
        coordinates_form.addRow("", self.lookup_button)
        
        coordinates_group.setLayout(coordinates_form)
        coordinates_layout.addWidget(coordinates_group)
        
        # Reverse geocoding results
        self.reverse_details = QGroupBox("Location Details")
        reverse_layout = QFormLayout()
        
        self.reverse_name_label = QLabel("")
        reverse_layout.addRow("Name:", self.reverse_name_label)
        
        self.reverse_country_label = QLabel("")
        reverse_layout.addRow("Country:", self.reverse_country_label)
        
        self.reverse_state_label = QLabel("")
        reverse_layout.addRow("State/Province:", self.reverse_state_label)
        
        self.reverse_city_label = QLabel("")
        reverse_layout.addRow("City:", self.reverse_city_label)
        
        self.reverse_details.setLayout(reverse_layout)
        coordinates_layout.addWidget(self.reverse_details)
        
        # Buttons
        reverse_button_layout = QHBoxLayout()
        
        self.select_reverse_button = QPushButton("Select Location")
        self.select_reverse_button.clicked.connect(self._on_select_reverse_clicked)
        self.select_reverse_button.setEnabled(False)
        reverse_button_layout.addWidget(self.select_reverse_button)
        
        self.favorite_reverse_button = QPushButton("Add to Favorites")
        self.favorite_reverse_button.clicked.connect(self._on_favorite_reverse_clicked)
        self.favorite_reverse_button.setEnabled(False)
        reverse_button_layout.addWidget(self.favorite_reverse_button)
        
        coordinates_layout.addLayout(reverse_button_layout)
        
        # Add coordinates tab
        self.tabs.addTab(coordinates_tab, "Coordinates")
        
        # Load favorites
        self._load_favorites()
    
    def _on_search_text_changed(self, text):
        """Handle search text changes.
        
        Args:
            text: New search text
        """
        # Reset the timer
        self.search_timer.stop()
        
        # Start the timer if there's text
        if text:
            self.search_timer.start(500)  # 500ms debounce
    
    def _perform_search(self):
        """Perform a location search."""
        # Get search text
        search_text = self.search_input.text().strip()
        
        # Skip if empty
        if not search_text:
            return
        
        # Clear results
        self.results_list.clear()
        self.search_results = []
        
        # Disable buttons
        self.select_button.setEnabled(False)
        self.favorite_button.setEnabled(False)
        
        # Clear details
        self._clear_details()
        
        # Search for locations
        locations = self.location_service.search_locations(search_text)
        
        # Store results
        self.search_results = locations
        
        # Add results to list
        for location in locations:
            item = QListWidgetItem(location.display_name)
            self.results_list.addItem(item)
        
        # Show message if no results
        if not locations:
            self.results_list.addItem("No results found")
    
    def _on_result_double_clicked(self, item):
        """Handle double-clicking a search result.
        
        Args:
            item: Clicked item
        """
        # Get the index
        index = self.results_list.row(item)
        
        # Check if valid
        if index < 0 or index >= len(self.search_results):
            return
        
        # Get the location
        location = self.search_results[index]
        
        # Show details
        self._show_details(location)
        
        # Enable buttons
        self.select_button.setEnabled(True)
        self.favorite_button.setEnabled(True)
    
    def _on_select_clicked(self):
        """Handle clicking the select button."""
        # Get the selected index
        index = self.results_list.currentRow()
        
        # Check if valid
        if index < 0 or index >= len(self.search_results):
            return
        
        # Get the location
        location = self.search_results[index]
        
        # Emit signal
        self.location_selected.emit(location)
    
    def _on_favorite_clicked(self):
        """Handle clicking the favorite button."""
        # Get the selected index
        index = self.results_list.currentRow()
        
        # Check if valid
        if index < 0 or index >= len(self.search_results):
            return
        
        # Get the location
        location = self.search_results[index]
        
        # Add to favorites
        self.location_service.add_favorite(location)
        
        # Reload favorites
        self._load_favorites()
    
    def _on_favorite_double_clicked(self, item):
        """Handle double-clicking a favorite.
        
        Args:
            item: Clicked item
        """
        # Get the index
        index = self.favorites_list.row(item)
        
        # Check if valid
        if index < 0:
            return
        
        # Get the location
        favorites = self.location_service.get_favorites()
        if index >= len(favorites):
            return
        
        location = favorites[index]
        
        # Enable buttons
        self.select_favorite_button.setEnabled(True)
        self.remove_favorite_button.setEnabled(True)
    
    def _on_select_favorite_clicked(self):
        """Handle clicking the select favorite button."""
        # Get the selected index
        index = self.favorites_list.currentRow()
        
        # Check if valid
        if index < 0:
            return
        
        # Get the location
        favorites = self.location_service.get_favorites()
        if index >= len(favorites):
            return
        
        location = favorites[index]
        
        # Emit signal
        self.location_selected.emit(location)
    
    def _on_remove_favorite_clicked(self):
        """Handle clicking the remove favorite button."""
        # Get the selected index
        index = self.favorites_list.currentRow()
        
        # Check if valid
        if index < 0:
            return
        
        # Get the location
        favorites = self.location_service.get_favorites()
        if index >= len(favorites):
            return
        
        location = favorites[index]
        
        # Remove from favorites
        self.location_service.remove_favorite(location)
        
        # Reload favorites
        self._load_favorites()
        
        # Disable buttons
        self.select_favorite_button.setEnabled(False)
        self.remove_favorite_button.setEnabled(False)
    
    def _on_lookup_clicked(self):
        """Handle clicking the lookup button."""
        # Get coordinates
        try:
            latitude = float(self.latitude_input.text())
            longitude = float(self.longitude_input.text())
        except ValueError:
            # Show error
            self.reverse_name_label.setText("Invalid coordinates")
            self.reverse_country_label.setText("")
            self.reverse_state_label.setText("")
            self.reverse_city_label.setText("")
            
            # Disable buttons
            self.select_reverse_button.setEnabled(False)
            self.favorite_reverse_button.setEnabled(False)
            
            return
        
        # Reverse geocode
        location = self.location_service.reverse_geocode(latitude, longitude)
        
        # Check if found
        if not location:
            # Show error
            self.reverse_name_label.setText("Location not found")
            self.reverse_country_label.setText("")
            self.reverse_state_label.setText("")
            self.reverse_city_label.setText("")
            
            # Disable buttons
            self.select_reverse_button.setEnabled(False)
            self.favorite_reverse_button.setEnabled(False)
            
            return
        
        # Show details
        self.reverse_name_label.setText(location.display_name)
        self.reverse_country_label.setText(location.country or "")
        self.reverse_state_label.setText(location.state or "")
        self.reverse_city_label.setText(location.city or "")
        
        # Store location
        self.reverse_location = location
        
        # Enable buttons
        self.select_reverse_button.setEnabled(True)
        self.favorite_reverse_button.setEnabled(True)
    
    def _on_select_reverse_clicked(self):
        """Handle clicking the select reverse button."""
        # Check if we have a location
        if not hasattr(self, "reverse_location"):
            return
        
        # Emit signal
        self.location_selected.emit(self.reverse_location)
    
    def _on_favorite_reverse_clicked(self):
        """Handle clicking the favorite reverse button."""
        # Check if we have a location
        if not hasattr(self, "reverse_location"):
            return
        
        # Add to favorites
        self.location_service.add_favorite(self.reverse_location)
        
        # Reload favorites
        self._load_favorites()
    
    def _show_details(self, location):
        """Show location details.
        
        Args:
            location: Location to show
        """
        self.name_label.setText(location.display_name)
        self.latitude_label.setText(str(location.latitude))
        self.longitude_label.setText(str(location.longitude))
        self.country_label.setText(location.country or "")
        self.state_label.setText(location.state or "")
        self.city_label.setText(location.city or "")
    
    def _clear_details(self):
        """Clear location details."""
        self.name_label.setText("")
        self.latitude_label.setText("")
        self.longitude_label.setText("")
        self.country_label.setText("")
        self.state_label.setText("")
        self.city_label.setText("")
    
    def _load_favorites(self):
        """Load favorite locations."""
        # Clear list
        self.favorites_list.clear()
        
        # Get favorites
        favorites = self.location_service.get_favorites()
        
        # Add to list
        for location in favorites:
            item = QListWidgetItem(location.display_name)
            self.favorites_list.addItem(item)
        
        # Show message if no favorites
        if not favorites:
            self.favorites_list.addItem("No favorite locations")
        
        # Disable buttons
        self.select_favorite_button.setEnabled(False)
        self.remove_favorite_button.setEnabled(False)
