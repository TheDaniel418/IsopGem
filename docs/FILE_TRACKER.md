# IsopGem File Tracker

This document provides a centralized overview of all files in the IsopGem project, organized by directory structure. Each entry includes the file path and a brief description of its purpose.

## Recently Changed
| File | Description | Date | Change Type |
|---|----|---|---|
| `shared/services/number_properties_service.py` | Enhanced service with support for general k-gonal numbers and centered polygonal numbers, including efficient caching and comprehensive number analysis capabilities | 2025-04-08 | Modified |
| `shared/ui/widgets/rtf_editor/*` | Comprehensive restructuring of RTF editor components with improved document management, table handling, and image editing capabilities | 2025-04-08 | Modified/Added |
| `tq/ui/widgets/ternary_visualizer.py` | New component for visualizing base-3 numbers using PNG images, enhancing the TQ functionality | 2025-04-08 | Added |
| `shared/ui/widgets/rtf_editor/models/document_format.py` | New model defining structure for rich text documents with support for annotations, images, and tables | 2025-04-08 | Added |
| `tq/ui/widgets/number_properties_panel.py` | Updated to display general polygonal numbers and centered polygonal numbers | 2025-04-08 | Modified |
| `shared/utils/app.py` | Fixed initialization order for NumberPropertiesService and CustomCipherService | 2025-04-08 | Modified |
| `gematria/services/calculation_database_service.py` | Non-singleton service used by NumberPropertiesPanel | 2025-04-08 | Referenced |
| `gematria/services/custom_cipher_service.py` | Non-singleton service used by NumberPropertiesPanel | 2025-04-08 | Referenced |
| `shared/utils/app.py` | Simplified Astrology and TQ pillars - kept tabs but removed buttons | 2025-04-06 | Modified |
| `shared/utils/app.py` | Simplified Geometry pillar - kept tab but removed buttons | 2025-04-06 | Modified |
| `shared/ui/widgets/rtf_editor/rtf_editor_adapter.py` | Removed adapter layer for direct RTFEditorWindow usage | 2025-04-06 | Removed |
| `shared/ui/widgets/editor.py` | Removed abstraction layer in favor of direct RTFEditorWindow usage | 2025-04-06 | Removed |
| `shared/ui/widgets/rtf_editor/test_rtf_editor_adapter.py` | Removed test for adapter class | 2025-04-06 | Removed |
| `shared/ui/widgets/rtf_editor/__init__.py` | Updated to remove references to deleted adapter | 2025-04-06 | Modified |
| `test_editor.py` | Updated to use RTFEditorWindow directly | 2025-04-06 | Modified |
| `document_manager/ui/document_tab.py` | Updated to use RTFEditorWindow directly | 2025-04-06 | Modified |
| `shared/ui/widgets/rtf_editor/models/*` | Moved and standardized document format models to RTF editor | 2023-11-02 | Added |
| `shared/ui/widgets/qgem_editor/*` | Removed in favor of RTFEditor implementation | 2023-11-02 | Removed |
| `document_manager/models/qgem_document.py` | Updated import for DocumentFormat | 2023-11-02 | Modified |
| `document_manager/services/qgem_document_service.py` | Updated import for DocumentFormat | 2023-11-02 | Modified |
| `shared/utils/app.py` | Removed old document window methods now handled by DocumentTab | 2023-11-01 | Modified |
| `document_manager/ui/panels/document_manager_panel.py` | Standardized window opening methods using open_window | 2023-11-01 | Modified |
| `shared/utils/app.py` | Updated to use DocumentTab class instead of tab_manager.add_window_button | 2023-10-31 | Modified |
| `document_manager/ui/__init__.py` | Updated to export DocumentTab class | 2023-10-31 | Modified |
| `document_manager/__init__.py` | Added DocumentTab to exports | 2023-10-31 | Modified |
| `document_manager/ui/panels/document_manager_panel.py` | Moved from ui/ to ui/panels/ to follow proper directory structure | 2023-10-30 | Moved |
| `shared/ui/widgets/rtf_editor/*` | Added stable rich text editor with table and image handling | 2023-10-29 | Added |
| `test_rtf_editor.py` | Added test script for the RTF editor | 2023-10-29 | Added |
| `gematria/ui/panels/search_panel.py` | Fixed unreachable statement MyPy error in _find_window_manager method | 2023-10-28 | Fixed |
| `shared/ui/dialogs/database_maintenance_window.py` | Fixed database stats by replacing get_favorites() with find_favorites() and other type safety improvements | 2023-10-28 | Fixed |
| `shared/repositories/database.py` | Fixed cursor return type in Database class for better type checking with MyPy | 2023-10-28 | Fixed |
| `shared/repositories/sqlite_tag_repository.py` | Improved created_at handling for Tag creation to fix type errors | 2023-10-28 | Fixed |
| `shared/repositories/sqlite_calculation_repository.py` | Fixed timestamp vs created_at property usage in save_calculation method | 2023-10-28 | Fixed |
| `gematria/ui/dialogs/edit_tags_window.py` | Improved tag editing with Apply button and better tag selection workflow | 2023-10-27 | Enhanced |
| `gematria/ui/dialogs/tag_selection_dialog.py` | Enhanced for better communication of selected tags | 2023-10-27 | Enhanced |
| `shared/services/calculation_database_service.py` | Updated to use SQLite repositories | 2023-10-26 | Modified |
| `docs/architecture/MODEL_CHANGES.md` | Updated documentation on calculation and tag models | 2023-10-25 | Updated |
| `docs/architecture/DATABASE_DESIGN.md` | Added documentation for SQLite database schema | 2023-10-25 | Added |
| `shared/ui/widgets/rtf_editor/rtf_editor_window.py` | Removed placeholder text from RTF Editor | 2025-04-06 | Modified |
| `shared/ui/widgets/rtf_editor/rtf_editor_adapter.py` | Deprecated in favor of using RTFEditorWindow directly | 2025-04-06 | Deprecated |
| `shared/ui/widgets/editor.py` | Deprecated in favor of using RTFEditorWindow directly | 2025-04-06 | Deprecated |
| `document_manager/services/qgem_document_service.py` | Improved error handling and type checking in service methods | 2025-04-07 | Modified |
| `document_manager/models/qgem_document.py` | Fixed field mappings and type handling in document conversion | 2025-04-07 | Modified |
| `shared/ui/widgets/rtf_editor/models/*` | Added models directory for RTF editor components | 2025-04-06 | Added |
| `shared/ui/widgets/qgem_editor/*` | Removed in favor of RTFEditor implementation | 2025-04-06 | Removed |
| `tq/ui/widgets/ternary_visualizer.py` | Created ternary digit visualizer for displaying base-3 numbers with PNG images | 2025-04-06 | Added |
| `tq/utils/ternary_transition.py` | Implemented Ternary Transition System for transforming ternary numbers | 2025-04-06 | Added |
| `tq/utils/ternary_converter.py` | Added utilities for converting between decimal and ternary number systems | 2025-04-06 | Added |
| `tq/ui/tq_tab.py` | Added ternary visualizer button to TQ tab | 2025-04-06 | Modified |
| `tq/ui/widgets/__init__.py` | Added package initialization for TQ UI widgets | 2025-04-06 | Added |
| `tq/ui/widgets/tq_grid_panel.py` | Added panel for displaying TQ Grid with base numbers and their transformations, including conrune and ternary digit reversal | 2025-04-06 | Added |

