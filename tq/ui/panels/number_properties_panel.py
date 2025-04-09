"""
Purpose: Provides a UI panel for displaying number properties analysis

This file is part of the tq pillar and serves as a UI component.
It displays comprehensive properties of numbers in a four-tab interface,
corresponding to the four numbers in the TQ Grid: base number,
conrune, reversal, and reversal's conrune.

Key components:
- NumberPropertiesPanel: Main widget with four tabs for number properties
- PropertiesTab: Individual tab showing properties for a specific number
- PropertySection: Section widget for grouping related properties

Dependencies:
- PyQt6: For UI components
- shared.services.number_properties_service: For number analysis
- tq.utils.ternary_transition: For applying conrune transformations
- tq.utils.ternary_converter: For ternary conversions
- gematria.services.search_service: For searching numbers in gematria
"""

import logging
from typing import Any, Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.search_service import SearchService
from shared.services.number_properties_service import NumberPropertiesService
from shared.services.service_locator import ServiceLocator
from tq.services.ternary_transition_service import TernaryTransitionService
from tq.services.tq_grid_service import TQGridService

logger = logging.getLogger(__name__)


class PropertySection(QWidget):
    """A section of related properties with a header."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.layout.setSpacing(4)

        # Create header
        header = QLabel(title)
        header.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
        """
        )
        self.layout.addWidget(header)

        # Add container for properties that can be shown/hidden
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        self.content_layout.setSpacing(8)

        # Create grid for properties
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        self.content_layout.addLayout(self.grid)  # Add grid only to content_layout

        self.layout.addWidget(self.content_widget)

        self.row = 0
        self._is_expanded = True

        # Store the last added property values
        self.last_properties = {}

        # Button container for actions (initially empty)
        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(8, 0, 8, 0)
        self.layout.addWidget(self.button_container)
        self.button_container.hide()  # Hide by default

    def setExpanded(self, expanded: bool) -> None:
        """Show or hide the section content."""
        self._is_expanded = expanded
        self.content_widget.setVisible(expanded)

    def isExpanded(self) -> bool:
        """Check if the section is expanded."""
        return self._is_expanded

    def add_property(self, name: str, value: str) -> None:
        """Add a property to the section."""
        name_label = QLabel(f"{name}:")
        name_label.setStyleSheet("font-weight: 500;")

        value_label = QLabel(str(value))
        value_label.setWordWrap(True)

        self.grid.addWidget(name_label, self.row, 0)
        self.grid.addWidget(value_label, self.row, 1)
        self.row += 1

        # Store the property
        self.last_properties[name] = value


