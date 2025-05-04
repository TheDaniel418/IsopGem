### /gematria/ui/widgets
This directory contains reusable widget components for the Gematria functionality, including the main calculator widget, calculation detail display, and the floating virtual keyboard for non-Latin input.

#### Key Files
- `word_abacus_widget.py`: Main calculator widget for gematria calculations, now supports a floating virtual keyboard for Hebrew/Greek input.
- `calculation_detail_widget.py`: Widget for displaying detailed calculation results.
- `virtual_keyboard_widget.py`: Floating virtual keyboard for Hebrew/Greek input, used by `word_abacus_widget.py` to allow users to input non-Latin characters easily.
- `.cursor/mcp.json`: Stores configuration for MCP servers, including GitHub, MCP Installer, @21st-dev/magic, and now context7 (for Upstash Context7 MCP integration). 

### /astrology
This directory contains the core astrology pillar, focused on birth chart calculations and essential astrological models, services, and UI components. All planner, event, and database manager features have been removed for a streamlined, chart-centric architecture.

#### Key Files & Directories
- `__init__.py`: Exposes main astrology components and sets up the pillar.
- `models/`: Data models for charts, aspects, zodiac, and celestial bodies.
  - `chart.py`: Chart and NatalChart models for birth chart calculations.
  - `aspect.py`: Aspect models for planetary relationships.
  - `zodiac.py`: Zodiac sign, house, and related models.
  - `celestial_body.py`: Models for planets and other celestial bodies.
- `services/`: Core services for astrological calculations and chart management.
  - `astrology_calculation_service.py`: Real-time calculation engine for planetary positions and aspects.
  - `chart_service.py`: Chart creation and management logic.
  - `kerykeion_service.py`: Integration with the Kerykeion astrology library.
  - `location_service.py`: Handles location data for charts.
  - `grand_fusion_service.py`: (If still present) Advanced or experimental chart features.
  - `zodiac_conrune_division.py`: Service for Zodiac and Kamea/Conrune division logic. Provides methods to retrieve Zodiac and Kamea factors, and to map Ditrune/Conrune pairs to Zodiacal and Kamea segments for visualization and analysis, using the assets/cvs/day_count.csv mapping.
- `ui/`: User interface components for astrology features.
  - `widgets/`: UI widgets for birth chart display, planetary positions, and midpoints.
    - `birth_chart_widget.py`: Main widget for displaying birth charts.
    - `location_search_widget.py`: Widget for searching and selecting locations.
    - `midpoints_widget.py`, `planetary_positions_widget.py`, etc.: Additional chart-related widgets.
  - `dialogs/`: Dialog windows for birth chart and location search.
    - `birth_chart_window.py`: Dialog for viewing/editing a birth chart.
    - `location_search_window.py`: Dialog for searching locations.
  - `astrology_tab.py`: Main tab UI for the astrology pillar.
- `utils/`: Utility functions (currently minimal).
- `data/`: (If present) Data files for astrology (currently empty).

### /astrology/utils
Utility functions for the astrology pillar, supporting mathematical and structural operations used throughout the system.

#### Key Files
- `__init__.py`: Marks the directory as a Python package.
- `factorization.py`: Provides functions to generate and return the factors of 360 (Zodiac) and 364 (Kamea/Prime Ditrune structure), supporting visualization and analysis features that require these mathematical divisions.

### /astrology/ui/panels
This directory contains additional UI components for the astrology pillar.

#### Key Files
- `zodiac_conrune_division_panel.py`: PyQt6 panel for visualizing Zodiac and Kamea/Conrune divisions. Displays the factors of 360 and 364, and is designed for future graphical enhancements such as wheel visualizations, using the ZodiacConruneDivisionService for data. 

### /document_manager/ui/panels
This directory contains additional UI components for the document manager.

#### Key Files
- `notes_manager_panel.py`: Main panel for the notes management functionality
- `notes_browser_panel.py`: Panel for browsing and managing notes

### /document_manager/services
This directory contains services for the document manager.

#### Key Files
- `notes_service.py`: Service for managing notes

### /document_manager/repositories
This directory contains repositories for the document manager.

#### Key Files
- `notes_repository.py`: Data access for notes

### /document_manager/models
This directory contains models for the document manager.

#### Key Files
- `note.py`: Note data model

### /document_manager/ui/dialogs
This directory contains dialogs for the document manager.

#### Key Files
- `quick_note_dialog.py`: Dialog for quick note creation/editing

**Update:** The Notes Manager feature and all related files have been purged from the codebase as of [date]. 