# TODO - Best Practices Improvements

> Generated: 2026-01-06
> Overall Project Grade: C- (5.3/10)

## 🔴 Critical Priority (Do First)

### Testing Infrastructure
- [x] Add `pytest` as development dependency to pyproject.toml
- [x] Create `tests/` directory
- [x] Write unit tests for `load_image()` function
- [x] Write unit tests for `xyz2lonlat()` function
- [x] Write unit tests for `lonlat2XY()` function
- [x] Write unit tests for `GetPerspective()` method
- [x] Write integration tests with sample images
- [x] Add `pytest-cov` for coverage reporting
- [x] Target minimum 80% code coverage
- [ ] Add coverage badge to README

### CI/CD Pipeline
- [ ] Create `.github/workflows/` directory
- [ ] Add `ci.yml` workflow for automated testing
  - Test on Python 3.9, 3.10, 3.11, 3.12
  - Test on Ubuntu, macOS, Windows
  - Run linting checks
  - Run type checking
  - Generate coverage report
- [ ] Add `publish.yml` workflow for PyPI releases
  - Trigger on git tags
  - Build wheel and sdist
  - Publish to PyPI
- [ ] Add status badges to README

### Error Handling & Validation
- [ ] Add error handling in `load_image()` (line 11-19)
  - Validate path exists
  - Handle file read errors
  - Handle image decode errors
  - Provide clear error messages
- [ ] Add input validation in `GetPerspective()` (line 53-95)
  - Validate FOV range (e.g., 1-180 degrees)
  - Validate THETA and PHI ranges
  - Validate height > 0 and width > 0
  - Raise ValueError with descriptive messages
- [ ] Add validation in `__init__()` (line 48-50)
  - Check if image loaded successfully
  - Verify image has 3 channels (color)

### Remove Debug Code
- [ ] Replace `print("Using TurboJPEG")` with proper logging (line 6)
- [ ] Replace `print("USING opencv imread")` with proper logging (line 8)
- [ ] Add Python logging module with configurable levels
- [ ] Use logger.debug() for optional diagnostic output

---

## 🟡 High Priority (Do Soon)

### Code Quality Tools
- [ ] Add `ruff` as development dependency
- [ ] Create `ruff.toml` or add ruff config to `pyproject.toml`
  - Configure line length (e.g., 100)
  - Select rule sets (pycodestyle, pyflakes, etc.)
- [ ] Run `ruff format` on entire codebase
- [ ] Run `ruff check --fix` to auto-fix issues
- [ ] Add `.ruff_cache/` to .gitignore

### Type Hints
- [ ] Add return type hint to `load_image()` → `np.ndarray`
- [ ] Add type hints to `xyz2lonlat()` parameters and return
- [ ] Add type hints to `lonlat2XY()` parameters and return
- [ ] Add docstring and types to `__init__()`
- [ ] Add `mypy` as development dependency
- [ ] Create `mypy.ini` configuration file
- [ ] Create `py.typed` marker file in package
- [ ] Run mypy and fix any type errors
- [ ] Add mypy to CI pipeline

### Pre-commit Hooks
- [ ] Add `pre-commit` as development dependency
- [ ] Create `.pre-commit-config.yaml`
  - Add ruff linting
  - Add ruff formatting
  - Add mypy type checking
  - Add trailing whitespace check
  - Add end-of-file fixer
  - Add YAML validation
- [ ] Run `pre-commit install`
- [ ] Run `pre-commit run --all-files`

### Documentation
- [ ] Add docstring to `load_image()` function
- [ ] Add docstring to `xyz2lonlat()` function
- [ ] Add docstring to `lonlat2XY()` function
- [ ] Add docstring to `__init__()` method
- [ ] Improve docstring in `GetPerspective()` with examples
- [ ] Use consistent docstring style (Google or NumPy)
- [ ] Create `CONTRIBUTING.md`
  - Development setup instructions
  - How to run tests
  - How to submit PRs
  - Code style guidelines
- [ ] Create `CHANGELOG.md`
  - Document version history
  - Note breaking changes
- [ ] Consider adding `CODE_OF_CONDUCT.md`

---

## 🟢 Medium Priority (Do When Possible)

### Package Structure
- [ ] Consider migrating to src-layout
  - Move `equirec2perspec/` to `src/equirec2perspec/`
  - Update pyproject.toml build configuration
  - Update import statements
- [ ] Rename `src/` directory to `examples/` or `assets/`
  - More accurate name for image files
  - Prevents confusion with src-layout
- [ ] Create proper `examples/` directory
  - Add example scripts (not just images)
  - Add `basic_usage.py`
  - Add `advanced_usage.py`
  - Add `batch_processing.py`

### API Improvements
- [ ] Consider renaming `GetPerspective()` to `get_perspective()`
  - Follow PEP 8 naming conventions (lowercase with underscores)
  - Add deprecation warning for old name
  - Update documentation
- [ ] Add context manager support to `Equirectangular` class
  ```python
  with Equirectangular('image.jpg') as equ:
      img = equ.get_perspective(60, 0, 0, 720, 1080)
  ```
- [ ] Consider adding batch processing method
  ```python
  def get_perspectives_batch(views: List[ViewParams]) -> List[np.ndarray]
  ```

### Security & Best Practices
- [ ] Add `bandit` for security linting
- [ ] Add `safety` to check dependencies for vulnerabilities
- [ ] Run security scans in CI
- [ ] Add dependabot configuration for dependency updates
- [ ] Consider adding image size limits to prevent memory issues
- [ ] Add resource cleanup in error cases

### Performance
- [ ] Add benchmarks directory
- [ ] Create performance tests
  - Measure conversion speed for different resolutions
  - Measure memory usage
  - Compare with/without TurboJPEG
- [ ] Consider caching coordinate maps for repeated conversions
- [ ] Profile code for optimization opportunities

---

## 🔵 Low Priority (Nice to Have)

### Documentation Enhancements
- [ ] Set up Sphinx for API documentation
- [ ] Add `docs/` directory
- [ ] Configure ReadTheDocs or GitHub Pages
- [ ] Add more visual examples
- [ ] Add comparison with other libraries
- [ ] Add FAQ section

### Additional Features
- [ ] Add CLI interface using argparse or click
- [ ] Add progress bars for batch operations
- [ ] Add support for video conversion
- [ ] Add preview/thumbnail generation
- [ ] Consider adding GPU acceleration (CUDA)

### Development Tools
- [ ] Add `.editorconfig` for consistent formatting
- [ ] Add VS Code workspace settings
- [ ] Add PyCharm configuration
- [ ] Create Docker development environment
- [ ] Add Makefile for common tasks

### Community & Marketing
- [ ] Add GitHub issue templates
- [ ] Add PR template
- [ ] Add GitHub Discussions
- [ ] Submit to awesome-python lists
- [ ] Write blog post about the library
- [ ] Create demo video or GIF
- [ ] Add to Python Package Index classifiers

---

## ✅ Quick Wins (< 30 minutes each)

These can be done immediately for quick improvements:

1. **Add logging module** (5 min)
   - Import logging
   - Replace print() with logger.debug()

2. **Add basic input validation** (15 min)
   - Check FOV > 0
   - Check dimensions > 0
   - Raise ValueError with messages

3. **Add missing docstrings** (20 min)
   - Document all helper functions
   - Add parameter descriptions

4. **Create basic CI workflow** (30 min)
   - Simple GitHub Actions that runs tests
   - Test on Python 3.9-3.12

5. **Add ruff configuration** (10 min)
   - Add to pyproject.toml
   - Run formatter
