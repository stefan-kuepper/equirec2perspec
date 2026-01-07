"""Helper functions for perspective transformation in equirectangular images.

This module contains refactored helper functions that were originally part of the
`get_perspective` method in the Equirectangular class. These functions are now
separately testable and maintainable.

"""

import cv2
import numpy as np

from .profiling import profile


def validate_perspective_params(
    FOV: float, THETA: float, PHI: float, height: int, width: int
) -> None:
    """Validate input parameters for perspective transformation.

    Args:
        FOV: Field of view in degrees (must be between 1 and 180)
        THETA: left/right angle in degrees (horizontal rotation, -180 to 180)
        PHI: up/down angle in degrees (vertical rotation, -90 to 90)
        height: output image height (must be > 0)
        width: output image width (must be > 0)

    Raises:
        ValueError: If any input parameter is out of valid range
    """
    # Validate FOV range
    if not (1 <= FOV <= 180):
        raise ValueError(f"FOV must be between 1 and 180 degrees, got: {FOV}")

    # Validate THETA range
    if not (-180 <= THETA <= 180):
        raise ValueError(f"THETA must be between -180 and 180 degrees, got: {THETA}")

    # Validate PHI range
    if not (-90 <= PHI <= 90):
        raise ValueError(f"PHI must be between -90 and 90 degrees, got: {PHI}")

    # Validate output dimensions
    if height <= 0:
        raise ValueError(f"height must be greater than 0, got: {height}")

    if width <= 0:
        raise ValueError(f"width must be greater than 0, got: {width}")


@profile("build_camera_matrix")
def build_camera_matrix(
    FOV: float, width: int, height: int
) -> tuple[np.ndarray, np.ndarray]:
    """Build intrinsic camera matrix and its inverse.

    Args:
        FOV: Field of view in degrees
        width: output image width
        height: output image height

    Returns:
        Tuple of (K, K_inv) where K is the camera matrix and K_inv is its inverse
    """
    f = 0.5 * width * 1 / np.tan(0.5 * FOV / 180.0 * np.pi)
    cx = (width - 1) / 2.0
    cy = (height - 1) / 2.0

    K = np.array(
        [
            [f, 0, cx],
            [0, f, cy],
            [0, 0, 1],
        ],
        np.float32,
    )
    K_inv = np.linalg.inv(K)

    return K, K_inv


@profile("generate_3d_coordinates")
def generate_3d_coordinates(width: int, height: int, K_inv: np.ndarray) -> np.ndarray:
    """Generate 3D ray coordinates for each pixel in the output image.

    Args:
        width: output image width
        height: output image height
        K_inv: inverse camera matrix

    Returns:
        Array of 3D coordinates with shape (height, width, 3)
    """
    x = np.arange(width)
    y = np.arange(height)
    x, y = np.meshgrid(x, y)
    z = np.ones_like(x)
    xyz = np.concatenate([x[..., None], y[..., None], z[..., None]], axis=-1)
    xyz = xyz @ K_inv.T

    result: np.ndarray = xyz.astype(np.float32)
    return result


@profile("compute_rotation_matrices")
def compute_rotation_matrices(THETA: float, PHI: float) -> np.ndarray:
    """Compute combined rotation matrix for THETA and PHI angles.

    Args:
        THETA: horizontal rotation angle in degrees
        PHI: vertical rotation angle in degrees

    Returns:
        Combined rotation matrix
    """
    y_axis = np.array([0.0, 1.0, 0.0], np.float32)
    x_axis = np.array([1.0, 0.0, 0.0], np.float32)

    R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
    R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
    R = R2 @ R1

    result: np.ndarray = R.astype(np.float32)
    return result


@profile("apply_transformations_and_remap")
def apply_transformations_and_remap(
    xyz: np.ndarray,
    R: np.ndarray,
    source_image: np.ndarray,
    interpolation: int = cv2.INTER_CUBIC,
) -> np.ndarray:
    """Apply coordinate transformations and perform final image remapping.

    Args:
        xyz: 3D coordinates array
        R: rotation matrix
        source_image: source equirectangular image
        interpolation: OpenCV interpolation method

    Returns:
        Remapped perspective image
    """
    from .Equirec2Perspec import xyz2lonlat, lonlat2XY

    # Apply rotation
    xyz_rotated = xyz @ R.T

    # Transform to spherical coordinates
    lonlat = xyz2lonlat(xyz_rotated)

    # Transform to pixel coordinates
    XY = lonlat2XY(lonlat, shape=source_image.shape).astype(np.float32)

    # Perform final remapping
    return cv2.remap(
        source_image, XY[..., 0], XY[..., 1], interpolation, borderMode=cv2.BORDER_WRAP
    )
