"""Unit tests for perspective helper functions.

Tests each individual helper function to ensure they work correctly
and handle edge cases appropriately.

"""

import cv2
import numpy as np
import pytest

from equirec2perspec.perspective_helpers import (
    apply_transformations_and_remap,
    build_camera_matrix,
    compute_rotation_matrices,
    generate_3d_coordinates,
    validate_perspective_params,
)


class TestValidatePerspectiveParams:
    """Test cases for validate_perspective_params function."""

    def test_valid_parameters(self):
        """Test with valid parameter values."""
        # Should not raise any exception
        validate_perspective_params(60, 0, 0, 480, 640)
        validate_perspective_params(1, -180, -90, 1, 1)
        validate_perspective_params(180, 180, 90, 1000, 1000)

    def test_invalid_fov(self):
        """Test FOV validation."""
        with pytest.raises(ValueError, match="FOV must be between 1 and 180"):
            validate_perspective_params(0, 0, 0, 480, 640)

        with pytest.raises(ValueError, match="FOV must be between 1 and 180"):
            validate_perspective_params(181, 0, 0, 480, 640)

    def test_invalid_theta(self):
        """Test THETA validation."""
        with pytest.raises(ValueError, match="THETA must be between -180 and 180"):
            validate_perspective_params(60, -181, 0, 480, 640)

        with pytest.raises(ValueError, match="THETA must be between -180 and 180"):
            validate_perspective_params(60, 181, 0, 480, 640)

    def test_invalid_phi(self):
        """Test PHI validation."""
        with pytest.raises(ValueError, match="PHI must be between -90 and 90"):
            validate_perspective_params(60, 0, -91, 480, 640)

        with pytest.raises(ValueError, match="PHI must be between -90 and 90"):
            validate_perspective_params(60, 0, 91, 480, 640)

    def test_invalid_dimensions(self):
        """Test dimension validation."""
        with pytest.raises(ValueError, match="height must be greater than 0"):
            validate_perspective_params(60, 0, 0, 0, 640)

        with pytest.raises(ValueError, match="width must be greater than 0"):
            validate_perspective_params(60, 0, 0, 480, 0)


class TestBuildCameraMatrix:
    """Test cases for build_camera_matrix function."""

    def test_camera_matrix_properties(self):
        """Test that camera matrix has correct properties."""
        FOV = 60
        width = 640
        height = 480

        K, K_inv = build_camera_matrix(FOV, width, height)

        # Check matrix shape
        assert K.shape == (3, 3)
        assert K_inv.shape == (3, 3)

        # Check that K_inv is actually the inverse of K
        identity = K @ K_inv
        np.testing.assert_allclose(identity, np.eye(3), atol=1e-6)

        # Check that K has correct structure
        assert K[0, 1] == 0  # No skew
        assert K[1, 0] == 0  # No skew
        assert K[2, 0] == 0  # Bottom row
        assert K[2, 1] == 0  # Bottom row
        assert K[2, 2] == 1  # Bottom row

    def test_focal_length_calculation(self):
        """Test focal length calculation for different FOVs."""
        width = 640
        height = 480

        # Test different FOV values
        for FOV in [30, 60, 90, 120]:
            K, K_inv = build_camera_matrix(FOV, width, height)

            # Focal length should be positive
            f = K[0, 0]
            assert f > 0

            # Higher FOV should result in smaller focal length
            # (wider angle = shorter focal length)
            if FOV > 30:  # Compare with previous
                K_prev, _ = build_camera_matrix(FOV - 30, width, height)
                f_prev = K_prev[0, 0]
                assert f < f_prev

    def test_principal_point(self):
        """Test principal point calculation."""
        FOV = 60
        width = 640
        height = 480

        K, K_inv = build_camera_matrix(FOV, width, height)

        # Principal point should be at image center
        expected_cx = (width - 1) / 2.0
        expected_cy = (height - 1) / 2.0

        assert K[0, 2] == expected_cx
        assert K[1, 2] == expected_cy


