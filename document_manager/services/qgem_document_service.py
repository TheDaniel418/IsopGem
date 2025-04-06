"""
Purpose: Provides services for managing QGem documents.

This file is part of the document_manager pillar and serves as a service component.
It handles operations related to QGem rich text documents, including conversion
between DocumentFormat and QGemDocument models.

Key components:
- QGemDocumentService: Service for managing QGem documents
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

from document_manager.models.document import DocumentType
from document_manager.models.qgem_document import QGemDocument
from document_manager.services.document_service import DocumentService
from shared.ui.widgets.rtf_editor.models.document_format import DocumentFormat

logger = logging.getLogger(__name__)


class QGemDocumentService:
    """Service for managing QGem documents."""

    def __init__(self, document_service: DocumentService):
        """Initialize the QGem document service.

        Args:
            document_service: Document service instance
        """
        self.document_service = document_service
        self.document_repository = document_service.document_repository
        logger.info("QGemDocumentService initialized")

    def create_document(self, doc_format: DocumentFormat) -> QGemDocument:
        """Create a new QGem document from a DocumentFormat.

        Args:
            doc_format: DocumentFormat instance

        Returns:
            The created QGemDocument
        """
        # Convert to QGemDocument
        qgem_doc = QGemDocument.from_document_format(doc_format)

        # Calculate checksum before saving
        self._calculate_checksum(qgem_doc)

        # Save to repository - repository.save() returns boolean success flag
        success = self.document_repository.save(qgem_doc)

        if not success:
            logger.error("Failed to save document to repository")
            return qgem_doc  # Return the original doc as fallback

        # If save was successful, get the newly saved document by ID
        saved_doc = self.document_service.get_document(qgem_doc.id)

        # Return the saved document if available, otherwise return the original
        if saved_doc is None:
            logger.error(f"Could not retrieve saved document with ID {qgem_doc.id}")
            return qgem_doc

        # Convert to QGemDocument if needed
        if isinstance(saved_doc, QGemDocument):
            return saved_doc

        try:
            if hasattr(saved_doc, "dict") and callable(saved_doc.dict):
                return QGemDocument(**saved_doc.dict())
        except Exception as e:
            logger.error(f"Error converting document: {e}")

        # Return original document as fallback
        return qgem_doc

    def update_document(self, doc_format: DocumentFormat) -> QGemDocument:
        """Update an existing QGem document from a DocumentFormat.

        Args:
            doc_format: DocumentFormat instance

        Returns:
            The updated QGemDocument

        Raises:
            ValueError: If document with given ID does not exist
        """
        # Get existing document
        existing_doc = self.document_service.get_document(doc_format.id)
        if not existing_doc:
            raise ValueError(f"Document with ID {doc_format.id} not found")

        # Convert to QGemDocument
        qgem_doc = QGemDocument.from_document_format(doc_format)

        # Preserve file path if it exists
        if existing_doc.file_path:
            qgem_doc.file_path = existing_doc.file_path

        # Calculate checksum
        self._calculate_checksum(qgem_doc)

        # Save to repository - repository.save() returns boolean success flag
        success = self.document_repository.save(qgem_doc)

        if not success:
            logger.error("Failed to update document in repository")
            return qgem_doc  # Return the original doc as fallback

        # If update was successful, get the updated document by ID
        updated_doc = self.document_service.get_document(qgem_doc.id)

        # Return the updated document if available, otherwise return the original
        if updated_doc is None:
            logger.error(f"Could not retrieve updated document with ID {qgem_doc.id}")
            return qgem_doc

        # Convert to QGemDocument if needed
        if isinstance(updated_doc, QGemDocument):
            return updated_doc

        try:
            if hasattr(updated_doc, "dict") and callable(updated_doc.dict):
                return QGemDocument(**updated_doc.dict())
        except Exception as e:
            logger.error(f"Error converting document: {e}")

        # Return original document as fallback
        return qgem_doc

    def get_document_by_id(self, document_id: str) -> Optional[QGemDocument]:
        """Get a QGem document by ID.

        Args:
            document_id: Document ID

        Returns:
            QGemDocument if found, None otherwise
        """
        doc = self.document_service.get_document(document_id)
        if not doc:
            return None

        # Convert to QGemDocument if it's a QTDOC
        if doc.file_type == DocumentType.QTDOC:
            if isinstance(doc, QGemDocument):
                return doc
            elif hasattr(doc, "dict") and callable(doc.dict):
                return QGemDocument(**doc.dict())
            else:
                logger.error(f"Unexpected document type from service: {type(doc)}")
                return None
        return None

    def get_all_qgem_documents(self) -> List[QGemDocument]:
        """Get all QGem documents.

        Returns:
            List of QGemDocument instances
        """
        # Get all documents
        all_docs = self.document_service.get_all_documents()

        # Filter QGem documents and convert to QGemDocument
        qgem_docs = []
        for doc in all_docs:
            if doc.file_type == DocumentType.QTDOC:
                if isinstance(doc, QGemDocument):
                    qgem_docs.append(doc)
                elif hasattr(doc, "dict") and callable(doc.dict):
                    qgem_docs.append(QGemDocument(**doc.dict()))
                else:
                    logger.warning(
                        f"Skipping document with ID {doc.id} due to unexpected type: {type(doc)}"
                    )

        return qgem_docs

    def delete_document(self, document_id: str) -> bool:
        """Delete a QGem document by ID.

        Args:
            document_id: Document ID

        Returns:
            True if document was deleted, False otherwise
        """
        # Get document
        doc = self.get_document_by_id(document_id)
        if not doc:
            logger.warning(
                f"Cannot delete QGem document with ID {document_id} - not found"
            )
            return False

        # Delete associated file if exists
        if doc.file_path and doc.file_path.exists():
            try:
                doc.file_path.unlink()
                logger.info(f"Deleted file for document {document_id}: {doc.file_path}")
            except Exception as e:
                logger.error(f"Error deleting file for document {document_id}: {e}")
                # Continue anyway - we still want to delete the document from repo

        # Delete document
        try:
            result = self.document_service.delete_document(document_id)
            if result:
                logger.info(f"Successfully deleted QGem document with ID {document_id}")
                return True
            else:
                logger.error(f"Failed to delete QGem document with ID {document_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting QGem document with ID {document_id}: {e}")
            return False

    def get_document_as_format(self, document_id: str) -> Optional[DocumentFormat]:
        """Get a document as DocumentFormat.

        Args:
            document_id: Document ID

        Returns:
            DocumentFormat if found, None otherwise
        """
        # Get document
        doc = self.get_document_by_id(document_id)
        if not doc:
            return None

        # Convert to DocumentFormat
        return doc.to_document_format()

    def save_document_format(self, doc_format: DocumentFormat) -> QGemDocument:
        """Save a DocumentFormat as a QGem document.

        Args:
            doc_format: DocumentFormat instance

        Returns:
            The saved QGemDocument
        """
        # Check if document already exists
        existing_doc = self.document_service.get_document(doc_format.id)
        if existing_doc:
            return self.update_document(doc_format)
        else:
            return self.create_document(doc_format)

    def export_to_json(self, document_id: str, output_path: Path) -> bool:
        """Export a QGem document to JSON.

        Args:
            document_id: Document ID
            output_path: Path to save JSON file

        Returns:
            True if export was successful, False otherwise
        """
        # Get document format
        doc_format = self.get_document_as_format(document_id)
        if not doc_format:
            logger.error(f"Document with ID {document_id} not found")
            return False

        try:
            # Convert to dict and write to file
            doc_dict = doc_format.dict()
            with open(output_path, "w") as f:
                json.dump(doc_dict, f, indent=2, default=str)
            logger.info(f"Document exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting document to JSON: {e}")
            return False

    def import_from_json(self, json_path: Path) -> Optional[QGemDocument]:
        """Import a QGem document from JSON.

        Args:
            json_path: Path to JSON file

        Returns:
            Imported QGemDocument if successful, None otherwise
        """
        try:
            # Read JSON file
            with open(json_path, "r") as f:
                doc_dict = json.load(f)

            # Convert to DocumentFormat
            doc_format = DocumentFormat(**doc_dict)

            # Save document
            return self.save_document_format(doc_format)
        except Exception as e:
            logger.error(f"Error importing document from JSON: {e}")
            return None

    def _calculate_checksum(self, document: QGemDocument) -> None:
        """Calculate checksum for document content.

        Args:
            document: QGemDocument to calculate checksum for
        """
        if document.html_content:
            content = document.html_content
        elif document.content:
            content = document.content
        else:
            content = f"{document.name}-{document.id}"

        # Calculate checksum
        checksum = hashlib.md5(content.encode()).hexdigest()
        document.checksum = checksum
