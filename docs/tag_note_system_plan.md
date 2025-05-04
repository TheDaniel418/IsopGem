# Tag-Based Note Management System: Architecture & Implementation Plan

---

## 1. Requirements Clarification

**Core Needs:**
- Flexible, tag-based note organization (not rigid folders)
- Visual, user-friendly UI inspired by OneNote (canvas, preview, quick actions)
- Universal search (across all notes, not just tags)
- Note properties (name, date, size, tags, UUID)
- Tag management (create, edit, delete, merge tags)
- Support for rich content (text, images, possibly sketches)
- **Rich Text Editing:** Use the `RTFEditorWindow` from `shared/ui/widgets/rtf_editor` as the main note editor, supporting formatted text, tables, images, and Unicode (Greek, Hebrew, etc.).
- Support for attachments (PDFs, audio, images, etc.)
    - **Attachment Storage Policy:** All attachments are stored in a default directory, such as a subdirectory of the notes (e.g., `/attachments/{note_uuid}/`).
    - **Attachment Opening Policy:** When a user opens an attachment, the app will use the system's default application for that file type.
- Quick access panel for related tools/features
- Cross-pillar communication (send/receive messages or data with other pillars/modules)
- **Unicode & Multilingual Support:** All text fields (note content, names, tags, attachment filenames) must support Greek, Hebrew, and other Unicode scripts for input, storage, search, and display.
- **Backup & Export:** Users can export and import all notes, tags, and attachments for backup or migration.
- **Extensibility:** The architecture must be highly extensible to support future features, new content types, analytics, or integrations.

**Assumptions:**
- Single-user only
- Desktop-first, but responsive for tablet use
- Data stored locally (no cloud, no sync, no collaboration)
- Strictly offline; no internet access or external API calls
- Privacy/security not a concern
- **Tech Stack:** Python 3.11, PyQt6, and all currently implemented libraries in the app. Whoosh will be added as the only new dependency for full-text search.

**Note Naming & Identity Policy:**
- Each note has a unique, immutable UUID (universally unique identifier) used for all internal, cross-pillar, and reference operations.
- Each note also has a user-defined, editable name for display, search, and organization.
- The name is not required to be unique; multiple notes can share the same name, but each is always uniquely identified by its UUID.
- All references, links, and cross-pillar messages use the UUID, not the name.
- The name is always associated with the UUID in the data model.

**Questions for Further Clarification:**
- Any integration with external tools/services required? (Assumed no)

---

## 2. System Overview

The system will provide a modern, tag-centric note-taking experience with a flexible UI, allowing users to create, organize, and retrieve notes efficiently. The architecture will separate business logic, data storage, and presentation for maintainability and scalability. All data is stored locally for a single user; there are no cloud, sync, or collaboration features. The application will operate strictly offline, with no internet access. A cross-pillar communication interface will enable integration and messaging with other modules in the application. Full-text search and indexing will be powered by the Whoosh library. Each note is uniquely identified by a UUID, with a user-defined name for display and search. **All text fields and search must support Unicode, including Greek and Hebrew scripts.**

**Backup & Export:**
- The system will provide a way for users to export and import all notes, tags, and attachments for backup, migration, or manual recovery.

**Extensibility:**
- The architecture will use modular, decoupled components and clear interfaces to make it easy to add new features, content types, analytics, or integrations in the future.

---

## 3. Component Breakdown

### 1. **UI Layer**
   - **Main Window:** Hosts all panels and navigation.
   - **Tag Selector Menu:** Displays all tags, allows selection and management.
   - **Files List Panel:** Shows notes for the selected tag(s).
   - **Note Preview Panel:** Displays selected note content.
   - **Note Properties Panel:** Shows and edits note metadata, including name and UUID.
   - **Tag Manager Panel:** For advanced tag operations.
   - **Quick Access Panel:** Shortcuts to tools/features.
   - **Search Bar & Results Panel:** Universal search interface (powered by Whoosh, must support Unicode input and display).
   - **Attachment Management UI:** Upload, preview, remove, and open attachments from notes. "Open" uses the system's default application for the file type.
   - **Backup/Export UI:** Interface for exporting and importing notes, tags, and attachments.
   - **Rich Text Editor Integration:** Embed the `RTFEditorWindow` as the main note editing/viewing component. Integrate save/load logic with the note data model. Images are handled natively; other attachments are managed via the attachment system.

