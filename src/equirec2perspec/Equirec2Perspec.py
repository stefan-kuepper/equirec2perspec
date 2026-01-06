from importlib.util import find_spec
import cv2
import numpy as np

try:
    from turbojpeg import TurboJPEG

    print("Using TurboJPEG")
except ImportError:
    print("USING opencv imread")


def load_image(path):
    if find_spec("turbojpeg") is not None:
        tjpg = TurboJPEG()
        with open(path, "rb") as img:
            image = tjpg.decode(img.read())
    else:
        image = cv2.imread(path, cv2.IMREAD_COLOR)

    return image


def xyz2lonlat(xyz):
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

    out = np.concatenate(lst, axis=-1)
    return out


def lonlat2XY(lonlat, shape):
    X = (lonlat[..., 0:1] / (2 * np.pi) + 0.5) * (shape[1] - 1)
    Y = (lonlat[..., 1:] / (np.pi) + 0.5) * (shape[0] - 1)
    lst = [X, Y]
    out = np.concatenate(lst, axis=-1)

    return out


class Equirectangular:
    def __init__(self, img_name):
        self._img = load_image(img_name)
        [self._height, self._width, _] = self._img.shape

    def GetPerspective(
        self,
        FOV: float,
        THETA: float,
        PHI: float,
        height: int,
        width: int,
        interpolation=cv2.INTER_CUBIC,
    ):
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
