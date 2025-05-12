"""
Purpose: Provides a widget for exploring the integrated Kamea network

This file is part of the tq pillar and serves as a UI component.
It provides a comprehensive visualization of the entire Kamea network,
showing the relationships between Hierophants, Acolytes, and Temples.

Key components:
- IntegratedNetworkExplorer: Class for generating network data
- IntegratedNetworkDialog: Dialog for displaying the visualization

Dependencies:
- PyQt6: For the user interface components
- PyQtWebEngine: For rendering the D3.js visualization
- tq.services.kamea_service: For Kamea-related operations
- tq.services.ternary_dimension_interpreter_new: For Hierophant and Acolyte data

Related files:
- tq/ui/panels/kamea_of_maut_panel.py: Panel that uses this explorer
- tq/services/kamea_service.py: Service for Kamea operations
"""

import json
from typing import Dict, List, Optional

from loguru import logger
from PyQt6.QtCore import Qt

# Try to import WebEngine, but provide a fallback if it's not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
    print(
        "Successfully imported PyQt6.QtWebEngineWidgets in integrated_network_explorer.py"
    )
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    print(
        f"Failed to import PyQt6.QtWebEngineWidgets in integrated_network_explorer.py: {e}"
    )

    # Create a dummy QWebEngineView class for type checking
    class QWebEngineView:
        pass


from PyQt6.QtWidgets import QMainWindow  # Add QMainWindow
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSlider,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from tq.services.ditrune_service import DitruneService
from tq.services.kamea_service import KameaService
from tq.services.ternary_dimension_interpreter_new import (
    ACOLYTES,
    HIEROPHANTS,
    TernaryDimensionInterpreter,
)


