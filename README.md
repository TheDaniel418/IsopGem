# IsopGem

<p align="center">
  <h1 align="center">🔯✨ IsopGem ✨🔯</h1>
</p>

A comprehensive suite for esoteric research, combining sacred geometry, gematria, document analysis, and cosmic patterns. IsopGem provides scholars, researchers, and enthusiasts with a unified environment for exploring numerical patterns in ancient texts, geometric principles in sacred architecture, cosmic calendars, and interconnected symbolic systems.

## 🔍 Features

### Gematria Analysis
- Support for Hebrew, Greek, and English gematria systems
- Over 20 calculation methods across all language systems
- Word/phrase analysis with extensive results
- Custom cipher creation and management
- Virtual keyboard for special characters
- Calculation history with search, filtering, and tagging
- Word abacus for rapid computations
- Import word lists from spreadsheets with automatic language detection

### Sacred Geometry Tools
- Platonic solid visualizations with OpenGL
- Polygonal number systems visualization with interactive controls
- Star number visualizations and calculations
- Vault of Hestia sacred geometric templates
- Golden ratio calculator and visualizer
- Measurement conversion between ancient and modern units

### Document Management
- Text pattern recognition across multiple languages
- Document database with duplicate detection
- Rich Text Format (RTF) editor with recovery utilities
- Non-modal editing for multitasking
- Document categorization and tagging
- Concordance generator
- Frequency analysis of words and phrases
- Integration with gematria calculations

### Kamea Cosmic Calendar
- Interactive visualization of the Kamea calendar system
- Zodiacal position mapping with precise angle calculations
- Factor connection visualization (2, 3, 4, 5, 6, 8, 9, 10, 12)
- Conrune reversal pair analysis
- Radial and circular visualization modes
- Interactive lookup and information panel

### Cosmological & Mathematical Tools
- Trigrammaton QBLH analysis
- Ternary dimension visualization
- Number properties explorer
- Pair finder with pattern detection
- Quadset analysis tools

## 🏗️ Architecture

IsopGem follows a domain-pillar architecture with five main pillars:

1. **Gematria** - Hebrew, Greek, and English numerical analysis tools
2. **Geometry** - Sacred geometry visualization and calculation tools
3. **Document Manager** - Analysis and organization of texts and documents
4. **Astrology** - Cosmic calendar, zodiacal mappings, and visualizations
5. **TQ** - Trigrammaton QBLH integration and advanced pattern analysis

Each pillar is organized into consistent components:
- **UI (User Interface)** - PyQt6-based interface components
- **Services** - Business logic and core functionality
- **Models** - Data structures and type definitions
- **Repositories** - Data access and persistence
- **Utils** - Helper functions and utilities

## ⚙️ Development Setup

### Prerequisites

- Python 3.11 or higher
- PyQt6
- pip
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/TheDaniel418/IsopGem.git
cd IsopGem
```

2. Create a virtual environment:
```bash
python -m venv venv_py311
source venv_py311/bin/activate  # On Windows: venv_py311\Scripts\activate
```

3. Install dependencies using the main requirements file:
```bash
pip install -r requirements.txt
```

Alternative installation options:
- For development with linting tools: 
```bash
pip install -r requirements/dev.txt
```
- For running tests: 
```bash
pip install -r requirements/test.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

5. Set up pre-commit hooks:
```bash
pre-commit install
```

### Running the Application

```bash
python main.py
```

Or use the entry point script (after installation):
```bash
isopgem
```

## 🧪 Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov
```

Run specific tests:
```bash
pytest tests/unit/
pytest tests/integration/
```

## ⚙️ Configuration

Configuration files are located in the `config/` directory:

- `default.yaml` - Default configuration values
- `development.yaml` - Development environment overrides
- `production.yaml` - Production environment overrides

The active environment is determined by the `ISOPGEM_ENV` environment variable.

Example configuration:
```yaml
application:
  name: IsopGem
  version: "0.1.0"
  theme: "light"

pillars:
  gematria:
    enabled: true
  geometry:
    enabled: true
  document_manager:
    enabled: true
  astrology:
    enabled: true
  tq:
    enabled: true

ui:
  window:
    title: "IsopGem - Esoteric Research Suite"
    width: 1200
    height: 800
    maximize_on_start: false
  theme_colors:
    primary: "#4a6da7"
    secondary: "#8daad9"
    accent: "#fb8c00"
    background: "#f5f5f5"
    text: "#333333"
