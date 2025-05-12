"""
Purpose: Provides a widget for visualizing the Kamea family network

This file is part of the tq pillar and serves as a UI component.
It visualizes the relationships between the nine Ditrunal Families
in the Kamea system, showing their connections and interactions.

Key components:
- FamilyNetworkVisualizer: Class for generating network data
- FamilyNetworkDialog: Dialog for displaying the visualization

Dependencies:
- PyQt6: For the user interface components
- PyQtWebEngine: For rendering the D3.js visualization
- tq.services.kamea_service: For Kamea-related operations
- tq.services.ternary_dimension_interpreter_new: For Hierophant data

Related files:
- tq/ui/panels/kamea_of_maut_panel.py: Panel that uses this visualizer
- tq/services/kamea_service.py: Service for Kamea operations
"""

import json
from typing import Dict

from PyQt6.QtCore import Qt

# Try to import WebEngine, but provide a fallback if it's not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    WEBENGINE_AVAILABLE = True
    print("Successfully imported PyQt6.QtWebEngineWidgets")
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    print(f"Failed to import PyQt6.QtWebEngineWidgets: {e}")

    # Create a dummy QWebEngineView class for type checking
    class QWebEngineView:
        pass


from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tq.services.kamea_service import KameaService
from tq.services.ternary_dimension_interpreter_new import HIEROPHANTS