class IntegratedNetworkExplorer:
    """Provides a comprehensive visualization of the entire Kamea network."""

    def __init__(self, kamea_service: KameaService):
        """Initialize with the Kamea service.

        Args:
            kamea_service: The Kamea service to use for operations
        """
        self.kamea_service = kamea_service
        self.interpreter = TernaryDimensionInterpreter()
        self.ditrune_service = DitruneService()  # Initialize the ditrune service
        # Cache for network data to improve performance
        self._network_cache = {}

    def generate_network_data(
        self, detail_level: str = "medium", filter_options: Optional[Dict] = None
    ) -> Dict:
        """Generate data for the integrated network visualization.

        Args:
            detail_level: "low" (families only), "medium" (families + hierophants + acolytes),
                         "high" (sample of temples), or "complete" (all 729 ditrunes)
            filter_options: Optional dictionary of filtering options

        Returns:
            Dictionary with nodes and links for the network
        """
        # Check cache first
        cache_key = f"{detail_level}_{json.dumps(filter_options or {})}"
        if cache_key in self._network_cache:
            logger.debug(f"Returning cached network data for {cache_key}")
            return self._network_cache[cache_key]

        logger.debug(f"Generating network data with detail level: {detail_level}")

        # Use filter options or default to empty dict
        filter_options = filter_options or {}

        nodes = []
        links = []
        node_id_map = {}  # Map from (type, family, position, ternary, decimal) to db id

        # Add family nodes (still constructed, as families are not in DB)
        for family_id in range(9):
            hierophant = self._get_hierophant(family_id)
            hierophant_name = (
                self._get_hierophant_name(hierophant)
                if hierophant
                else f"Family {family_id}"
            )
            family_node_id = f"family_{family_id}"
            nodes.append(
                {
                    "id": family_node_id,
                    "name": f"Family {family_id}",
                    "full_name": f"Family {family_id}: {hierophant_name}",
                    "type": "family",
                    "group": self._get_family_group(family_id),
                    "level": 1,
                    "description": self._get_family_description(family_id),
                }
            )
            node_id_map[("family", family_id)] = family_node_id

        # Hierophants from DB
        if detail_level in ["medium", "high", "complete"]:
            for h in self.ditrune_service.get_all_hierophants():
                hid = h["id"]
                nodes.append(
                    {
                        **h,
                        "id": hid,
                        "type": "hierophant",
                        "level": 2,
                        "group": self._get_family_group(h["family"]),
                    }
                )
                node_id_map[("hierophant", h["family"])] = hid
                # Link Hierophant to Family
                links.append(
                    {
                        "source": hid,
                        "target": node_id_map[("family", h["family"])],
                        "value": 2,
                        "type": "hierophant_family",
                    }
                )

            # Acolytes from DB
            for a in self.ditrune_service.get_all_acolytes():
                if a["family"] is None or a["position"] is None:
                    continue
                if (
                    "family" in filter_options
                    and a["family"] != filter_options["family"]
                    and filter_options["family"] != -1
                ):
                    continue
                aid = a["id"]
                nodes.append(
                    {
                        **a,
                        "id": aid,
                        "type": "acolyte",
                        "level": 3,
                        "group": self._get_family_group(a["family"]),
                    }
                )
                node_id_map[("acolyte", a["family"], a["position"])] = aid
                # Link Acolyte to Hierophant
                hiero_id = node_id_map.get(("hierophant", a["family"]))
                if hiero_id:
                    links.append(
                        {
                            "source": aid,
                            "target": hiero_id,
                            "value": 1.5,
                            "type": "acolyte_hierophant",
                        }
                    )

        # Temples from DB (complete mode)
        if detail_level == "complete":
            all_ditrunes = self.ditrune_service.get_all_ditrunes()
            temples_added = 0
            max_temples = filter_options.get("max_temples", 600)
            for d in all_ditrunes:
                if d["type"] != "temple":
                    continue
                if (
                    "family" in filter_options
                    and d["family"] != filter_options["family"]
                    and filter_options["family"] != -1
                ):
                    continue
                if temples_added >= max_temples:
                    continue
                tid = d["id"]
                nodes.append(
                    {
                        **d,
                        "id": tid,
                        "type": "temple",
                        "level": 4,
                        "group": self._get_family_group(d["family"]),
                    }
                )
                # Link Temple to its governing Acolyte(s)
                for acolyte in self.ditrune_service.get_governing_acolytes(
                    d["ternary"]
                ):
                    aid = acolyte["id"]
                    if (
                        "family" in filter_options
                        and acolyte["family"] != filter_options["family"]
                        and filter_options["family"] != -1
                    ):
                        continue
                    links.append(
                        {
                            "source": tid,
                            "target": aid,
                            "value": 1,
                            "type": "temple_acolyte",
                        }
                    )
                # If no governing Acolytes found, link directly to the Hierophant
                if not self.ditrune_service.get_governing_acolytes(d["ternary"]):
                    hiero_id = node_id_map.get(("hierophant", d["family"]))
                    if hiero_id:
                        links.append(
                            {
                                "source": tid,
                                "target": hiero_id,
                                "value": 0.5,
                                "type": "temple_hierophant",
                            }
                        )
                temples_added += 1

        # Add family relationships
        self._add_family_relationships(links)

        # Apply any additional filtering based on filter_options
        if filter_options and "relationship_types" in filter_options:
            allowed_types = filter_options["relationship_types"]
            links = [link for link in links if link["type"] in allowed_types]

        result = {"nodes": nodes, "links": links}

        # --- Validation step: Remove or log links with missing node ids ---
        node_ids = set(n["id"] for n in nodes)
        valid_links = []
        invalid_links = []
        for link in links:
            src = link["source"]
            tgt = link["target"]
            if src in node_ids and tgt in node_ids:
                valid_links.append(link)
            else:
                invalid_links.append(link)
        if invalid_links:
            logger.warning(
                f"Removed {len(invalid_links)} links with missing node ids: {invalid_links[:5]} ..."
            )
        result["links"] = valid_links

        # Only cache if no specific filtering was applied
        if not filter_options:
            self._network_cache[cache_key] = result

        return result

    def search_network(self, query: str, detail_level: str = "complete") -> List[Dict]:
        """Search for nodes matching the query.

        Args:
            query: The search query string
            detail_level: Detail level to search within

        Returns:
            List of matching nodes
        """
        query = query.lower()
        network_data = self.generate_network_data(detail_level)
        results = []

        for node in network_data["nodes"]:
            # Search in name, full_name, ternary, greek, and description
            searchable_text = " ".join(
                [
                    node.get("name", ""),
                    node.get("full_name", ""),
                    node.get("ternary", ""),
                    node.get("greek", ""),
                    node.get("description", ""),
                ]
            ).lower()

            if query in searchable_text:
                results.append(node)

        return results

    def export_network_data(
        self, format_type: str, detail_level: str, filter_options: Optional[Dict] = None
    ) -> Dict:
        """Export the network data in various formats.

        Args:
            format_type: Format to export ("json", "csv", "graphml")
            detail_level: Detail level to export
            filter_options: Optional dictionary of filtering options

        Returns:
            Dict with export data and metadata
        """
        network_data = self.generate_network_data(detail_level, filter_options)

        if format_type == "json":
            return {
                "data": json.dumps(network_data, indent=2),
                "mime_type": "application/json",
                "extension": "json",
            }

        elif format_type == "csv":
            # Generate two CSV files (nodes and edges) and zip them
            nodes_csv = "id,name,type,family,level,group\n"
            for node in network_data["nodes"]:
                nodes_csv += f"{node['id']},{node['name']},{node['type']},{node.get('family', '')},{node['level']},{node['group']}\n"

            links_csv = "source,target,type,value\n"
            for link in network_data["links"]:
                source = (
                    link["source"]
                    if isinstance(link["source"], str)
                    else link["source"]["id"]
                )
                target = (
                    link["target"]
                    if isinstance(link["target"], str)
                    else link["target"]["id"]
                )
                links_csv += f"{source},{target},{link['type']},{link['value']}\n"

            return {
                "nodes": nodes_csv,
                "links": links_csv,
                "mime_type": "text/csv",
                "extension": "csv",
            }

        elif format_type == "graphml":
            # Generate GraphML format (XML-based graph format)
            graphml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
            graphml += (
                '  <key id="name" for="node" attr.name="name" attr.type="string"/>\n'
            )
            graphml += (
                '  <key id="type" for="node" attr.name="type" attr.type="string"/>\n'
            )
            graphml += (
                '  <key id="family" for="node" attr.name="family" attr.type="int"/>\n'
            )
            graphml += (
                '  <key id="level" for="node" attr.name="level" attr.type="int"/>\n'
            )
            graphml += '  <key id="relation_type" for="edge" attr.name="relation_type" attr.type="string"/>\n'
            graphml += '  <graph id="G" edgedefault="directed">\n'

            # Add nodes
            for node in network_data["nodes"]:
                graphml += f'    <node id="{node["id"]}">\n'
                graphml += f'      <data key="name">{node["name"]}</data>\n'
                graphml += f'      <data key="type">{node["type"]}</data>\n'
                if "family" in node:
                    graphml += f'      <data key="family">{node["family"]}</data>\n'
                graphml += f'      <data key="level">{node["level"]}</data>\n'
                graphml += "    </node>\n"

            # Add edges
            edge_id = 0
            for link in network_data["links"]:
                source = (
                    link["source"]
                    if isinstance(link["source"], str)
                    else link["source"]["id"]
                )
                target = (
                    link["target"]
                    if isinstance(link["target"], str)
                    else link["target"]["id"]
                )
                graphml += (
                    f'    <edge id="e{edge_id}" source="{source}" target="{target}">\n'
                )
                graphml += f'      <data key="relation_type">{link["type"]}</data>\n'
                graphml += "    </edge>\n"
                edge_id += 1

            graphml += "  </graph>\n</graphml>"

            return {
                "data": graphml,
                "mime_type": "application/xml",
                "extension": "graphml",
            }

        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def _add_family_relationships(self, links: List[Dict]) -> None:
        """Add relationships between families.

        Args:
            links: The links list to add to
        """
        # Immutable Region (0) connects to all other families
        for family_id in range(1, 9):
            links.append(
                {
                    "source": "family_0",
                    "target": f"family_{family_id}",
                    "value": 1,
                    "type": "central",
                }
            )

        # Pure Conrune Pairs (4 & 8)
        links.append(
            {
                "source": "family_4",
                "target": "family_8",
                "value": 2,
                "type": "conrune",
            }
        )

        # Complementary Regions (5 & 7)
        links.append(
            {
                "source": "family_5",
                "target": "family_7",
                "value": 2,
                "type": "complementary",
            }
        )

        # Bigrammic Quadset (1, 2, 3, 6)
        for i in [1, 2, 3, 6]:
            for j in [1, 2, 3, 6]:
                if i < j:  # Avoid duplicate links
                    links.append(
                        {
                            "source": f"family_{i}",
                            "target": f"family_{j}",
                            "value": 1.5,
                            "type": "quadset",
                        }
                    )

    def _get_family_group(self, family_id: int) -> str:
        """Get the group type for a family.

        Args:
            family_id: The family ID (0-8)

        Returns:
            The family group type
        """
        if family_id == 0:
            return "immutable"
        elif family_id in [4, 8]:
            return "pure_conrune"
        elif family_id in [5, 7]:
            return "complementary"
        else:  # 1, 2, 3, 6
            return "bigrammic"

    def _get_hierophant(self, family_id: int) -> str:
        """Get the Hierophant (Prime Ditrune) for a family.

        Args:
            family_id: The family ID (0-8)

        Returns:
            The Hierophant's ternary value
        """
        return HIEROPHANTS.get(family_id, {}).get("ternary", "")

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

    def _get_family_description(self, family_id: int) -> str:
        """Get the description of a family.

        Args:
            family_id: The family ID (0-8)

        Returns:
            The family's description
        """
        descriptions = {
            0: "The Immutable Region - The Void - Source of all potential",
            1: "The Bigrammic Quadset - The Dynamo - Pure transformative energy",
            2: "The Bigrammic Quadset - The Matrix - Pure structural pattern",
            3: "The Bigrammic Quadset - The Oscillator - Rhythmic movement between states",
            4: "The Pure Conrune Pair - The Enclosure - Structured openness",
            5: "The Complementary Region - The Liberator - Dynamic liberation",
            6: "The Bigrammic Quadset - The Weaver - Perfect alternation of expression and form",
            7: "The Complementary Region - The Foundation - Formed potential",
            8: "The Pure Conrune Pair - The Harmonizer - Structured dynamism",
        }

        return descriptions.get(family_id, f"Family {family_id}")

    def _determine_temple_type(self, ternary_value: str) -> str:
        """Determine the Temple type based on the ternary value.

        Args:
            ternary_value: The Temple's ternary value

        Returns:
            Temple type name
        """
        # Use the first bigram (positions 1 & 6) to determine Temple type
        first_bigram_decimal = int(ternary_value[0]) * 3 + int(ternary_value[5])

        # Temple types from docs/kamea/elemental_analysis_reference.md
        temple_types = [
            "The Nexus",  # 0 - Σύνδεσμος (Syndesmos) - Point of connection and convergence
            "The Crucible",  # 1 - Χωνευτήριον (Choneuterion) - Vessel of transformation
            "The Beacon",  # 2 - Φρυκτωρία (Phryktoria) - Source of illumination
            "The Reservoir",  # 3 - Δεξαμενή (Dexamene) - Container that collects and distributes
            "The Threshold",  # 4 - Κατώφλιον (Katophlion) - Boundary between states
            "The Conduit",  # 5 - Ὀχετός (Ochetos) - Channel that directs and focuses flow
            "The Resonator",  # 6 - Ἠχεῖον (Echeion) - Structure that amplifies and harmonizes
            "The Catalyst",  # 7 - Ἐπιταχυντής (Epitachyntes) - Agent that accelerates processes
            "The Fulcrum",  # 8 - Ὑπομόχλιον (Hypomochlion) - Point of balance and leverage
        ]

        if 0 <= first_bigram_decimal < len(temple_types):
            return temple_types[first_bigram_decimal]

        return "The Nexus"  # Default

    def _determine_element_descriptor(self, ternary_value: str) -> str:
        """Determine the element descriptor based on the ternary value.

        Args:
            ternary_value: The Temple's ternary value

        Returns:
            Element descriptor from docs/kamea/elemental_analysis_reference.md
        """
        # Count elements
        aperture_count = ternary_value.count("0")
        surge_count = ternary_value.count("1")
        lattice_count = ternary_value.count("2")

        # Check for palindromic pattern
        if ternary_value == ternary_value[::-1]:
            return "of Perfect Reflection"  # Palindromic pattern creating mirror-like symmetry

        # Check for ascending pattern (0→1→2)
        if "012" in ternary_value:
            return "of Rising Power"  # Ascending pattern creating evolutionary momentum

        # Check for descending pattern (2→1→0)
        if "210" in ternary_value:
            return "of Deepening Wisdom"  # Descending pattern creating involutionary insight

        # Check for alternating pattern
        if "010" in ternary_value or "121" in ternary_value or "202" in ternary_value:
            return "of Rhythmic Exchange"  # Alternating pattern creating cyclical flow

        # Check for concentrated pattern (3+ of same digit)
        if aperture_count >= 3:
            return "of Open Mystery"  # Dominated by Aperture energy, creating receptive space
        elif surge_count >= 3:
            return "of Flowing Energy"  # Dominated by Surge energy, creating dynamic transformation
        elif lattice_count >= 3:
            return "of Formed Pattern"  # Dominated by Lattice energy, creating stable structure

        # Default to balanced
        return "of Harmonic Balance"  # Balanced elements creating equilibrium and integration

    def _get_governing_acolytes(self, ternary_value: str, family: int) -> List[str]:
        """Get the Acolytes that govern a Temple.

        Args:
            ternary_value: The Temple's ternary value
            family: The family ID (0-8)

        Returns:
            List of Acolyte IDs formatted as "acolyte_{family}_{position}"
        """
        governing_acolytes = []

        # For each Acolyte in the family
        for acolyte_id, acolyte in ACOLYTES.items():
            if acolyte.get("family") == family:
                # For now, use a simple matching rule:
                # If the Temple shares at least 3 digits with the Acolyte, it's governed by it
                acolyte_ternary = acolyte.get("ternary", "")
                if not acolyte_ternary:
                    continue

                matches = sum(
                    1
                    for i in range(min(len(ternary_value), len(acolyte_ternary)))
                    if ternary_value[i] == acolyte_ternary[i]
                )

                if matches >= 3:
                    # The acolyte_id is already in the format "family_position" (e.g., "1_1")
                    # We need to format it as "acolyte_family_position" to match node IDs
                    formatted_acolyte_id = f"acolyte_{acolyte_id}"
                    governing_acolytes.append(formatted_acolyte_id)

        return governing_acolytes

    def create_d3_visualization(self, network_data: Dict) -> str:
        """Create D3.js HTML for the network visualization.

        Args:
            network_data: Dictionary with nodes and links

        Returns:
            HTML string with the D3.js visualization
        """
        # Convert network data to JSON
        network_data_json = json.dumps(network_data)

        # Load the HTML template from file
        import os

        template_path = os.path.join(os.path.dirname(__file__), "network_template.html")

        try:
            with open(template_path, "r") as f:
                html_template = f.read()

            # Replace the placeholder with the actual network data
            html_template = html_template.replace(
                "NETWORK_DATA_PLACEHOLDER", network_data_json
            )
            return html_template
        except Exception as e:
            logger.error(f"Error loading network template: {e}")
            # Fallback to a simple HTML template
            html_template = (
                """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Integrated Kamea Network</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { margin: 0; font-family: Arial, sans-serif; background-color: #f9f9f9; }
                svg { background-color: #ffffff; border: 1px solid #ddd; border-radius: 5px; }

                /* Links */
                .links line {
                    stroke-opacity: 0.6;
                    transition: stroke-opacity 0.3s, stroke-width 0.3s;
                }
                .links line:hover {
                    stroke-opacity: 1.0;
                    stroke-width: 3px;
                }

                /* Nodes */
                .nodes circle {
                    stroke: #fff;
                    stroke-width: 1.5px;
                    transition: r 0.3s, stroke-width 0.3s;
                    cursor: pointer;
                }
                .nodes circle:hover {
                    stroke-width: 3px;
                    r: 1.5em !important;
                }

                /* Labels */
                .node-label {
                    font-size: 10px;
                    pointer-events: none;
                    font-weight: bold;
                    text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 3px #fff;
                }

                /* Family groups */
                .immutable { fill: #1f77b4; }
                .pure_conrune { fill: #ff7f0e; }
                .complementary { fill: #2ca02c; }
                .bigrammic { fill: #d62728; }

                /* Node types */
                .family { stroke-width: 3px; }
                .hierophant { stroke-width: 2px; }
                .acolyte { stroke-width: 1.5px; opacity: 0.9; }
                .temple { stroke-width: 1px; opacity: 0.7; }

                /* Link types */
                .central { stroke: #aaa; }
                .conrune { stroke: #ff7f0e; stroke-width: 3px; }
                .complementary { stroke: #2ca02c; stroke-width: 3px; }
                .quadset { stroke: #d62728; }
                .hierophant_family { stroke: #9467bd; stroke-width: 2px; }
                .acolyte_hierophant { stroke: #8c564b; }
                .temple_acolyte { stroke: #e377c2; stroke-width: 1px; }
                .temple_hierophant { stroke: #7f7f7f; stroke-width: 0.5px; stroke-dasharray: 3,3; }

                /* Tooltip */
                .tooltip {
                    position: absolute;
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 12px;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.3s;
                    max-width: 300px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .tooltip h4 {
                    margin: 0 0 5px 0;
                    font-size: 14px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                .tooltip p {
                    margin: 3px 0;
                }
                .tooltip .ternary {
                    font-family: monospace;
                    background-color: #f0f0f0;
                    padding: 2px 4px;
                    border-radius: 3px;
                }

                /* Legend */
                .legend {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 12px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .legend h3 {
                    margin: 0 0 5px 0;
                    font-size: 14px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin: 5px 0;
                }
                .legend-color {
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    margin-right: 5px;
                    border: 1px solid #fff;
                }
                .legend-label {
                    flex: 1;
                }
            </style>
        </head>
        <body>
            <svg width="1000" height="800"></svg>
            <div class="tooltip"></div>
            <div class="legend">
                <h3>Kamea Network Legend</h3>
                <div class="legend-section">
                    <h4>Family Groups</h4>
                    <div class="legend-item">
                        <div class="legend-color immutable"></div>
                        <div class="legend-label">Immutable Region</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color pure_conrune"></div>
                        <div class="legend-label">Pure Conrune Pair</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color complementary"></div>
                        <div class="legend-label">Complementary Region</div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color bigrammic"></div>
                        <div class="legend-label">Bigrammic Quadset</div>
                    </div>
                </div>
                <div class="legend-section">
                    <h4>Node Types</h4>
                    <div class="legend-item">
                        <svg width="20" height="20">
                            <circle cx="10" cy="10" r="10" class="family immutable"></circle>
                        </svg>
                        <div class="legend-label">Family</div>
                    </div>
                    <div class="legend-item">
                        <svg width="20" height="20">
                            <circle cx="10" cy="10" r="6" class="hierophant immutable"></circle>
                        </svg>
                        <div class="legend-label">Hierophant</div>
                    </div>
                    <div class="legend-item">
                        <svg width="20" height="20">
                            <circle cx="10" cy="10" r="4" class="acolyte immutable"></circle>
                        </svg>
                        <div class="legend-label">Acolyte</div>
                    </div>
                    <div class="legend-item">
                        <svg width="20" height="20">
                            <circle cx="10" cy="10" r="2" class="temple immutable"></circle>
                        </svg>
                        <div class="legend-label">Temple</div>
                    </div>
                </div>
            </div>
            <script>
            // Network data
            const data = %s;

            // Create the force simulation
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(function(d) { return d.id; }).distance(function(d) {
                    // Adjust link distance based on node types
                    if (d.type === "hierophant_family") return 60;
                    if (d.type === "acolyte_hierophant") return 100;
                    if (d.type === "temple_acolyte") return 40;
                    if (d.type === "temple_hierophant") return 80;
                    if (d.type === "central") return 150;
                    if (d.type === "conrune") return 120;
                    if (d.type === "complementary") return 120;
                    if (d.type === "quadset") return 130;
                    return 100;  // Default
                }))
                .force("charge", d3.forceManyBody().strength(function(d) {
                    // Adjust repulsion force based on node type
                    if (d.type === "family") return -800;
                    if (d.type === "hierophant") return -400;
                    if (d.type === "acolyte") return -200;
                    return -80;  // Temples
                }))
                .force("center", d3.forceCenter(500, 400))
                .force("x", d3.forceX().strength(0.05))
                .force("y", d3.forceY().strength(0.05))
                .force("collision", d3.forceCollide().radius(function(d) {
                    // Adjust collision radius based on node type
                    if (d.type === "family") return 30;
                    if (d.type === "hierophant") return 20;
                    if (d.type === "acolyte") return 12;
                    return 6;  // Temples
                }));

            // Get the SVG element
            const svg = d3.select("svg");

            // Create a tooltip
            const tooltip = d3.select(".tooltip");

            // Create the links
            const link = svg.append("g")
                .selectAll("line")
                .data(data.links)
                .enter().append("line")
                .attr("class", function(d) { return "links " + d.type; })
                .attr("stroke-width", function(d) { return Math.sqrt(d.value) * 1.5; });

            // Create the nodes
            const node = svg.append("g")
                .selectAll("circle")
                .data(data.nodes)
                .enter().append("circle")
                .attr("class", function(d) { return "nodes " + d.group + " " + d.type; })
                .attr("r", function(d) {
                    // Adjust radius based on node type
                    if (d.type === "family") return 20;
                    if (d.type === "hierophant") return 12;
                    if (d.type === "acolyte") return 8;
                    return 4;  // Temples
                })
                .on("mouseover", function(event, d) {
                    // Highlight connected links and nodes
                    highlightConnections(d);

                    // Show tooltip
                    tooltip.style("opacity", 1)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 10) + "px");

                    // Set tooltip content based on node type
                    let content = "";
                    if (d.type === "family") {
                        content = \`
                            <h4>\${d.full_name}</h4>
                            <p>\${d.description}</p>
                        \`;
                    } else if (d.type === "hierophant") {
                        content = \`
                            <h4>Hierophant: \${d.name}</h4>
                            <p>Greek: \${d.greek}</p>
                            <p>Ternary: <span class="ternary">\${d.ternary}</span></p>
                            <p>Family: \${d.family}</p>
                            <p>\${d.description}</p>
                        \`;
                    } else if (d.type === "acolyte") {
                        content = \`
                            <h4>Acolyte: \${d.name}</h4>
                            <p>Greek: \${d.greek}</p>
                            <p>Ternary: <span class="ternary">\${d.ternary}</span></p>
                            <p>Family: \${d.family}</p>
                            <p>Function: \${d.function}</p>
                        \`;
                    } else { // Temple
                        content = \`
                            <h4>Temple: \${d.name}</h4>
                            <p>Ternary: <span class="ternary">\${d.ternary}</span></p>
                            <p>Position: \${d.position}</p>
                            <p>Kamea Locator: \${d.kamea_locator}</p>
                            <p>Family: \${d.family}</p>
                        \`;
                    }
                    tooltip.html(content);
                })
                .on("mouseout", function(event, d) {
                    // Remove highlighting
                    resetHighlighting();

                    // Hide tooltip
                    tooltip.style("opacity", 0);
                })
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            // Add labels to the nodes
            const label = svg.append("g")
                .selectAll("text")
                .data(data.nodes)
                .enter().append("text")
                .attr("class", "node-label")
                .attr("text-anchor", "middle")
                .attr("dy", function(d) {
                    // Adjust label position based on node type
                    if (d.type === "family") return -25;
                    if (d.type === "hierophant") return -15;
                    return -10;  // Acolytes and Temples
                })
                .text(function(d) {
                    // Only show labels for families and hierophants by default
                    if (d.type === "family" || d.type === "hierophant") {
                        return d.name;
                    }
                    return "";  // No labels for acolytes and temples by default
                });

            // Function to highlight connected nodes and links
            function highlightConnections(d) {
                // Reduce opacity of all nodes and links
                node.style("opacity", 0.2);
                link.style("opacity", 0.1);

                // Highlight the selected node
                d3.select(this).style("opacity", 1);

                // Find connected nodes and links
                const connectedNodeIds = new Set();
                connectedNodeIds.add(d.id);

                // Find directly connected nodes
                data.links.forEach(function(l) {
                    if (l.source.id === d.id || l.target.id === d.id) {
                        connectedNodeIds.add(l.source.id);
                        connectedNodeIds.add(l.target.id);
                    }
                });

                // Highlight connected nodes
                node.filter(function(n) { return connectedNodeIds.has(n.id); })
                    .style("opacity", 1);

                // Highlight connected links
                link.filter(function(l) { return connectedNodeIds.has(l.source.id) && connectedNodeIds.has(l.target.id); })
                    .style("opacity", 1);
            }

            // Function to reset highlighting
            function resetHighlighting() {
                node.style("opacity", function(d) {
                    if (d.type === "temple") return 0.7;
                    if (d.type === "acolyte") return 0.9;
                    return 1;
                });
                link.style("opacity", 0.6);
            }

            // Update positions on each tick
            simulation.on("tick", function() {
                link
                    .attr("x1", function(d) { return d.source.x; })
                    .attr("y1", function(d) { return d.source.y; })
                    .attr("x2", function(d) { return d.target.x; })
                    .attr("y2", function(d) { return d.target.y; });

                node
                    .attr("cx", function(d) { return d.x; })
                    .attr("cy", function(d) { return d.y; });

                label
                    .attr("x", function(d) { return d.x; })
                    .attr("y", function(d) { return d.y; });
            });

            // Drag functions
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }

            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }

            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }

            // Function to toggle node labels
            window.toggleLabels = function(nodeType, show) {
                label.filter(function(d) { return d.type === nodeType; })
                    .text(function(d) { return show ? d.name : ""; });
            }

            // Function to filter nodes by family
            window.filterByFamily = function(familyId, show) {
                // If familyId is -1, show/hide all families
                if (familyId === -1) {
                    node.style("display", show ? "block" : "none");
                    link.style("display", show ? "block" : "none");
                    label.style("display", show ? "block" : "none");
                    return;
                }

                // Otherwise, filter by the specific family
                node.filter(function(d) { return d.family === familyId; })
                    .style("display", show ? "block" : "none");

                // Also filter labels
                label.filter(function(d) { return d.family === familyId; })
                    .style("display", show ? "block" : "none");

                // Also filter links connected to this family
                link.filter(function(d) {
                    const sourceFamily = typeof d.source === 'object' ? d.source.family : null;
                    const targetFamily = typeof d.target === 'object' ? d.target.family : null;
                    return sourceFamily === familyId || targetFamily === familyId;
                })
                .style("display", show ? "block" : "none");
            }
            </script>
        </body>
        </html>
        """
                % network_data_json
            )

        return html_template


