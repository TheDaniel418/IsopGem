# Document Manager

The document manager provides capabilities for importing, organizing, and searching various document types within the IsopGem application.

## Features

- **Document Importing**:
  - PDF, DOCX, TXT file support
  - LibreOffice formats (ODT, ODS, ODP) support
  - Single file import
  - Batch import functionality (multiple files or entire directories)
  - Parallel processing for improved import performance
  - Bulk category assignment during import
- **Text Extraction**: Automatically extracts text content from documents for searching
  - Support for proper Unicode Greek letter extraction from Symbol font
  - Intelligent detection and conversion of Greek text in older documents
- **Organization**:
  - Hierarchical categories for document organization
  - Tagging system for flexible organization
  - Custom metadata
- **Search Capabilities**:
  - Full-text search with SQLite FTS
  - Filter by category, tags, document type, and date
  - Combined search criteria
  - Proper handling of Greek characters in search queries

## Architecture

The Document Manager follows the Model-View-Controller (MVC) pattern:

### Models
- `Document`: Core data model representing a document and its metadata
- `DocumentCategory`: Model for representing hierarchical categories
- `DocumentType`: Enum defining supported document types (PDF, DOCX, TXT, ODT, ODS, ODP)
- `Annotation`: Model for document annotations and highlights

### Repositories
- `DocumentRepository`: Handles document persistence and retrieval
- `CategoryRepository`: Manages document categories
- `AnnotationRepository`: Stores and retrieves document annotations

### Services
- `DocumentService`: Business logic for document operations, text extraction, and search
  - Includes special handling for Windows Symbol font Greek characters
- `CategoryService`: Management of document categories and hierarchies

### UI Components
- `DocumentBrowserPanel`: Panel for browsing, searching, and managing documents
- `DocumentViewerDialog`: Dialog for viewing document content and metadata
- `CategoryManagerDialog`: UI for managing document categories

## Usage

### Importing Documents

Single document import:
```python
from document_manager.services.document_service import DocumentService

# Create service
doc_service = DocumentService()

# Import a document
document = doc_service.import_document('/path/to/document.pdf')
```

Batch import with category assignment:
```python
# Import multiple documents at once with category assignment
file_paths = ['/path/to/doc1.pdf', '/path/to/doc2.docx', '/path/to/doc3.odt']
category_id = "research_category_id"
documents = doc_service.batch_import_documents(
    file_paths,
    max_workers=4,
    category_id=category_id
)

# Import all documents from a directory with category assignment
documents = doc_service.import_documents_from_directory(
    '/path/to/documents', 
    recursive=True,
    max_workers=4,
    category_id=category_id
)
```

### Greek Text Support

The document manager detects and properly converts Greek text that might be encoded using Windows Symbol font:

```python
# Check if a document contains Greek text
document = doc_service.get_document(document_id)
has_greek = document.metadata.get("has_greek_text", False)

# The extracted text will already have any Greek characters properly converted
greek_text = document.content  # Contains proper Unicode Greek characters
```

### Managing Categories

```python
from document_manager.services.category_service import CategoryService

# Create service
cat_service = CategoryService()

# Create a category
research_category = cat_service.create_category("Research", description="Research materials")

# Create a subcategory
papers_category = cat_service.create_category(
    "Papers", 
    description="Published papers",
    parent_id=research_category.id
)

# Assign document to category
doc_service.set_document_category(document.id, research_category.id)
```

### Searching Documents

```python
# Basic search
results = doc_service.search_documents(query="quantum physics")

# Search with Greek terms (will work properly with Unicode Greek)
results = doc_service.search_documents(query="αβγ theory")

# Combined search
results = doc_service.search_documents(
    query="quantum physics",
    category="Research",
    doc_type=DocumentType.PDF,
    date_from=datetime(2023, 1, 1)
)
```

## UI Integration

To add the document browser panel to your application:

```python
from document_manager.ui.document_manager_panel import DocumentManagerPanel

# Create the panel
document_panel = DocumentManagerPanel(parent_widget)

# Add to your application's layout
layout.addWidget(document_panel)
```

## Dependencies

- `PyMuPDF`: For PDF processing
- `python-docx`: For DOCX processing
- `odfpy`: For LibreOffice documents (ODT, ODS, ODP)
- `pydantic`: For data validation
- `sqlite3`: For document storage and search

Install dependencies with:
```bash
pip install PyMuPDF python-docx odfpy pydantic
``` 