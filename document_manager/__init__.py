"""
Document Manager pillar for IsopGem.

This pillar provides document management capabilities including:
- Document importing, storage, and organization
- Text extraction from various document formats
- Category management for organizing documents
- UI components for browsing and viewing documents
- Rich text editing with QGem editor components

Key components:
- Models: Document, DocumentCategory, QGemDocument
- Services: DocumentService, CategoryService, QGemDocumentService
- UI Components: DocumentManagerPanel, DocumentBrowserPanel, DocumentViewerDialog
"""

# Version
__version__ = "0.1.0"

# Expose key components
from document_manager.models.document import Document, DocumentType
from document_manager.models.document_category import DocumentCategory
from document_manager.models.qgem_document import QGemDocument, QGemDocumentType
from document_manager.services.document_service import DocumentService
from document_manager.services.category_service import CategoryService
from document_manager.services.qgem_document_service import QGemDocumentService
from document_manager.repositories.document_repository import DocumentRepository
from document_manager.ui.panels.document_manager_panel import DocumentManagerPanel
from document_manager.ui.panels.document_browser_panel import DocumentBrowserPanel
from document_manager.ui.panels.document_analysis_panel import DocumentAnalysisPanel
from document_manager.ui.document_tab import DocumentTab

from document_manager.document_manager_pillar import DocumentManagerPillar

__all__ = [
    "DocumentManagerPillar",
    "Document",
    "DocumentType",
    "DocumentCategory",
    "QGemDocument",
    "QGemDocumentType",
    "DocumentService",
    "CategoryService",
    "QGemDocumentService",
    "DocumentRepository",
    "DocumentManagerPanel",
    "DocumentBrowserPanel",
    "DocumentAnalysisPanel",
    "DocumentTab",
]
