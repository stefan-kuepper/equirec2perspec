# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Equirec2Perspec is a Python library that converts equirectangular 360-degree panoramic images into standard perspective views. It uses OpenCV for image processing and NumPy for mathematical transformations.

## Development Commands

```bash
# Install dependencies and create virtual environment
uv sync

# Install with optional TurboJPEG support (faster JPEG loading)
uv sync --extra turbojpeg

# Activate virtual environment
source .venv/bin/activate
```

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