```

## 🔍 Code Quality

### Type Checking

Static type checking with mypy:
```bash
mypy .
```

### Code Formatting

- Format code with Black:
```bash
black .
```

- Sort imports with isort:
```bash
isort .
```

- Check code with ruff:
```bash
ruff check .
```

### Pre-commit Hooks

We use pre-commit hooks to enforce code quality standards. Hooks include:
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- black
- isort
- ruff
- mypy

## 📁 Project Structure

```
IsopGem/
├── astrology/                        # Astrology pillar
│   ├── models/                       # Data models
│   ├── repositories/                 # Data access
│   ├── services/                     # Business logic
│   ├── ui/                           # User interface
│   │   ├── dialogs/                  # Popup dialogs
│   │   ├── panels/                   # Main panels
│   │   ├── widgets/                  # Reusable UI components
│   │   │   └── kamea_calendar/       # Kamea Cosmic Calendar components
│   │   └── windows/                  # Window components
│   └── utils/                        # Utilities
├── assets/                           # Static assets
│   ├── cvs/                          # CSV data files
│   └── geometry/                     # Geometry assets
├── config/                           # Configuration files
├── docs/                             # Documentation
│   ├── kamea/                        # Kamea Cosmic Calendar documentation
│   ├── geometry_tasks/               # Geometry implementation documentation
│   ├── note_manager_tasks/           # Note manager documentation
│   └── FILE_TRACKER.md               # File tracking and documentation
├── document_manager/                 # Document analysis pillar
│   ├── models/                       # Document models
│   ├── repositories/                 # Document data access
│   ├── services/                     # Document business logic
│   └── ui/                           # Document UI
│       ├── dialogs/                  # Document dialogs
│       ├── panels/                   # Document panels
│       └── widgets/                  # Document widgets
├── gematria/                         # Gematria pillar
│   ├── models/                       # Data models
│   ├── repositories/                 # Data access
│   ├── services/                     # Business logic
│   ├── ui/                           # User interface
│   │   ├── dialogs/                  # Popup dialogs
│   │   ├── panels/                   # Main panels
│   │   ├── widgets/                  # Reusable UI components
│   │   └── windows/                  # Window components
│   └── utils/                        # Utilities
├── geometry/                         # Sacred geometry pillar
│   ├── calculator/                   # Geometry calculators
│   ├── models/                       # Geometry models
│   ├── services/                     # Geometry services
│   └── ui/                           # Geometry UI
│       ├── dialogs/                  # Geometry dialogs
│       ├── panels/                   # Geometry panels
│       └── widgets/                  # Geometry widgets
├── shared/                           # Shared components
│   ├── models/                       # Shared data models
│   ├── repositories/                 # Shared repositories
│   ├── services/                     # Shared services
│   ├── ui/                           # Shared UI components
│   │   ├── components/               # Reusable UI components
│   │   ├── dialogs/                  # Common dialogs
│   │   ├── widgets/                  # Shared widgets
│   │   │   └── rtf_editor/           # Rich Text Format editor
│   │   └── window_management.py      # Window manager
│   └── utils/                        # Shared utilities
│       ├── app.py                    # Application initialization
│       ├── cli.py                    # Command-line interface
│       └── config.py                 # Configuration management
├── tests/                            # Test suite
│   ├── integration/                  # Integration tests
│   └── unit/                         # Unit tests
│       ├── document_manager/         # Document manager tests
│       ├── note_manager/             # Note manager tests
│       └── shared/                   # Shared component tests
├── tq/                               # Trigrammaton Qabalah pillar
│   ├── models/                       # TQ models
│   ├── repositories/                 # TQ data access
│   ├── services/                     # TQ services
│   ├── ui/                           # TQ UI components
│   │   ├── dialogs/                  # TQ dialogs
│   │   ├── panels/                   # TQ panels
│   │   ├── styles/                   # TQ styling
│   │   └── widgets/                  # TQ widgets
│   └── utils/                        # TQ utilities
├── main.py                           # Application entry point
├── pyproject.toml                    # Project metadata
├── README.md                         # Project documentation
└── requirements.txt                  # Dependency specifications

```

## 🌟 Key Features Highlight

### Kamea Cosmic Calendar
The Kamea Cosmic Calendar provides a unique visualization of temporal and zodiacal patterns. The interactive radial display makes it easy to identify relationships between differentials, with precise calculations for zodiacal positions. The calendar offers factor connection visualization at key geometric intervals (60°, 120°, etc.) and conrune reversal pair analysis.

### Polygonal Number Visualization
The geometry module now includes comprehensive tools for visualizing and calculating polygonal number systems. The interactive controls allow real-time manipulation of geometric parameters, supporting triangular, square, pentagonal, hexagonal, and other polygonal sequences.

### Enhanced Document Management
The document manager now includes duplicate detection, database utilities, and a fully-featured RTF editor with recovery capabilities. The non-modal editing interface allows for multitasking while maintaining document integrity.

### Virtual Keyboard for Special Characters
A specialized virtual keyboard has been added to assist with entering characters from esoteric alphabets and symbol systems, making gematria calculations more accessible.

## 🔮 Future Directions

- Note manager with advanced tagging system
- Cross-pillar search capabilities
- Enhanced visualization export options
- Mobile companion application
- Cloud synchronization for research data

## 📜 License

This project is proprietary software.

## 🙏 Acknowledgments

Special thanks to the esoteric research community for their valuable feedback and support.
