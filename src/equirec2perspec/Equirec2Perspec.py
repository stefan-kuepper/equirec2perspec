import logging
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

from .perspective_helpers import (
    apply_transformations_and_remap,
    build_camera_matrix,
    compute_rotation_matrices,
    generate_3d_coordinates,
    validate_perspective_params,
)
from .profiling import profile

logger = logging.getLogger(__name__)

try:
    from turbojpeg import TurboJPEG

    logger.debug("TurboJPEG available")
except ImportError:
    TurboJPEG = None
    logger.debug("TurboJPEG not available, using OpenCV")


@profile("load_image")
def load_image(path: Union[str, Path]) -> np.ndarray:
    """Load an image from file path, supporting both str and Path objects.

    Args:
        path: Path to the image file

    Returns:
        Loaded image as numpy array

    Raises:
        FileNotFoundError: If the image file does not exist
        ValueError: If the image file cannot be decoded or is invalid
        IOError: If the image file cannot be read

    """
    path_obj = Path(path)

    # Validate path exists
    if not path_obj.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    if not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path}")

    path_str = str(path)
    image: Optional[np.ndarray] = None
    logger.debug(f"Loading image: {path_str}")

    try:
        if TurboJPEG is not None:
            tjpg = TurboJPEG()
            try:
                with open(path_str, "rb") as img:
                    image = tjpg.decode(img.read())
                logger.debug(f"Successfully decoded with TurboJPEG: {path_str}")
            except Exception as e:
                raise ValueError(
                    f"Failed to decode image with TurboJPEG: {path}"
                ) from e
        else:
            image = cv2.imread(path_str, cv2.IMREAD_COLOR)
            logger.debug(f"Successfully decoded with OpenCV: {path_str}")
    except OSError as e:
        raise OSError(f"Failed to read image file: {path}") from e

    # Validate image was decoded successfully
    if image is None:
        raise ValueError(
            f"Failed to decode image (unsupported format or corrupted file): {path}"
        )

    logger.debug(f"Image loaded: shape={image.shape}, dtype={image.dtype}")
    return image


def xyz2lonlat(xyz: np.ndarray) -> np.ndarray:
    """Convert 3D Cartesian coordinates to spherical longitude/latitude coordinates.

    Args:
        xyz: Array of 3D Cartesian coordinates with shape (..., 3) where the last
            dimension contains [x, y, z] coordinates

    Returns:
        Array of spherical coordinates with shape (..., 2) where the last dimension
        contains [longitude, latitude] in radians. Longitude ranges from -π to π,
        latitude ranges from -π/2 to π/2.

    """
    atan2 = np.arctan2
    asin = np.arcsin

    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    xyz_norm = xyz / norm
    x = xyz_norm[..., 0:1]
    y = xyz_norm[..., 1:2]
    z = xyz_norm[..., 2:]

    lon = atan2(x, z)
    lat = asin(y)

    out: np.ndarray = np.concatenate([lon, lat], axis=-1)
    return out


def lonlat2XY(lonlat: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    """Convert spherical longitude/latitude coordinates to equirectangular image pixel coordinates.

    Args:
        lonlat: Array of spherical coordinates with shape (..., 2) where the last
            dimension contains [longitude, latitude] in radians
        shape: Shape of the equirectangular image as (height, width, channels)

    Returns:
        Array of pixel coordinates with shape (..., 2) where the last dimension
        contains [X, Y] pixel positions in the equirectangular image.

    """
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    out: np.ndarray = np.concatenate([X, Y], axis=-1)

    return out


class Equirectangular:
    def __init__(self, img_name: Union[str, Path]):
        """Initialize Equirectangular with an image file.

        Args:
            img_name: Path to the equirectangular panorama image

        Raises:
            FileNotFoundError: If the image file does not exist
            ValueError: If the image file is invalid or does not have 3 color channels
            IOError: If the image file cannot be read

        """
        img = load_image(img_name)
        self._img: np.ndarray = img

        # Verify image has 3 channels (color)
        if len(self._img.shape) != 3 or self._img.shape[2] != 3:
            raise ValueError(
                f"Image must have 3 color channels (RGB), got shape: {self._img.shape}"
            )

        [self._height, self._width, _] = self._img.shape

    def __enter__(self) -> "Equirectangular":
        """Enter context manager.

        Returns:
            Self reference for context manager usage
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """Exit context manager.

        No cleanup is required as the image is stored in-memory as a NumPy array
        and doesn't hold file handles or other system resources needing explicit
        release. The image data will be garbage collected when this instance is
        deleted.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        pass

    @profile("get_perspective")
    def get_perspective(
        self,
        FOV: float,
        THETA: float,
        PHI: float,
        height: int,
        width: int,
        interpolation: int = cv2.INTER_CUBIC,
    ) -> np.ndarray:
        """Split equirectangular panorama into normal perspective view.

                Args:
                    FOV (float): Field of view in degrees (must be between 1 and 180)
                    THETA (float): left/right angle in degrees (horizontal rotation, -180 to 180)
                    PHI (float): up/down angle in degrees (vertical rotation, -90 to 90)
                    height (int): output image height (must be > 0)
                    width (int): output image width (must be > 0)
                    interpolation (int, optional): OpenCV interpolation method. Defaults to cv2.INTER_CUBIC.
                        See cv2.remap for all available options.

                Returns:
                    np.ndarray: Perspective view image as a numpy array

                Raises:
                    ValueError: If any input parameter is out of valid range
        Example:
            >>> import equirec2perspec
            >>> # Load panorama and extract perspective view
            >>> with equirec2perspec.Equirectangular('panorama.jpg') as equ:
            ...     perspective = equ.get_perspective(60, 0, 0, 720, 1080)
            ...     # Extract front view (60° FOV)
            ...     front_view = equ.get_perspective(60, 0, 0, 720, 1080)
            ...     # Extract right view (90° FOV, looking 90° to the right)
            ...     right_view = equ.get_perspective(90, 90, 0, 720, 1080)
            ...     # Extract up view (45° FOV, looking 30° up)
            ...     up_view = equ.get_perspective(45, 0, -30, 720, 1080)
        """
        # Validate input parameters
        validate_perspective_params(FOV, THETA, PHI, height, width)

        # Build camera matrix and generate 3D coordinates
        K, K_inv = build_camera_matrix(FOV, width, height)
        xyz = generate_3d_coordinates(width, height, K_inv)

        # Compute rotation matrices
        R = compute_rotation_matrices(THETA, PHI)

        # Apply transformations and return final image
        return apply_transformations_and_remap(xyz, R, self._img, interpolation)