## Directory Structure

### /.cursor/rules
Configuration files for AI assistant rules and behaviors.

#### /.cursor/rules/core-rules
- `file-documentation-agent.mdc`: Rule enforcing comprehensive documentation for all new files.
- `file-tracker-agent.mdc`: Rule for maintaining this file tracker document.
- `project-architecture-agent.mdc`: Rule governing the 5-pillar project architecture.
- `rule-generating-agent.mdc`: Rule for maintaining consistency in rule creation.

#### /.cursor/rules/modes
- `README.md`: Documentation of available AI assistant modes and usage.
- `plan_mode.mdc`: Mode for system architecture and requirements planning.
- `code_mode.mdc`: Mode for implementing new features and components.
- `debug_mode.mdc`: Mode for troubleshooting and fixing issues.
- `refactor_mode.mdc`: Mode for improving code quality without changing functionality.
- `review_mode.mdc`: Mode for evaluating code quality and providing feedback.
- `test_mode.mdc`: Mode for creating test plans and implementations.
- `document_mode.mdc`: Mode for creating or improving documentation.
- `optimize_mode.mdc`: Mode for improving performance and efficiency.
- `ux_mode.mdc`: Mode for enhancing user interfaces and user experience.
- `learn_mode.mdc`: Mode for exploring and understanding unfamiliar code.
- `devops_mode.mdc`: Mode for handling deployment and infrastructure.
- `modularize_mode.mdc`: Mode for breaking down monolithic code into modules.
- `brainstorm_mode.mdc`: Mode for generating ideas without implementation details.

#### /.cursor/rules/my-rules
- `_communication-style-always.mdc`: Rule for custom communication style.

#### /.cursor/rules/global-rules
- `emoji-communication-always.mdc`: Rule for emoji usage in communication.

### /gematria
Components related to Hebrew gematria calculations and analysis.

