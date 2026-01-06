import os
import numpy as np
import pytest
from unittest.mock import Mock

# Test fixtures and configuration
TEST_IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
SAMPLE_PANORAMA = os.path.join(TEST_IMAGE_DIR, "image.jpg")
SAMPLE_PERSPECTIVE = os.path.join(TEST_IMAGE_DIR, "perspective.jpg")


@pytest.fixture
def sample_panorama_path():
    """Path to the sample panorama image."""
    return SAMPLE_PANORAMA


@pytest.fixture
def mock_image():
    """Create a mock equirectangular image for testing."""
    # Create a test pattern: gradient from left to right
    height, width = 512, 1024
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Create a gradient pattern
    for x in range(width):
        for y in range(height):
            # Simulate equirectangular pattern
            hue = (x / width) * 255
            brightness = (y / height) * 128 + 127
            image[y, x] = [hue, brightness, 255 - hue]

    return image


@pytest.fixture
def mock_turbojpeg():
    """Mock TurboJPEG for testing without the actual dependency."""
    mock_tjpg = Mock()
    mock_tjpg.decode.return_value = np.zeros((512, 1024, 3), dtype=np.uint8)
    return mock_tjpg


@pytest.fixture
def temp_image_file(tmp_path, mock_image):
    """Create a temporary image file for testing."""
    import cv2

    temp_file = tmp_path / "test_image.jpg"
    cv2.imwrite(str(temp_file), mock_image)
    return str(temp_file)


@pytest.fixture
def invalid_image_file(tmp_path):
    """Create a file that's not a valid image."""
    invalid_file = tmp_path / "invalid.jpg"
    invalid_file.write_text("not an image")
    return str(invalid_file)


# Test configuration
@pytest.fixture(autouse=True)
def configure_test_environment():
    """Configure test environment variables."""
    # Suppress print statements during testing
    import sys
    from io import StringIO

    # Capture stdout to suppress debug prints
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    yield

    # Restore stdout
    sys.stdout = original_stdout