class PropertiesTab(QWidget):
    """Tab showing properties for a single number."""

    def __init__(self):
        super().__init__()

        # Create main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: white;
            }
        """
        )
        self.layout.addWidget(scroll)

        # Create container for sections
        container = QWidget()
        self.sections_layout = QVBoxLayout(container)
        self.sections_layout.setContentsMargins(16, 16, 16, 16)
        self.sections_layout.setSpacing(16)
        scroll.setWidget(container)

        # Create sections
        self.prime = PropertySection("Prime Properties")
        self.factors = PropertySection("Factors")
        self.polygonal = PropertySection("Polygonal Numbers")
        self.centered = PropertySection("Centered Polygonal Numbers")
        self.special = PropertySection("Special Properties")
        self.database = PropertySection("Database Lookup")

        # Add lookup button
        lookup_container = QWidget()
        lookup_layout = QHBoxLayout(lookup_container)
        lookup_layout.setContentsMargins(8, 0, 8, 0)

        self.lookup_button = QPushButton("Find Words with this Value")
        self.lookup_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """
        )
        lookup_layout.addWidget(self.lookup_button)
        self.database.layout.addWidget(lookup_container)

        # Add results label
        self.results_label = QLabel()
        self.results_label.setWordWrap(True)
        self.results_label.setStyleSheet(
            """
            QLabel {
                color: #2c3e50;
                padding: 8px;
            }
        """
        )
        self.database.layout.addWidget(self.results_label)

        # Add "Send to Ternary Transitions" button container
        self.transition_button_container = QWidget()
        transition_layout = QHBoxLayout(self.transition_button_container)
        transition_layout.setContentsMargins(8, 0, 8, 0)

        self.transition_button = QPushButton("Send to Ternary Transitions")
        self.transition_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        self.transition_button.clicked.connect(self._send_to_transitions)
        self.transition_button.setEnabled(False)  # Initially disabled
        transition_layout.addWidget(self.transition_button)

        # Add button after special properties
        self.special.layout.addWidget(self.transition_button_container)

        # Add "Send to Series Transitions" button
        self.series_button = QPushButton("Send Factors to Series Transitions")
        self.series_button.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #6c3483;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )
        self.series_button.clicked.connect(self._send_to_series_transitions)
        self.series_button.setEnabled(False)  # Initially disabled
        self.factors.button_layout.addWidget(self.series_button)
        self.factors.button_container.show()

        # Add sections to layout
        self.sections_layout.addWidget(self.prime)
        self.sections_layout.addWidget(self.factors)
        self.sections_layout.addWidget(self.polygonal)
        self.sections_layout.addWidget(self.centered)
        self.sections_layout.addWidget(self.special)
        self.sections_layout.addWidget(self.database)

        # Add stretch at the end
        self.sections_layout.addStretch()

        # Store current number
        self.current_number = 0

        # Connect button signal
        self.lookup_button.clicked.connect(self._lookup_in_database)

    def _lookup_in_database(self) -> None:
        """Look up the current number in the calculation database."""
        if not self.current_number:
            self.results_label.setText("Please enter a number first.")
            return

        try:
            # Get the calculation database service
            calc_service = ServiceLocator.get(CalculationDatabaseService)
            if not calc_service:
                raise RuntimeError("Calculation database service not available")

            # Find calculations with this value
            results = calc_service.find_calculations_by_value(self.current_number)

            if results:
                # Format results with better organization
                results_by_type = {}
                for result in results:
                    calc_type = result.calculation_type
                    if calc_type not in results_by_type:
                        results_by_type[calc_type] = []
                    results_by_type[calc_type].append(
                        result.input_text
                    )  # Use input_text instead of text

                # Build formatted text
                result_text = []
                for calc_type, words in results_by_type.items():
                    result_text.append(f"{calc_type}:")
                    for word in sorted(words):
                        result_text.append(f"  • {word}")
                    result_text.append("")  # Add blank line between sections

                self.results_label.setText("\n".join(result_text).strip())
            else:
                self.results_label.setText(
                    f"No words found with value {self.current_number}."
                )

        except Exception as e:
            logger.error(f"Error looking up in database: {str(e)}")
            error_msg = "Error looking up words in database."
            if isinstance(e, RuntimeError):
                error_msg = str(e)
            self.results_label.setText(error_msg)

        # Ensure the results are visible
        self.database.setExpanded(True)

    def _send_to_transitions(self):
        """Send the aliquot sum and abundance/deficiency to the ternary transitions panel."""
        try:
            # Get the values from the special properties section
            aliquot_sum = int(self.special.last_properties.get("Aliquot Sum", "0"))
            abundance_text = self.special.last_properties.get(
                "Abundance/Deficiency", "0"
            )
            logger.debug(f"Raw abundance text: {abundance_text}")

            # Extract the number from the abundance text
            abundance_value = int("".join(filter(str.isdigit, abundance_text)))
            logger.debug(
                f"Sending to transitions - aliquot_sum: {aliquot_sum}, abundance_value: {abundance_value}"
            )

            # Use the service to set the transition numbers
            transition_service = TernaryTransitionService.get_instance()
            transition_service.set_transition_numbers(aliquot_sum, abundance_value)
            logger.debug("Transition numbers set successfully")

        except Exception as e:
            logger.error(f"Error in _send_to_transitions: {e}")
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error", f"Could not send values to Ternary Transitions: {str(e)}"
            )

    def _send_to_series_transitions(self):
        """Send the factors to the series transitions panel."""
        try:
            # Get the factors using NumberPropertiesService
            service = NumberPropertiesService.get_instance()
            factors = service.get_factors(self.current_number)

            if not factors:
                logger.warning("No factors found to send to Series Transitions")
                return

            # Sort factors to ensure proper pairing
            factors.sort()

            # Create pairs of adjacent factors that multiply to make the number
            pairs = []
            for i in range(len(factors)):
                for j in range(i + 1, len(factors)):
                    if factors[i] * factors[j] == self.current_number:
                        pairs.append((factors[i], factors[j]))

            logger.debug(f"Created factor pairs for {self.current_number}: {pairs}")

            # Import and initialize the service
            from tq.services.series_transition_service import SeriesTransitionService

            # Initialize the service first (this will register it with ServiceLocator)
            series_service = SeriesTransitionService.get_instance()
            logger.debug("Initialized SeriesTransitionService singleton")

            # Get the window and clear existing pairs through its widget
            window = series_service.get_window()
            window.transition_widget.clear_pairs()
            logger.debug("Cleared existing pairs")

            # Add additional pair slots if needed (window starts with 2 by default)
            if len(pairs) > 2:
                for _ in range(len(pairs) - 2):
                    window.transition_widget._add_number_pair()
                logger.debug(f"Added {len(pairs) - 2} additional pair slots")

            # Set the values for each pair
            for i, (first, second) in enumerate(pairs):
                window.transition_widget.pair_inputs[i].first_number.setText(str(first))
                window.transition_widget.pair_inputs[i].second_number.setText(
                    str(second)
                )
                logger.debug(f"Set pair {i+1}: {first}, {second}")

            # Calculate transitions
            window.transition_widget._calculate_transitions()

            # Show and raise the window
            window.show()
            window.raise_()
            window.update()

        except Exception as e:
            logger.error(f"Error in _send_to_series_transitions: {e}")
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Error", f"Could not send factors to Series Transitions: {str(e)}"
            )

    def update_properties(self, properties: Dict[str, Any]) -> None:
        """Update all properties in the tab."""
        # Store current number for database lookup
        self.current_number = properties.get("number", 0)

        # Clear existing properties
        for section in [
            self.prime,
            self.factors,
            self.polygonal,
            self.centered,
            self.special,
        ]:
            for i in reversed(range(section.grid.count())):
                section.grid.itemAt(i).widget().deleteLater()
            section.row = 0  # Reset row counter

        try:
            # Update prime properties
            is_prime = properties.get("is_prime", False)
            self.prime.add_property("Is Prime", "Yes" if is_prime else "No")
            if is_prime:
                prime_ordinal = properties.get("prime_ordinal")
                if prime_ordinal is not None:
                    self.prime.add_property("Prime Index", str(prime_ordinal))

            # Update factors
            factors = properties.get("factors", [])
            if factors:
                factor_str = ", ".join(str(f) for f in sorted(factors))
                self.factors.add_property("Factors", factor_str)
                self.series_button.setEnabled(
                    True
                )  # Enable the button if we have factors

                # Calculate sum of factors
                factor_sum = sum(factors)
                self.factors.add_property("Sum of Factors", str(factor_sum))
            else:
                self.series_button.setEnabled(False)  # Disable if no factors

            # Update polygonal numbers with indices
            for k in range(3, 11):  # Check triangular through decagonal
                idx = properties.get(f"polygonal_{k}_index")
                if idx is not None:
                    shape_name = {
                        3: "Triangular",
                        4: "Square",
                        5: "Pentagonal",
                        6: "Hexagonal",
                        7: "Heptagonal",
                        8: "Octagonal",
                        9: "Nonagonal",
                        10: "Decagonal",
                    }[k]
                    self.polygonal.add_property(f"{shape_name}", f"Yes (Index: {idx})")

            # Update centered polygonal numbers with indices
            for k in range(3, 11):
                idx = properties.get(f"centered_{k}_index")
                if idx is not None:
                    shape_name = {
                        3: "Centered Triangular",
                        4: "Centered Square",
                        5: "Centered Pentagonal",
                        6: "Centered Hexagonal",
                        7: "Centered Heptagonal",
                        8: "Centered Octagonal",
                        9: "Centered Nonagonal",
                        10: "Centered Decagonal",
                    }[k]
                    self.centered.add_property(f"{shape_name}", f"Yes (Index: {idx})")

            # Update special properties
            aliquot_sum = properties.get("aliquot_sum", 0)
            self.special.add_property("Aliquot Sum", str(aliquot_sum))
            logger.debug(f"Setting aliquot sum: {aliquot_sum}")

            if properties.get("is_perfect"):
                self.special.add_property("Perfect Number", "Yes")
            elif properties.get("is_abundant"):
                abundance = aliquot_sum - properties.get("number", 0)
                self.special.add_property("Abundance/Deficiency", f"{abundance}")
                logger.debug(f"Setting abundance value: {abundance}")
            elif properties.get("is_deficient"):
                deficiency = properties.get("number", 0) - aliquot_sum
                self.special.add_property("Abundance/Deficiency", f"{deficiency}")
                logger.debug(f"Setting deficiency value: {deficiency}")

            # Check if we should enable the transition button
            abundance_text = properties.get("special", {}).get(
                "Abundance/Deficiency", ""
            )
            is_perfect = "perfect" in abundance_text.lower()
            self.transition_button.setEnabled(
                not is_perfect
            )  # Enable only if not perfect

            # Clear any previous database results
            self.results_label.setText("")

        except Exception as e:
            logger.error(f"Error updating properties: {e}")
            # Add a message to the prime section indicating the error
            self.prime.add_property("Status", "Error loading properties")


