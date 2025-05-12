"""
Purpose: Provides a widget for analyzing a Temple's position in the Kamea network

This file is part of the tq pillar and serves as a UI component.
It analyzes a Temple's unique position in the Kamea network, showing its
relationships to Hierophants and Acolytes, its dimensional resonance,
element distribution, and connections to other Temples.

Key components:
- TemplePositionAnalyzer: Class for analyzing Temple positions
- TemplePositionDialog: Dialog for displaying the analysis

Dependencies:
- PyQt6: For the user interface components
- tq.services.kamea_service: For Kamea-related operations
- tq.services.ternary_dimension_interpreter_new: For Hierophant and Acolyte data

Related files:
- tq/ui/panels/kamea_of_maut_panel.py: Panel that uses this analyzer
- tq/services/kamea_service.py: Service for Kamea operations
"""

from typing import Dict, List

from loguru import logger
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tq.services.kamea_service import KameaService
from tq.services.ternary_dimension_interpreter_new import (
    ACOLYTES,
    HIEROPHANTS,
    TernaryDimensionInterpreter,
)


class TemplePositionAnalyzer:
    """Analyzes a Temple's unique position in the Kamea network."""

    def __init__(self, kamea_service: KameaService):
        """Initialize with the Kamea service.

        Args:
            kamea_service: The Kamea service to use for operations
        """
        self.kamea_service = kamea_service
        self.interpreter = TernaryDimensionInterpreter()

    def analyze_temple(self, ternary_value: str) -> Dict:
        """Analyze a Temple's position and relationships.

        Args:
            ternary_value: The ternary value of the Temple to analyze

        Returns:
            Dictionary with analysis results
        """
        # Ensure we have a valid ternary value
        if not ternary_value or len(str(ternary_value).strip()) == 0:
            return {"error": "Invalid ternary value"}

        ternary_value = str(ternary_value).zfill(6)

        # Determine if this is a Temple, Acolyte, or Hierophant
        cell_type = self._determine_cell_type(ternary_value)
        if cell_type != "Temple":
            return {"error": f"Selected cell is a {cell_type}, not a Temple"}

        # Get basic information
        family = self._determine_family(ternary_value)
        hierophant = self._get_hierophant(family)
        acolytes = self._get_governing_acolytes(ternary_value, family)

        # Get Kamea Locator
        kamea_locator = self.kamea_service.calculate_kamea_locator(ternary_value)

        # Analyze dimensional resonance
        dimensional_resonance = self._analyze_dimensional_resonance(ternary_value)

        # Analyze element distribution
        element_distribution = self._analyze_element_distribution(ternary_value)

        # Find connected Temples
        connected_temples = self._find_connected_temples(ternary_value, family)

        # Determine Temple type and descriptor
        temple_type = self._determine_temple_type(ternary_value)
        element_descriptor = self._determine_element_descriptor(ternary_value)

        # Create a comprehensive analysis
        return {
            "ternary_value": ternary_value,
            "family": family,
            "hierophant": {
                "ternary": hierophant,
                "name": self._get_hierophant_name(hierophant),
                "greek": self._get_hierophant_greek(hierophant),
                "description": self._get_hierophant_description(hierophant),
            },
            "acolytes": [
                {
                    "ternary": acolyte,
                    "title": self._get_acolyte_title(acolyte),
                    "greek": self._get_acolyte_greek(acolyte),
                    "function": self._get_acolyte_function(acolyte),
                }
                for acolyte in acolytes
            ],
            "kamea_locator": kamea_locator,
            "dimensional_resonance": dimensional_resonance,
            "element_distribution": element_distribution,
            "temple_type": {
                "name": temple_type,
                "greek": self._get_temple_type_greek(temple_type),
                "description": self._get_temple_type_description(temple_type),
            },
            "element_descriptor": {
                "name": element_descriptor,
                "description": self._get_element_descriptor_description(
                    element_descriptor
                ),
            },
            "connected_temples": connected_temples,
        }

    def _determine_cell_type(self, ternary_value: str) -> str:
        """Determine if a cell is a Temple, Acolyte, or Hierophant.

        Args:
            ternary_value: The ternary value to check

        Returns:
            "Hierophant", "Acolyte", or "Temple"
        """
        # Check if it's a Hierophant
        for family_id, hierophant in HIEROPHANTS.items():
            if ternary_value == hierophant["ternary"]:
                return "Hierophant"

        # Check if it's an Acolyte
        for acolyte_id, acolyte in ACOLYTES.items():
            if ternary_value == acolyte["ternary"]:
                return "Acolyte"

        # If it's neither, it's a Temple
        return "Temple"

    def _determine_family(self, ternary_value: str) -> int:
        """Determine which family a ternary value belongs to.

        Args:
            ternary_value: The ternary value to check

        Returns:
            Family ID (0-8)
        """
        # Use the interpreter to determine the family
        return self.interpreter.determine_family(ternary_value)

    def _get_hierophant(self, family: int) -> str:
        """Get the Hierophant (Prime Ditrune) for a family.

        Args:
            family: The family ID (0-8)

        Returns:
            The Hierophant's ternary value
        """
        return HIEROPHANTS.get(family, {}).get("ternary", "")

    def _get_governing_acolytes(self, ternary_value: str, family: int) -> List[str]:
        """Get the Acolytes that govern a Temple.

        Args:
            ternary_value: The Temple's ternary value
            family: The family ID (0-8)

        Returns:
            List of Acolyte ternary values
        """
        # This is a simplified implementation
        # In a real implementation, this would use the family type to determine
        # the correct Acolytes based on the Temple's position
        acolytes = []

        # Get all Acolytes in this family
        for acolyte_id, acolyte in ACOLYTES.items():
            if acolyte.get("family") == family:
                acolytes.append(acolyte["ternary"])

        # For now, just return the first Acolyte (or an empty list)
        return acolytes[:1] if acolytes else []

    def _analyze_dimensional_resonance(self, ternary_value: str) -> Dict:
        """Analyze the dimensional resonance of a ternary value.

        Args:
            ternary_value: The ternary value to analyze

        Returns:
            Dictionary with dimensional resonance information
        """
        # Extract positions
        positions = {
            "Seed": ternary_value[0],
            "Echo": ternary_value[1],
            "Weave": ternary_value[2],
            "Pulse": ternary_value[3],
            "Flow": ternary_value[4],
            "Nova": ternary_value[5],
        }

        # Determine resonance strength for each position
        resonance = {}
        for position, value in positions.items():
            if value == "0":
                resonance[position] = "Aperture (Receptive)"
            elif value == "1":
                resonance[position] = "Surge (Transformative)"
            else:  # value == "2"
                resonance[position] = "Lattice (Structural)"

        return {"positions": positions, "resonance": resonance}

    def _analyze_element_distribution(self, ternary_value: str) -> Dict:
        """Analyze the distribution of elements in a ternary value.

        Args:
            ternary_value: The ternary value to analyze

        Returns:
            Dictionary with element distribution information
        """
        # Count elements
        aperture_count = ternary_value.count("0")
        surge_count = ternary_value.count("1")
        lattice_count = ternary_value.count("2")

        # Calculate percentages
        total = len(ternary_value)
        aperture_percent = (aperture_count / total) * 100
        surge_percent = (surge_count / total) * 100
        lattice_percent = (lattice_count / total) * 100

        # Determine dominant element
        if aperture_count > surge_count and aperture_count > lattice_count:
            dominant = "Aperture"
        elif surge_count > aperture_count and surge_count > lattice_count:
            dominant = "Surge"
        elif lattice_count > aperture_count and lattice_count > surge_count:
            dominant = "Lattice"
        else:
            dominant = "Balanced"

        return {
            "aperture": {"count": aperture_count, "percent": aperture_percent},
            "surge": {"count": surge_count, "percent": surge_percent},
            "lattice": {"count": lattice_count, "percent": lattice_percent},
            "dominant": dominant,
        }

    def _find_connected_temples(self, ternary_value: str, family: int) -> List[Dict]:
        """Find Temples connected to this Temple.

        Args:
            ternary_value: The Temple's ternary value
            family: The family ID (0-8)

        Returns:
            List of connected Temple information
        """
        # For now, just find the conrune pair
        conrune_pair = self.kamea_service.get_conrune_pair(ternary_value)
        if not conrune_pair:
            return []

        # Find the position of the conrune pair
        conrune_position = self.kamea_service.find_cell_position(conrune_pair)
        if not conrune_position:
            return []

        # Return the connected Temple
        return [
            {
                "ternary": conrune_pair,
                "position": conrune_position,
                "relationship": "Conrune Pair",
                "description": "Complementary pattern that balances this Temple",
            }
        ]

    def _determine_temple_type(self, ternary_value: str) -> str:
        """Determine the Temple type based on the ternary value.

        Args:
            ternary_value: The Temple's ternary value

        Returns:
            Temple type name
        """
        # This is a simplified implementation
        # In a real implementation, this would use a more sophisticated algorithm
        # based on the Temple's position in the family

        # For now, use a simple mapping based on the first digit
        first_digit = ternary_value[0]
        if first_digit == "0":
            return "The Nexus"
        elif first_digit == "1":
            return "The Crucible"
        elif first_digit == "2":
            return "The Beacon"

        return "The Nexus"  # Default

    def _determine_element_descriptor(self, ternary_value: str) -> str:
        """Determine the element descriptor based on the ternary value.

        Args:
            ternary_value: The Temple's ternary value

        Returns:
            Element descriptor
        """
        # Count elements
        aperture_count = ternary_value.count("0")
        surge_count = ternary_value.count("1")
        lattice_count = ternary_value.count("2")

        # Check for palindromic pattern
        if ternary_value == ternary_value[::-1]:
            return "of Perfect Reflection"

        # Check for ascending pattern (0→1→2)
        if "012" in ternary_value:
            return "of Rising Power"

        # Check for descending pattern (2→1→0)
        if "210" in ternary_value:
            return "of Deepening Wisdom"

        # Check for alternating pattern
        if "010" in ternary_value or "121" in ternary_value or "202" in ternary_value:
            return "of Rhythmic Exchange"

        # Check for concentrated pattern (3+ of same digit)
        if aperture_count >= 3:
            return "of Open Mystery"
        elif surge_count >= 3:
            return "of Flowing Energy"
        elif lattice_count >= 3:
            return "of Formed Pattern"

        # Default to balanced
        return "of Harmonic Balance"

    def _get_hierophant_name(self, hierophant: str) -> str:
        """Get the name of a Hierophant.

        Args:
            hierophant: The Hierophant's ternary value

        Returns:
            The Hierophant's name
        """
        # Look up the Hierophant in the HIEROPHANTS dictionary
        for family_id, h in HIEROPHANTS.items():
            if h["ternary"] == hierophant:
                return h.get("name", "Unknown")

        return "Unknown"

    def _get_hierophant_greek(self, hierophant: str) -> str:
        """Get the Greek name of a Hierophant.

        Args:
            hierophant: The Hierophant's ternary value

        Returns:
            The Hierophant's Greek name
        """
        # Look up the Hierophant in the HIEROPHANTS dictionary
        for family_id, h in HIEROPHANTS.items():
            if h["ternary"] == hierophant:
                return h.get("greek", "Unknown")

        return "Unknown"

    def _get_hierophant_description(self, hierophant: str) -> str:
        """Get the description of a Hierophant.

        Args:
            hierophant: The Hierophant's ternary value

        Returns:
            The Hierophant's description
        """
        # Look up the Hierophant in the HIEROPHANTS dictionary
        for family_id, h in HIEROPHANTS.items():
            if h["ternary"] == hierophant:
                return h.get("description", "Unknown")

        return "Unknown"

    def _get_acolyte_title(self, acolyte: str) -> str:
        """Get the title of an Acolyte.

        Args:
            acolyte: The Acolyte's ternary value

        Returns:
            The Acolyte's title
        """
        # Look up the Acolyte in the ACOLYTES dictionary
        for acolyte_id, a in ACOLYTES.items():
            if a["ternary"] == acolyte:
                return a.get("title", "Unknown")

        return "Unknown"

    def _get_acolyte_greek(self, acolyte: str) -> str:
        """Get the Greek name of an Acolyte.

        Args:
            acolyte: The Acolyte's ternary value

        Returns:
            The Acolyte's Greek name
        """
        # Look up the Acolyte in the ACOLYTES dictionary
        for acolyte_id, a in ACOLYTES.items():
            if a["ternary"] == acolyte:
                return a.get("greek", "Unknown")

        return "Unknown"

    def _get_acolyte_function(self, acolyte: str) -> str:
        """Get the function of an Acolyte.

        Args:
            acolyte: The Acolyte's ternary value

        Returns:
            The Acolyte's function
        """
        # Look up the Acolyte in the ACOLYTES dictionary
        for acolyte_id, a in ACOLYTES.items():
            if a["ternary"] == acolyte:
                return a.get("function", "Unknown")

        return "Unknown"

    def _get_temple_type_greek(self, temple_type: str) -> str:
        """Get the Greek name of a Temple type.

        Args:
            temple_type: The Temple type

        Returns:
            The Temple type's Greek name
        """
        # Map Temple types to Greek names
        greek_names = {
            "The Nexus": "Σύνδεσμος (Syndesmos)",
            "The Crucible": "Χωνευτήριον (Choneuterion)",
            "The Beacon": "Φρυκτωρία (Phryktoria)",
            "The Reservoir": "Δεξαμενή (Dexamene)",
            "The Threshold": "Κατώφλιον (Katophlion)",
            "The Conduit": "Ὀχετός (Ochetos)",
            "The Resonator": "Ἠχεῖον (Echeion)",
            "The Catalyst": "Ἐπιταχυντής (Epitachyntes)",
            "The Fulcrum": "Ὑπομόχλιον (Hypomochlion)",
        }

        return greek_names.get(temple_type, "Unknown")

    def _get_temple_type_description(self, temple_type: str) -> str:
        """Get the description of a Temple type.

        Args:
            temple_type: The Temple type

        Returns:
            The Temple type's description
        """
        # Map Temple types to descriptions
        descriptions = {
            "The Nexus": "Point of connection and convergence where multiple forces meet",
            "The Crucible": "Vessel of transformation where elements combine and transmute",
            "The Beacon": "Source of illumination that guides and reveals hidden patterns",
            "The Reservoir": "Container that collects, preserves, and distributes essential energies",
            "The Threshold": "Boundary between states that facilitates transition and initiation",
            "The Conduit": "Channel that directs and focuses flow between different domains",
            "The Resonator": "Structure that amplifies, harmonizes, and propagates vibrations",
            "The Catalyst": "Agent that accelerates processes and triggers transformations",
            "The Fulcrum": "Point of balance and leverage that enables movement and change",
        }

        return descriptions.get(temple_type, "Unknown")

    def _get_element_descriptor_description(self, element_descriptor: str) -> str:
        """Get the description of an element descriptor.

        Args:
            element_descriptor: The element descriptor

        Returns:
            The element descriptor's description
        """
        # Map element descriptors to descriptions
        descriptions = {
            "of Open Mystery": "Dominated by Aperture energy, creating receptive space for potential",
            "of Flowing Energy": "Dominated by Surge energy, creating dynamic transformation",
            "of Formed Pattern": "Dominated by Lattice energy, creating stable structure",
            "of Harmonic Balance": "Balanced elements creating equilibrium and integration",
            "of Perfect Reflection": "Palindromic pattern creating mirror-like symmetry",
            "of Rising Power": "Ascending pattern (0→1→2) creating evolutionary momentum",
            "of Deepening Wisdom": "Descending pattern (2→1→0) creating involutionary insight",
            "of Rhythmic Exchange": "Alternating pattern creating cyclical flow and exchange",
        }

        return descriptions.get(element_descriptor, "Unknown")