class FamilyNetworkVisualizer:
    """Visualizes the network of relationships between Kamea families."""

    def __init__(self, kamea_service: KameaService):
        """Initialize with the Kamea service.

        Args:
            kamea_service: The Kamea service to use for operations
        """
        self.kamea_service = kamea_service

    def generate_network_data(self) -> Dict:
        """Generate data for the family network visualization.

        Returns:
            Dictionary with nodes and links for the network
        """
        # Create nodes for each family
        nodes = []
        for family_id in range(9):
            hierophant = self._get_hierophant(family_id)
            nodes.append(
                {
                    "id": family_id,
                    "name": f"Family {family_id}",
                    "hierophant": hierophant,
                    "hierophant_name": self._get_hierophant_name(hierophant),
                    "group": self._get_family_group(family_id),
                }
            )

        # Create links between families
        links = []

        # Immutable Region (0) connects to all other families
        for family_id in range(1, 9):
            links.append(
                {"source": 0, "target": family_id, "value": 1, "type": "central"}
            )

        # Pure Conrune Pairs (4 & 8)
        links.append({"source": 4, "target": 8, "value": 2, "type": "conrune"})

        # Complementary Regions (5 & 7)
        links.append({"source": 5, "target": 7, "value": 2, "type": "complementary"})

        # Bigrammic Quadset (1, 2, 3, 6)
        for i in [1, 2, 3, 6]:
            for j in [1, 2, 3, 6]:
                if i < j:  # Avoid duplicate links
                    links.append(
                        {"source": i, "target": j, "value": 1.5, "type": "quadset"}
                    )

        return {"nodes": nodes, "links": links}

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

    def create_d3_visualization(self, network_data: Dict) -> str:
        """Create D3.js HTML for the network visualization.

        Args:
            network_data: Dictionary with nodes and links

        Returns:
            HTML string with the D3.js visualization
        """
        # This generates the HTML/JS for a D3.js force-directed graph
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Kamea Family Network</title>
            <script src="https://d3js.org/d3.v7.min.js"></script>
            <style>
                body { margin: 0; font-family: Arial, sans-serif; }
                .links line { stroke-opacity: 0.6; }
                .nodes circle { stroke: #fff; stroke-width: 1.5px; }
                .node-label { font-size: 12px; }
                .immutable { fill: #1f77b4; }
                .pure_conrune { fill: #ff7f0e; }
                .complementary { fill: #2ca02c; }
                .bigrammic { fill: #d62728; }
                .central { stroke: #aaa; }
                .conrune { stroke: #ff7f0e; stroke-width: 3px; }
                .complementary { stroke: #2ca02c; stroke-width: 3px; }
                .quadset { stroke: #d62728; }
            </style>
        </head>
        <body>
            <svg width="800" height="600"></svg>
            <script>
            // Network data
            const data = %s;

            // Create the force simulation
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id))
                .force("charge", d3.forceManyBody().strength(-400))
                .force("center", d3.forceCenter(400, 300));

            // Get the SVG element
            const svg = d3.select("svg");

            // Create the links
            const link = svg.append("g")
                .selectAll("line")
                .data(data.links)
                .enter().append("line")
                .attr("class", d => "links " + d.type)
                .attr("stroke-width", d => Math.sqrt(d.value) * 2);

            // Create the nodes
            const node = svg.append("g")
                .selectAll("circle")
                .data(data.nodes)
                .enter().append("circle")
                .attr("class", d => "nodes " + d.group)
                .attr("r", 15)
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
                .attr("dy", ".35em")
                .text(d => d.name);

            // Add tooltips
            node.append("title")
                .text(d => `Family ${d.id}\\nHierophant: ${d.hierophant_name} (${d.hierophant})`);

            // Update positions on each tick
            simulation.on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);

                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
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
            </script>
        </body>
        </html>
        """ % json.dumps(
            network_data
        )

        return html


class FamilyNetworkDialog(QDialog):
    """Dialog for displaying the Family Network visualization."""

    def __init__(self, parent, kamea_service: KameaService):
        """Initialize the dialog.

        Args:
            parent: The parent widget
            kamea_service: The Kamea service to use
        """
        super().__init__(parent)

        self.kamea_service = kamea_service

        # Create the visualizer
        self.visualizer = FamilyNetworkVisualizer(self.kamea_service)

        # Generate the network data
        self.network_data = self.visualizer.generate_network_data()

        # Create the HTML
        self.html = self.visualizer.create_d3_visualization(self.network_data)

        # Set up the dialog
        self.setWindowTitle("Kamea Family Network")
        self.resize(850, 650)

        # Create the layout
        self.layout = QVBoxLayout(self)

        # Create a legend
        self.legend_widget = self._create_legend()
        self.layout.addWidget(self.legend_widget)

        # Check if WebEngine is available
        if WEBENGINE_AVAILABLE:
            # Create a web view for the D3.js visualization
            self.web_view = QWebEngineView()
            self.web_view.setHtml(self.html)
            self.layout.addWidget(self.web_view)
        else:
            # Create a fallback message
            fallback_label = QLabel(
                "The D3.js visualization requires PyQt6.QtWebEngineWidgets, which is not installed.\n"
                "Please install it with: pip install PyQtWebEngine"
            )
            fallback_label.setWordWrap(True)
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(fallback_label)

            # Add a text representation of the network data
            text_representation = QLabel(
                "Family Network Structure:\n"
                "- Family 0 (The Void) connects to all other families\n"
                "- Families 4 & 8 (The Enclosure & The Harmonizer) form a Pure Conrune Pair\n"
                "- Families 5 & 7 (The Liberator & The Foundation) form a Complementary Region\n"
                "- Families 1, 2, 3, 6 (The Dynamo, The Matrix, The Oscillator, The Weaver) form a Bigrammic Quadset"
            )
            text_representation.setWordWrap(True)
            text_representation.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.layout.addWidget(text_representation)

        # Add a close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.layout.addWidget(self.close_button)

    def _create_legend(self) -> QWidget:
        """Create a legend for the Family Network visualization.

        Returns:
            The legend widget
        """
        legend = QWidget()
        legend_layout = QHBoxLayout(legend)

        # Family types
        family_types = [
            ("Immutable Region", "#1f77b4"),
            ("Pure Conrune Pairs", "#ff7f0e"),
            ("Complementary Regions", "#2ca02c"),
            ("Bigrammic Quadset", "#d62728"),
        ]

        # Connection types
        connection_types = [
            ("Central Connection", "#aaa", 1),
            ("Conrune Pair", "#ff7f0e", 3),
            ("Complementary", "#2ca02c", 3),
            ("Quadset", "#d62728", 1),
        ]

        # Create family type legend
        family_legend = QGroupBox("Family Types")
        family_layout = QVBoxLayout(family_legend)

        for name, color in family_types:
            item = QHBoxLayout()
            color_box = QFrame()
            color_box.setFixedSize(20, 20)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
            item.addWidget(color_box)
            item.addWidget(QLabel(name))
            family_layout.addLayout(item)

        # Create connection type legend
        connection_legend = QGroupBox("Connection Types")
        connection_layout = QVBoxLayout(connection_legend)

        for name, color, width in connection_types:
            item = QHBoxLayout()
            line = QFrame()
            line.setFixedSize(30, width)
            line.setStyleSheet(f"background-color: {color};")
            item.addWidget(line)
            item.addWidget(QLabel(name))
            connection_layout.addLayout(item)

        # Add to legend layout
        legend_layout.addWidget(family_legend)
        legend_layout.addWidget(connection_legend)

        return legend
