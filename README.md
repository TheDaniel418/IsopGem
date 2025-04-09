# IsopGem

<p align="center">
  <h1 align="center">🔯✨ IsopGem ✨🔯</h1>
</p>

A comprehensive tool for sacred geometry, gematria, and esoteric document analysis. IsopGem provides scholars, researchers, and enthusiasts with a unified environment for exploring numerical patterns in ancient texts, geometric principles in sacred architecture, and interconnected symbolic systems.

## 🔍 Features

### Gematria Analysis
- Support for Hebrew, Greek, and English gematria systems
- Over 20 calculation methods across all language systems
- Word/phrase analysis with extensive results
- Custom cipher creation and management
- Calculation history with search, filtering, and tagging
- Word abacus for rapid computations
- Import word lists from spreadsheets with automatic language detection

### Sacred Geometry Tools
- Platonic solid visualizations and measurements
- Golden ratio calculator and visualizer
- Sacred geometric pattern generator
- Measurement conversion between ancient and modern units

### Document Analysis
- Text pattern recognition across multiple languages
- Concordance generator
- Frequency analysis of words and phrases
- Integration with gematria calculations

### Astrological Calculations
- Planetary position calculations
- Astrological chart generation
- Timing calculations for celestial events
- Integration with document and gematria analysis

## 🏗️ Architecture

IsopGem follows a domain-pillar architecture with five main pillars:

1. **Gematria** - Hebrew, Greek, and English numerical analysis tools
2. **Geometry** - Sacred geometry visualization and calculation tools
3. **Document Manager** - Analysis of texts and documents
4. **Astrology** - Astrological calculations and visualizations
5. **TQ** - Trigrammaton QBLH integration and advanced pattern analysis

Each pillar is organized into consistent components:
- **UI (User Interface)** - PyQt6-based interface components
- **Services** - Business logic and core functionality
- **Models** - Data structures and type definitions
- **Repositories** - Data access and persistence
- **Utils** - Helper functions and utilities

## ⚙️ Development Setup

### Prerequisites

- Python 3.12 or higher
- PyQt6
- pip
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/isopgem.git
cd isopgem
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements/dev.txt
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
    enabled: false
  astrology:
    enabled: false
  tq:
    enabled: false

ui:
  window:
    title: "IsopGem - Sacred Geometry & Gematria"
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

Note: Test files are excluded from pre-commit checks.

## 📁 Project Structure

```
isopgem/
├── astrology/            # Astrology pillar
├── config/               # Configuration files
├── docs/                 # Documentation
│   └── FILE_TRACKER.md   # File tracking and documentation
├── document_manager/     # Document analysis pillar
├── gematria/             # Gematria pillar
│   ├── models/           # Data models
│   ├── repositories/     # Data access
│   ├── services/         # Business logic
│   ├── ui/               # User interface
│   │   ├── dialogs/      # Popup dialogs
│   │   ├── panels/       # Main panels
│   │   ├── widgets/      # Reusable UI components
│   │   └── windows/      # Window components
│   └── utils/            # Utilities
├── geometry/             # Sacred geometry pillar
├── shared/               # Shared components
│   ├── models/           # Shared data models
│   ├── services/         # Shared services
│   ├── ui/               # Shared UI components
│   │   └── window_management.py  # Window manager
│   └── utils/            # Shared utilities
│       ├── app.py        # Application initialization
│       ├── cli.py        # Command-line interface
│       └── config.py     # Configuration management
├── tq/                   # Trigammaton Qabalah pillar
├── main.py               # Application entry point
├── pyproject.toml        # Project metadata
├── README.md             # Project documentation
└── requirements/         # Dependency specifications
    ├── base.txt          # Base dependencies
    ├── dev.txt           # Development dependencies
    └── test.txt          # Testing dependencies
```

## 🌌 Pillars Overview

### Trigammaton Qabalah (TQ)

The TQ pillar implements an innovative metaphysical-mathematical system based on ternary (base-3) numbers. Key features include:

- **Ternary Number System**: Uses 0, 1, and 2 digits to represent Tao/Void, Yang/Active, and Yin/Receptive forces
- **Geometric Mapping**: Maps ternary numbers to geometric elements (vertices, edges, faces) in multi-dimensional hypercubes
- **Quadset Analysis**: Tools for analyzing relationships between sets of four related ternary numbers
- **Ternary Transitions**: Implementation of the Ternary Transition System for transformational operations
- **Conrune Visualization**: Visual representation system for ternary numbers
- **Metaphysical Framework**: Combines mathematical precision with philosophical depth

The TQ system creates a bridge between number, form, and metaphysical principles, offering a unique approach to pattern analysis and transformation.

### Gematria

The Gematria pillar provides tools for analyzing and working with Hebrew, Greek, and other alphanumeric systems. Key features include:

- **Multiple Calculation Methods**: Support for traditional and modern gematria calculation methods
- **Cross-Reference Analysis**: Find words and phrases with matching gematria values
- **Semantic Insights**: Discover meaningful connections between terms with equivalent numeric values
- **Historical Context**: Access to traditional and historical gematria interpretations
- **Export and Sharing**: Save and share gematria analysis results

This pillar facilitates deep exploration of the numerical relationships within sacred texts and other written works.

### Geometry

The Geometry pillar focuses on sacred geometry principles and visualization. Key features include:

- **Sacred Shape Generation**: Create and manipulate traditional sacred geometry forms
- **Geometric Analysis**: Analyze proportions and relationships within geometric constructions
- **Measurement Tools**: Precise tools for working with sacred measurements and ratios
- **Dynamic Visualization**: Interactive visualization of geometric transformations
- **Overlay System**: Compare and align different geometric systems

This pillar helps users explore the mathematical beauty and significance of sacred geometry patterns.

### Document Manager

The Document Manager pillar provides capabilities for importing, organizing, and analyzing documents. Key features include:

- **Multi-format Support**: Import and work with PDF, DOCX, TXT and other document formats
- **Text Extraction**: Automatically extract text content for analysis
- **Organization System**: Categorize and tag documents for easy retrieval
- **Search Capabilities**: Powerful full-text search across document collections
- **Cross-pillar Integration**: Connect document content with other pillars for comprehensive analysis

This pillar serves as a research foundation, helping users organize and extract insights from their document collections.

### Astrology

The Astrology pillar offers tools for astrological calculations and chart analysis. Key features include:

- **Chart Generation**: Create natal, transit, and other astrological charts
- **Multiple Traditions**: Support for Western, Vedic, and other astrological systems
- **Aspect Analysis**: Identify and analyze planetary aspects and configurations
- **Timing Tools**: Determine auspicious times using astrological principles
- **Visual Representation**: Clear visual presentation of astrological data

This pillar provides precise astrological calculations and interpretations for personal and research purposes.

## 🌐 Contributing

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Run tests to ensure functionality
4. Run pre-commit hooks to ensure code quality
5. Submit a pull request

## 📚 Documentation

Additional documentation is available in the `docs/` directory.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or support, please contact us at support@isopgem.com
