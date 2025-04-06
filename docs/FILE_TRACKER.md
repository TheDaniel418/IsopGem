# IsopGem File Tracker

This document tracks all the files in the IsopGem project, their purpose, and their status.

## Recently Changed Files

| Path | Description | Last Modified | Change Type |
| ---- | ----------- | ------------ | ----------- |
| shared/utils/app.py | Simplified Astrology and TQ pillars - kept tabs but removed buttons | 2025-04-06 | Modified |
| shared/utils/app.py | Simplified Geometry pillar - kept tab but removed buttons | 2025-04-06 | Modified |
| shared/ui/widgets/rtf_editor/rtf_editor_adapter.py | Removed adapter layer for direct RTFEditorWindow usage | 2025-04-06 | Removed |
| shared/ui/widgets/editor.py | Removed abstraction layer in favor of direct RTFEditorWindow usage | 2025-04-06 | Removed |
| shared/ui/widgets/rtf_editor/test_rtf_editor_adapter.py | Removed test for adapter class | 2025-04-06 | Removed |
| shared/ui/widgets/rtf_editor/__init__.py | Updated to remove references to deleted adapter | 2025-04-06 | Modified |
| test_editor.py | Updated to use RTFEditorWindow directly | 2025-04-06 | Modified |
| document_manager/ui/document_tab.py | Updated to use RTFEditorWindow directly | 2025-04-06 | Modified |
| shared/ui/widgets/rtf_editor/models/* | Moved and standardized document format models to RTF editor | 2023-11-02 | Added |
| shared/ui/widgets/qgem_editor/* | Removed in favor of RTFEditor implementation | 2023-11-02 | Removed |
| document_manager/models/qgem_document.py | Updated import for DocumentFormat | 2023-11-02 | Modified |
| document_manager/services/qgem_document_service.py | Updated import for DocumentFormat | 2023-11-02 | Modified |
| shared/utils/app.py | Removed old document window methods now handled by DocumentTab | 2023-11-01 | Modified |
| document_manager/ui/panels/document_manager_panel.py | Standardized window opening methods using open_window | 2023-11-01 | Modified |
| shared/utils/app.py | Updated to use DocumentTab class instead of tab_manager.add_window_button | 2023-10-31 | Modified |
| document_manager/ui/__init__.py | Updated to export DocumentTab class | 2023-10-31 | Modified |
| document_manager/__init__.py | Added DocumentTab to exports | 2023-10-31 | Modified |
| document_manager/ui/panels/document_manager_panel.py | Moved from ui/ to ui/panels/ to follow proper directory structure | 2023-10-30 | Moved |
| shared/ui/widgets/rtf_editor/* | Added stable rich text editor with table and image handling | 2023-10-29 | Added |
| test_rtf_editor.py | Added test script for the RTF editor | 2023-10-29 | Added |
| gematria/ui/panels/search_panel.py | Fixed unreachable statement MyPy error in _find_window_manager method | 2023-10-28 | Fixed |
| shared/ui/dialogs/database_maintenance_window.py | Fixed database stats by replacing get_favorites() with find_favorites() and other type safety improvements | 2023-10-28 | Fixed |
| shared/repositories/database.py | Fixed cursor return type in Database class for better type checking with MyPy | 2023-10-28 | Fixed |
| shared/repositories/sqlite_tag_repository.py | Improved created_at handling for Tag creation to fix type errors | 2023-10-28 | Fixed |
| shared/repositories/sqlite_calculation_repository.py | Fixed timestamp vs created_at property usage in save_calculation method | 2023-10-28 | Fixed |
| gematria/ui/dialogs/edit_tags_window.py | Improved tag editing with Apply button and better tag selection workflow | 2023-10-27 | Enhanced |
| gematria/ui/dialogs/tag_selection_dialog.py | Enhanced for better communication of selected tags | 2023-10-27 | Enhanced |
| shared/services/calculation_database_service.py | Updated to use SQLite repositories | 2023-10-26 | Modified |
| docs/architecture/MODEL_CHANGES.md | Updated documentation on calculation and tag models | 2023-10-25 | Updated |
| docs/architecture/DATABASE_DESIGN.md | Added documentation for SQLite database schema | 2023-10-25 | Added |
| shared/ui/widgets/rtf_editor/rtf_editor_window.py | Removed placeholder text from RTF Editor | 2025-04-06 | Modified |
| shared/ui/widgets/rtf_editor/rtf_editor_adapter.py | Deprecated in favor of using RTFEditorWindow directly | 2025-04-06 | Deprecated |
| shared/ui/widgets/editor.py | Deprecated in favor of using RTFEditorWindow directly | 2025-04-06 | Deprecated |

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

##### /geometry/ui/widgets
- `__init__.py`: Initialization and exports for geometry UI widgets.

##### /geometry/ui/dialogs
- `__init__.py`: Initialization and exports for geometry dialog components.

#### /geometry/utils
- `__init__.py`: Initialization and exports for geometry utilities.

### /tq
Components for additional specialized functionalities related to Trigrammaton Qabalah.

- `__init__.py`: Initialization and exports for the TQ package.

#### /tq/models
- `__init__.py`: Initialization and exports for TQ data models.

#### /tq/services
- `__init__.py`: Initialization and exports for TQ services.

#### /tq/repositories
- `__init__.py`: Initialization and exports for TQ data repositories.

#### /tq/ui
- `__init__.py`: Initialization and exports for TQ UI components.

##### /tq/ui/panels
- `__init__.py`: Initialization and exports for TQ UI panels.

##### /tq/ui/widgets
- `__init__.py`: Initialization and exports for TQ UI widgets.

##### /tq/ui/dialogs
- `__init__.py`: Initialization and exports for TQ dialog components.

#### /tq/utils
- `__init__.py`: Initialization and exports for TQ utilities.

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
- `__init__.py`: Initialization and exports for RTF editor models.
- `document_format.py`: Document format model defining the structure for rich text documents, including support for annotations, images, and tables.

##### /shared/ui/dialogs
- `__init__.py`: Initialization and exports for shared UI dialogs.
- `database_maintenance_window.py`: Window for database maintenance operations including cleaning, finding duplicates, optimization, and backup/restore functionality.

#### /shared/services
- `__init__.py`: Initialization and exports for shared services.

#### /shared/repositories
- `__init__.py`: Initialization and exports for shared data repositories.

#### /shared/models
- `__init__.py`: Initialization and exports for shared data models.

#### /shared/utils
- `__init__.py`: Initialization file for shared utilities.
- `app.py`: Core application utilities, including application startup and initialization.
- `cli.py`: Command-line interface utilities for the application, providing command parsing and execution.
- `config.py`: Configuration management utilities, handling application settings and preferences.

### /docs
Documentation files for the project.

- `FILE_TRACKER.md`: This file - centralized overview of all files.

### /tests
Test files for various components of the application.

- `conftest.py`: Test configuration and fixtures for pytest.
- `__init__.py`: Package initialization for tests.
- `run_window_test.py`: Script for running window-related tests.
- `window_verification_test.py`: Tests for verifying window functionality.
- `test_calculation_db.py`: Test script for checking the calculation database functionality.
- `test_calculation_history.py`: Test script for checking the calculation history panel functionality.
- `test_basic_functionality.py`: Basic functionality tests for the application.
- `test_document.py`: Demonstrates file documentation and tracking rule implementation.
- `test_pyqt.py`: PyQt test utilities.

#### /tests/unit
Unit tests for individual components.

- `__init__.py`: Package initialization for unit tests.

##### /tests/unit/shared
- `__init__.py`: Package initialization for shared component tests.

##### /tests/unit/shared/ui
- `conftest.py`: Test configuration and fixtures specific to UI testing.
- `__init__.py`: Package initialization for UI tests.
- `test_window_mode.py`: Tests for window mode functionality.

##### /tests/unit/shared/utils
- `test_config.py`: Unit tests for configuration utilities and settings management.

### /config
Configuration files and settings.

### /requirements
Project requirements files.

### /scripts
Utility scripts for development and operations.

### /logs
Application logs directory.

### /xnotes
Additional development notes and documentation.

- `__init__.py`: Initialization and exports for development notes.

### Root Files
- `main.py`: Application entry point.
- `run_tests.py`: Script for running tests with configuration.
- `pytest.ini`: Configuration file for pytest testing framework.
- `pyproject.toml`: Project configuration and dependencies.
- `setup.py`: Package setup configuration.
- `README.md`: Project overview and documentation.
- `test_document.py`: Demonstrates file documentation and tracking rule implementation.
- `.env`: Environment configuration (should be gitignored in production).
- `.env.example`: Example environment configuration template.
- `.gitignore`: Git ignore configuration.
- `.pre-commit-config.yaml`: Pre-commit hooks configuration.
- `mypy.ini`: MyPy type checking configuration.
- `test_pyqt.py`: PyQt test utilities.
- `test_basic_functionality.py`: Basic functionality tests.
- `verify_window_mode.py`: Verification script for window mode functionality.
- `__init__.py`: Root package initialization.