class TestGenerate3DCoordinates:
    """Test cases for generate_3d_coordinates function."""

    def test_output_shape(self):
        """Test that output has correct shape."""
        width = 640
        height = 480

        # Create a simple inverse camera matrix
        K_inv = np.eye(3, dtype=np.float32)

        xyz = generate_3d_coordinates(width, height, K_inv)

        assert xyz.shape == (height, width, 3)

    def test_coordinate_values(self):
        """Test that coordinate values are reasonable."""
        width = 3
        height = 2

        # Use simple identity matrix for predictable results
        K_inv = np.eye(3, dtype=np.float32)

        xyz = generate_3d_coordinates(width, height, K_inv)

        # Check that x coordinates increase from left to right
        assert np.allclose(xyz[0, :, 0], [0, 1, 2])

        # Check that y coordinates increase from top to bottom
        assert np.allclose(xyz[:, 0, 1], [0, 1])

        # Check that z coordinates are all 1 (normalized depth)
        assert np.allclose(xyz[:, :, 2], 1)

    def test_camera_matrix_effect(self):
        """Test that camera matrix affects coordinates correctly."""
        width = 2
        height = 2

        # Identity matrix (no transformation)
        K_inv_identity = np.eye(3, dtype=np.float32)
        xyz_identity = generate_3d_coordinates(width, height, K_inv_identity)

        # Scaling matrix (should scale coordinates)
        K_inv_scale = np.diag([2.0, 2.0, 1.0]).astype(np.float32)
        xyz_scaled = generate_3d_coordinates(width, height, K_inv_scale)

        # Scaled coordinates should be larger
        assert np.allclose(xyz_scaled[:, :, :2], xyz_identity[:, :, :2] * 2)


class TestComputeRotationMatrices:
    """Test cases for compute_rotation_matrices function."""

    def test_zero_rotation(self):
        """Test with zero rotation."""
        R = compute_rotation_matrices(0, 0)

        # Should be identity matrix
        np.testing.assert_allclose(R, np.eye(3), atol=1e-6)

    def test_rotation_matrix_properties(self):
        """Test that rotation matrix has correct properties."""
        R = compute_rotation_matrices(45, 30)

        # Should be 3x3 matrix
        assert R.shape == (3, 3)

        # Should be orthogonal (R @ R.T = I)
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-6)

        # Should have determinant 1 (proper rotation)
        assert abs(np.linalg.det(R) - 1.0) < 1e-6

    def test_theta_rotation(self):
        """Test THETA (horizontal) rotation."""
        # Pure horizontal rotation should only affect x-z plane
        R = compute_rotation_matrices(90, 0)

        # This should rotate the viewing direction around y-axis
        z_axis = np.array([0, 0, 1])  # Forward direction
        rotated_z = R @ z_axis

        # After 90-degree rotation, forward direction should point to negative x
        # (looking to the right from the original perspective)
        np.testing.assert_allclose(rotated_z[:2], [1, 0], atol=1e-6)

    def test_phi_rotation(self):
        """Test PHI (vertical) rotation."""
        # Test 90-degree upward rotation
        R = compute_rotation_matrices(0, 90)

        # This should make the camera look straight up
        z_axis = np.array([0, 0, 1])
        rotated_z = R @ z_axis

        # After 90-degree upward rotation, forward direction should point down
        # (negative y in this coordinate system)
        assert rotated_z[1] < -0.9  # Should mostly point in -y direction