#### /gematria/models
- `__init__.py`: Initialization and exports for the gematria models package.
- `calculation_type.py`: Defines calculation methods for Hebrew (gematria), Greek (isopsophy), and English (TQ) systems with corresponding terminology.
- `calculation_result.py`: Data model for storing and retrieving calculation results with support for tags, notes, and favorite status.
- `custom_cipher_config.py`: Data model for custom gematria cipher configurations, supporting Hebrew, Greek, and English alphabets with options for case sensitivity and final forms.
- `tag.py`: Data model for categorizing and organizing gematria calculations.

#### /gematria/services
- `__init__.py`: Initialization and exports for the gematria services package.
- `gematria_service.py`: Comprehensive calculation service supporting three writing systems (Hebrew, Greek, English) with multiple methods for each, including specialized substitution ciphers and custom-named Greek methods.
- `history_service.py`: Service for tracking and retrieving calculation history.
- `custom_cipher_service.py`: Service for managing custom gematria ciphers, including persistence, retrieval, and template generation.
- `calculation_database_service.py`: Unified service for managing gematria calculations and tags in the database with comprehensive search and filtering capabilities.

#### /gematria/ui
- `__init__.py`: Initialization and exports for the gematria UI components.
- `gematria_tab.py`: Main tab layout for gematria functionality in the application.

##### /gematria/ui/panels
- `__init__.py`: Initialization and exports for gematria UI panels.
- `word_abacus_panel.py`: UI panel providing visualization and interaction with the word abacus tool.
- `calculation_history_panel.py`: UI panel for displaying and managing calculation history with filtering, sorting, and detailed view.
- `search_panel.py`: Added new search panel that allows users to search for calculations in the database with multiple filter criteria
- `main_panel.py`: Main panel for the Gematria tab providing central UI layout and organization.
- `tag_management_panel.py`: Panel for managing gematria tags with creation, editing, and deletion capabilities.

##### /gematria/ui/widgets
UI widgets specific to gematria functionality.

- `__init__.py`: Initialization and exports for gematria UI widgets.
- `word_abacus_widget.py`: UI widget providing gematria calculation functionality.
- `calculation_detail_widget.py`: Widget for displaying detailed information about a selected calculation, including text, value, method, favorites, tags, and notes.

##### /gematria/ui/windows
- `__init__.py`: Initialization and exports for gematria window components.
- `gematria_window.py`: Standalone window implementation for gematria functionality with full UI capabilities.

##### /gematria/ui/dialogs
- `__init__.py`: Initialization and exports for gematria dialog components.
- `gematria_help_dialog.py`: Comprehensive help dialog with detailed explanations of all gematria calculation methods across Hebrew, Greek, and English systems, including original names, transliterations, meanings, and examples.
- `word_abacus_window.py`: Standalone window implementation for the Word Abacus calculator, uses the WordAbacusPanel to provide access to the help system.
- `custom_cipher_dialog.py`: Dialog for creating, editing, and managing custom gematria ciphers with a comprehensive letter value editor interface.
- `save_calculation_dialog.py`: Dialog for saving calculation results with tags, notes, and favorite status.
- `create_tag_dialog.py`: Dialog for creating and editing tags with name, color, and description.
- `tag_selection_dialog.py`: Dialog for selecting and managing tags for calculations.
- `edit_tags_window.py`: Window for editing tags associated with a calculation.
- `import_word_list_dialog.py`: Dialog for importing word lists from CSV, ODS, or Excel spreadsheets with column mapping and language detection capabilities.

#### /gematria/repositories
- `__init__.py`: Initialization and exports for gematria repositories.
- `calculation_repository.py`: Repository for storing, retrieving, updating, and deleting calculation results using JSON file persistence.
- `tag_repository.py`: Repository for storing, retrieving, updating, and deleting tags with support for default tag creation.

#### /gematria/utils
Utility functions and helpers specific to gematria calculations.

### /astrology
Components for astrological calculations and analysis.

- `__init__.py`: Initialization and exports for the astrology package.

#### /astrology/models
- `__init__.py`: Initialization and exports for astrology data models.

#### /astrology/services
- `__init__.py`: Initialization and exports for astrology services.

#### /astrology/repositories
- `__init__.py`: Initialization and exports for astrology data repositories.

#### /astrology/ui
- `__init__.py`: Initialization and exports for astrology UI components.

##### /astrology/ui/panels
- `__init__.py`: Initialization and exports for astrology UI panels.

##### /astrology/ui/widgets
- `__init__.py`: Initialization and exports for astrology UI widgets.

##### /astrology/ui/dialogs
- `__init__.py`: Initialization and exports for astrology dialog components.

#### /astrology/utils
- `__init__.py`: Initialization and exports for astrology utilities.

### /document_manager
Components for document handling and management.

- `__init__.py`: Initialization and exports for the document manager package.

#### /document_manager/models
- `__init__.py`: Initialization and exports for document manager data models.

