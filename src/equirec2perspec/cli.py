#!/usr/bin/env python3
"""Command-line interface for equirec2perspec.

This module provides a CLI for converting equirectangular panoramic images
to perspective views using the equirec2perspec library.
"""

import os
from pathlib import Path
from typing import Optional

import click
import cv2

from .Equirec2Perspec import Equirectangular


def _get_interpolation_method(method: str) -> int:
    """Map interpolation method string to OpenCV constant.

    Args:
        method: Interpolation method name

    Returns:
        OpenCV interpolation constant

    Raises:
        ValueError: If method is not supported
    """
    interpolation_map = {
        "nearest": cv2.INTER_NEAREST,
        "bilinear": cv2.INTER_LINEAR,
        "bicubic": cv2.INTER_CUBIC,
        "lanczos": cv2.INTER_LANCZOS4,
    }

    if method not in interpolation_map:
        raise ValueError(f"Unsupported interpolation method: {method}")

    return interpolation_map[method]


def _calculate_dimensions(
    width: Optional[int], height: Optional[int]
) -> tuple[int, int]:
    """Calculate output dimensions with smart defaults.

    Args:
        width: Output width (optional)
        height: Output height (optional)

    Returns:
        Tuple of (width, height)

    Raises:
        ValueError: If dimensions are invalid
    """
    if width is None and height is None:
        # Default to 1920x1080 (16:9 aspect ratio)
        return 1920, 1080

    if width is None:
        if height is None or height <= 0:
            raise ValueError("Height must be greater than 0")
        # Calculate width from height assuming 16:9 aspect ratio
        return int(height * 16 / 9), height

    if height is None:
        if width <= 0:
            raise ValueError("Width must be greater than 0")
        # Calculate height from width assuming 16:9 aspect ratio
        return width, int(width * 9 / 16)

    # Both provided
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be greater than 0")

    return width, height


@click.command()
@click.argument(
    "input_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
)
@click.argument(
    "output_path",
    type=click.Path(file_okay=True, dir_okay=False, resolve_path=True),
)
@click.option(
    "--fov",
    type=float,
    default=60.0,
    help="Field of view angle in degrees (1-180, default: 60)",
)
@click.option(
    "--theta",
    type=float,
    default=0.0,
    help="Horizontal rotation angle in degrees (-180 to 180, default: 0)",
)
@click.option(
    "--phi",
    type=float,
    default=0.0,
    help="Vertical rotation angle in degrees (-90 to 90, default: 0)",
)
@click.option(
    "--width",
    type=int,
    help="Output image width in pixels (auto-calculated if not provided)",
)
@click.option(
    "--height",
    type=int,
    help="Output image height in pixels (auto-calculated if not provided)",
)
@click.option(
    "--interpolation",
    type=click.Choice(["nearest", "bilinear", "bicubic", "lanczos"]),
    default="bicubic",
    help="Interpolation method (default: bicubic)",
)
@click.option(
    "--quality",
    type=int,
    default=95,
    help="JPEG quality 1-100 (default: 95)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable detailed output",
)
def main(
    input_path: str,
    output_path: str,
    fov: float,
    theta: float,
    phi: float,
    width: Optional[int],
    height: Optional[int],
    interpolation: str,
    quality: int,
    verbose: bool,
) -> None:
    """Convert equirectangular images to perspective views.

    INPUT_PATH: Path to input equirectangular image
    OUTPUT_PATH: Path for output perspective image

    Examples:
        equirec2perspec panorama.jpg perspective.jpg
        equirec2perspec --fov 90 --theta 45 input.jpg output.jpg
        equirec2perspec --fov 60 --interpolation lanczos --quality 100 input.jpg output.jpg
    """
    # Validate parameters
    if not (1 <= fov <= 180):
        raise click.BadParameter("FOV must be between 1 and 180 degrees")

    if not (-180 <= theta <= 180):
        raise click.BadParameter("THETA must be between -180 and 180 degrees")

    if not (-90 <= phi <= 90):
        raise click.BadParameter("PHI must be between -90 and 90 degrees")

    if not (1 <= quality <= 100):
        raise click.BadParameter("Quality must be between 1 and 100")

    # Calculate output dimensions
    try:
        output_width, output_height = _calculate_dimensions(width, height)
    except ValueError as e:
        raise click.BadParameter(str(e)) from e

    # Check output directory is writable
    output_dir = Path(output_path).parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise click.ClickException(f"Cannot create output directory: {e}") from e

    if not os.access(output_dir, os.W_OK):
        raise click.ClickException(f"Output directory is not writable: {output_dir}")

    # Get interpolation method
    interpolation_cv = _get_interpolation_method(interpolation)

    try:
        if verbose:
            click.echo(f"Loading equirectangular image: {input_path}")

        # Load equirectangular image
        with Equirectangular(input_path) as equ:
            if verbose:
                click.echo(
                    f"Extracting {output_width}x{output_height} perspective view:"
                    f" FOV={fov}°, θ={theta}°, φ={phi}°, interpolation={interpolation}"
                )

            # Extract perspective view
            perspective_img = equ.get_perspective(
                fov, theta, phi, output_height, output_width, interpolation_cv
            )

            if verbose:
                click.echo(f"Saving to: {output_path}")

            # Save with JPEG quality
            success = cv2.imwrite(
                output_path, perspective_img, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )

            if not success:
                raise click.ClickException("Failed to save output image")

            if verbose:
                click.echo("✓ Successfully converted image")
            else:
                click.echo(f"✓ {output_path}")

    except FileNotFoundError as e:
        raise click.ClickException(f"File not found: {e}") from e
    except ValueError as e:
        raise click.ClickException(f"Invalid parameter: {e}") from e
    except Exception as e:
        raise click.ClickException(f"Processing failed: {e}") from e


if __name__ == "__main__":
    main()
