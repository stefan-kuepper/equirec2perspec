"""Tests for CLI functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import cv2
import pytest
from click.testing import CliRunner

from equirec2perspec.cli import main


class TestCLI:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.test_image_path = Path(__file__).parent.parent / "images" / "image.jpg"

        if not self.test_image_path.exists():
            pytest.skip(f"Test image not found: {self.test_image_path}")

    def test_basic_conversion(self):
        """Test basic CLI conversion."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, [str(self.test_image_path), tmp_path])

            assert result.exit_code == 0
            assert "✓" in result.output
            assert os.path.exists(tmp_path)

            # Verify output image is valid
            img = cv2.imread(tmp_path)
            assert img is not None
            assert len(img.shape) == 3  # Should be color image

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_with_fov_option(self):
        """Test CLI with FOV option."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main, ["--fov", "90", str(self.test_image_path), tmp_path]
            )

            assert result.exit_code == 0
            assert os.path.exists(tmp_path)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_with_all_options(self):
        """Test CLI with all options specified."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main,
                [
                    "--fov",
                    "75",
                    "--theta",
                    "45",
                    "--phi",
                    "-15",
                    "--width",
                    "1280",
                    "--height",
                    "720",
                    "--interpolation",
                    "lanczos",
                    "--quality",
                    "85",
                    "--verbose",
                    str(self.test_image_path),
                    tmp_path,
                ],
            )

            assert result.exit_code == 0
            assert "Loading" in result.output
            assert "Extracting" in result.output
            assert "Saving" in result.output
            assert os.path.exists(tmp_path)

            # Verify output dimensions
            img = cv2.imread(tmp_path)
            assert img.shape[1] == 1280  # width
            assert img.shape[0] == 720  # height

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_auto_dimension_calculation(self):
        """Test auto-calculation of dimensions."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test width only
            result = self.runner.invoke(
                main, ["--width", "1600", str(self.test_image_path), tmp_path]
            )

            assert result.exit_code == 0
            img = cv2.imread(tmp_path)
            assert img.shape[1] == 1600  # width
            assert img.shape[0] == 900  # height (16:9 ratio)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_interpolation_methods(self):
        """Test different interpolation methods."""
        methods = ["nearest", "bilinear", "bicubic", "lanczos"]

        for method in methods:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                result = self.runner.invoke(
                    main,
                    ["--interpolation", method, str(self.test_image_path), tmp_path],
                )

                assert result.exit_code == 0
                assert os.path.exists(tmp_path)

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def test_invalid_fov(self):
        """Test validation of FOV parameter."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main, ["--fov", "200", str(self.test_image_path), tmp_path]
            )

            assert result.exit_code != 0
            assert "FOV must be between 1 and 180 degrees" in result.output

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_invalid_theta(self):
        """Test validation of THETA parameter."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main, ["--theta", "200", str(self.test_image_path), tmp_path]
            )

            assert result.exit_code != 0
            assert "THETA must be between -180 and 180 degrees" in result.output

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_invalid_quality(self):
        """Test validation of quality parameter."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(
                main, ["--quality", "150", str(self.test_image_path), tmp_path]
            )

            assert result.exit_code != 0
            assert "Quality must be between 1 and 100" in result.output

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_nonexistent_input_file(self):
        """Test handling of nonexistent input file."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, ["nonexistent.jpg", tmp_path])

            assert result.exit_code != 0

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_output_directory_creation(self):
        """Test automatic creation of output directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = Path(tmp_dir) / "nested" / "subdir" / "output.jpg"

            result = self.runner.invoke(
                main, [str(self.test_image_path), str(nested_path)]
            )

            assert result.exit_code == 0
            assert nested_path.exists()
            assert nested_path.parent.exists()

    def test_help_output(self):
        """Test help output contains expected information."""
        result = self.runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Convert equirectangular images" in result.output
        assert "--fov" in result.output
        assert "--theta" in result.output
        assert "--phi" in result.output
        assert "--interpolation" in result.output

    @patch("equirec2perspec.cli.Equirectangular")
    def test_library_error_handling(self, mock_equirec):
        """Test handling of library errors."""
        mock_equirec.side_effect = ValueError("Test error")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            result = self.runner.invoke(main, [str(self.test_image_path), tmp_path])

            assert result.exit_code != 0
            assert "Invalid parameter" in result.output

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
