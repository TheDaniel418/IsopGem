#!/usr/bin/env python3
"""
SavedVisualization class for storing and retrieving visualization data.
"""

import json
import os
from datetime import datetime

from PyQt6.QtGui import QColor


class SavedVisualization:
    """Class representing a saved visualization with all its parameters and groups."""

    def __init__(
        self, viz_id=None, name="", description="", viz_type="regular", sides=3, index=1
    ):
        """Initialize a SavedVisualization.

        Args:
            viz_id: Unique identifier for the visualization (generated if None)
            name: User-friendly name for the visualization
            description: Optional description
            viz_type: Type of polygonal number ("regular" or "centered")
            sides: Number of sides for the polygonal number
            index: Index value for the polygonal number
        """
        self.id = viz_id or self._generate_id(viz_type, sides, index)
        self.name = name
        self.description = description
        self.type = viz_type  # "regular" or "centered"
        self.sides = sides
        self.index = index
        self.groups = {}  # Dict of {group_name: [dot_ids]}
        self.colors = {}  # Dict of {group_name: QColor}
        self.connections = (
            []
        )  # List of connection data (dot1, dot2, color, width, style)
        self.created = datetime.now().isoformat()
        self.modified = self.created

    def _generate_id(self, viz_type, sides, index):
        """Generate a unique ID for this visualization.

        Args:
            viz_type: Type of polygonal number
            sides: Number of sides
            index: Index value

        Returns:
            A unique identifier string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{viz_type}_{sides}_{index}_{timestamp}"

    def to_dict(self):
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the visualization
        """
        # Serialize connections
        serialized_connections = []
        for conn in self.connections:
            # Check if this is a Connection object or a tuple
            if hasattr(conn, "dot1") and hasattr(conn, "dot2"):
                # It's a Connection object
                conn_data = {
                    "dot1": conn.dot1,
                    "dot2": conn.dot2,
                    "color": {
                        "r": conn.color.red(),
                        "g": conn.color.green(),
                        "b": conn.color.blue(),
                        "a": conn.color.alpha(),
                    },
                    "width": conn.width,
                    "style": int(
                        conn.style.value
                    ),  # Convert Qt.PenStyle enum to int for serialization
                }
            else:
                # It's a tuple (legacy format or simplified)
                dot1, dot2 = conn[:2]
                conn_data = {
                    "dot1": dot1,
                    "dot2": dot2,
                    "color": {"r": 100, "g": 100, "b": 255, "a": 150},  # Default color
                    "width": 2,  # Default width
                    "style": 1,  # Default style (solid line)
                }
            serialized_connections.append(conn_data)

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "sides": self.sides,
            "index": self.index,
            "groups": self.groups,
            "colors": {
                group: {
                    "r": color.red(),
                    "g": color.green(),
                    "b": color.blue(),
                    "a": color.alpha(),
                }
                for group, color in self.colors.items()
            },
            "connections": serialized_connections,
            "created": self.created,
            "modified": self.modified,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a SavedVisualization from a dictionary.

        Args:
            data: Dictionary containing visualization data

        Returns:
            A SavedVisualization instance
        """
        viz = cls(
            viz_id=data["id"],
            name=data["name"],
            description=data["description"],
            viz_type=data["type"],
            sides=data["sides"],
            index=data["index"],
        )
        viz.groups = data["groups"]
        viz.colors = {
            group: QColor(color["r"], color["g"], color["b"], color["a"])
            for group, color in data["colors"].items()
        }

        # Deserialize connections if present
        if "connections" in data:
            # We'll store the connection data in a format that can be easily converted
            # to Connection objects when loaded into the visualization
            viz.connections = []
            for conn_data in data["connections"]:
                # Store the connection data as a dictionary
                viz.connections.append(conn_data)

        viz.created = data["created"]
        viz.modified = data["modified"]
        return viz


class VisualizationManager:
    """Manager class for saving, loading, and managing visualizations."""

    def __init__(self):
        """Initialize the VisualizationManager."""
        self.base_dir = os.path.expanduser("~/.isopgem/data/geometry")
        self.viz_dir = os.path.join(self.base_dir, "visualizations")
        self.index_file = os.path.join(self.base_dir, "visualizations.json")

        # Create directories if they don't exist
        os.makedirs(self.viz_dir, exist_ok=True)

        # Initialize the index if it doesn't exist
        if not os.path.exists(self.index_file):
            self._save_index({})

    def _save_index(self, index):
        """Save the visualization index.

        Args:
            index: Dictionary of visualization metadata
        """
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)

    def _load_index(self):
        """Load the visualization index.

        Returns:
            Dictionary of visualization metadata
        """
        try:
            with open(self.index_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_visualization(self, visualization):
        """Save a visualization to disk.

        Args:
            visualization: SavedVisualization instance to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the modified timestamp
            visualization.modified = datetime.now().isoformat()

            # Convert to dictionary
            viz_data = visualization.to_dict()

            # Save to individual file
            viz_file = os.path.join(self.viz_dir, f"{visualization.id}.json")
            with open(viz_file, "w") as f:
                json.dump(viz_data, f, indent=2)

            # Update the index
            index = self._load_index()
            index[visualization.id] = {
                "name": visualization.name,
                "description": visualization.description,
                "type": visualization.type,
                "sides": visualization.sides,
                "index": visualization.index,
                "modified": visualization.modified,
            }
            self._save_index(index)

            return True
        except Exception as e:
            print(f"Error saving visualization: {e}")
            return False

    def load_visualization(self, viz_id):
        """Load a visualization from disk.

        Args:
            viz_id: ID of the visualization to load

        Returns:
            SavedVisualization instance or None if not found
        """
        viz_file = os.path.join(self.viz_dir, f"{viz_id}.json")
        try:
            with open(viz_file, "r") as f:
                viz_data = json.load(f)
            return SavedVisualization.from_dict(viz_data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading visualization: {e}")
            return None

    def delete_visualization(self, viz_id):
        """Delete a visualization.

        Args:
            viz_id: ID of the visualization to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from index
            index = self._load_index()
            if viz_id in index:
                del index[viz_id]
                self._save_index(index)

            # Delete the file
            viz_file = os.path.join(self.viz_dir, f"{viz_id}.json")
            if os.path.exists(viz_file):
                os.remove(viz_file)

            return True
        except Exception as e:
            print(f"Error deleting visualization: {e}")
            return False

    def get_all_visualizations(self):
        """Get a list of all saved visualizations.

        Returns:
            Dictionary of visualization metadata
        """
        return self._load_index()
