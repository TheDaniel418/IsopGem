# Technical Specifications for Tag Note System

This document provides detailed technical specifications for implementing the Tag-Based Note Management System, including data structures, algorithms, interfaces, and implementation patterns.

## 1. Data Structures

### Note Model

```python
class Note:
    uuid: str  # UUID4 string
    name: str  # Unicode string, user-defined name
    content: str  # Unicode RTF content
    tags: List[Tag]  # Many-to-many relationship
    attachments: List[Attachment]  # One-to-many relationship
    created_at: datetime
    modified_at: datetime
    
    # Methods
    add_tag(tag: Tag) -> None
    remove_tag(tag: Tag) -> None
    add_attachment(attachment: Attachment) -> None
    remove_attachment(attachment: Attachment) -> None
    update_content(content: str) -> None
    to_dict() -> Dict
    from_dict(data: Dict) -> Note  # Class method
```

### Tag Model

```python
class Tag:
    uuid: str  # UUID4 string
    name: str  # Unicode string, user-defined name
    color: str  # Hex color code (e.g., "#FF5733")
    notes: List[Note]  # Many-to-many relationship
    
    # Methods
    add_note(note: Note) -> None
    remove_note(note: Note) -> None
    to_dict() -> Dict
    from_dict(data: Dict) -> Tag  # Class method
```

### Attachment Model

```python
class Attachment:
    uuid: str  # UUID4 string
    filename: str  # Unicode string, original filename
    path: str  # Relative path to attachment storage
    mime_type: str  # MIME type (e.g., "image/jpeg")
    size: int  # File size in bytes
    note_uuid: str  # UUID of parent note
    created_at: datetime
    
    # Methods
    get_absolute_path() -> str
    to_dict() -> Dict
    from_dict(data: Dict) -> Attachment  # Class method
```

## 2. Database Schema

### SQLite Schema

```sql
-- Notes table
CREATE TABLE notes (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    content TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);

-- Tags table
CREATE TABLE tags (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT NOT NULL
);

-- Note-Tag relationship (many-to-many)
CREATE TABLE note_tags (
    note_uuid TEXT NOT NULL,
    tag_uuid TEXT NOT NULL,
    PRIMARY KEY (note_uuid, tag_uuid),
    FOREIGN KEY (note_uuid) REFERENCES notes(uuid) ON DELETE CASCADE,
    FOREIGN KEY (tag_uuid) REFERENCES tags(uuid) ON DELETE CASCADE
);

-- Attachments table
CREATE TABLE attachments (
    uuid TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    size INTEGER NOT NULL,
    note_uuid TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (note_uuid) REFERENCES notes(uuid) ON DELETE CASCADE
);

-- Search index metadata
CREATE TABLE search_index_metadata (
    last_updated TEXT NOT NULL
);
```

## 3. API Interfaces

### Repository Interfaces

```python
class INoteRepository(ABC):
    @abstractmethod
    def create(self, note: Note) -> Note:
        pass
        
    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[Note]:
        pass
        
    @abstractmethod
    def get_all(self) -> List[Note]:
        pass
        
    @abstractmethod
    def get_by_tag(self, tag_uuid: str) -> List[Note]:
        pass
        
    @abstractmethod
    def update(self, note: Note) -> Note:
        pass
        
    @abstractmethod
    def delete(self, uuid: str) -> bool:
        pass
```

Similar interfaces for `ITagRepository` and `IAttachmentRepository`.

### Service Interfaces

```python
class INoteService(ABC):
    @abstractmethod
    def create_note(self, name: str, content: str = "", tags: List[str] = None) -> Note:
        pass
        
    @abstractmethod
    def get_note(self, uuid: str) -> Optional[Note]:
        pass
        
    @abstractmethod
    def get_all_notes(self) -> List[Note]:
        pass
        
    @abstractmethod
    def get_notes_by_tag(self, tag_uuid: str) -> List[Note]:
        pass
        
    @abstractmethod
    def update_note(self, uuid: str, name: str = None, content: str = None) -> Note:
        pass
        
    @abstractmethod
    def delete_note(self, uuid: str) -> bool:
        pass
        
    @abstractmethod
    def add_tag_to_note(self, note_uuid: str, tag_uuid: str) -> Note:
        pass
        
    @abstractmethod
    def remove_tag_from_note(self, note_uuid: str, tag_uuid: str) -> Note:
        pass
```

Similar interfaces for `ITagService`, `IAttachmentService`, `ISearchService`, etc.

## 4. File System Structure

### Attachment Storage

```
/attachments/
  /{note_uuid}/
    /{attachment_uuid}_{filename}
```

### Search Index

```
/search_index/
  /notes/
  /tags/
  /metadata.json
```

### Backup/Export

```
/backups/
  /{timestamp}_backup.zip
```

## 5. Algorithms

### Search Indexing

1. Create Whoosh schema for notes and tags
2. For each note:
   - Extract text content from RTF
   - Index note name, content, and tag names
   - Store UUID for retrieval
