# IsopGem File Tracker

This document provides a centralized overview of all files in the IsopGem project, organized by directory structure. Each entry includes the file path and a brief description of its purpose.

## Recently Changed
| File | Description | Date | Change Type |
|------|-------------|------|------------|
| `gematria/ui/dialogs/import_word_list_dialog.py` | Fixed type errors and improved type safety with explicit type conversions for pandas integration | 2023-04-05 | Modified |
| `gematria/ui/dialogs/import_word_list_dialog.py` | Added new dialog for importing word lists from CSV, Excel, and ODS files with column mapping and preview functionality | 2023-04-05 | Added |
| `gematria/ui/panels/word_abacus_panel.py` | Enhanced to support importing word lists | 2023-04-05 | Modified |
| `gematria/models/calculation_type.py` | Extended with new detection methods for determining calculation types | 2023-04-05 | Modified |
| `gematria/ui/dialogs/__init__.py` | Updated to export the new ImportWordListDialog class | 2023-04-05 | Modified |
| `gematria/models/tag.py` | Data model for categorizing and organizing gematria calculations | 2023-04-04 | Added |
| `gematria/models/calculation_result.py` | Enhanced data model for storing and retrieving calculation results with tags, notes, and favorite status | 2023-04-04 | Modified |
| `gematria/repositories/calculation_repository.py` | Repository for storing, retrieving, updating, and deleting calculation results | 2023-04-04 | Added |
| `gematria/repositories/tag_repository.py` | Repository for storing, retrieving, updating, and deleting tags | 2023-04-04 | Added |
| `gematria/services/calculation_database_service.py` | Unified service for managing gematria calculations and tags in the database | 2023-04-04 | Added |
| `gematria/services/gematria_service.py` | Updated to support calculation database service integration | 2023-04-04 | Modified |
| `gematria/ui/dialogs/save_calculation_dialog.py` | Dialog for saving calculations with tags, notes, and favorite status | 2023-04-04 | Added |
| `gematria/ui/dialogs/create_tag_dialog.py` | Dialog for creating and editing tags with name, color, and description | 2023-04-04 | Added |
| `gematria/ui/panels/calculation_history_panel.py` | UI panel for displaying and managing calculation history with filtering and sorting | 2023-04-04 | Added |
| `gematria/models/calculation_type.py` | Added get_calculation_type_name function to convert enum values to display names | 2023-04-04 | Modified |
| `gematria/ui/dialogs/tag_selection_dialog.py` | Dialog for selecting and managing tags for calculations | 2023-04-04 | Added |
| `gematria/ui/dialogs/edit_tags_window.py` | Window for editing tags associated with a calculation | 2023-04-04 | Added |
| `test_calculation_db.py` | Test script for checking the calculation database functionality | 2023-04-04 | Added |
| `test_calculation_history.py` | Test script for checking the calculation history panel functionality | 2023-04-04 | Added |
| `gematria/models/custom_cipher_config.py` | Data model for custom gematria cipher configurations with support for Hebrew, Greek, and English languages | 2023-11-09 | Added |
| `gematria/services/custom_cipher_service.py` | Service for managing custom cipher configurations, including saving, loading, and templating | 2023-11-09 | Added |
| `gematria/ui/dialogs/custom_cipher_dialog.py` | Dialog for creating and editing custom gematria ciphers with a comprehensive letter value editor | 2023-11-09 | Added |
| `gematria/services/gematria_service.py` | Updated to support custom cipher calculations in addition to predefined calculation types | 2023-11-09 | Modified |
| `gematria/models/calculation_result.py` | Enhanced to support custom cipher methods in calculation history | 2023-11-09 | Modified |
| `gematria/ui/widgets/word_abacus_widget.py` | Added custom cipher integration to the Word Abacus widget, including custom method categories and management button | 2023-11-09 | Modified |
| `gematria/ui/dialogs/gematria_help_dialog.py` | Updated to be non-modal and enhanced with detailed information about the Trigrammaton Qabalah system developed by R.L. Gillis | 2023-11-08 | Modified |
| `gematria/ui/panels/word_abacus_panel.py` | Modified to handle non-modal help dialog persistence and management | 2023-11-08 | Modified |
| `gematria/ui/dialogs/word_abacus_window.py` | Updated to use WordAbacusPanel instead of directly using WordAbacusWidget to include the help button | 2023-11-08 | Modified |
| `gematria/ui/dialogs/gematria_help_dialog.py` | Comprehensive help dialog explaining Hebrew, Greek, and English calculation methods with detailed descriptions and examples | 2023-11-08 | Added |
| `gematria/ui/widgets/word_abacus_widget.py` | Improved the UI with a nested dropdown structure to organize calculation methods by language (Hebrew, Greek, English) and category (Standard, Advanced, Substitution Ciphers). Enhanced styling and usability | 2023-11-07 | Modified |
| `gematria/models/calculation_type.py` | Added additional Hebrew calculation methods and their Greek equivalents, including large values, building, triangular, hidden, full name, individual square, and additive | 2023-11-07 | Modified |
| `gematria/services/gematria_service.py` | Implemented new Hebrew and Greek calculation methods with equivalent functionality across both systems | 2023-11-07 | Modified |
| `gematria/models/calculation_type.py` | Added comprehensive Greek isopsophy calculation methods | 2023-11-05 | Modified |
| `gematria/services/gematria_service.py` | Implemented Greek isopsophy methods with unique Greek terminology | 2023-11-05 | Modified |
| `gematria/services/gematria_service.py` | Added functionality to strip diacritical marks from Hebrew and Greek text | 2023-11-05 | Modified |
| `gematria/models/calculation_type.py` | Updated to include Greek Isopsophy and TQ English methods | 2023-11-05 | Modified |
| `test_document.py` | Demonstrates file documentation and tracking rules | 2023-11-05 | Added |
| `gematria/ui/gematria_tab.py` | UI tab for gematria functionality | 2023-11-05 | Added |
| `gematria/ui/panels/word_abacus_panel.py` | Updated the Word Abacus panel to include a scroll area for better user experience and consistent styling with the widget improvements | 2023-11-07 | Modified |
| `gematria/ui/widgets/word_abacus_widget.py` | Improved the UI with a nested dropdown structure to organize calculation methods by language (Hebrew, Greek, English) and category (Standard, Advanced, Substitution Ciphers). Enhanced styling and usability | 2023-11-07 | Modified |
| `shared/ui/window_management.py` | Core window management functionality | 2023-11-05 | Added |

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

##### /gematria/ui/widgets
UI widgets specific to gematria functionality.

##### /gematria/ui/windows
Custom windows for gematria-specific functionality.

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

### /geometry
Components for geometric analysis and visualization.

### /document_manager
Components for document handling and management.

### /astrology
Components for astrological calculations and analysis.

### /tq
Components for additional specialized functionalities.

### /shared
Core shared components, utilities, and services used across multiple pillars.

#### /shared/ui
- `__init__.py`: Initialization file for shared UI components.
- `window_management.py`: Core functionality for window management across the application.

##### /shared/ui/widgets
Shared UI widgets used across multiple pillars.

#### /shared/services
Shared services used across multiple pillars.

#### /shared/repositories
Shared data access repositories.

#### /shared/models
Shared data models and types.

#### /shared/utils
Shared utility functions and helpers.

### /docs
Documentation files for the project.

- `FILE_TRACKER.md`: This file - centralized overview of all files.

### /tests
Test files for various components of the application.

#### /tests/unit
Unit tests for individual components.

##### /tests/unit/shared/ui
- `test_window_mode.py`: Tests for window mode functionality.

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

### /gematria/models/calculation_type.py
Added comprehensive Greek isopsophy calculation methods | 2023-11-05 | Modified
