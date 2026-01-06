import os
import numpy as np
import pytest
import cv2

from equirec2perspec.Equirec2Perspec import Equirectangular


class TestIntegration:
    """Integration tests for end-to-end functionality."""

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_full_workflow_with_sample_image(self, sample_panorama_path):
        """Test complete workflow with real sample image."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        # Load the panorama
        equ = Equirectangular(sample_panorama_path)

        # Extract multiple perspective views
        views = [
            (60, 0, 0, 720, 1080),  # Front view
            (60, 90, 0, 720, 1080),  # Right view
            (60, 180, 0, 720, 1080),  # Back view
            (60, -90, 0, 720, 1080),  # Left view
            (60, 0, 45, 720, 1080),  # Up view
            (60, 0, -45, 720, 1080),  # Down view
        ]

        results = []
        for fov, theta, phi, height, width in views:
            result = equ.GetPerspective(fov, theta, phi, height, width)

            # Validate each result
            assert isinstance(result, np.ndarray)
            assert result.shape == (height, width, 3)
            assert result.dtype == np.uint8
            assert np.all(result >= 0) and np.all(result <= 255)

            results.append(result)

        # All views should be different (unless the panorama is uniform)
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                # Allow for some similarity in uniform areas, but views should be generally different
                similarity = np.sum(results[i] == results[j]) / results[i].size
                assert similarity < 0.95, f"Views {i} and {j} are too similar"

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_different_fov_values(self, sample_panorama_path):
        """Test perspective extraction with different FOV values."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        equ = Equirectangular(sample_panorama_path)

        fov_values = [30, 45, 60, 90, 120]
        results = []

        for fov in fov_values:
            result = equ.GetPerspective(fov, 0, 0, 480, 640)
            results.append(result)

            assert result.shape == (480, 640, 3)
            assert isinstance(result, np.ndarray)

        # Different FOV values should produce different results
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                assert not np.array_equal(results[i], results[j])

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_different_output_dimensions(self, sample_panorama_path):
        """Test perspective extraction with different output dimensions."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        equ = Equirectangular(sample_panorama_path)

        dimensions = [
            (240, 320),  # Small
            (480, 640),  # Medium
            (720, 1080),  # Large
            (1080, 1920),  # HD
        ]

        for height, width in dimensions:
            result = equ.GetPerspective(60, 0, 0, height, width)

            assert result.shape == (height, width, 3)
            assert isinstance(result, np.ndarray)
            assert result.dtype == np.uint8

    @pytest.mark.skipif(
        not os.path.exists(
            os.path.join(os.path.dirname(__file__), "..", "images", "image.jpg")
        ),
        reason="Sample image not available",
    )
    def test_interpolation_methods_comparison(self, sample_panorama_path):
        """Test different interpolation methods with real image."""
        if not os.path.exists(sample_panorama_path):
            pytest.skip("Sample panorama image not found")

        equ = Equirectangular(sample_panorama_path)

        import cv2

        interpolation_methods = [
            (cv2.INTER_NEAREST, "Nearest"),
            (cv2.INTER_LINEAR, "Linear"),
            (cv2.INTER_CUBIC, "Cubic"),
            (cv2.INTER_LANCZOS4, "Lanczos4"),
        ]

        results = {}
        for method, name in interpolation_methods:
            result = equ.GetPerspective(60, 0, 0, 480, 640, interpolation=method)
            results[name] = result

            assert result.shape == (480, 640, 3)
            assert isinstance(result, np.ndarray)

        # Different interpolation methods should produce slightly different results
        # (except possibly in uniform areas)
        for name1, result1 in results.items():
            for name2, result2 in results.items():
                if name1 != name2:
                    similarity = np.sum(result1 == result2) / result1.size
                    # Allow for high similarity but not identical results
                    assert similarity < 1.0, (
                        f"Interpolation methods {name1} and {name2} produced identical results"
                    )

    def test_synthetic_panorama_processing(self):
        """Test processing of synthetic equirectangular panorama."""
        # Create a synthetic equirectangular image with test pattern
        height, width = 512, 1024
        synthetic_image = np.zeros((height, width, 3), dtype=np.uint8)

        # Create a test pattern: colored stripes
        for x in range(width):
            color_value = int((x / width) * 255)
            synthetic_image[:, x] = [color_value, 255 - color_value, 128]

        # Add some distinctive features
        synthetic_image[height // 2, width // 4] = [255, 0, 0]  # Red dot
        synthetic_image[height // 2, width // 2] = [0, 255, 0]  # Green dot
        synthetic_image[height // 2, 3 * width // 4] = [0, 0, 255]  # Blue dot

        # Save synthetic image temporarily
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, synthetic_image)

            try:
                # Process with Equirectangular
                equ = Equirectangular(tmp_file.name)

                # Extract perspective views
                result = equ.GetPerspective(60, 0, 0, 200, 400)

                assert isinstance(result, np.ndarray)
                assert result.shape == (200, 400, 3)
                assert result.dtype == np.uint8

                # The result should show some variation (not uniform)
                assert np.std(result) > 0

            finally:
                # Clean up temporary file
                os.unlink(tmp_file.name)

    def test_boundary_conditions(self):
        """Test processing with boundary conditions."""
        # Create minimal test image
        minimal_image = np.ones((100, 200, 3), dtype=np.uint8) * 128

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, minimal_image)

            try:
                equ = Equirectangular(tmp_file.name)

                # Test with minimal output dimensions
                result = equ.GetPerspective(60, 0, 0, 1, 1)
                assert result.shape == (1, 1, 3)

                # Test with very large FOV
                result = equ.GetPerspective(179, 0, 0, 100, 100)
                assert result.shape == (100, 100, 3)

                # Test with extreme angles
                result = equ.GetPerspective(60, 180, 90, 50, 50)
                assert result.shape == (50, 50, 3)

            finally:
                os.unlink(tmp_file.name)

    def test_memory_usage(self):
        """Test that memory usage is reasonable for large images."""
        # Create a moderately sized test image
        test_image = np.random.randint(0, 256, (1024, 2048, 3), dtype=np.uint8)

        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, test_image)

            try:
                equ = Equirectangular(tmp_file.name)

                # Test with large output dimensions
                result = equ.GetPerspective(60, 0, 0, 1080, 1920)

                assert result.shape == (1080, 1920, 3)
                assert isinstance(result, np.ndarray)

                # Memory usage should be reasonable (this is a basic check)
                expected_memory = 1080 * 1920 * 3  # bytes for uint8
                actual_memory = result.nbytes
                assert actual_memory == expected_memory

            finally:
                os.unlink(tmp_file.name)

    def test_performance_consistency(self):
        """Test that performance is consistent across multiple calls."""
        # Create test image
        test_image = np.random.randint(0, 256, (512, 1024, 3), dtype=np.uint8)

        import tempfile
        import time

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, test_image)

            try:
                equ = Equirectangular(tmp_file.name)

                # Time multiple calls
                times = []
                for _ in range(5):
                    start_time = time.time()
                    equ.GetPerspective(60, 0, 0, 480, 640)
                    end_time = time.time()
                    times.append(end_time - start_time)

                # All times should be reasonably consistent (within factor of 2)
                max_time = max(times)
                min_time = min(times)
                assert max_time / min_time < 2.0, f"Performance too variable: {times}"

            finally:
                os.unlink(tmp_file.name)
