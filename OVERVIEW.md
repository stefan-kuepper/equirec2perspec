# Equirec2Perspec - Project Overview

## Project Summary

**Equirec2Perspec** is a Python library that converts equirectangular 360-degree panoramic images into standard perspective views. It enables extraction of normal perspective images from spherical panoramas by specifying viewing angles and field of view parameters.

## Purpose

This tool addresses the need to extract perspective views from 360-degree panoramic images, which is useful for:
- Virtual reality content processing
- Panoramic image analysis
- Computer vision applications requiring perspective projections
- Creating multiple viewpoints from a single panoramic source

## Key Features

- **Equirectangular to Perspective Conversion**: Transform 360° panoramas into standard perspective images
- **Flexible View Control**: Specify exact viewing direction using theta (horizontal) and phi (vertical) angles
- **Adjustable Field of View**: Control the FOV to simulate different lens characteristics
- **Custom Output Dimensions**: Define output image height and width
- **Interpolation Options**: Support for multiple OpenCV interpolation methods
- **Optional TurboJPEG Support**: Faster JPEG loading with optional TurboJPEG acceleration

## Technical Implementation

### Core Algorithm

The conversion process uses the following steps:

1. **Camera Model Creation**: Constructs an intrinsic camera matrix based on FOV and output dimensions
2. **Pixel Ray Computation**: Generates 3D rays for each output pixel using the inverse camera matrix
3. **Rotation Application**: Applies rotation matrices based on theta (y-axis) and phi (x-axis) angles using Rodrigues' rotation formula
4. **Spherical Mapping**: Converts rotated 3D coordinates to longitude/latitude on the sphere
5. **Equirectangular Sampling**: Maps spherical coordinates to pixel coordinates in the source image
6. **Image Remapping**: Uses OpenCV's remap function with specified interpolation

### Mathematical Foundation

The transformation pipeline:
```
2D Output Coordinates → 3D Ray → Rotation → Spherical Coordinates → Equirectangular Coordinates
```

Key coordinate systems:
- **Output image space**: Standard 2D pixel coordinates
- **Camera space**: 3D normalized coordinates after inverse projection
- **Rotated space**: Camera space rotated by viewing angles
- **Spherical space**: Longitude and latitude on unit sphere
- **Equirectangular space**: Input panorama pixel coordinates

## Dependencies

### Required
- **Python**: ≥3.9
- **NumPy**: ^1.26.4 - Numerical operations and array manipulation
- **OpenCV-Python**: ^4.9.0.80 - Image loading, remapping, and rotation functions

### Optional
- **PyTurboJPEG**: ^1.7.3 - Accelerated JPEG decoding (20-30% faster than OpenCV)

## Installation

### Using Poetry (Recommended)
```bash
# Basic installation
poetry install

# With TurboJPEG support
poetry install -E turbojpeg
```

### Using pip
```bash
pip install -e .
```

## Usage

### Basic Example
```python
import cv2
import Equirec2Perspec as E2P

# Load equirectangular panorama
equ = E2P.Equirectangular('src/image.jpg')

# Extract perspective view
# FOV: 60 degrees
# theta: 0 degrees (center horizontally)
# phi: 0 degrees (center vertically)
# Output: 720x1080 pixels
img = equ.GetPerspective(60, 0, 0, 720, 1080)

# Save or display the result
cv2.imwrite('output.jpg', img)
```

### Parameter Reference

**`GetPerspective(FOV, THETA, PHI, height, width, interpolation=cv2.INTER_CUBIC)`**

- `FOV` (float): Field of view in degrees (typical range: 30-120)
- `THETA` (float): Horizontal viewing angle in degrees
  - 0°: Forward
  - Positive: Right
  - Negative: Left
- `PHI` (float): Vertical viewing angle in degrees
  - 0°: Horizon
  - Positive: Up
  - Negative: Down
- `height` (int): Output image height in pixels
- `width` (int): Output image width in pixels
- `interpolation`: OpenCV interpolation method (default: `cv2.INTER_CUBIC`)
  - `cv2.INTER_NEAREST`: Fastest, lowest quality
  - `cv2.INTER_LINEAR`: Fast, good quality
  - `cv2.INTER_CUBIC`: Slower, better quality (default)
  - `cv2.INTER_LANCZOS4`: Slowest, best quality

### Advanced Examples

```python
import cv2
import Equirec2Perspec as E2P

equ = E2P.Equirectangular('panorama.jpg')

# Look right at 45 degrees
right_view = equ.GetPerspective(60, 45, 0, 720, 1080)

# Look up at 30 degrees
up_view = equ.GetPerspective(60, 0, 30, 720, 1080)

# Wide angle view (90 degrees FOV)
wide_view = equ.GetPerspective(90, 0, 0, 720, 1080)

# High-quality interpolation
hq_view = equ.GetPerspective(60, 0, 0, 720, 1080, cv2.INTER_LANCZOS4)
```

## Project Structure

```
equirec2perspec/
├── equirec2perspec/          # Main package directory
│   ├── __init__.py           # Package initialization
│   └── Equirec2Perspec.py    # Core conversion implementation
├── src/                      # Example images
│   ├── image.jpg             # Sample equirectangular panorama
│   └── perspective.jpg       # Sample perspective output
├── pyproject.toml            # Poetry configuration
├── setup.py                  # setuptools configuration
├── LICENSE.md                # MIT License
└── README.md                 # User documentation
```

## Package Management

The project supports both modern (Poetry) and traditional (setuptools) Python packaging:

- **Poetry** (`pyproject.toml`): Modern dependency management, extras support
- **setuptools** (`setup.py`): Traditional installation for broader compatibility

## Performance Considerations

### TurboJPEG Optimization
When TurboJPEG is installed, the library automatically uses it for JPEG decoding, providing:
- 20-30% faster image loading
- Lower memory usage during decode
- No impact on non-JPEG formats

### Interpolation Trade-offs
| Method | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| INTER_NEAREST | Fastest | Lowest | Real-time preview |
| INTER_LINEAR | Fast | Good | General use |
| INTER_CUBIC | Medium | Better | Default recommendation |
| INTER_LANCZOS4 | Slowest | Best | Final output/archival |

## Algorithm Complexity

- **Time Complexity**: O(H × W) where H and W are output image dimensions
- **Space Complexity**: O(H × W) for coordinate maps and output image
- **Preprocessing**: O(1) - intrinsic matrix and rotation matrix computation

## Limitations

- Input must be proper equirectangular projection
- No distortion correction for non-ideal panoramas
- Memory usage scales with output resolution
- Border handling uses wrap mode (assumes full 360° coverage)

## License

MIT License - See LICENSE.md for details

## Author

Stefan Küpper (stefan.kuepper@posteo.de)

## Repository

https://github.com/stefan-kuepper/equirec2perspec

## Version History

- **0.1.0**: Initial release
  - Core equirectangular to perspective conversion
  - Poetry packaging support
  - Optional TurboJPEG acceleration
  - Python 3.9+ compatibility
