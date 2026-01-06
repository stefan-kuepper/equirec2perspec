# Equirec2Perspec

## Overview

**Equirec2Perspec** is a Python library that converts equirectangular 360-degree panoramic images into standard perspective views. It enables extraction of normal perspective images from spherical panoramas by specifying viewing angles and field of view parameters.

## Purpose

This tool addresses the need to extract perspective views from 360-degree panoramic images, which is useful for:
- Virtual reality content processing
- Panoramic image analysis
- Computer vision applications requiring perspective projections
- Creating multiple viewpoints from a single panoramic source

## Visual Example

### Input: Equirectangular Panorama
Given an input of 360 degree panorama:
<center><img src="src/image.jpg"></center>

### Output: Perspective View
Split panorama into perspective view with given parameters:
<center><img src="src/perspective.jpg"></center>

## Key Features

- **Equirectangular to Perspective Conversion**: Transform 360° panoramas into standard perspective images
- **Flexible View Control**: Specify exact viewing direction using theta (horizontal) and phi (vertical) angles
- **Adjustable Field of View**: Control the FOV to simulate different lens characteristics
- **Custom Output Dimensions**: Define output image height and width
- **Interpolation Options**: Support for multiple OpenCV interpolation methods
- **Optional TurboJPEG Support**: Faster JPEG loading with optional TurboJPEG acceleration

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

### Installing uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installing the package

```bash
# Install from PyPI (when published)
uv pip install equirec2perspec

# Or install from source
git clone https://github.com/stefan-kuepper/equirec2perspec.git
cd equirec2perspec
uv sync
```

### Optional dependencies

To install with TurboJPEG support for faster JPEG processing:

```bash
uv sync --extra turbojpeg
```

### Dependencies

**Required:**
- Python ≥3.9
- NumPy ≥1.26.4
- OpenCV-Python ≥4.9.0.80

**Optional:**
- PyTurboJPEG ≥1.7.3 (20-30% faster JPEG decoding)

## Development

```bash
# Clone the repository
git clone https://github.com/stefan-kuepper/equirec2perspec.git
cd equirec2perspec

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows

# Run your code
python your_script.py
```

## Usage

### Basic Example
```python
import cv2
import Equirec2Perspec as E2P

if __name__ == '__main__':
    # Load equirectangular image
    equ = E2P.Equirectangular('src/image.jpg')

    # Extract perspective view
    # FOV: 60 degrees
    # theta: 0 degrees (center horizontally - z-axis rotation)
    # phi: 0 degrees (center vertically - y-axis rotation)
    # Output: 720x1080 pixels (height, width)
    img = equ.GetPerspective(60, 0, 0, 720, 1080)

    # Save or display the result
    cv2.imwrite('output.jpg', img)
```

### Parameter Reference

**`GetPerspective(FOV, THETA, PHI, height, width, interpolation=cv2.INTER_CUBIC)`**

| Parameter | Type | Description |
|-----------|------|-------------|
| `FOV` | float | Field of view in degrees (typical range: 30-120) |
| `THETA` | float | Horizontal viewing angle (z-axis rotation)<br>• 0°: Forward<br>• Positive: Right<br>• Negative: Left |
| `PHI` | float | Vertical viewing angle (y-axis rotation)<br>• 0°: Horizon<br>• Positive: Up<br>• Negative: Down |
| `height` | int | Output image height in pixels |
| `width` | int | Output image width in pixels |
| `interpolation` | int | OpenCV interpolation method (default: `cv2.INTER_CUBIC`) |

### Interpolation Methods

| Method | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `cv2.INTER_NEAREST` | Fastest | Lowest | Real-time preview |
| `cv2.INTER_LINEAR` | Fast | Good | General use |
| `cv2.INTER_CUBIC` | Medium | Better | Default recommendation |
| `cv2.INTER_LANCZOS4` | Slowest | Best | Final output/archival |

### Advanced Examples

```python
import cv2
import Equirec2Perspec as E2P

equ = E2P.Equirectangular('panorama.jpg')

# Look right at 45 degrees
right_view = equ.GetPerspective(60, 45, 0, 720, 1080)

# Look up at 30 degrees
up_view = equ.GetPerspective(60, 0, 30, 720, 1080)

# Look down-left (combining angles)
down_left_view = equ.GetPerspective(60, -45, -20, 720, 1080)

# Wide angle view (90 degrees FOV)
wide_view = equ.GetPerspective(90, 0, 0, 720, 1080)

# Narrow telephoto view (30 degrees FOV)
tele_view = equ.GetPerspective(30, 0, 0, 720, 1080)

# High-quality interpolation for final output
hq_view = equ.GetPerspective(60, 0, 0, 1080, 1920, cv2.INTER_LANCZOS4)
```

## Technical Implementation

### Algorithm Overview

The conversion process uses the following steps:

1. **Camera Model Creation**: Constructs an intrinsic camera matrix based on FOV and output dimensions
2. **Pixel Ray Computation**: Generates 3D rays for each output pixel using the inverse camera matrix
3. **Rotation Application**: Applies rotation matrices based on theta (y-axis) and phi (x-axis) angles using Rodrigues' rotation formula
4. **Spherical Mapping**: Converts rotated 3D coordinates to longitude/latitude on the sphere
5. **Equirectangular Sampling**: Maps spherical coordinates to pixel coordinates in the source image
6. **Image Remapping**: Uses OpenCV's remap function with specified interpolation

### Transformation Pipeline

```
2D Output Coordinates → 3D Ray → Rotation → Spherical Coordinates → Equirectangular Coordinates
```

Key coordinate systems:
- **Output image space**: Standard 2D pixel coordinates
- **Camera space**: 3D normalized coordinates after inverse projection
- **Rotated space**: Camera space rotated by viewing angles
- **Spherical space**: Longitude and latitude on unit sphere
- **Equirectangular space**: Input panorama pixel coordinates

### Performance Considerations

**Algorithm Complexity:**
- Time Complexity: O(H × W) where H and W are output image dimensions
- Space Complexity: O(H × W) for coordinate maps and output image
- Preprocessing: O(1) - intrinsic matrix and rotation matrix computation

**TurboJPEG Optimization:**
When TurboJPEG is installed, the library automatically uses it for JPEG decoding, providing:
- 20-30% faster image loading
- Lower memory usage during decode
- No impact on non-JPEG formats

## Project Structure

```
equirec2perspec/
├── equirec2perspec/          # Main package directory
│   ├── __init__.py           # Package initialization
│   └── Equirec2Perspec.py    # Core conversion implementation
├── src/                      # Example images
│   ├── image.jpg             # Sample equirectangular panorama
│   └── perspective.jpg       # Sample perspective output
├── pyproject.toml            # Package configuration
├── setup.py                  # setuptools configuration
├── LICENSE.md                # MIT License
└── README.md                 # This file
```

## Limitations

- Input must be proper equirectangular projection
- No distortion correction for non-ideal panoramas
- Memory usage scales with output resolution
- Border handling uses wrap mode (assumes full 360° coverage)

## License

MIT License - See [LICENSE.md](LICENSE.md) for details

## Author

Stefan Küpper
Email: stefan.kuepper@posteo.de
GitHub: [@stefan-kuepper](https://github.com/stefan-kuepper)

## Repository

https://github.com/stefan-kuepper/equirec2perspec

## Version

0.1.0 - Initial release with core functionality and modern packaging support
