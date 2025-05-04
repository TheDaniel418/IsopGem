# IsopGem

<p align="center">
  <h1 align="center">🔯✨ IsopGem ✨🔯</h1>
</p>

A specialized application for exploring sacred geometry, gematria, and numerical patterns. IsopGem provides researchers and enthusiasts with tools for analyzing alphanumeric systems, visualizing geometric relationships, and exploring the Kamea Cosmic Calendar.

## 🔍 Features

### Gematria Analysis
- Support for Hebrew, Greek, and English gematria systems
- Multiple calculation methods for different traditions
- Word/phrase analysis with numerical results
- Custom cipher creation and basic management
- Calculation history storage
- Word abacus for computations

### Sacred Geometry Tools
- Platonic solid visualizations with basic OpenGL
- Polygonal number visualization in development
- Golden ratio calculator
- Measurement tools for geometric patterns

### Document Management
- Basic document organization
- Text extraction and analysis
- RTF editor with basic functionality
- Document categorization

### Kamea Cosmic Calendar
- Visualization of the Kamea calendar system
- Zodiacal position mapping
- Factor connection visualization (2, 3, 4, 5, 6, 8, 9, 10, 12)
- Conrune reversal pair analysis
- Radial and circular visualization modes

### Mathematical Tools
- Trigrammaton QBLH basic analysis
- Ternary dimension visualization
- Number properties explorer
- Pair finder with basic pattern detection
- Quadset analysis tools

## 🏗️ Architecture

IsopGem follows a domain-pillar architecture with five main pillars:

1. **Gematria** - Hebrew, Greek, and English numerical analysis tools
2. **Geometry** - Sacred geometry visualization and calculation tools
3. **Document Manager** - Analysis and organization of texts and documents
4. **Astrology** - Cosmic calendar and zodiacal mappings
5. **TQ** - Trigrammaton QBLH integration and pattern analysis

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

4. Install the package in development mode:
```bash
pip install -e .
```

### Running the Application

```bash
python main.py
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

## ⚙️ Configuration

Configuration is handled through YAML files located in the `config/` directory.

## 🔍 Code Quality

The project uses pre-commit hooks including:
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
├── gematria/                         # Gematria pillar
├── geometry/                         # Sacred geometry pillar
├── shared/                           # Shared components
├── tests/                            # Test suite
├── tq/                               # Trigrammaton Qabalah pillar
├── main.py                           # Application entry point
├── pyproject.toml                    # Project metadata
├── README.md                         # Project documentation
└── requirements.txt                  # Dependency specifications
```

## 🌟 Current Focus

### Kamea Cosmic Calendar
The recently implemented Kamea Cosmic Calendar visualization provides zodiacal pattern analysis and factor connections. The calendar is still being enhanced with additional features and refinements.

### Document Management
Basic document management functionality is available, with ongoing improvements to the text analysis capabilities.

### Geometry Module
The geometry module is being expanded with new visualization tools for exploring polygonal number systems and sacred geometry patterns.

## 🔮 Work in Progress

- Virtual keyboard for special characters
- Enhanced RTF editor with recovery utilities
- Document duplicate detection
- Advanced visualization options for geometric patterns
- Cross-pillar search capabilities
- Note manager with tagging system

## 📜 License

This project is proprietary software.

## 🙏 Acknowledgments

Special thanks to the esoteric research community for their valuable feedback and support.
