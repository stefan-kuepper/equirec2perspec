# TODO - Best Practices Improvements

> Generated: 2026-01-06
> Overall Project Grade: C- (5.3/10)

## 🔴 Critical Priority (Do First)

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

---

## 🟡 High Priority (Do Soon)

### Type Hints
- [ ] Add return type hint to `load_image()` → `np.ndarray`
- [ ] Add type hints to `xyz2lonlat()` parameters and return
- [ ] Add type hints to `lonlat2XY()` parameters and return
- [ ] Add docstring and types to `__init__()`
- [ ] Create `py.typed` marker file in package
- [ ] Run mypy and fix any type errors

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

### Package Structure
- [ ] Create proper `examples/` directory
  - Add example scripts (not just images)
  - Add `basic_usage.py`
  - Add `advanced_usage.py`
  - Add `batch_processing.py`

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

### Community & Marketing
- [ ] Write blog post about the library
- [ ] Create demo video or GIF
- [ ] Add to Python Package Index classifiers

---

## ✅ Quick Wins (< 30 minutes each)

These can be done immediately for quick improvements:

1. **Add basic input validation** (15 min)
   - Check FOV > 0
   - Check dimensions > 0
   - Raise ValueError with messages

2. **Add missing docstrings** (20 min)
   - Document all helper functions
   - Add parameter descriptions

3. **Add ruff configuration** (10 min)
   - Add to pyproject.toml
   - Run formatter
