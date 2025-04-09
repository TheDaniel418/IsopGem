"""
Purpose: Defines the Document Manager pillar for the IsopGem application.

This file is part of the document_manager pillar and serves as the entry point.
It provides the pillar class that integrates document management into the main application.

Key components:
- DocumentManagerPillar: Main pillar class for document management functionality
"""

from typing import Any, Dict, Optional


class DocumentManagerPillar:
    """Document Manager pillar for IsopGem application."""

    def __init__(self):
        """Initialize the document manager pillar."""
        self.name = "Document Manager"
        self.description = (
            "Manages document importing, storage, text extraction, and organization."
        )

    def initialize(self, app_context: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the document manager pillar.

        Args:
            app_context: Application context with shared services

        Returns:
            True if initialization was successful, False otherwise
        """
        return True

    def get_name(self) -> str:
        """Get the name of the pillar.

        Returns:
            Pillar name
        """
        return self.name

    def get_description(self) -> str:
        """Get the description of the pillar.

        Returns:
            Pillar description
        """
        return self.description
