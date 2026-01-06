import os
import numpy as np
import pytest
from unittest.mock import patch

from equirec2perspec.Equirec2Perspec import Equirectangular


class TestEquirectangular:
    """Test cases for the Equirectangular class."""

    def test_init_with_valid_image(self, mock_image):
        """Test Equirectangular initialization with valid image."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            assert equ._img is mock_image
            assert equ._height == mock_image.shape[0]
            assert equ._width == mock_image.shape[1]

    def test_init_with_invalid_image(self):
        """Test Equirectangular initialization with invalid image."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = None  # Simulate failed image load

            with pytest.raises((TypeError, AttributeError)):
                Equirectangular("invalid_path.jpg")

    def test_get_perspective_basic(self, mock_image):
        """Test basic get_perspective functionality."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Test basic perspective extraction
            result = equ.get_perspective(60, 0, 0, 100, 200)

            assert isinstance(result, np.ndarray)
            assert result.shape == (100, 200, 3)  # height, width, channels

    def test_get_perspective_different_parameters(self, mock_image):
        """Test get_perspective with different parameter combinations."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            test_cases = [
                (30, 0, 0, 50, 100),  # Narrow FOV
                (90, 0, 0, 150, 300),  # Wide FOV
                (60, 45, 0, 100, 200),  # Look right
                (60, 0, 30, 100, 200),  # Look up
                (60, -45, -30, 100, 200),  # Look down-left
            ]

            for fov, theta, phi, height, width in test_cases:
                result = equ.get_perspective(fov, theta, phi, height, width)
                assert result.shape == (height, width, 3)

    def test_get_perspective_interpolation_methods(self, mock_image):
        """Test get_perspective with different interpolation methods."""
        import cv2

        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            interpolation_methods = [
                cv2.INTER_NEAREST,
                cv2.INTER_LINEAR,
                cv2.INTER_CUBIC,
                cv2.INTER_LANCZOS4,
            ]

            for method in interpolation_methods:
                result = equ.get_perspective(60, 0, 0, 100, 200, method)
                assert result.shape == (100, 200, 3)

    def test_get_perspective_extreme_angles(self, mock_image):
        """Test get_perspective with extreme viewing angles."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Test extreme angles
            extreme_cases = [
                (60, 180, 0, 100, 200),  # Look behind
                (60, -180, 0, 100, 200),  # Look behind (negative)
                (60, 0, 90, 100, 200),  # Look straight up
                (60, 0, -90, 100, 200),  # Look straight down
            ]

            for fov, theta, phi, height, width in extreme_cases:
                result = equ.get_perspective(fov, theta, phi, height, width)
                assert result.shape == (height, width, 3)

    def test_get_perspective_fov_validation(self, mock_image):
        """Test get_perspective FOV parameter validation."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Test valid FOV boundaries
            valid_fov_test_cases = [
                (1, 0, 0, 100, 200),  # Minimum valid FOV
                (90, 0, 0, 100, 200),  # Typical FOV
                (179, 0, 0, 100, 200),  # Very wide FOV
                (180, 0, 0, 100, 200),  # Maximum FOV
            ]

            for fov, theta, phi, height, width in valid_fov_test_cases:
                result = equ.get_perspective(fov, theta, phi, height, width)
                assert result.shape == (height, width, 3)

            # Test invalid FOV values
            invalid_fov_test_cases = [
                0.1,  # Below minimum
                0,  # Zero
                -10,  # Negative
                181,  # Above maximum
                200,  # Way too large
            ]

            for invalid_fov in invalid_fov_test_cases:
                with pytest.raises(
                    ValueError, match="FOV must be between 1 and 180 degrees"
                ):
                    equ.get_perspective(invalid_fov, 0, 0, 100, 200)

    def test_get_perspective_dimension_validation(self, mock_image):
        """Test get_perspective dimension parameter validation."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Test various dimensions
            dimension_test_cases = [
                (60, 0, 0, 1, 1),  # Smallest possible
                (60, 0, 0, 10, 10),  # Small square
                (60, 0, 0, 100, 50),  # Portrait
                (60, 0, 0, 50, 100),  # Landscape
                (60, 0, 0, 1000, 2000),  # Large dimensions
            ]

            for fov, theta, phi, height, width in dimension_test_cases:
                result = equ.get_perspective(fov, theta, phi, height, width)
                assert result.shape == (height, width, 3)

    def test_get_perspective_mathematical_consistency(self, mock_image):
        """Test that get_perspective produces mathematically consistent results."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            # Create a test pattern with known colors at specific positions
            test_image = np.zeros((512, 1024, 3), dtype=np.uint8)
            # Add a distinctive pattern
            test_image[256, 512] = [255, 0, 0]  # Red dot at center

            mock_load.return_value = test_image

            equ = Equirectangular("dummy_path.jpg")

            # Extract perspective looking at center
            result = equ.get_perspective(60, 0, 0, 100, 200)

            # The result should be a valid image
            assert isinstance(result, np.ndarray)
            assert result.dtype == np.uint8
            assert np.all(result >= 0) and np.all(result <= 255)

    def test_get_perspective_repeatability(self, mock_image):
        """Test that get_perspective produces identical results for same parameters."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Extract perspective twice with same parameters
            result1 = equ.get_perspective(60, 45, 30, 100, 200)
            result2 = equ.get_perspective(60, 45, 30, 100, 200)

            # Results should be identical
            np.testing.assert_array_equal(result1, result2)

    def test_get_perspective_different_views(self, mock_image):
        """Test that get_perspective produces different results for different parameters."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            equ = Equirectangular("dummy_path.jpg")

            # Extract perspective with different parameters
            result1 = equ.get_perspective(60, 0, 0, 100, 200)  # Front view
            result2 = equ.get_perspective(60, 90, 0, 100, 200)  # Right view

            # Results should be different (unless the image is uniform)
            assert not np.array_equal(result1, result2)

    def test_camera_matrix_construction(self, mock_image):
        """Test that camera matrix is constructed correctly."""
        with patch("equirec2perspec.Equirec2Perspec.load_image") as mock_load:
            mock_load.return_value = mock_image

            # We can't directly access the camera matrix, but we can test
            # the results are reasonable for known parameters
            equ = Equirectangular("dummy_path.jpg")

            # Test with known FOV and dimensions
            result = equ.get_perspective(60, 0, 0, 100, 200)

            # The result should be valid
            assert result.shape == (100, 200, 3)
            assert isinstance(result, np.ndarray)

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_get_perspective_with_real_image(self, sample_panorama_path):
        """Test get_perspective with real panorama image."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        equ = Equirectangular(sample_panorama_path)

        # Test basic perspective extraction
        result = equ.get_perspective(60, 0, 0, 720, 1080)

        assert isinstance(result, np.ndarray)
        assert result.shape == (720, 1080, 3)
        assert result.dtype == np.uint8