class NumberPropertiesPanel(QWidget):
    """Panel showing properties for all four TQ Grid numbers."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Get services
        self.number_service = NumberPropertiesService.get_instance()
        self.calculation_service = ServiceLocator.get(CalculationDatabaseService)
        self.search_service = ServiceLocator.get(SearchService)

        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget {
                min-width: 400px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 12px;
                margin: 0;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: white;
                border: 1px solid #ddd;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-bottom: none;
            }
        """
        )

        # Create property tabs
        self.base_tab = PropertiesTab()
        self.conrune_tab = PropertiesTab()
        self.reversal_tab = PropertiesTab()
        self.reversal_conrune_tab = PropertiesTab()

        # Add tabs with initial labels (will be updated with numbers)
        self.tabs.addTab(self.base_tab, "0")
        self.tabs.addTab(self.conrune_tab, "0")
        self.tabs.addTab(self.reversal_tab, "0")
        self.tabs.addTab(self.reversal_conrune_tab, "0")

        self.layout.addWidget(self.tabs)

        # Track current numbers
        self._current_numbers = {
            "base": 0,
            "conrune": 0,
            "reversal": 0,
            "reversal_conrune": 0,
        }

    def set_number(self, number: int) -> None:
        """
        Update properties panel with numbers from the TQ Grid.

        Args:
            number: The base number to analyze
        """
        try:
            # Get the TQ Grid service
            grid_service = TQGridService.get_instance()

            # Get the current grid display values
            grid = grid_service.get_current_grid()

            # Update all tabs with grid values
            self.update_numbers(
                grid.base_number, grid.conrune, grid.reversal, grid.reversal_conrune
            )

            # Select the base number tab
            self.tabs.setCurrentIndex(0)

        except Exception as e:
            logger.error(f"Error in set_number: {e}")
            # Update with error values
            self.update_numbers(number, 0, 0, 0)

    def update_numbers(
        self, base: int, conrune: int, reversal: int, reversal_conrune: int
    ) -> None:
        """Update properties for all four numbers."""
        # Store current numbers
        self._current_numbers = {
            "base": base,
            "conrune": conrune,
            "reversal": reversal,
            "reversal_conrune": reversal_conrune,
        }

        # Update tab labels with the actual numbers
        self.tabs.setTabText(0, str(base))
        self.tabs.setTabText(1, str(conrune))
        self.tabs.setTabText(2, str(reversal))
        self.tabs.setTabText(3, str(reversal_conrune))

        # Get properties for each number
        base_props = self.number_service.get_number_properties(base)
        conrune_props = self.number_service.get_number_properties(conrune)
        reversal_props = self.number_service.get_number_properties(reversal)
        reversal_conrune_props = self.number_service.get_number_properties(
            reversal_conrune
        )

        # Update each tab
        self.base_tab.update_properties(base_props)
        self.conrune_tab.update_properties(conrune_props)
        self.reversal_tab.update_properties(reversal_props)
        self.reversal_conrune_tab.update_properties(reversal_conrune_props)
