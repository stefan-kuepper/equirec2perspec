import logging
from importlib.util import find_spec
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple, Union

import cv2
import numpy as np

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    try:
        from turbojpeg import TurboJPEG
    except ImportError:
        TurboJPEG = None
else:
    try:
        from turbojpeg import TurboJPEG

        logger.debug("Using TurboJPEG")
    except ImportError:
        logger.debug("USING opencv imread")
        TurboJPEG = None
    TurboJPEG = None


def load_image(path: Union[str, Path]) -> Optional[np.ndarray]:
    """Load an image from file path, supporting both str and Path objects.

    Args:
        path: Path to the image file

    Returns:
        Loaded image as numpy array, or None if loading fails

    """
    path_str = str(path)

    image: Optional[np.ndarray]
    if find_spec("turbojpeg") is not None and TurboJPEG is not None:
        tjpg = TurboJPEG()
        with open(path_str, "rb") as img:
            image = tjpg.decode(img.read())
    else:
        image = cv2.imread(path_str, cv2.IMREAD_COLOR)

    return image


def xyz2lonlat(xyz: np.ndarray) -> np.ndarray:
    atan2 = np.arctan2
    asin = np.arcsin

    norm = np.linalg.norm(xyz, axis=-1, keepdims=True)
    xyz_norm = xyz / norm
    x = xyz_norm[..., 0:1]
    y = xyz_norm[..., 1:2]
    z = xyz_norm[..., 2:]

    lon = atan2(x, z)
    lat = asin(y)
    lst = [lon, lat]

    out: np.ndarray = np.concatenate(lst, axis=-1)
    return out


def lonlat2XY(lonlat: np.ndarray, shape: Tuple[int, int, int]) -> np.ndarray:
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    lst = [X, Y]
    out: np.ndarray = np.concatenate(lst, axis=-1)

    return out


class Equirectangular:
    def __init__(self, img_name: Union[str, Path]):
        """Initialize Equirectangular with an image file.

        Args:
            img_name: Path to the equirectangular panorama image

        Raises:
            AttributeError: If the image fails to load

        """
        img = load_image(img_name)
        if img is None:
            raise AttributeError(f"Failed to load image: {img_name}")
        self._img: np.ndarray = img
        [self._height, self._width, _] = self._img.shape

    def GetPerspective(
        self,
        FOV: float,
        THETA: float,
        PHI: float,
        height: int,
        width: int,
        interpolation: int = cv2.INTER_CUBIC,
    ) -> np.ndarray:
        """Split equirectangular panorama into normal perspective view

        Args:
            FOV (float): Field of view
            THETA (float): left/right angle in degrees
            PHI (float):  up/down angle in degrees
            height (int): output image height
            width (int): output image width
            interpolation (_type_, optional): see cv2.remap. Defaults to cv2.INTER_CUBIC.

        Returns:
            np.ndarray: perspective view
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

        x = np.arange(width)
        y = np.arange(height)
        x, y = np.meshgrid(x, y)
        z = np.ones_like(x)
        xyz = np.concatenate([x[..., None], y[..., None], z[..., None]], axis=-1)
        xyz = xyz @ K_inv.T

        y_axis = np.array([0.0, 1.0, 0.0], np.float32)
        x_axis = np.array([1.0, 0.0, 0.0], np.float32)
        R1, _ = cv2.Rodrigues(y_axis * np.radians(THETA))
        R2, _ = cv2.Rodrigues(np.dot(R1, x_axis) * np.radians(PHI))
        R = R2 @ R1
        xyz = xyz @ R.T
        lonlat = xyz2lonlat(xyz)
        XY = lonlat2XY(lonlat, shape=self._img.shape).astype(np.float32)
        persp = cv2.remap(
            self._img, XY[..., 0], XY[..., 1], interpolation, borderMode=cv2.BORDER_WRAP
        )

        return persp
