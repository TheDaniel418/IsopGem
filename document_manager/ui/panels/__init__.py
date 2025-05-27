"""
UI panels for the document manager pillar.

This module provides panel classes for document management UI.
"""

from document_manager.ui.panels.document_analysis_panel import DocumentAnalysisPanel
from document_manager.ui.panels.document_browser_panel import DocumentBrowserPanel
from document_manager.ui.panels.document_database_manager_panel import DocumentDatabaseManagerPanel
from document_manager.ui.panels.document_database_utility_panel import DocumentDatabaseUtilityPanel
from document_manager.ui.panels.document_manager_panel import DocumentManagerPanel
from document_manager.ui.panels.concordance_panel import ConcordancePanel

__all__ = [
    "DocumentBrowserPanel",
    "DocumentAnalysisPanel",
    "DocumentManagerPanel",
    "DocumentDatabaseManagerPanel",
    "DocumentDatabaseUtilityPanel",
    "ConcordancePanel",
]