#### /document_manager/services
- `__init__.py`: Initialization and exports for document manager services.

#### /document_manager/repositories
- `__init__.py`: Initialization and exports for document manager data repositories.

#### /document_manager/ui
- `__init__.py`: Initialization and exports for document manager UI components.

##### /document_manager/ui/panels
- `__init__.py`: Initialization and exports for document manager UI panels.

##### /document_manager/ui/widgets
- `__init__.py`: Initialization and exports for document manager UI widgets.

##### /document_manager/ui/dialogs
- `__init__.py`: Initialization and exports for document manager dialog components.

#### /document_manager/utils
- `__init__.py`: Initialization and exports for document manager utilities.

### /geometry
Components for geometric analysis and visualization.

- `__init__.py`: Initialization and exports for the geometry package.

#### /geometry/models
- `__init__.py`: Initialization and exports for geometry data models.

#### /geometry/services
- `__init__.py`: Initialization and exports for geometry services.

#### /geometry/repositories
- `__init__.py`: Initialization and exports for geometry data repositories.

#### /geometry/ui
- `__init__.py`: Initialization and exports for geometry UI components.

##### /geometry/ui/panels
- `__init__.py`: Initialization and exports for geometry UI panels.
- `regular_polygon_panel.py`: Panel for calculating properties of regular polygons
- `platonic_solid_panel.py`: Panel for calculating properties of Platonic solids
- `vault_of_hestia_panel.py`: Panel for exploring the Vault of Hestia geometric design (square, isosceles triangle, inscribed circle)

##### /geometry/ui/widgets
- `__init__.py`: Initialization and exports for geometry UI widgets.

##### /geometry/ui/dialogs
- `__init__.py`: Initialization and exports for geometry dialog components.

#### /geometry/utils
- `__init__.py`: Initialization and exports for geometry utilities.

### /tq
Components for Ternary Qabala (TQ) analysis and visualization.

- `__init__.py`: Initialization and exports for the TQ package.

#### /tq/models
- `__init__.py`: Initialization and exports for TQ data models.

#### /tq/services
- `__init__.py`: Initialization and exports for TQ services.

#### /tq/repositories
- `__init__.py`: Initialization and exports for TQ data repositories.

#### /tq/ui
- `__init__.py`: Initialization and exports for TQ UI components.
- `tq_tab.py`: Main tab for TQ functionality with Matrix-inspired background and buttons for TQ tools.

##### /tq/ui/panels
- `__init__.py`: Initialization and exports for TQ UI panels.

##### /tq/ui/widgets
- `__init__.py`: Initialization and exports for TQ UI widgets.
- `number_properties_panel.py`: Panel for displaying comprehensive properties of numbers in a tabbed interface, showing base number, conrune, ternary reversal, and reversal conrune with rich property details including polygonal and centered polygonal numbers. Includes gematria search functionality.
- `ternary_visualizer.py`: Created ternary digit visualizer for displaying base-3 numbers with PNG images.
- `tq_grid_panel.py`: Panel for displaying TQ Grid with base numbers and their transformations, including conrune and ternary digit reversal.

##### /tq/ui/dialogs
- `__init__.py`: Initialization and exports for TQ dialog components.

#### /tq/utils
- `__init__.py`: Initialization and exports for TQ utilities.
- `ternary_converter.py`: Utilities for converting between decimal and ternary number systems.
- `ternary_transition.py`: Implementation of Ternary Transition System for transforming ternary numbers.

### /shared
Core shared components, utilities, and services used across multiple pillars.

#### /shared/ui
- `__init__.py`: Initialization file for shared UI components.
- `window_management.py`: Core functionality for window management across the application.

##### /shared/ui/widgets
- `__init__.py`: Initialization and exports for shared UI widgets.

###### /shared/ui/widgets/rtf_editor
- `__init__.py`: Initialization and exports for the RTF editor package.
- `rtf_editor_window.py`: Main RTF editor window class with comprehensive rich text editing functionality.
- `rtf_editor_adapter.py`: Adapter class that integrates the RTF editor with IsopGem providing a consistent API.
- `format_toolbar.py`: Toolbar implementation for text formatting controls.
- `document_manager.py`: Manages document operations like save, open, and new document.
- `table_manager.py`: Manages table operations including creating, editing, and formatting tables.
- `image_manager.py`: Manages image operations including inserting, editing, and formatting images.
- `zoom_manager.py`: Manages zoom functionality for the editor.
- `image_properties_dialog.py`: Dialog for editing image properties.
- `image_editor_dialog.py`: Dialog for editing image content.
- `table_properties_dialog.py`: Dialog for editing table properties.
- `test_rtf_editor_adapter.py`: Test script for the RTF editor adapter.

####### /shared/ui/widgets/rtf_editor/models
- `