class TestApplyTransformationsAndRemap:
    """Test cases for apply_transformations_and_remap function."""

    def test_output_properties(self):
        """Test that output has correct properties."""
        # Create simple test image
        source_image = np.ones((100, 200, 3), dtype=np.uint8) * 128

        # Create simple 3D coordinates and identity rotation
        xyz = np.ones((50, 100, 3), dtype=np.float32)
        R = np.eye(3, dtype=np.float32)

        result = apply_transformations_and_remap(xyz, R, source_image)

        # Should have same height and width as xyz array
        assert result.shape == (50, 100, 3)
        assert result.dtype == np.uint8

    def test_different_interpolation_methods(self):
        """Test with different interpolation methods."""
        source_image = np.random.randint(0, 256, (50, 100, 3), dtype=np.uint8)
        xyz = np.ones((25, 50, 3), dtype=np.float32)
        R = np.eye(3, dtype=np.float32)

        methods = [cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_CUBIC]

        for method in methods:
            result = apply_transformations_and_remap(xyz, R, source_image, method)
            assert result.shape == (25, 50, 3)
            assert result.dtype == np.uint8

    def test_transformation_chain(self):
        """Test that the transformation chain works correctly."""
        # Create a test pattern with larger features
        source_image = np.zeros((180, 360, 3), dtype=np.uint8)

        # Add distinctive regions (larger areas for better sampling)
        source_image[80:100, 170:190] = [255, 0, 0]  # Red region at center
        source_image[40:50, 80:100] = [0, 255, 0]  # Green region at quarter
        source_image[130:140, 260:280] = [0, 0, 255]  # Blue region at three-quarters

        # Generate coordinates for a small output with wide FOV
        width, height = 20, 10
        K, K_inv = build_camera_matrix(120, width, height)  # Wide FOV to see more
        xyz = generate_3d_coordinates(width, height, K_inv)

        # Use identity rotation (should see center area of source image)
        R = compute_rotation_matrices(0, 0)

        result = apply_transformations_and_remap(xyz, R, source_image)

        # Result should be non-uniform (contain some variation)
        assert np.std(result) > 0

    def test_rotation_effect(self):
        """Test that rotation affects the output."""
        # Create non-uniform source image
        source_image = np.random.randint(0, 256, (100, 200, 3), dtype=np.uint8)

        width, height = 20, 20
        K, K_inv = build_camera_matrix(60, width, height)
        xyz = generate_3d_coordinates(width, height, K_inv)

        # Test with different rotations
        R_identity = compute_rotation_matrices(0, 0)
        R_rotated = compute_rotation_matrices(90, 0)

        result_identity = apply_transformations_and_remap(xyz, R_identity, source_image)
        result_rotated = apply_transformations_and_remap(xyz, R_rotated, source_image)

        # Results should be different (unless source is uniform)
        assert not np.array_equal(result_identity, result_rotated)


class TestIntegration:
    """Integration tests for the complete helper function chain."""

    def test_complete_chain(self):
        """Test the complete transformation chain."""
        # Create test image
        source_image = np.ones((180, 360, 3), dtype=np.uint8) * 100

        # Parameters
        FOV, THETA, PHI = 60, 45, 30
        width, height = 50, 40

        # Run the complete chain
        K, K_inv = build_camera_matrix(FOV, width, height)
        xyz = generate_3d_coordinates(width, height, K_inv)
        R = compute_rotation_matrices(THETA, PHI)
        result = apply_transformations_and_remap(xyz, R, source_image)

        # Check final result
        assert result.shape == (height, width, 3)
        assert result.dtype == np.uint8
        assert np.all(result >= 0) and np.all(result <= 255)

    def test_edge_case_parameters(self):
        """Test with edge case parameters."""
        source_image = np.ones((10, 20, 3), dtype=np.uint8) * 128

        # Minimal dimensions
        K, K_inv = build_camera_matrix(1, 1, 1)
        xyz = generate_3d_coordinates(1, 1, K_inv)
        R = compute_rotation_matrices(-180, -90)
        result = apply_transformations_and_remap(xyz, R, source_image)

        assert result.shape == (1, 1, 3)

        # Maximum dimensions tested with smaller image for performance
        K, K_inv = build_camera_matrix(180, 100, 100)
        xyz = generate_3d_coordinates(100, 100, K_inv)
        R = compute_rotation_matrices(180, 90)
        result = apply_transformations_and_remap(xyz, R, source_image)

        assert result.shape == (100, 100, 3)
