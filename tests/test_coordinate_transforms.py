import numpy as np

from equirec2perspec.Equirec2Perspec import xyz2lonlat, lonlat2XY


class TestCoordinateTransforms:
    """Test cases for coordinate transformation functions."""

    def test_xyz2lonlat_basic(self):
        """Test basic xyz2lonlat coordinate transformation."""
        # Test with known coordinates
        # Point on positive X axis (should be lon=π/2, lat=0 based on atan2(x,z))
        xyz = np.array([[[1.0, 0.0, 0.0]]])
        result = xyz2lonlat(xyz)

        assert result.shape == (1, 1, 2)
        np.testing.assert_allclose(result[0, 0, 0], np.pi / 2, atol=1e-10)  # longitude
        np.testing.assert_allclose(result[0, 0, 1], 0.0, atol=1e-10)  # latitude

    def test_xyz2lonlat_multiple_points(self):
        """Test xyz2lonlat with multiple coordinate points."""
        # Create test points on unit sphere
        xyz = np.array(
            [
                [[1.0, 0.0, 0.0]],  # Front (lon=π/2, lat=0) based on atan2(x,z)
                [[0.0, 1.0, 0.0]],  # Top (lon=0, lat=π/2)
                [[-1.0, 0.0, 0.0]],  # Back (lon=-π/2, lat=0)
                [[0.0, -1.0, 0.0]],  # Bottom (lon=0, lat=-π/2)
            ]
        )

        result = xyz2lonlat(xyz)

        assert result.shape == (4, 1, 2)

        # Check each point based on actual implementation atan2(x,z)
        np.testing.assert_allclose(result[0, 0, 0], np.pi / 2, atol=1e-10)  # Front
        np.testing.assert_allclose(result[0, 0, 1], 0.0, atol=1e-10)

        np.testing.assert_allclose(result[1, 0, 0], 0.0, atol=1e-10)  # Top
        np.testing.assert_allclose(result[1, 0, 1], np.pi / 2, atol=1e-10)

        np.testing.assert_allclose(result[2, 0, 0], -np.pi / 2, atol=1e-10)  # Back
        np.testing.assert_allclose(result[2, 0, 1], 0.0, atol=1e-10)

        np.testing.assert_allclose(result[3, 0, 0], 0.0, atol=1e-10)  # Bottom
        np.testing.assert_allclose(result[3, 0, 1], -np.pi / 2, atol=1e-10)

    def test_xyz2lonlat_normalization(self):
        """Test that xyz2lonlat properly normalizes input vectors."""
        # Test with non-unit vector
        xyz = np.array([[[2.0, 0.0, 0.0]]])  # Same direction as [1,0,0] but longer
        result = xyz2lonlat(xyz)

        # Should give same result as unit vector
        expected = np.array([[[np.pi / 2, 0.0]]])
        np.testing.assert_allclose(result, expected, atol=1e-10)

    def test_xyz2lonlat_zero_vector(self):
        """Test xyz2lonlat handling of zero vector."""
        xyz = np.array([[[0.0, 0.0, 0.0]]])

        # Should not crash, but result is undefined (division by zero)
        result = xyz2lonlat(xyz)
        assert result.shape == (1, 1, 2)
        # Values might be NaN or inf due to division by zero
        assert not np.isfinite(result).all()

    def test_lonlat2XY_basic(self):
        """Test basic lonlat2XY coordinate transformation."""
        # Test with known coordinates
        # Center of equirectangular image (lon=0, lat=0)
        lonlat = np.array([[[0.0, 0.0]]])
        shape = (512, 1024)  # height, width

        result = lonlat2XY(lonlat, shape)

        assert result.shape == (1, 1, 2)
        # Should map to center of image
        np.testing.assert_allclose(result[0, 0, 0], (1024 - 1) / 2, atol=1e-10)  # X
        np.testing.assert_allclose(result[0, 0, 1], (512 - 1) / 2, atol=1e-10)  # Y

    def test_lonlat2XY_corners(self):
        """Test lonlat2XY with corner coordinates."""
        shape = (360, 720)  # height, width

        # Test four corners of equirectangular projection
        test_cases = [
            ([-np.pi, -np.pi / 2], [0, 0]),  # Top-left
            ([np.pi, -np.pi / 2], [719, 0]),  # Top-right
            ([0, np.pi / 2], [359.5, 359]),  # Bottom-center
            ([-np.pi, np.pi / 2], [0, 359]),  # Bottom-left
        ]

        for lonlat_input, expected_xy in test_cases:
            lonlat = np.array([[[lonlat_input[0], lonlat_input[1]]]])
            result = lonlat2XY(lonlat, shape)

            np.testing.assert_allclose(result[0, 0, 0], expected_xy[0], atol=1)
            np.testing.assert_allclose(result[0, 0, 1], expected_xy[1], atol=1)

    def test_lonlat2XY_wrap_around(self):
        """Test lonlat2XY with longitude wrap-around."""
        shape = (180, 360)

        # Longitude 2π should map to right edge, not wrap to 0
        lonlat_2pi = np.array([[[2 * np.pi, 0.0]]])
        lonlat_0 = np.array([[[0.0, 0.0]]])

        result_2pi = lonlat2XY(lonlat_2pi, shape)
        result_0 = lonlat2XY(lonlat_0, shape)

        # 2π should map beyond right edge based on formula, 0 should map to center
        # X = (lon / (2π) + 0.5) * (width - 1)
        # For lon=2π: (2π / (2π) + 0.5) * 359 = (1 + 0.5) * 359 = 1.5 * 359 = 538.5
        # For lon=0: (0 / (2π) + 0.5) * 359 = (0 + 0.5) * 359 = 0.5 * 359 = 179.5
        np.testing.assert_allclose(
            result_2pi[0, 0, 0], 538.5, atol=1
        )  # Beyond right edge
        np.testing.assert_allclose(result_0[0, 0, 0], 179.5, atol=1)  # Center

    def test_lonlat2XY_multiple_points(self):
        """Test lonlat2XY with multiple coordinate points."""
        shape = (100, 200)
        lonlat = np.array(
            [
                [[0.0, 0.0]],  # Center
                [[-np.pi, -np.pi / 2]],  # Top-left
                [[np.pi, np.pi / 2]],  # Bottom-right
            ]
        )

        result = lonlat2XY(lonlat, shape)

        assert result.shape == (3, 1, 2)
        assert np.all(result >= 0)  # All coordinates should be non-negative
        assert np.all(result[:, :, 0] < shape[1])  # X coordinates within width
        assert np.all(result[:, :, 1] < shape[0])  # Y coordinates within height

    def test_coordinate_transform_roundtrip(self):
        """Test that coordinate transforms are consistent in roundtrip."""
        # This is a simplified test - full roundtrip would require 3D->spherical->2D->spherical->3D
        shape = (512, 1024)

        # Test some known points
        test_xyz = np.array(
            [
                [[1.0, 0.0, 0.0]],  # Front
                [[0.0, 1.0, 0.0]],  # Top
            ]
        )

        lonlat = xyz2lonlat(test_xyz)
        xy = lonlat2XY(lonlat, shape)

        # Verify shapes and reasonable values
        assert lonlat.shape == (2, 1, 2)
        assert xy.shape == (2, 1, 2)

        # XY coordinates should be within image bounds
        assert np.all(xy[:, :, 0] >= 0) and np.all(xy[:, :, 0] < shape[1])
        assert np.all(xy[:, :, 1] >= 0) and np.all(xy[:, :, 1] < shape[0])

    def test_xyz2lonlat_edge_cases(self):
        """Test xyz2lonlat with edge case coordinates."""
        # Test with points very close to poles
        xyz_pole_north = np.array([[[0.0, 0.999999, 0.0]]])
        xyz_pole_south = np.array([[[0.0, -0.999999, 0.0]]])

        result_north = xyz2lonlat(xyz_pole_north)
        result_south = xyz2lonlat(xyz_pole_south)

        # Latitude should be close to ±π/2
        np.testing.assert_allclose(result_north[0, 0, 1], np.pi / 2, atol=1e-3)
        np.testing.assert_allclose(result_south[0, 0, 1], -np.pi / 2, atol=1e-3)
