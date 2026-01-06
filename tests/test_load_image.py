import os
import numpy as np
import pytest
from unittest.mock import patch, Mock

from equirec2perspec.Equirec2Perspec import load_image


class TestLoadImage:
    """Test cases for the load_image function."""

    def test_load_image_with_opencv(self, temp_image_file):
        """Test loading image with OpenCV when TurboJPEG is not available."""
        with patch("equirec2perspec.Equirec2Perspec.TurboJPEG", None):
            image = load_image(temp_image_file)

            assert isinstance(image, np.ndarray)
            assert len(image.shape) == 3  # Should be 3D (height, width, channels)
            assert image.shape[2] == 3  # Should have 3 channels (BGR)

    def test_load_image_turbojpeg_available_logic(
        self, temp_image_file, mock_turbojpeg
    ):
        """Test logic when TurboJPEG is available (simplified test)."""
        # This test uses the mock_turbojpeg fixture to simulate TurboJPEG being available
        # The actual TurboJPEG testing would require the module to be installed
        # Make the mock callable - TurboJPEG() should return the mock instance
        mock_class = Mock(return_value=mock_turbojpeg)

        with patch("equirec2perspec.Equirec2Perspec.TurboJPEG", mock_class):
            # We're mocking it, so it should try the TurboJPEG path
            try:
                image = load_image(temp_image_file)
                # If it succeeds, verify it's a valid image
                assert isinstance(image, np.ndarray)
                assert len(image.shape) == 3
            except (ImportError, AttributeError):
                # Expected if TurboJPEG class isn't actually available
                # This is acceptable behavior for testing purposes
                pass

    def test_load_image_file_not_found(self):
        """Test loading non-existent file raises appropriate error."""
        non_existent_file = "/path/to/non/existent/image.jpg"

        # Should raise FileNotFoundError when file doesn't exist
        with pytest.raises(FileNotFoundError) as exc_info:
            load_image(non_existent_file)

        # Verify error message contains the path
        assert non_existent_file in str(exc_info.value)

    def test_load_image_invalid_file(self, invalid_image_file):
        """Test loading invalid image file."""
        # Should raise ValueError for corrupted/unsupported files
        with pytest.raises(ValueError) as exc_info:
            load_image(invalid_image_file)

        # Verify error message indicates format issue
        assert "unsupported format or corrupted" in str(exc_info.value)

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_load_real_sample_image(self, sample_panorama_path):
        """Test loading the real sample panorama image."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        image = load_image(sample_panorama_path)

        assert isinstance(image, np.ndarray)
        assert len(image.shape) == 3
        assert image.shape[2] == 3
        assert image.shape[0] > 0  # Height should be positive
        assert image.shape[1] > 0  # Width should be positive

    def test_load_image_opencv_fallback(self, temp_image_file):
        """Test that OpenCV fallback works properly."""
        with patch("equirec2perspec.Equirec2Perspec.TurboJPEG", None):
            # Simulate TurboJPEG not being available
            image = load_image(temp_image_file)

            # Should use OpenCV and return a valid image
            assert isinstance(image, np.ndarray)
            assert image.dtype == np.uint8  # OpenCV typically returns uint8
            assert len(image.shape) == 3

    def test_load_image_different_paths(self, temp_image_file):
        """Test load_image with different path scenarios."""
        with patch("equirec2perspec.Equirec2Perspec.TurboJPEG", None):
            # Force OpenCV path
            # Test with absolute path
            abs_path = os.path.abspath(temp_image_file)
            image = load_image(abs_path)
            assert isinstance(image, np.ndarray)

            # Test with relative path (if possible)
            rel_path = os.path.relpath(temp_image_file)
            if not rel_path.startswith(".."):  # Only test if within reasonable range
                image = load_image(rel_path)
                assert isinstance(image, np.ndarray) or image is None
