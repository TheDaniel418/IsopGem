"""
Repositories for the document manager pillar.

This module provides repository classes for document data persistence.
"""

from document_manager.repositories.concordance_repository import ConcordanceRepository
from document_manager.repositories.document_repository import DocumentRepository
from document_manager.repositories.category_repository import CategoryRepository

__all__ = ["ConcordanceRepository", "DocumentRepository", "CategoryRepository"]