class IntegratedNetworkDialog(QMainWindow):
    """Window for displaying the Integrated Network visualization (now a QMainWindow)."""

    def __init__(self, parent, kamea_service: KameaService):
        super().__init__(parent)
        self.kamea_service = kamea_service
        self.explorer = IntegratedNetworkExplorer(self.kamea_service)
        self.setWindowTitle("Integrated Kamea Network Explorer")
        self.resize(1200, 900)
        # Ensure window is always on top and gets focus
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.show()
        self.raise_()
        self.activateWindow()

        # Central widget setup
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        # Splitter for sidebar and visualization
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        # Sidebar: tab widget for controls
        self.sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumWidth(340)
        self.visualization_tab = self._create_visualization_tab()
        self.advanced_filters_tab = self._create_advanced_filters_tab()
        self.search_tab = self._create_search_tab()
        self.export_tab = self._create_export_tab()
        self.tab_widget.addTab(self.visualization_tab, "Visualization")
        self.tab_widget.addTab(self.advanced_filters_tab, "Advanced Filters")
        self.tab_widget.addTab(self.search_tab, "Search")
        self.tab_widget.addTab(self.export_tab, "Export")
        sidebar_layout.addWidget(self.tab_widget)
        self.sidebar_widget.setMaximumWidth(360)
        self.splitter.addWidget(self.sidebar_widget)
        # Central area: visualization
        self.central_widget = QWidget()
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_level = "medium"
        self.filter_options = {}
        self.network_data = self.explorer.generate_network_data(self.detail_level)
        self.html = self.explorer.create_d3_visualization(self.network_data)
        if WEBENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setHtml(self.html)
            central_layout.addWidget(self.web_view, 1)
        else:
            fallback_label = QLabel(
                "The D3.js visualization requires PyQt6.QtWebEngineWidgets, which is not installed.\n"
                "Please install it with: pip install PyQtWebEngine"
            )
            fallback_label.setWordWrap(True)
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            central_layout.addWidget(fallback_label)
            text_representation = QLabel(
                "Integrated Network Structure:\n\n"
                "Level 1: Nine Families\n"
                "- Family 0 (The Void) connects to all other families\n"
                "- Families 4 & 8 form a Pure Conrune Pair\n"
                "- Families 5 & 7 form a Complementary Region\n"
                "- Families 1, 2, 3, 6 form a Bigrammic Quadset\n\n"
                "Level 2: Nine Hierophants (Prime Ditrunes)\n"
                "- Each Hierophant is connected to its Family\n\n"
                "Level 3: 72 Acolytes (Composite Ditrunes)\n"
                "- Each Acolyte is connected to its Hierophant\n\n"
                "Level 4: 648 Temples (Concurrent Ditrunes)\n"
                "- Each Temple is connected to its governing Acolyte(s)"
            )
            text_representation.setWordWrap(True)
            text_representation.setAlignment(Qt.AlignmentFlag.AlignLeft)
            central_layout.addWidget(text_representation, 1)
        self.status_bar = QLabel("")
        self.status_bar.setStyleSheet(
            "background-color: #f0f0f0; padding: 3px; border-radius: 3px;"
        )
        central_layout.addWidget(self.status_bar)
        # Controls below visualization (refresh, fullscreen, help, close)
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh View")
        self.refresh_button.clicked.connect(self._refresh_view)
        button_layout.addWidget(self.refresh_button)
        self.fullscreen_button = QPushButton("Toggle Fullscreen")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)
        button_layout.addWidget(self.fullscreen_button)
        button_layout.addStretch()
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self._show_help)
        button_layout.addWidget(self.help_button)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)  # Use close() for QMainWindow
        button_layout.addWidget(self.close_button)
        central_layout.addLayout(button_layout)
        self.splitter.addWidget(self.central_widget)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        # Hide sidebar by default
        self.sidebar_widget.setVisible(False)
        self.splitter.handle(1).setEnabled(False)
        # Toggle sidebar button (floating at top left)
        self.toggle_sidebar_btn = QPushButton("☰ Controls")
        self.toggle_sidebar_btn.setFixedWidth(100)
        self.toggle_sidebar_btn.setStyleSheet(
            "position: absolute; left: 10px; top: 10px;"
        )
        self.toggle_sidebar_btn.raise_()
        self.toggle_sidebar_btn.clicked.connect(self._toggle_sidebar)
        # Add everything to main layout
        main_layout.addWidget(self.toggle_sidebar_btn, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.splitter, 1)
        # Set the central widget for QMainWindow
        self.setCentralWidget(central_widget)

    def _toggle_sidebar(self):
        visible = self.sidebar_widget.isVisible()
        self.sidebar_widget.setVisible(not visible)
        # Optionally, enable/disable splitter handle
        self.splitter.handle(1).setEnabled(not visible)

    def _create_visualization_tab(self) -> QWidget:
        """Create the visualization tab.

        Returns:
            The visualization tab widget
        """
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Basic visualization controls
        basic_controls = QGroupBox("Detail Level")
        basic_layout = QVBoxLayout(basic_controls)

        self.detail_combo = QComboBox()
        self.detail_combo.addItem("Low (Families Only)", "low")
        self.detail_combo.addItem(
            "Medium (Families + Hierophants + Acolytes)", "medium"
        )
        self.detail_combo.addItem("High (Sample of Temples)", "high")
        self.detail_combo.addItem("Complete (All 729 Ditrunes)", "complete")
        self.detail_combo.setCurrentIndex(1)  # Medium by default
        self.detail_combo.currentIndexChanged.connect(self._on_detail_level_changed)

        # Add a warning label for complete mode
        self.complete_warning = QLabel(
            "Note: Complete mode may be slow to load and navigate."
        )
        self.complete_warning.setStyleSheet("color: #e74c3c;")  # Red warning text
        self.complete_warning.setVisible(False)

        basic_layout.addWidget(self.detail_combo)
        basic_layout.addWidget(self.complete_warning)

        # Add performance tips
        tips_label = QLabel(
            "Tip: For better performance, use Medium detail level and filter by family."
        )
        tips_label.setWordWrap(True)
        basic_layout.addWidget(tips_label)

        # Label visibility control
        label_group = QGroupBox("Show Labels")
        label_layout = QVBoxLayout(label_group)

        self.family_labels_check = QCheckBox("Families")
        self.family_labels_check.setChecked(True)
        self.family_labels_check.stateChanged.connect(
            lambda state: self._toggle_labels("family", state == Qt.CheckState.Checked)
        )

        self.hierophant_labels_check = QCheckBox("Hierophants")
        self.hierophant_labels_check.setChecked(True)
        self.hierophant_labels_check.stateChanged.connect(
            lambda state: self._toggle_labels(
                "hierophant", state == Qt.CheckState.Checked
            )
        )

        self.acolyte_labels_check = QCheckBox("Acolytes")
        self.acolyte_labels_check.setChecked(False)
        self.acolyte_labels_check.stateChanged.connect(
            lambda state: self._toggle_labels("acolyte", state == Qt.CheckState.Checked)
        )

        self.temple_labels_check = QCheckBox("Temples")
        self.temple_labels_check.setChecked(False)
        self.temple_labels_check.stateChanged.connect(
            lambda state: self._toggle_labels("temple", state == Qt.CheckState.Checked)
        )

        label_layout.addWidget(self.family_labels_check)
        label_layout.addWidget(self.hierophant_labels_check)
        label_layout.addWidget(self.acolyte_labels_check)
        label_layout.addWidget(self.temple_labels_check)

        # Family filter control
        filter_group = QGroupBox("Filter by Family")
        filter_layout = QVBoxLayout(filter_group)

        self.family_combo = QComboBox()
        self.family_combo.addItem("All Families", -1)
        for i in range(9):
            self.family_combo.addItem(f"Family {i}", i)

        self.family_combo.currentIndexChanged.connect(self._on_family_filter_changed)

        filter_layout.addWidget(self.family_combo)

        # Add description of currently selected family
        self.family_description = QLabel("")
        self.family_description.setWordWrap(True)
        self.family_description.setMinimumHeight(100)
        filter_layout.addWidget(self.family_description)

        # Add groups to panel
        layout.addWidget(basic_controls)
        layout.addWidget(label_group)
        layout.addWidget(filter_group)

        return tab

    def _create_advanced_filters_tab(self) -> QWidget:
        """Create the advanced filters tab.

        Returns:
            The advanced filters tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Relationship type filters
        relationship_group = QGroupBox("Relationship Types")
        relationship_layout = QVBoxLayout(relationship_group)

        self.relationship_checkboxes = {}
        relationship_types = [
            ("central", "Central Connections (Family 0 to Others)"),
            ("conrune", "Conrune Pair Connections (Families 4 & 8)"),
            ("complementary", "Complementary Region Connections (Families 5 & 7)"),
            ("quadset", "Bigrammic Quadset Connections (1, 2, 3, 6)"),
            ("hierophant_family", "Hierophant to Family"),
            ("acolyte_hierophant", "Acolyte to Hierophant"),
            ("temple_acolyte", "Temple to Acolyte"),
            ("temple_hierophant", "Temple to Hierophant"),
        ]

        for rel_type, label in relationship_types:
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._update_relationship_filters)
            self.relationship_checkboxes[rel_type] = checkbox
            relationship_layout.addWidget(checkbox)

        # Element pattern filters
        pattern_group = QGroupBox("Element Patterns")
        pattern_layout = QVBoxLayout(pattern_group)

        self.pattern_checkboxes = {}
        pattern_types = [
            ("reflection", "Perfect Reflection (Palindromic)"),
            ("rising", "Rising Power (0→1→2)"),
            ("deepening", "Deepening Wisdom (2→1→0)"),
            ("rhythmic", "Rhythmic Exchange (Alternating)"),
            ("aperture", "Open Mystery (3+ Aperture/0)"),
            ("surge", "Flowing Energy (3+ Surge/1)"),
            ("lattice", "Formed Pattern (3+ Lattice/2)"),
        ]

        for pattern_type, label in pattern_types:
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self._update_element_filters)
            self.pattern_checkboxes[pattern_type] = checkbox
            pattern_layout.addWidget(checkbox)

        # Temple count slider
        temple_group = QGroupBox("Temple Count (High/Complete Detail Only)")
        temple_layout = QVBoxLayout(temple_group)

        self.temple_count_slider = QSlider(Qt.Orientation.Horizontal)
        self.temple_count_slider.setMinimum(50)
        self.temple_count_slider.setMaximum(600)
        self.temple_count_slider.setValue(150)
        self.temple_count_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temple_count_slider.setTickInterval(50)

        self.temple_count_label = QLabel(
            f"Max Temples: {self.temple_count_slider.value()}"
        )

        self.temple_count_slider.valueChanged.connect(
            lambda v: self.temple_count_label.setText(f"Max Temples: {v}")
        )

        temple_layout.addWidget(self.temple_count_label)
        temple_layout.addWidget(self.temple_count_slider)

        # Apply filters button
        self.apply_filters_button = QPushButton("Apply Filters")
        self.apply_filters_button.clicked.connect(self._apply_advanced_filters)

        # Reset filters button
        self.reset_filters_button = QPushButton("Reset Filters")
        self.reset_filters_button.clicked.connect(self._reset_advanced_filters)

        # Add button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.apply_filters_button)
        button_layout.addWidget(self.reset_filters_button)

        # Add all components to the layout
        layout.addWidget(relationship_group)
        layout.addWidget(pattern_group)
        layout.addWidget(temple_group)
        layout.addLayout(button_layout)

        return tab

    def _create_search_tab(self) -> QWidget:
        """Create the search tab.

        Returns:
            The search tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Search controls
        search_group = QGroupBox("Search Network")
        search_layout = QVBoxLayout(search_group)

        search_input_layout = QHBoxLayout()
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setMinimumWidth(300)
        self.search_input.setPlaceholderText(
            "Enter search term (name, ternary value, description)"
        )

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self._perform_search)

        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)

        # Search scope
        scope_layout = QHBoxLayout()
        scope_label = QLabel("Search in:")

        self.search_families = QCheckBox("Families")
        self.search_families.setChecked(True)

        self.search_hierophants = QCheckBox("Hierophants")
        self.search_hierophants.setChecked(True)

        self.search_acolytes = QCheckBox("Acolytes")
        self.search_acolytes.setChecked(True)

        self.search_temples = QCheckBox("Temples")
        self.search_temples.setChecked(False)

        scope_layout.addWidget(scope_label)
        scope_layout.addWidget(self.search_families)
        scope_layout.addWidget(self.search_hierophants)
        scope_layout.addWidget(self.search_acolytes)
        scope_layout.addWidget(self.search_temples)
        scope_layout.addStretch()

        # Results area
        self.search_results = QListWidget()
        self.search_results.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.search_results.itemSelectionChanged.connect(
            self._on_search_result_selected
        )

        search_layout.addLayout(search_input_layout)
        search_layout.addLayout(scope_layout)
        search_layout.addWidget(QLabel("Search Results:"))
        search_layout.addWidget(self.search_results)

        # Result details
        details_group = QGroupBox("Details")
        details_layout = QVBoxLayout(details_group)

        self.result_details = QLabel("Select a search result to view details")
        self.result_details.setWordWrap(True)
        self.result_details.setMinimumHeight(150)
        self.result_details.setStyleSheet(
            "background-color: #f8f8f8; padding: 10px; border-radius: 5px;"
        )

        details_layout.addWidget(self.result_details)

        # Focus button
        self.focus_button = QPushButton("Focus on Selected Node")
        self.focus_button.clicked.connect(self._focus_on_selected_node)
        self.focus_button.setEnabled(False)
        details_layout.addWidget(self.focus_button)

        # Add to layout
        layout.addWidget(search_group, 2)
        layout.addWidget(details_group, 1)

        return tab

    def _create_export_tab(self) -> QWidget:
        """Create the export tab.

        Returns:
            The export tab widget
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)

        self.export_format = QComboBox()
        self.export_format.addItem("JSON Format", "json")
        self.export_format.addItem("CSV Format", "csv")
        self.export_format.addItem("GraphML Format", "graphml")

        format_description = QLabel(
            "JSON: Complete network structure with all attributes\n"
            "CSV: Two files (nodes.csv and links.csv) with basic attributes\n"
            "GraphML: XML-based format for graph visualization tools"
        )
        format_description.setWordWrap(True)

        format_layout.addWidget(self.export_format)
        format_layout.addWidget(format_description)

        # Export scope
        scope_group = QGroupBox("Export Scope")
        scope_layout = QVBoxLayout(scope_group)

        self.export_detail_level = QComboBox()
        self.export_detail_level.addItem("Current View (as displayed)", "current")
        self.export_detail_level.addItem("Low (Families Only)", "low")
        self.export_detail_level.addItem(
            "Medium (Families + Hierophants + Acolytes)", "medium"
        )
        self.export_detail_level.addItem("High (Sample of Temples)", "high")
        self.export_detail_level.addItem("Complete (All 729 Ditrunes)", "complete")

        scope_layout.addWidget(QLabel("Detail Level:"))
        scope_layout.addWidget(self.export_detail_level)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.export_include_descriptions = QCheckBox("Include Full Descriptions")
        self.export_include_descriptions.setChecked(True)

        self.export_include_coordinates = QCheckBox(
            "Include Coordinates (if available)"
        )
        self.export_include_coordinates.setChecked(True)

        self.export_include_kamea_locators = QCheckBox("Include Kamea Locators")
        self.export_include_kamea_locators.setChecked(True)

        options_layout.addWidget(self.export_include_descriptions)
        options_layout.addWidget(self.export_include_coordinates)
        options_layout.addWidget(self.export_include_kamea_locators)

        # Export button
        self.export_button = QPushButton("Export Network Data")
        self.export_button.clicked.connect(self._export_network_data)

        # Add all components to the layout
        layout.addWidget(format_group)
        layout.addWidget(scope_group)
        layout.addWidget(options_group)
        layout.addStretch()
        layout.addWidget(self.export_button)

        return tab

    def _refresh_view(self) -> None:
        """Refresh the network visualization with current settings."""
        # Get the current detail level
        detail_level = self.detail_combo.currentData()

        # Build filter options
        filter_options = self.filter_options.copy()
        filter_options["family"] = self.family_combo.currentData()
        filter_options["max_temples"] = self.temple_count_slider.value()

        # Update network data
        self.network_data = self.explorer.generate_network_data(
            detail_level, filter_options
        )

        # Update visualization
        self.html = self.explorer.create_d3_visualization(self.network_data)

        # Update the web view if available
        if WEBENGINE_AVAILABLE and hasattr(self, "web_view"):
            self.web_view.setHtml(self.html)

        # Update status
        node_count = len(self.network_data["nodes"])
        link_count = len(self.network_data["links"])
        self.status_bar.setText(
            f"Network loaded with {node_count} nodes and {link_count} links"
        )

        # Apply label toggles
        self._toggle_labels("family", self.family_labels_check.isChecked())
        self._toggle_labels("hierophant", self.hierophant_labels_check.isChecked())
        self._toggle_labels("acolyte", self.acolyte_labels_check.isChecked())
        self._toggle_labels("temple", self.temple_labels_check.isChecked())

    def _on_detail_level_changed(self, _: int) -> None:
        """Handle detail level change.

        Args:
            _: The index of the selected item (unused)
        """
        # Get the new detail level
        self.detail_level = self.detail_combo.currentData()

        # Show/hide the complete mode warning
        self.complete_warning.setVisible(self.detail_level == "complete")

        # Update checkboxes based on detail level
        if self.detail_level == "low":
            self.hierophant_labels_check.setEnabled(False)
            self.acolyte_labels_check.setEnabled(False)
            self.temple_labels_check.setEnabled(False)
        elif self.detail_level == "medium":
            self.hierophant_labels_check.setEnabled(True)
            self.acolyte_labels_check.setEnabled(True)
            self.temple_labels_check.setEnabled(False)
        else:  # high or complete
            self.hierophant_labels_check.setEnabled(True)
            self.acolyte_labels_check.setEnabled(True)
            self.temple_labels_check.setEnabled(True)

            # For complete mode, uncheck temple labels by default to avoid visual clutter
            if self.detail_level == "complete" and self.temple_labels_check.isChecked():
                self.temple_labels_check.setChecked(False)

        # Refresh the view
        self._refresh_view()

    def _toggle_labels(self, node_type: str, show: bool) -> None:
        """Toggle labels for a specific node type.

        Args:
            node_type: The type of node ("family", "hierophant", "acolyte", "temple")
            show: Whether to show the labels
        """
        # Call the JavaScript function to toggle labels if WebEngine is available
        if WEBENGINE_AVAILABLE and hasattr(self, "web_view"):
            self.web_view.page().runJavaScript(
                f"toggleLabels('{node_type}', {str(show).lower()});"
            )

    def _on_family_filter_changed(self, index: int) -> None:
        """Handle family filter change.

        Args:
            index: The index of the selected item
        """
        # Get the selected family ID
        family_id = self.family_combo.currentData()

        # Update the description for the selected family
        if family_id != -1:
            family_description = self.explorer._get_family_description(family_id)
            self.family_description.setText(family_description)
        else:
            self.family_description.setText("All families selected")

        # Update filter options and refresh the view
        self.filter_options["family"] = family_id
        self._refresh_view()

    def _update_relationship_filters(self) -> None:
        """Update relationship filters based on checkbox states."""
        # This just keeps track of checkbox states but doesn't apply them yet
        pass

    def _update_element_filters(self) -> None:
        """Update element pattern filters based on checkbox states."""
        # This just keeps track of checkbox states but doesn't apply them yet
        pass

    def _apply_advanced_filters(self) -> None:
        """Apply all advanced filters."""
        # Get selected relationship types
        relationship_types = [
            rel_type
            for rel_type, checkbox in self.relationship_checkboxes.items()
            if checkbox.isChecked()
        ]

        # Get selected element patterns
        element_patterns = [
            pattern
            for pattern, checkbox in self.pattern_checkboxes.items()
            if checkbox.isChecked()
        ]

        # Update filter options
        self.filter_options["relationship_types"] = relationship_types
        self.filter_options["element_patterns"] = element_patterns
        self.filter_options["max_temples"] = self.temple_count_slider.value()

        # Refresh the view
        self._refresh_view()

    def _reset_advanced_filters(self) -> None:
        """Reset all advanced filters to defaults."""
        # Reset relationship checkboxes
        for checkbox in self.relationship_checkboxes.values():
            checkbox.setChecked(True)

        # Reset pattern checkboxes
        for checkbox in self.pattern_checkboxes.values():
            checkbox.setChecked(True)

        # Reset temple count slider
        self.temple_count_slider.setValue(150)

        # Clear filter options
        self.filter_options = {}

        # Refresh the view
        self._refresh_view()

    def _perform_search(self) -> None:
        """Perform a search in the network."""
        # Get the search query
        query = self.search_input.currentText().strip()

        if not query:
            return

        # Add query to search history if not already present
        if self.search_input.findText(query) == -1:
            self.search_input.addItem(query)

        # Determine search scope based on checkboxes
        search_types = []
        if self.search_families.isChecked():
            search_types.append("family")
        if self.search_hierophants.isChecked():
            search_types.append("hierophant")
        if self.search_acolytes.isChecked():
            search_types.append("acolyte")
        if self.search_temples.isChecked():
            search_types.append("temple")

        # Perform the search
        results = self.explorer.search_network(query, "complete")

        # Filter results by type
        results = [r for r in results if r["type"] in search_types]

        # Show results
        self.search_results.clear()

        if not results:
            self.search_results.addItem("No results found")
            self.result_details.setText("No matching nodes found.")
            self.focus_button.setEnabled(False)
            return

        # Add results to the list
        for result in results:
            item = QListWidgetItem(f"{result['name']} ({result['type']})")
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.search_results.addItem(item)

        self.status_bar.setText(f"Search found {len(results)} matching nodes")

    def _on_search_result_selected(self) -> None:
        """Handle selection of a search result."""
        items = self.search_results.selectedItems()
        if not items:
            self.result_details.setText("Select a search result to view details")
            self.focus_button.setEnabled(False)
            return

        # Get the selected result data
        result = items[0].data(Qt.ItemDataRole.UserRole)

        if isinstance(result, dict):
            # Format details based on node type
            if result["type"] == "family":
                details = (
                    f"<b>{result.get('full_name', result['name'])}</b><br>"
                    f"<b>Type:</b> Family<br>"
                    f"<b>Group:</b> {result.get('group', '')}<br>"
                    f"<b>Description:</b> {result.get('description', '')}"
                )
            elif result["type"] == "hierophant":
                details = (
                    f"<b>{result.get('full_name', result['name'])}</b><br>"
                    f"<b>Type:</b> Hierophant (Prime Ditrune)<br>"
                    f"<b>Ternary:</b> {result.get('ternary', '')}<br>"
                    f"<b>Greek:</b> {result.get('greek', '')}<br>"
                    f"<b>Family:</b> {result.get('family', '')}<br>"
                    f"<b>Description:</b> {result.get('description', '')}"
                )
            elif result["type"] == "acolyte":
                details = (
                    f"<b>{result.get('full_name', result['name'])}</b><br>"
                    f"<b>Type:</b> Acolyte (Composite Ditrune)<br>"
                    f"<b>Ternary:</b> {result.get('ternary', '')}<br>"
                    f"<b>Greek:</b> {result.get('greek', '')}<br>"
                    f"<b>Family:</b> {result.get('family', '')}<br>"
                    f"<b>Position:</b> {result.get('position', '')}<br>"
                    f"<b>Description:</b> {result.get('description', '')}"
                )
            else:  # temple
                details = (
                    f"<b>{result.get('full_name', result['name'])}</b><br>"
                    f"<b>Type:</b> Temple (Concurrent Ditrune)<br>"
                    f"<b>Ternary:</b> {result.get('ternary', '')}<br>"
                    f"<b>Kamea Locator:</b> {result.get('kamea_locator', '')}<br>"
                    f"<b>Family:</b> {result.get('family', '')}<br>"
                    f"<b>Position:</b> {result.get('position', '')}"
                )

            self.result_details.setText(details)
            self.focus_button.setEnabled(True)
        else:
            self.result_details.setText("No details available for this result")
            self.focus_button.setEnabled(False)

    def _focus_on_selected_node(self) -> None:
        """Focus on the selected search result node in the visualization."""
        items = self.search_results.selectedItems()
        if not items:
            return

        # Get the selected result data
        result = items[0].data(Qt.ItemDataRole.UserRole)

        if isinstance(result, dict) and "id" in result:
            node_id = result["id"]

            # Check if we need to change detail level
            current_detail = self.detail_combo.currentData()
            node_type = result["type"]

            if node_type == "temple" and current_detail not in ["high", "complete"]:
                # Need to switch to high detail to see temples
                self.detail_combo.setCurrentIndex(self.detail_combo.findData("high"))

            # Focus on the node using JavaScript
            if WEBENGINE_AVAILABLE and hasattr(self, "web_view"):
                # First ensure the node will be visible by applying appropriate filters
                family_id = result.get("family")
                if family_id is not None:
                    family_index = self.family_combo.findData(family_id)
                    if family_index >= 0:
                        self.family_combo.setCurrentIndex(family_index)

                # Focus on the node
                focus_script = f"""
                // Find the node
                const nodeToFocus = data.nodes.find(n => n.id === "{node_id}");
                if (nodeToFocus) {{
                    // Zoom and center on the node
                    const svg = d3.select("svg");
                    const width = svg.attr("width");
                    const height = svg.attr("height");

                    // Reset any previous transforms
                    svg.transition().duration(750).call(
                        zoom.transform,
                        d3.zoomIdentity
                            .translate(width/2, height/2)
                            .scale(2)
                            .translate(-nodeToFocus.x, -nodeToFocus.y)
                    );

                    // Highlight the node
                    const node = d3.selectAll(".nodes").filter(d => d.id === "{node_id}");
                    node.style("stroke", "red").style("stroke-width", "3px");

                    // Highlight connected nodes and links
                    highlightConnections(nodeToFocus);

                    // Show the label
                    const label = d3.selectAll(".node-label").filter(d => d.id === "{node_id}");
                    label.text(nodeToFocus.name).style("font-weight", "bold");
                }}
                """
                self.web_view.page().runJavaScript(focus_script)

                # Update status
                self.status_bar.setText(f"Focused on node: {result['name']}")

    def _export_network_data(self) -> None:
        """Export network data in the selected format."""
        import os

        from PyQt6.QtWidgets import QFileDialog, QMessageBox

        # Get export format
        format_type = self.export_format.currentData()

        # Get export detail level
        detail_level = self.export_detail_level.currentData()
        if detail_level == "current":
            detail_level = self.detail_combo.currentData()

        # Build filter options
        filter_options = {}
        if self.export_include_descriptions.isChecked():
            filter_options["include_descriptions"] = True
        if self.export_include_coordinates.isChecked():
            filter_options["include_coordinates"] = True
        if self.export_include_kamea_locators.isChecked():
            filter_options["include_kamea_locators"] = True

        # Generate export data
        try:
            export_data = self.explorer.export_network_data(
                format_type, detail_level, filter_options
            )

            # Determine file extension and mime type
            extension = export_data.get("extension", format_type)
            mime_type = export_data.get("mime_type", "text/plain")

            # Get save file name
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Network Data",
                f"kamea_network.{extension}",
                f"{format_type.upper()} Files (*.{extension})",
            )

            if not file_path:
                return

            # Save the file
            if format_type == "csv":
                # For CSV, we need to save two files
                nodes_path = file_path
                links_path = os.path.splitext(file_path)[0] + "_links.csv"

                with open(nodes_path, "w") as f:
                    f.write(export_data["nodes"])

                with open(links_path, "w") as f:
                    f.write(export_data["links"])

                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Exported network data to:\n{nodes_path}\n{links_path}",
                )
            else:
                # For other formats, just save the single file
                with open(file_path, "w") as f:
                    f.write(export_data["data"])

                QMessageBox.information(
                    self, "Export Complete", f"Exported network data to:\n{file_path}"
                )

            # Update status
            self.status_bar.setText(
                f"Network data exported to {os.path.basename(file_path)}"
            )

        except Exception as e:
            QMessageBox.warning(
                self, "Export Error", f"Failed to export network data: {e}"
            )
            logger.error(f"Error exporting network data: {e}")

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode for the dialog."""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_button.setText("Toggle Fullscreen")
        else:
            self.showFullScreen()
            self.fullscreen_button.setText("Exit Fullscreen")

    def _show_help(self) -> None:
        """Show help information."""
        from PyQt6.QtWidgets import QMessageBox

        help_text = """
        <h3>Integrated Network Explorer Help</h3>

        <p><b>Visualization Tab:</b> Control the level of detail and filtering for the network visualization.</p>
        <ul>
            <li>Use the Detail Level dropdown to control how many nodes are shown</li>
            <li>Toggle labels for different node types</li>
            <li>Filter by Family to focus on specific parts of the network</li>
        </ul>

        <p><b>Advanced Filters Tab:</b> Apply more specific filters to the network.</p>
        <ul>
            <li>Filter by relationship types to show only certain connections</li>
            <li>Filter by element patterns to focus on specific temple types</li>
            <li>Control the maximum number of temples shown for better performance</li>
        </ul>

        <p><b>Search Tab:</b> Find specific nodes in the network.</p>
        <ul>
            <li>Search by name, ternary value, or description</li>
            <li>Select search results to see detailed information</li>
            <li>Focus on nodes to highlight them in the visualization</li>
        </ul>

        <p><b>Export Tab:</b> Export the network data for use in other applications.</p>
        <ul>
            <li>Choose from JSON, CSV, or GraphML formats</li>
            <li>Select the detail level for the export</li>
            <li>Configure which attributes to include in the export</li>
        </ul>

        <p><b>Navigation:</b> In the visualization, you can:</p>
        <ul>
            <li>Drag nodes to rearrange the network</li>
            <li>Hover over nodes to see details</li>
            <li>Click on nodes to highlight their connections</li>
        </ul>
        """

        QMessageBox.information(self, "Integrated Network Explorer Help", help_text)
