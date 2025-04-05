"""
Purpose: Provides document management business logic for the application.

This file is part of the document_manager pillar and serves as a service component.
It is responsible for handling document operations, text extraction, and processing.

Key components:
- DocumentService: Service class for document management operations

Dependencies:
- document_manager.models.document: For Document model
- document_manager.repositories.document_repository: For document persistence
- PyMuPDF: For PDF processing (imported as fitz)
- python-docx: For DOCX processing
"""

import concurrent.futures
import os
import re
import shutil
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import List, Optional, Union

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from loguru import logger

from document_manager.models.document import Document, DocumentType
from document_manager.repositories.document_repository import DocumentRepository


class DocumentService:
    """Service for document management operations."""

    # Windows Symbol font to Unicode Greek letter mapping
    SYMBOL_TO_GREEK = {
        "a": "α",
        "b": "β",
        "g": "γ",
        "d": "δ",
        "e": "ε",
        "z": "ζ",
        "h": "η",
        "q": "θ",
        "i": "ι",
        "k": "κ",
        "l": "λ",
        "m": "μ",
        "n": "ν",
        "x": "ξ",
        "o": "ο",
        "p": "π",
        "r": "ρ",
        "s": "σ",
        "ς": "ς",
        "t": "τ",
        "u": "υ",
        "f": "φ",
        "c": "χ",
        "y": "ψ",
        "w": "ω",
        "A": "Α",
        "B": "Β",
        "G": "Γ",
        "D": "Δ",
        "E": "Ε",
        "Z": "Ζ",
        "H": "Η",
        "Q": "Θ",
        "I": "Ι",
        "K": "Κ",
        "L": "Λ",
        "M": "Μ",
        "N": "Ν",
        "X": "Ξ",
        "O": "Ο",
        "P": "Π",
        "R": "Ρ",
        "S": "Σ",
        "T": "Τ",
        "U": "Υ",
        "F": "Φ",
        "C": "Χ",
        "Y": "Ψ",
        "W": "Ω",
    }

    # Special Symbol font characters that map to other Greek characters or symbols
    SYMBOL_SPECIAL = {
        # Symbol font uses "V" for the end-of-word sigma (ς)
        "V": "ς",
        # Other special mappings for mathematical symbols often used in Greek texts
        "@": "∈",  # Element of
        "∃": "∃",  # There exists
        "∀": "∀",  # For all
        "∂": "∂",  # Partial differential
        "∇": "∇",  # Nabla/Del
        "∞": "∞",  # Infinity
        "∝": "∝",  # Proportional to
    }

    def __init__(self, document_repository: Optional[DocumentRepository] = None):
        """Initialize the document service.

        Args:
            document_repository: Repository for document storage, created if not provided
        """
        self.document_repository = document_repository or DocumentRepository()
        self.storage_dir = Path("data/documents")

        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)

    def _convert_symbol_to_greek(self, text: str) -> str:
        """Convert Symbol font characters to proper Unicode Greek letters.

        This function detects text that appears to be in Symbol font (common in older documents)
        and converts it to proper Unicode Greek characters for better searchability.

        Args:
            text: Text that may contain Symbol font encoded Greek letters

        Returns:
            Text with Symbol font characters converted to Unicode Greek
        """
        # Check for definite markers of Symbol font use
        # Pattern of Latin characters that would form Greek words when converted
        greek_word_patterns = [
            r"\b[abgdezhqiklmnxoprVsctufcyw]{2,}\b",  # Lowercase Greek words
            r"\b[ABGDEZHQIKLMNXOPRVSCTUFCYW]{2,}\b",  # Uppercase Greek words
        ]

        # If we detect potential Symbol font Greek text
        potential_greek = False
        for pattern in greek_word_patterns:
            if re.search(pattern, text):
                potential_greek = True
                break

        if potential_greek:
            # Replace common Symbol font encoded Greek with proper Unicode
            for latin, greek in self.SYMBOL_TO_GREEK.items():
                text = text.replace(latin, greek)

            # Handle special Symbol font characters
            for symbol, replacement in self.SYMBOL_SPECIAL.items():
                text = text.replace(symbol, replacement)

            # Log that we did a conversion
            logger.info("Converted Symbol font Greek characters to Unicode")

        return text

    def import_document(self, file_path: Union[str, Path]) -> Optional[Document]:
        """Import a document from a file.

        This copies the file to the storage directory and extracts metadata.

        Args:
            file_path: Path to the document file

        Returns:
            Imported document if successful, None otherwise
        """
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            # Get document type from extension
            try:
                document_type = DocumentType.from_extension(file_path.suffix)
            except ValueError:
                logger.error(f"Unsupported file type: {file_path.suffix}")
                return None

            # Create document object with metadata
            document = Document.from_file(file_path)

            # Copy file to storage directory
            storage_path = self.storage_dir / f"{document.id}{file_path.suffix}"
            shutil.copy2(file_path, storage_path)

            # Update file path to storage location
            document.file_path = Path(str(storage_path))

            # Extract text content if possible
            self.extract_text(document)

            # Save document to repository
            self.document_repository.save(document)

            return document
        except Exception as e:
            logger.error(f"Error importing document: {e}")
            return None

    def batch_import_documents(
        self,
        file_paths: List[Union[str, Path]],
        max_workers: int = 4,
        category_id: Optional[str] = None,
    ) -> List[Document]:
        """Import multiple documents at once.

        Args:
            file_paths: List of paths to document files
            max_workers: Maximum number of worker threads for parallel processing
            category_id: Optional category ID to assign to all imported documents

        Returns:
            List of successfully imported documents
        """
        logger.info(f"Batch importing {len(file_paths)} documents")
        imported_documents = []

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all import tasks
            future_to_path = {
                executor.submit(self.import_document, path): path for path in file_paths
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    document = future.result()
                    if document:
                        # Assign category if provided
                        if category_id is not None:
                            document.category = category_id
                            self.document_repository.save(document)

                        imported_documents.append(document)
                        logger.info(f"Successfully imported: {path}")
                    else:
                        logger.warning(f"Failed to import: {path}")
                except Exception as e:
                    logger.error(f"Exception importing {path}: {e}")

        logger.info(
            f"Batch import completed. {len(imported_documents)} of {len(file_paths)} documents imported successfully"
        )
        return imported_documents

    def import_documents_from_directory(
        self,
        directory_path: Union[str, Path],
        file_patterns: Optional[List[str]] = None,
        recursive: bool = False,
        max_workers: int = 4,
        category_id: Optional[str] = None,
    ) -> List[Document]:
        """Import all documents from a directory.

        Args:
            directory_path: Path to directory containing documents
            file_patterns: List of glob patterns to match files (e.g., ["*.pdf", "*.docx"])
            recursive: Whether to search subdirectories recursively
            max_workers: Maximum number of worker threads for parallel processing
            category_id: Optional category ID to assign to all imported documents

        Returns:
            List of successfully imported documents
        """
        directory_path = Path(directory_path)

        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return []

        # Default patterns include all supported document types
        if file_patterns is None:
            file_patterns = [f"*.{t.value}" for t in DocumentType]

        # Find all matching files
        all_files = []
        for pattern in file_patterns:
            if recursive:
                # Search recursively through subdirectories
                search_pattern = str(directory_path / "**" / pattern)
                matches = glob(search_pattern, recursive=True)
            else:
                # Search only in the specified directory
                search_pattern = str(directory_path / pattern)
                matches = glob(search_pattern)

            all_files.extend(matches)

        # Remove duplicates
        all_files = list(set(all_files))

        logger.info(f"Found {len(all_files)} files to import in {directory_path}")

        # Convert string paths to Path objects before calling batch_import_documents
        # This fixes the type compatibility issue
        all_files_paths: List[Union[str, Path]] = [
            Path(f) if isinstance(f, str) else f for f in all_files
        ]
        return self.batch_import_documents(
            all_files_paths, max_workers=max_workers, category_id=category_id
        )

    def extract_text(self, document: Document) -> bool:
        """Extract text content from a document.

        Args:
            document: Document to process

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(document.file_path):
            logger.error(f"Document file not found: {document.file_path}")
            return False

        try:
            # Extract text based on file type
            if document.file_type == DocumentType.PDF:
                return self._extract_text_from_pdf(document)
            elif document.file_type == DocumentType.DOCX:
                return self._extract_text_from_docx(document)
            elif document.file_type == DocumentType.TXT:
                return self._extract_text_from_txt(document)
            elif document.file_type == DocumentType.ODT:
                return self._extract_text_from_odt(document)
            elif document.file_type == DocumentType.ODS:
                return self._extract_text_from_ods(document)
            elif document.file_type == DocumentType.ODP:
                return self._extract_text_from_odp(document)

            # If we get here, the file type is not supported
            logger.warning(f"Text extraction not supported for {document.file_type}")
            return False

        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return False

    def _extract_text_from_pdf(self, document: Document) -> bool:
        """Extract text from a PDF document.

        Args:
            document: PDF document

        Returns:
            True if successful, False otherwise
        """
        try:
            pdf = fitz.open(document.file_path)
            text = ""
            page_count = 0
            word_count = 0

            # Extract text from each page
            for page in pdf:
                page_text = page.get_text()

                # Convert any Symbol font Greek characters to Unicode
                page_text = self._convert_symbol_to_greek(page_text)

                text += page_text
                page_count += 1
                # Approximate word count
                word_count += len(page_text.split())

            # Update document with extracted text and metadata
            document.content = text
            document.page_count = page_count
            document.word_count = word_count
            document.metadata["page_count"] = page_count
            document.metadata["word_count"] = word_count

            # Save updated document
            self.document_repository.save(document)

            return True
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return False

    def _extract_text_from_docx(self, document: Document) -> bool:
        """Extract text from a DOCX document.

        Args:
            document: DOCX document

        Returns:
            True if successful, False otherwise
        """
        try:
            doc = DocxDocument(str(document.file_path))
            text = ""
            word_count = 0

            # Check for Symbol font usage in the document
            has_symbol_font = False
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if run.font and run.font.name and "Symbol" in run.font.name:
                        has_symbol_font = True
                        break
                if has_symbol_font:
                    break

            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text:
                    para_text = para.text

                    # Check for potential Symbol font in this paragraph
                    for run in para.runs:
                        if run.font and run.font.name and "Symbol" in run.font.name:
                            # This run is in Symbol font, so its text should be treated as Greek
                            # Note: We're processing the whole paragraph text since the runs
                            # information might not give us perfect boundary information
                            para_text = self._convert_symbol_to_greek(para_text)
                            break

                    text += para_text + "\n"
                    word_count += len(para_text.split())

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text:
                            cell_text = cell.text

                            # Check if Symbol font might be used in this cell
                            if has_symbol_font:
                                cell_text = self._convert_symbol_to_greek(cell_text)

                            text += cell_text + "\n"
                            word_count += len(cell_text.split())

            # If document has Symbol font anywhere, do a final pass on the whole text
            if has_symbol_font:
                text = self._convert_symbol_to_greek(text)

            # Update document with extracted text and metadata
            document.content = text
            document.word_count = word_count
            document.page_count = len(doc.sections)  # Approximate
            document.metadata["word_count"] = word_count
            document.metadata["page_count"] = len(doc.sections)
            document.metadata["has_greek_text"] = has_symbol_font

            # Save updated document
            self.document_repository.save(document)

            return True
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return False

    def _extract_text_from_txt(self, document: Document) -> bool:
        """Extract text from a TXT document.

        Args:
            document: TXT document

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(document.file_path, "r", encoding="utf-8") as file:
                text = file.read()

            # Convert potential Symbol font Greek text
            text = self._convert_symbol_to_greek(text)

            # Update document with text content
            document.content = text
            document.word_count = len(text.split())
            document.page_count = 1  # Plain text files don't have pages
            document.metadata["word_count"] = len(text.split())
            document.metadata["page_count"] = 1

            # Save updated document
            self.document_repository.save(document)

            return True
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            return False

    def _extract_text_from_odt(self, document: Document) -> bool:
        """Extract text from a LibreOffice Writer (ODT) document.

        Args:
            document: ODT document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Attempt to use odfpy library for extraction
            from odf import style, teletype, text
            from odf.opendocument import load

            textdoc = load(document.file_path)
            allparas = textdoc.getElementsByType(text.P)

            extracted_text = ""
            word_count = 0

            # Check for Symbol font usage
            has_symbol_font = False
            styles = textdoc.getElementsByType(style.Style)
            for s in styles:
                text_props = s.getElementsByType(style.TextProperties)
                for prop in text_props:
                    if prop.getAttribute("fontname") and "Symbol" in prop.getAttribute(
                        "fontname"
                    ):
                        has_symbol_font = True
                        break
                if has_symbol_font:
                    break

            for para in allparas:
                para_text = teletype.extractText(para)

                # Check for Greek letters if Symbol font is used
                if has_symbol_font:
                    para_text = self._convert_symbol_to_greek(para_text)

                extracted_text += para_text + "\n"
                word_count += len(para_text.split())

            # Approximate page count (1 page per 500 words)
            page_count = max(1, word_count // 500)

            # Update document with text content
            document.content = extracted_text
            document.word_count = word_count
            document.page_count = page_count
            document.metadata["word_count"] = word_count
            document.metadata["page_count"] = page_count
            document.metadata["has_greek_text"] = has_symbol_font

            # Save updated document
            self.document_repository.save(document)

            return True
        except ImportError:
            logger.error(
                "odfpy library not installed. Please install odfpy to process ODT files."
            )
            return False
        except Exception as e:
            logger.error(f"Error extracting ODT text: {e}")
            return False

    def _extract_text_from_ods(self, document: Document) -> bool:
        """Extract text from a LibreOffice Calc (ODS) document.

        Args:
            document: ODS document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Attempt to use odfpy library for extraction
            from odf import table, teletype, text
            from odf.opendocument import load

            spreadsheet = load(document.file_path)

            # Get all tables (sheets)
            tables = spreadsheet.getElementsByType(table.Table)

            extracted_text = ""
            word_count = 0
            sheet_count = len(tables)

            # Process each table (sheet)
            for sheet in tables:
                sheet_name = sheet.getAttribute("name")
                extracted_text += f"Sheet: {sheet_name}\n\n"

                # Get all rows
                rows = sheet.getElementsByType(table.TableRow)
                for row in rows:
                    row_text = ""
                    # Get all cells in this row
                    cells = row.getElementsByType(table.TableCell)
                    for cell in cells:
                        # Get cell content (which may include paragraphs)
                        paras = cell.getElementsByType(text.P)
                        for para in paras:
                            cell_text = teletype.extractText(para)
                            row_text += cell_text + "\t"

                    extracted_text += row_text + "\n"
                    word_count += len(row_text.split())

                extracted_text += "\n\n"

            # Update document with text content
            document.content = extracted_text
            document.word_count = word_count
            document.page_count = sheet_count
            document.metadata["word_count"] = word_count
            document.metadata["sheet_count"] = sheet_count
            document.metadata["page_count"] = sheet_count

            # Save updated document
            self.document_repository.save(document)

            return True
        except ImportError:
            logger.error(
                "odfpy library not installed. Please install odfpy to process ODS files."
            )
            return False
        except Exception as e:
            logger.error(f"Error extracting ODS text: {e}")
            return False

    def _extract_text_from_odp(self, document: Document) -> bool:
        """Extract text from a LibreOffice Impress (ODP) document.

        Args:
            document: ODP document

        Returns:
            True if successful, False otherwise
        """
        try:
            # Attempt to use odfpy library for extraction
            from odf import draw, teletype, text
            from odf.opendocument import load

            presentation = load(document.file_path)

            # Get all slides (pages)
            slides = presentation.getElementsByType(draw.Page)

            extracted_text = ""
            word_count = 0
            slide_count = len(slides)

            # Process each slide
            for slide_idx, slide in enumerate(slides, 1):
                slide_name = slide.getAttribute("name") or f"Slide {slide_idx}"
                extracted_text += f"Slide: {slide_name}\n\n"

                # Get all text frames in this slide
                frames = slide.getElementsByType(draw.Frame)
                for frame in frames:
                    # Get text boxes in this frame
                    textboxes = frame.getElementsByType(draw.TextBox)
                    for textbox in textboxes:
                        # Get paragraphs in this text box
                        paras = textbox.getElementsByType(text.P)
                        for para in paras:
                            para_text = teletype.extractText(para)
                            extracted_text += para_text + "\n"
                            word_count += len(para_text.split())

                extracted_text += "\n\n"

            # Update document with text content
            document.content = extracted_text
            document.word_count = word_count
            document.page_count = slide_count
            document.metadata["word_count"] = word_count
            document.metadata["slide_count"] = slide_count
            document.metadata["page_count"] = slide_count

            # Save updated document
            self.document_repository.save(document)

            return True
        except ImportError:
            logger.error(
                "odfpy library not installed. Please install odfpy to process ODP files."
            )
            return False
        except Exception as e:
            logger.error(f"Error extracting ODP text: {e}")
            return False

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        return self.document_repository.get_by_id(document_id)

    def get_all_documents(self) -> List[Document]:
        """Get all documents.

        Returns:
            List of all documents
        """
        return self.document_repository.get_all()

    def save_document(self, document: Document) -> bool:
        """Save a document.

        Args:
            document: Document to save

        Returns:
            True if successful, False otherwise
        """
        return self.document_repository.save(document)

    def delete_document(self, document_id: str) -> bool:
        """Delete a document.

        This will remove both the database entry and the file.

        Args:
            document_id: Document ID

        Returns:
            True if successful, False otherwise
        """
        document = self.document_repository.get_by_id(document_id)

        if not document:
            logger.error(f"Document not found: {document_id}")
            return False

        # Delete file
        try:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
        except Exception as e:
            logger.error(f"Error deleting document file: {e}")
            return False

        # Delete from repository
        return self.document_repository.delete(document_id)

    def search_documents(
        self,
        query: str = "",
        category: Optional[str] = None,
        doc_type: Optional[DocumentType] = None,
        tag_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Document]:
        """Search for documents with various filters.

        Args:
            query: Text search query
            category: Filter by category
            doc_type: Filter by document type
            tag_ids: Filter by tag IDs
            date_from: Filter by creation date (from)
            date_to: Filter by creation date (to)

        Returns:
            List of matching documents
        """
        # Get documents and total count
        documents, _ = self.document_repository.search(
            query=query,
            category=category,
            doc_type=doc_type,
            tags=tag_ids,
            date_from=date_from,
            date_to=date_to,
        )

        return documents

    def add_tag_to_document(self, document_id: str, tag_id: str) -> bool:
        """Add a tag to a document.

        Args:
            document_id: Document ID
            tag_id: Tag ID

        Returns:
            True if successful, False otherwise
        """
        document = self.document_repository.get_by_id(document_id)

        if not document:
            logger.error(f"Document not found: {document_id}")
            return False

        document.add_tag(tag_id)
        return self.document_repository.save(document)

    def remove_tag_from_document(self, document_id: str, tag_id: str) -> bool:
        """Remove a tag from a document.

        Args:
            document_id: Document ID
            tag_id: Tag ID

        Returns:
            True if successful, False otherwise
        """
        document = self.document_repository.get_by_id(document_id)

        if not document:
            logger.error(f"Document not found: {document_id}")
            return False

        document.remove_tag(tag_id)
        return self.document_repository.save(document)

    def set_document_category(
        self, document_id: str, category_id: Optional[str]
    ) -> bool:
        """Set the category for a document.

        Args:
            document_id: Document ID
            category_id: Category ID, or None to clear

        Returns:
            True if successful, False otherwise
        """
        document = self.document_repository.get_by_id(document_id)

        if not document:
            logger.error(f"Document not found: {document_id}")
            return False

        document.category = category_id
        return self.document_repository.save(document)

    def get_documents_by_category(self, category_id: str) -> List[Document]:
        """Get all documents in a category.

        Args:
            category_id: Category ID

        Returns:
            List of documents
        """
        return self.document_repository.get_by_category(category_id)