3. For each tag:
   - Index tag name
   - Store UUID for retrieval
4. Implement incremental indexing for updates

### Tag Suggestion

1. Analyze note content using TF-IDF
2. Compare with existing tag corpus
3. Rank tags by relevance score
4. Return top N suggestions

### Backup/Export

1. Create temporary directory
2. Export notes and tags to JSON
3. Copy attachments to temporary directory
4. Create ZIP archive
5. Clean up temporary directory

## 6. UI Component Specifications

### Main Window Layout

```
+-----------------------------------------------+
| Menu Bar                                      |
+-----------------------------------------------+
| Toolbar                                       |
+-----------------------------------------------+
| +----------+ +---------------------------+    |
| |          | |                           |    |
| | Tag      | | Note List                 |    |
| | Selector | |                           |    |
| |          | |                           |    |
| |          | |                           |    |
| +----------+ +---------------------------+    |
|                                               |
| +-------------------------------------------+ |
| |                                           | |
| | Note Editor / Preview                     | |
| |                                           | |
| |                                           | |
| |                                           | |
| +-------------------------------------------+ |
|                                               |
| +----------+ +---------------------------+    |
| |          | |                           |    |
| | Note     | | Attachment List           |    |
| | Props    | |                           |    |
| |          | |                           |    |
| +----------+ +---------------------------+    |
+-----------------------------------------------+
| Status Bar                                    |
+-----------------------------------------------+
```

### UI Component Hierarchy

```
MainWindow
├── MenuBar
├── Toolbar
├── SplitterLayout
│   ├── TagSelectorPanel
│   ├── NoteListPanel
│   ├── NoteEditorPanel
│   │   └── RTFEditorWindow (embedded)
│   ├── NotePropertiesPanel
│   └── AttachmentPanel
└── StatusBar
```

## 7. Cross-Pillar Communication Protocol

### Data Packet Structure

```json
{
  "source": "note_manager",
  "destination": "astrology_module",
  "operation": "note_reference",
  "timestamp": "2024-06-15T14:30:00Z",
  "payload": {
    "note_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "action": "view",
    "context": {
      "section": "chart_analysis"
    }
  }
}
```

### Standard Operations

- `note_reference`: Reference a note from another pillar
- `note_update`: Notify that a note has been updated
- `note_delete`: Notify that a note has been deleted
- `tag_update`: Notify that a tag has been updated
- `search_request`: Request a search from another pillar
- `data_request`: Request specific data from another pillar

## 8. Error Handling Strategy

### Exception Hierarchy

```
BaseError
├── RepositoryError
│   ├── DatabaseError
│   ├── FileSystemError
│   └── ConcurrencyError
├── ServiceError
│   ├── ValidationError
│   ├── BusinessRuleError
│   └── OperationError
├── UIError
│   ├── RenderingError
│   └── InputError
└── IntegrationError
    ├── CrossPillarError
    └── ExternalSystemError
```

### Error Handling Pattern

```python
try:
    # Operation that might fail
    result = perform_operation()
    return result
except ValidationError as e:
    # Log and handle validation errors
    log.warning(f"Validation error: {e}")
    show_user_friendly_error(str(e))
    return None
except DatabaseError as e:
    # Log and handle database errors
    log.error(f"Database error: {e}")
    show_error_dialog("Database operation failed")
    return None
except Exception as e:
    # Log and handle unexpected errors
    log.critical(f"Unexpected error: {e}")
    show_error_dialog("An unexpected error occurred")
    return None
```

## 9. Performance Considerations

### Search Optimization

- Use incremental indexing for updates
- Implement caching for frequent searches
- Use background indexing for large documents
- Optimize query parsing for performance

### UI Responsiveness

- Implement lazy loading for large documents
- Use background threads for long operations
- Implement progress reporting for user feedback
- Use pagination for large result sets

### Memory Management

- Implement resource cleanup for attachments
- Use weak references for large objects
- Implement memory monitoring and diagnostics
- Create cache eviction policies

## 10. Security Considerations

### Input Validation

- Sanitize all user input
- Validate file uploads
- Implement MIME type checking
- Validate Unicode input

### File System Security

- Use safe path construction
- Implement file size limits
- Create secure temporary files
- Implement proper file permissions

## 11. Testing Strategy

### Unit Testing

- Test each component in isolation
- Use mock objects for dependencies
- Test edge cases and error conditions
- Test Unicode support

### Integration Testing

- Test component interactions
- Test database operations
- Test file system operations
- Test cross-pillar communication

### System Testing

- Test end-to-end workflows
- Test performance with large data sets
- Test UI responsiveness
- Test error handling and recovery

## 12. Deployment Considerations

### Installation

- Create installation package
- Implement dependency checking
- Create database initialization
- Implement configuration setup

### Updates

- Implement version checking
- Create database migration
- Implement configuration migration
- Create backup before update

### Uninstallation

- Implement clean uninstallation
- Create data backup option
- Implement resource cleanup
- Remove configuration