class TemplePositionDialog(QDialog):
    """Dialog for displaying Temple position analysis."""

    def __init__(self, parent, kamea_service: KameaService, row: int, col: int):
        """Initialize the dialog.

        Args:
            parent: The parent widget
            kamea_service: The Kamea service to use
            row: The row of the selected cell
            col: The column of the selected cell
        """
        super().__init__(parent)

        self.kamea_service = kamea_service
        self.row = row
        self.col = col

        # Get the ternary value
        self.ternary_value = self.kamea_service.get_kamea_value(row, col, False)
        if not self.ternary_value:
            logger.error(f"No ternary value found at ({row}, {col})")
            self.reject()
            return

        # Ensure it's a string and padded to 6 digits
        self.ternary_value = str(self.ternary_value).zfill(6)

        # Create the analyzer
        self.analyzer = TemplePositionAnalyzer(self.kamea_service)

        # Get the analysis
        self.analysis = self.analyzer.analyze_temple(self.ternary_value)

        # Check for errors
        if "error" in self.analysis:
            logger.error(f"Analysis error: {self.analysis['error']}")
            self.reject()
            return

        # Set up the dialog
        self.setWindowTitle(f"Temple Position Analysis: {self.ternary_value}")
        self.resize(800, 600)

        # Create the layout
        self.layout = QVBoxLayout(self)

        # Create the tabs
        self.tabs = QTabWidget()

        # Create the tabs
        self.lineage_tab = self._create_lineage_tab()
        self.position_tab = self._create_position_tab()
        self.composition_tab = self._create_composition_tab()
        self.connections_tab = self._create_connections_tab()

        # Add the tabs
        self.tabs.addTab(self.lineage_tab, "Lineage")
        self.tabs.addTab(self.position_tab, "Position")
        self.tabs.addTab(self.composition_tab, "Composition")
        self.tabs.addTab(self.connections_tab, "Connections")

        # Add the tabs to the layout
        self.layout.addWidget(self.tabs)

        # Add a close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.layout.addWidget(self.close_button)

    def _create_lineage_tab(self) -> QWidget:
        """Create the Lineage tab.

        Returns:
            The Lineage tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Hierophant section
        hierophant_group = QGroupBox("Hierophant (Prime Ditrune)")
        hierophant_layout = QVBoxLayout(hierophant_group)

        # Hierophant name and ternary
        hierophant_name = QLabel(
            f"<b>{self.analysis['hierophant']['name']}</b> ({self.analysis['hierophant']['ternary']})"
        )
        hierophant_layout.addWidget(hierophant_name)

        # Hierophant Greek name
        hierophant_greek = QLabel(f"Greek: {self.analysis['hierophant']['greek']}")
        hierophant_layout.addWidget(hierophant_greek)

        # Hierophant description
        hierophant_desc = QLabel(
            f"Description: {self.analysis['hierophant']['description']}"
        )
        hierophant_desc.setWordWrap(True)
        hierophant_layout.addWidget(hierophant_desc)

        # Add the Hierophant group to the layout
        layout.addWidget(hierophant_group)

        # Acolytes section
        acolytes_group = QGroupBox("Governing Acolytes")
        acolytes_layout = QVBoxLayout(acolytes_group)

        # Add each Acolyte
        for acolyte in self.analysis["acolytes"]:
            acolyte_widget = QWidget()
            acolyte_layout = QVBoxLayout(acolyte_widget)

            # Acolyte title and ternary
            acolyte_title = QLabel(f"<b>{acolyte['title']}</b> ({acolyte['ternary']})")
            acolyte_layout.addWidget(acolyte_title)

            # Acolyte Greek name
            acolyte_greek = QLabel(f"Greek: {acolyte['greek']}")
            acolyte_layout.addWidget(acolyte_greek)

            # Acolyte function
            acolyte_function = QLabel(f"Function: {acolyte['function']}")
            acolyte_function.setWordWrap(True)
            acolyte_layout.addWidget(acolyte_function)

            # Add the Acolyte widget to the layout
            acolytes_layout.addWidget(acolyte_widget)

        # Add the Acolytes group to the layout
        layout.addWidget(acolytes_group)

        # Add a spacer
        layout.addStretch()

        return tab

    def _create_position_tab(self) -> QWidget:
        """Create the Position tab.

        Returns:
            The Position tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Kamea Locator section
        locator_group = QGroupBox("Kamea Locator")
        locator_layout = QVBoxLayout(locator_group)

        # Kamea Locator value
        locator_value = QLabel(f"<b>{self.analysis['kamea_locator']}</b>")
        locator_layout.addWidget(locator_value)

        # Kamea Locator explanation
        locator_explanation = QLabel(
            "The Kamea Locator provides a unique address for this Temple in the Kamea network, in the format region-area-cell."
        )
        locator_explanation.setWordWrap(True)
        locator_layout.addWidget(locator_explanation)

        # Add the Locator group to the layout
        layout.addWidget(locator_group)

        # Dimensional Resonance section
        resonance_group = QGroupBox("Dimensional Resonance")
        resonance_layout = QVBoxLayout(resonance_group)

        # Add each position
        for position, value in self.analysis["dimensional_resonance"][
            "positions"
        ].items():
            resonance_widget = QWidget()
            resonance_layout_h = QHBoxLayout(resonance_widget)

            # Position name
            position_label = QLabel(f"<b>{position}:</b>")
            position_label.setFixedWidth(80)
            resonance_layout_h.addWidget(position_label)

            # Position value
            value_label = QLabel(
                f"{value} - {self.analysis['dimensional_resonance']['resonance'][position]}"
            )
            resonance_layout_h.addWidget(value_label)

            # Add the position widget to the layout
            resonance_layout.addWidget(resonance_widget)

        # Add the Resonance group to the layout
        layout.addWidget(resonance_group)

        # Add a spacer
        layout.addStretch()

        return tab

    def _create_composition_tab(self) -> QWidget:
        """Create the Composition tab.

        Returns:
            The Composition tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Element Distribution section
        element_group = QGroupBox("Element Distribution")
        element_layout = QVBoxLayout(element_group)

        # Dominant element
        dominant_label = QLabel(
            f"Dominant Element: <b>{self.analysis['element_distribution']['dominant']}</b>"
        )
        element_layout.addWidget(dominant_label)

        # Element counts
        aperture_label = QLabel(
            f"Aperture (0): {self.analysis['element_distribution']['aperture']['count']} ({self.analysis['element_distribution']['aperture']['percent']:.1f}%)"
        )
        element_layout.addWidget(aperture_label)

        surge_label = QLabel(
            f"Surge (1): {self.analysis['element_distribution']['surge']['count']} ({self.analysis['element_distribution']['surge']['percent']:.1f}%)"
        )
        element_layout.addWidget(surge_label)

        lattice_label = QLabel(
            f"Lattice (2): {self.analysis['element_distribution']['lattice']['count']} ({self.analysis['element_distribution']['lattice']['percent']:.1f}%)"
        )
        element_layout.addWidget(lattice_label)

        # Add the Element group to the layout
        layout.addWidget(element_group)

        # Temple Type section
        type_group = QGroupBox("Temple Type")
        type_layout = QVBoxLayout(type_group)

        # Temple type name
        type_name = QLabel(f"<b>{self.analysis['temple_type']['name']}</b>")
        type_layout.addWidget(type_name)

        # Temple type Greek name
        type_greek = QLabel(f"Greek: {self.analysis['temple_type']['greek']}")
        type_layout.addWidget(type_greek)

        # Temple type description
        type_desc = QLabel(
            f"Description: {self.analysis['temple_type']['description']}"
        )
        type_desc.setWordWrap(True)
        type_layout.addWidget(type_desc)

        # Add the Type group to the layout
        layout.addWidget(type_group)

        # Element Descriptor section
        descriptor_group = QGroupBox("Element Descriptor")
        descriptor_layout = QVBoxLayout(descriptor_group)

        # Element descriptor name
        descriptor_name = QLabel(
            f"<b>{self.analysis['element_descriptor']['name']}</b>"
        )
        descriptor_layout.addWidget(descriptor_name)

        # Element descriptor description
        descriptor_desc = QLabel(
            f"Description: {self.analysis['element_descriptor']['description']}"
        )
        descriptor_desc.setWordWrap(True)
        descriptor_layout.addWidget(descriptor_desc)

        # Add the Descriptor group to the layout
        layout.addWidget(descriptor_group)

        # Add a spacer
        layout.addStretch()

        return tab

    def _create_connections_tab(self) -> QWidget:
        """Create the Connections tab.

        Returns:
            The Connections tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Connected Temples section
        connected_group = QGroupBox("Connected Temples")
        connected_layout = QVBoxLayout(connected_group)

        # Add each connected Temple
        if not self.analysis["connected_temples"]:
            no_connections = QLabel("No connected Temples found.")
            connected_layout.addWidget(no_connections)
        else:
            for temple in self.analysis["connected_temples"]:
                temple_widget = QWidget()
                temple_layout = QVBoxLayout(temple_widget)

                # Temple ternary and position
                temple_ternary = QLabel(
                    f"<b>{temple['ternary']}</b> at position ({temple['position'][0]}, {temple['position'][1]})"
                )
                temple_layout.addWidget(temple_ternary)

                # Temple relationship
                temple_relationship = QLabel(f"Relationship: {temple['relationship']}")
                temple_layout.addWidget(temple_relationship)

                # Temple description
                temple_desc = QLabel(f"Description: {temple['description']}")
                temple_desc.setWordWrap(True)
                temple_layout.addWidget(temple_desc)

                # Add the Temple widget to the layout
                connected_layout.addWidget(temple_widget)

        # Add the Connected group to the layout
        layout.addWidget(connected_group)

        # Add a spacer
        layout.addStretch()

        return tab
