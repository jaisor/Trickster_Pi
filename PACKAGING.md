# Trickster Pi - Packaging and Distribution Guide

## Overview

This guide explains how to package and distribute the Trickster Pi project using modern Python packaging standards.

## Prerequisites

Ensure you have the following tools installed:

```bash
pip install --upgrade pip
pip install build twine setuptools wheel
```

## Project Structure for Packaging

```
Trickster_Pi/
├── src/                     # Source package
│   ├── __init__.py         # Package metadata
│   ├── main.py             # Entry point
│   ├── config.py           # Configuration
│   ├── audio_manager.py    # Audio handling
│   ├── gpio_controller.py  # Hardware control
│   ├── trickster_controller.py  # Main logic
│   └── api_routes.py       # REST API
├── pyproject.toml          # Modern Python packaging
├── setup.cfg               # Additional setuptools config
├── MANIFEST.in             # File inclusion rules
├── requirements.txt        # Dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
└── MODULES.md             # Module documentation
```

## Building the Package

### 1. Local Development Build

```bash
# Build the package
python -m build

# This creates:
# dist/trickster-pi-1.0.0.tar.gz      (source distribution)
# dist/trickster_pi-1.0.0-py3-none-any.whl  (wheel distribution)
```

### 2. Install from Local Build

```bash
# Install the wheel
pip install dist/trickster_pi-1.0.0-py3-none-any.whl

# Or install in development mode
pip install -e .
```

### 3. Verify Installation

```bash
# Test the command-line entry point
trickster-pi --help

# Or run directly
python -c "import src.main; src.main.main()"
```

## Development Installation

### Install with Development Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install with documentation dependencies
pip install -e ".[docs]"

# Install with all optional dependencies
pip install -e ".[dev,docs]"
```

## Distribution Options

### 1. GitHub Releases

Upload the built packages to GitHub releases:

```bash
# Tag the release
git tag v1.0.0
git push origin v1.0.0

# Upload dist/* files to the GitHub release
```

### 2. PyPI Distribution (if desired)

```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### 3. Private Package Repository

For organizational use, consider hosting on:
- GitLab Package Registry
- GitHub Packages
- Azure Artifacts
- JFrog Artifactory

## Package Features

### Command Line Interface

After installation, users can run:

```bash
trickster-pi
```

This executes `src.main:main()` function.

### Modular Installation

Users can install specific components:

```bash
# Basic installation
pip install trickster-pi

# With development tools
pip install trickster-pi[dev]

# With documentation tools
pip install trickster-pi[docs]
```

## Platform-Specific Dependencies

The `pyproject.toml` includes conditional dependencies:

- `RPi.GPIO`, `lgpio`, `rpi-lgpio` only install on ARM platforms
- Other dependencies install on all platforms
- This allows development on non-Raspberry Pi systems

## Version Management

Version is managed in two places:
1. `src/__init__.py` - `__version__ = "1.0.0"`
2. `pyproject.toml` - `version = "1.0.0"`

Keep these synchronized for consistency.

## Quality Assurance

The package includes configuration for:
- **Black**: Code formatting
- **isort**: Import sorting
- **MyPy**: Type checking
- **Flake8**: Linting
- **Pytest**: Testing
- **Coverage**: Test coverage

Run quality checks:

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
flake8 src/

# Run tests (when available)
pytest
```

## Docker Distribution (Optional)

Create a `Dockerfile` for containerized distribution:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Raspberry Pi GPIO
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install the package
COPY dist/trickster_pi-1.0.0-py3-none-any.whl /tmp/
RUN pip install /tmp/trickster_pi-1.0.0-py3-none-any.whl

# Set the entry point
CMD ["trickster-pi"]
```

## Continuous Integration

Consider setting up CI/CD with GitHub Actions:

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
        pip install -e ".[dev]"
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
```

This comprehensive packaging setup makes Trickster Pi easy to install, distribute, and maintain! 🎃📦
