# IsopGem File Tracker

This document tracks the files in the project and their purposes to make navigation and maintenance easier.

## Core Components

### Shared
- `shared/` - Common utilities and components used across the application
  - `shared/ui/` - UI-related components and widgets
    - `shared/ui/components/` - Reusable UI components
      - `shared/ui/components/message_box.py` - Standardized message box implementation
    - `shared/ui/widgets/` - Base widgets for UI consistency
      - `shared/ui/widgets/panel.py` - Base panel widget for consistent panel styling
  - `shared/utils/` - General utility functions and classes
  - `shared/db/` - Database-related utilities and services
  - `shared/services/` - Shared services used across multiple pillars
    - `shared/services/service_locator.py` - Service locator for dependency injection
    - `shared/services/tag_service.py` - Service for managing tags
    - `shared/services/number_properties_service.py` - Service for calculating and analyzing number properties

## Application Pillars

### Document Manager
- `document_manager/` - Document management functionality
  - `document_manager/models/` - Data models for documents and categories
    - `document_manager/models/document.py` - Document data model
    - `document_manager/models/document_category.py` - Document category model
  - `document_manager/repositories/` - Repository layer for data persistence
    - `document_manager/repositories/document_repository.py` - Document persistence
    - `document_manager/repositories/category_repository.py` - Category persistence
  - `document_manager/services/` - Business logic services
    - `document_manager/services/document_service.py` - Document operations
    - `document_manager/services/category_service.py` - Category operations
  - `document_manager/ui/` - User interface components
    - `document_manager/ui/document_manager_panel.py` - Main document manager panel
    - `document_manager/ui/panels/` - Panels for document management
      - `document_manager/ui/panels/document_browser_panel.py` - Browse and manage documents
    - `document_manager/ui/dialogs/` - Dialogs for document operations
      - `document_manager/ui/dialogs/document_viewer_dialog.py` - View document content
      - `document_manager/ui/dialogs/category_manager_dialog.py` - Manage categories

### Gematria
- `gematria/` - Gematria calculation and analysis functionality

### Geometry
- `geometry/` - Geometric visualization and analysis

### Astrology
- `astrology/` - Astrological computations and visualizations

### Text Quest (TQ)
- `tq/` - Text analysis and exploration tools
  - `tq/ui/` - User interface components for TQ
    - `tq/ui/tq_tab.py` - Main tab UI for TQ functionality
    - `tq/ui/widgets/` - Widgets for TQ visualization
      - `tq/ui/widgets/ternary_visualizer.py` - Visualizer for ternary digits
      - `tq/ui/widgets/tq_grid_panel.py` - TQ Grid panel for number analysis
      - `tq/ui/widgets/number_properties_panel.py` - Panel for displaying detailed number properties
  - `tq/services/` - Services for TQ functionality
    - `tq/services/tq_analysis_service.py` - Service for TQ Grid and Quadset Analysis

## Documentation and Configuration
- `docs/` - Documentation files
  - `docs/file_tracker.md` - This file
- `requirements/` - Project dependencies
  - `requirements/base.txt` - Core project dependencies
  - `requirements/dev.txt` - Development-specific dependencies
  - `requirements/test.txt` - Testing-specific dependencies
