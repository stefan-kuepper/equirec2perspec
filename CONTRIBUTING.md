# Contributing to Equirec2Perspec

This document provides guidelines for contributing to the Equirec2Perspec project, designed for both human contributors and AI agents.

## Quick Start for Contributors

```bash
# Clone and setup
git clone https://github.com/stefan-kuepper/equirec2perspec.git
cd equirec2perspec
uv sync --all-extras

# Run pre-commit checks (same as CI)
./scripts/lint.sh
./scripts/test.sh
```

## Development Workflow

### 1. Making Changes

- Edit code in `src/equirec2perspec/`
- Follow existing code style (ruff will enforce this)
- Add tests for new functionality in `tests/`

### 2. Quality Checks

Before submitting, run all quality gates:

```bash
# Lint and format (must pass)
uv run ruff check
uv run ruff format

# Type checking (must pass)  
uv run mypy src/equirec2perspec

# Tests with coverage (must pass, min 80% coverage)
uv run pytest --cov=src/equirec2perspec --cov-report=term-missing
```

### 3. Testing Strategy

- **Unit tests**: Test individual functions/classes (`-m unit`)
- **Integration tests**: Test end-to-end functionality (`-m integration`)
- **Coverage**: Maintain minimum 80% test coverage
- **Performance**: Use `@pytest.mark.slow` for performance-intensive tests

## Code Standards

### Style
- Use `ruff` for formatting and linting
- Follow PEP 8 and existing code patterns
- Type hints required for all public APIs

### Architecture
- Single-module design in `src/equirec2perspec/Equirec2Perspec.py`
- Core class: `Equirectangular` with `GetPerspective()` method
- Coordinate utilities: `xyz2lonlat()`, `lonlat2XY()`

### Performance Guidelines
- Prefer vectorized NumPy operations
- Use `cv2.remap` for efficient image resampling
- Leverage TurboJPEG when available (auto-detected)

## Submitting Changes

### For Humans
1. Fork the repository
2. Create a feature branch
3. Make changes with passing tests
4. Submit a pull request

### For AI Agents
1. Make changes directly in the working directory
2. Run quality checks before completion
3. Ensure all tests pass and coverage is maintained
4. Follow existing code patterns and conventions

## Quality Gates

All contributions must pass:
- ✅ **Linting**: No `ruff check` errors
- ✅ **Formatting**: Code matches `ruff format` standards  
- ✅ **Type Checking**: All code passes `mypy` strict mode
- ✅ **Tests**: All tests pass across Python 3.9-3.12
- ✅ **Coverage**: Minimum 80% test coverage

## Dependencies

- **Required**: numpy, opencv-python
- **Optional**: pyturbojpeg (for faster JPEG loading)
- **Development**: pytest, ruff, mypy, coverage

## Getting Help

- Check existing issues and discussions
- Review test files for usage examples
- Consult `AGENTS.md` for detailed development environment info
- See `README.md` for API documentation and examples