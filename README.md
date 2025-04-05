# IsopGem

A comprehensive tool for sacred geometry, gematria, and esoteric document analysis.

## Project Structure

IsopGem follows a domain-pillar architecture with five main pillars:

1. **Gematria** - Hebrew numerical analysis tools
2. **Geometry** - Sacred geometry visualization and calculation tools
3. **Document Manager** - Analysis of texts and documents
4. **Astrology** - Astrological calculations and visualizations
5. **TQ** - (Placeholder for future features)

Each pillar is organized into consistent components:
- UI (User Interface) components
- Services (Business logic)
- Models (Data structures)
- Repositories (Data access)
- Utils (Helper functions)

## Development Setup

### Prerequisites

- Python 3.12 or higher
- PyQt6
- pip

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

### Running the Application

```bash
python -m shared.utils.cli
```

Or use the entry point script (after installation):
```bash
isopgem
```

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov
```

## Configuration

Configuration files are located in the `config/` directory:

- `default.yaml` - Default configuration values
- `development.yaml` - Development environment overrides
- `production.yaml` - Production environment overrides

The active environment is determined by the `ISOPGEM_ENV` environment variable.

## Type Checking

Static type checking with mypy:
```bash
mypy .
```

## Code Quality Tools

- Format code with Black:
```bash
black .
```

- Sort imports with isort:
```bash
isort .
```

- Check code with flake8:
```bash
flake8
```

## Contributing

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 