### 2. **Business Logic Layer**
   - **Note Service:** CRUD operations, tag assignment, note linking, attachment handling, UUID management. All text fields must be Unicode. Integrate with `RTFEditorWindow` for saving/loading note content.
   - **Tag Service:** Tag CRUD, merging, analytics, suggestions. Tag names must support Unicode.
   - **Search Service:** Full-text and tag-based search, filters (using Whoosh, configured for Unicode/Greek/Hebrew support).
   - **Cross-Pillar Communication Service:** Interface for sending/receiving messages or data with other pillars/modules, always referencing notes by UUID.
   - **Backup/Export Service:** Handles export and import of all notes, tags, and attachments.

### 3. **Data Layer**
   - **Note Repository:** Persistent storage for notes, each with UUID and user-defined name. All text fields are Unicode.
   - **Tag Repository:** Persistent storage for tags and relationships. Tag names are Unicode.
   - **Attachment Storage:** Local file system, with all attachments stored in a default directory structure (e.g., `/attachments/{note_uuid}/`). Filenames and paths support Unicode.
   - **Whoosh Index:** Local Whoosh index for fast full-text search and retrieval. Indexes Unicode text fields.
   - **Backup/Export Storage:** Exported files (e.g., ZIP, JSON, or custom format) containing all notes, tags, and attachments.

---

## 4. Note Data Model Example

```python
{
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Σημειώσεις Έργου",  # Greek example
    "content": "פגישה על פרויקט X",  # Hebrew example
    "tags": ["meeting", "projectX", "σημείωση", "פגישה"],
    "created_at": "2024-06-10T14:30:00Z",
    "modified_at": "2024-06-10T15:00:00Z",
    "attachments": [
        {"filename": "סיכום.pdf", "path": "/attachments/a1b2c3d4/סיכום.pdf"}
    ]
}
```
- All internal operations (edit, delete, link, cross-pillar comms) use the UUID.
- The name, content, tags, and attachment filenames are Unicode and support Greek/Hebrew.

---

## 5. Interfaces & Data Flow

```
UI[UI Layer] -->|User Actions| NoteService
UI -->|User Actions| TagService
UI -->|Search Queries| SearchService
UI -->|Attachment Actions| NoteService
UI -->|Cross-Pillar Events| CrossPillarService
UI -->|Backup/Export Actions| BackupExportService
NoteService -->|CRUD| NoteRepository
NoteService -->|Attachment CRUD| AttachmentStorage
TagService -->|CRUD| TagRepository
SearchService -->|Index/Query| WhooshIndex
BackupExportService -->|Export/Import| BackupExportStorage
NoteRepository <--> TagRepository
NoteService <--> TagService
CrossPillarService <--> OtherPillars
```

- **User interacts with UI** (selects tags, creates/edits notes, manages attachments, searches, exports/imports data; all text fields support Unicode input/display)
- **UI calls business logic services** (NoteService, TagService, SearchService, CrossPillarService, BackupExportService)
- **Services interact with repositories** for persistent storage
- **NoteService manages attachments via AttachmentStorage**
- **SearchService uses Whoosh for fast full-text search and retrieval, including Greek/Hebrew text**
- **BackupExportService handles export/import of all notes, tags, and attachments**
- **CrossPillarService enables communication with other pillars/modules, always referencing notes by UUID**

---

## 6. Unicode & Multilingual Support

- **All text fields (note content, names, tags, attachment filenames) must support Unicode, including Greek and Hebrew scripts.**
- **Database:** Use UTF-8 encoding for all text fields (default in Python 3.11 and most DBs).
- **UI:** All input fields, labels, and displays in PyQt6 must be Unicode-aware. Choose fonts that support Greek and Hebrew.
- **Search (Whoosh):** Configure analyzers/tokenizers to handle Greek and Hebrew scripts for accurate indexing and searching. For basic search, Whoosh will index and search Unicode text as-is.
- **Attachments:** Support Unicode filenames and paths.
- **Testing:** Validate input, storage, search, and display with Greek and Hebrew examples.

---

## 7. Implementation Strategy

**Phase 1: Core Functionality**
- UI skeleton: main window, tag selector, files list, note preview
- Note and tag CRUD (create, read, update, delete)
- Basic tag assignment and filtering
- Universal search (text-based, powered by Whoosh, with Unicode support)
- Local storage (e.g., SQLite, JSON, or lightweight DB)
- Basic attachment support (add/remove/view attachments, Unicode filenames, store in default directory structure, open with system default app)
- UUID generation and management for all notes
- **Rich Text Editor Integration:** Integrate `RTFEditorWindow` for note editing and viewing. Connect save/load logic to the note data model. Test with Greek/Hebrew input and large notes.
- **Standard error handling:** Use normal methods for error detection, reporting, and recovery (e.g., try/except, logging, user notifications).

**Phase 2: Enhanced Features**
- Tag management tools (merge, analytics, color coding)
- Rich content support (images, formatting)
- Quick access panel and shortcuts
- Tag-based smart filters and saved searches
- Responsive design for tablet use
- Enhanced attachment features (previews, drag-and-drop, attachment metadata)
- **Backup/Export:** Implement export/import UI and logic for notes, tags, and attachments.

