# Equirec2Perspec
## Introduction
<strong>Equirec2Perspec</strong> is a python tool to split equirectangular panorama into normal perspective view.

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

## Panorama
Given an input of 360 degree panorama
<center><img src="src/image.jpg"></center>

## Perpective
Split panorama into perspective view with given parameters
<center><img src="src/perspective.jpg"></center>

## Usage
```python
import cv2 
import Equirec2Perspec as E2P 

if __name__ == '__main__':
    equ = E2P.Equirectangular('src/image.jpg')    # Load equirectangular image
    
    #
    # FOV unit is degree 
    # theta is z-axis angle(right direction is positive, left direction is negative)
    # phi is y-axis angle(up direction positive, down direction negative)
    # height and width is output image dimension 
    #
    img = equ.GetPerspective(60, 0, 0, 720, 1080) # Specify parameters(FOV, theta, phi, height, width)
```

