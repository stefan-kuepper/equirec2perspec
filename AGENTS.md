# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Equirec2Perspec is a Python library that converts equirectangular 360-degree panoramic images into standard perspective views. It uses OpenCV for image processing and NumPy for mathematical transformations.

## Development Environment Setup

### Prerequisites

1. **Install uv** (fast Python package manager):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and setup**:
   ```bash
   git clone https://github.com/stefan-kuepper/equirec2perspec.git
   cd equirec2perspec
   uv sync
   ```

3. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

4. **Optional: Install with TurboJPEG support**:
   ```bash
   uv sync --extra turbojpeg
   ```

## Local Development Commands

### Linting and Formatting

Run all lint checks (used in CI):
```bash
./scripts/lint.sh
```

Individual lint commands:
```bash
# Code style and error checking
uv run ruff check

# Code formatting check
uv run ruff format --check

# Auto-format code
uv run ruff format

# Type checking
uv run mypy src/equirec2perspec
```

### Testing

Run all tests with coverage:
```bash
./scripts/test.sh
```

Individual test commands:
```bash
# Basic test run
uv run pytest

# Run with coverage (like CI)
uv run pytest --cov=src/equirec2perspec --cov-report=xml --cov-report=term-missing

# Run specific test markers
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests

# Run specific test file
uv run pytest tests/test_specific.py
```

### Building and Publishing

```bash
# Build package
./scripts/build.sh

# Build manually
uv run build

# Check package (before publishing)
uv run twine check dist/*
```

## Version Control

This project uses **jj (Jujutsu)** as its version control system. Use `jj` commands instead of `git`.

## CI System

### GitHub Actions Workflows

The project uses GitHub Actions for automated testing and deployment:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - **Triggers**: Push to main, Pull Requests to main
   - **Lint Job**: Runs ruff, mypy, and format checks on Ubuntu with Python 3.12
   - **Test Matrix**: Runs tests on Ubuntu with Python 3.9, 3.10, 3.11, 3.12
   - **Coverage**: Generates coverage reports with 80% minimum threshold

2. **Publish Workflow** (`.github/workflows/publish.yml`):
   - **Triggers**: Tags pushed to repository
   - **Action**: Builds and publishes to PyPI using trusted publishing

3. **Update Dependencies Workflow** (`.github/workflows/update-deps.yml`):
   - **Triggers**: Weekly schedule
   - **Action**: Automatically updates dependencies and creates PR

### CI Environment

- **Runner**: ubuntu-latest
- **Python Management**: uv for fast dependency installation
- **Test Framework**: pytest with coverage reporting
- **Linting**: ruff for formatting/linting, mypy for type checking
- **Coverage Requirements**: Minimum 80% test coverage

### Local CI Simulation

To run the same checks as CI locally:

```bash
# Run lint checks (exact same as CI job)
./scripts/lint.sh

# Run tests with coverage (exact same as CI job)
COVERAGE=true ./scripts/test.sh

# Test with multiple Python versions (like CI matrix)
for version in 3.9 3.10 3.11 3.12; do
    PYTHON_VERSION=$version ./scripts/test.sh
done
```

### Quality Gates

- **Code Coverage**: Minimum 80% required to pass
- **Type Checking**: All code must pass mypy strict mode
- **Formatting**: Code must match ruff format standards
- **Linting**: No ruff check errors allowed
- **Tests**: All tests must pass across all supported Python versions

### Performance Optimization

- **TurboJPEG**: Optional dependency for 20-30% faster JPEG loading
- **uv**: Fast dependency installation and caching in CI
- **Parallel Testing**: pytest runs tests in parallel by default
- **Coverage Reports**: Generated in multiple formats (XML, HTML, terminal)

## Architecture

The library follows a simple single-module design:

- **`src/equirec2perspec/Equirec2Perspec.py`**: Core implementation containing:
  - `Equirectangular` class: Main interface that loads panorama and provides `GetPerspective()` method
  - `load_image()`: Image loading with automatic TurboJPEG detection
  - `xyz2lonlat()` / `lonlat2XY()`: Coordinate transformation utilities

### Transformation Pipeline

The perspective extraction uses this coordinate transformation chain:
```
2D Output Pixels → 3D Rays (via inverse camera matrix) → Rotated Rays (Rodrigues rotation) → Spherical Coords → Equirectangular Pixel Coords
```

Key math:
1. Build intrinsic camera matrix K from FOV and output dimensions
2. Generate 3D rays for each output pixel using K⁻¹
3. Apply rotation matrices for THETA (y-axis) and PHI (x-axis) using `cv2.Rodrigues`
4. Convert to spherical coordinates (longitude/latitude)
5. Map to input image coordinates and use `cv2.remap` for final sampling

## Package Structure

Uses `src` layout with `hatchling` build backend. The package exports `Equirectangular` class via `__init__.py`.

## Dependencies

- **Required**: numpy, opencv-python
- **Optional**: pyturbojpeg (auto-detected at runtime for faster JPEG decode)