**Phase 3: Cross-Pillar Communication & Advanced Features**
- Implement cross-pillar communication interface (event bus, message queue, or shared service), always referencing notes by UUID
- AI-powered tag suggestions and analytics
- Integration with external tools (if ever required)
- **Extensibility:** Continue to modularize and decouple components to support future features and integrations.

---

## 8. Risks & Considerations

- **Attachment File Size & Storage:** Large attachments may impact local storage; consider file size limits or warnings. Ensure directory structure is managed and cleaned up on note deletion.
- **Performance:** Large numbers of notes/tags/attachments may slow search—Whoosh indexing is critical.
- **Extensibility:** Architecture must remain modular and decoupled to support future features and integrations.
- **Cross-Pillar Communication Robustness:** Ensure messaging is decoupled and does not create tight dependencies between pillars. All cross-pillar references to notes must use UUIDs.
- **Unicode Handling:** Ensure all layers (UI, storage, search) are tested and validated for Greek, Hebrew, and other Unicode scripts.
- **Backup/Export Integrity:** Ensure exported/imported data is validated and error handling is robust.
- **Error Handling:** Use standard error handling methods (try/except, logging, user notifications) throughout the system.

---

## 9. Next Steps

1. **Finalize Requirements:**  
   - Confirm must-have features, nice-to-haves, and any technical constraints.
2. **UI/UX Prototyping:**  
   - Create wireframes/mockups for all major panels and flows, including attachment management and cross-pillar communication points.
3. **Select Tech Stack:**  
   - Use Python 3.11, PyQt6, and all currently implemented libraries in the app. Add Whoosh as the only new dependency for full-text search.
4. **Define Data Models:**  
   - Draft schemas for notes, tags, attachments, and relationships, ensuring UUID is the primary identifier for notes.
5. **Set Up Project Structure:**  
   - Implement initial skeleton with clear separation of concerns.
6. **Iterative Development:**  
   - Build core features, test with users, and refine.

---

## 10. File Structure: 5-Pillar Architecture for Note Manager

The note manager feature will be implemented under `document_manager/note_manager/` following the 5-pillar architecture. This ensures clear separation of concerns, maintainability, and extensibility.

```
document_manager/
└── note_manager/
    ├── models/
    │   ├── note.py                # Note data structure, types, validation
    │   ├── tag.py                 # Tag data structure, types
    │   └── attachment.py          # Attachment data structure, types
    ├── repositories/
    │   ├── note_repository.py     # Handles note DB interactions
    │   ├── tag_repository.py      # Handles tag DB interactions
    │   ├── attachment_repository.py # Handles attachment storage/retrieval
    │   └── interfaces.py          # Repository interfaces/abstractions
    ├── services/
    │   ├── note_service.py        # Business logic for notes
    │   ├── tag_service.py         # Business logic for tags
    │   ├── attachment_service.py  # Business logic for attachments
    │   ├── search_service.py      # Whoosh integration, search logic
    │   ├── backup_export_service.py # Backup/export logic
    │   ├── cross_pillar_service.py  # Cross-pillar communication logic
    │   └── interfaces.py          # Service interfaces/abstractions
    ├── ui/
    │   ├── components/
    │   │   ├── note_editor.py     # Integrates RTFEditorWindow
    │   │   ├── tag_selector.py
    │   │   ├── files_list_panel.py
    │   │   ├── note_properties_panel.py
    │   │   ├── attachment_manager.py
    │   │   ├── backup_export_ui.py
    │   │   └── ...
    │   ├── styles/
    │   │   └── note_manager.qss   # (Optional) Stylesheets
    │   └── main_window.py         # Main window for the note manager
    └── utils/
        ├── helpers.py             # Helper functions, pure utilities
        ├── constants.py           # Shared constants
        └── validators.py          # Validation logic for models, input, etc.
```

**Pillar Descriptions:**
- **models/**: Data structures, types, and validation for notes, tags, and attachments.
- **repositories/**: Data access layer for notes, tags, and attachments. Handles all DB and file system interactions.
- **services/**: Business logic, search (Whoosh), backup/export, cross-pillar communication, and service interfaces.
- **ui/**: All UI components, including the main window, note editor (integrating RTFEditorWindow), tag selector, and attachment manager.
- **utils/**: Pure helper functions, shared constants, and validation logic.

This structure ensures:
- Clear separation of concerns
- No cross-pillar imports except via interfaces
- UI interacts with services only (not repositories directly)
- Utils are pure and reusable
- Easy extensibility for future features

--- 