#!/usr/bin/env python3
"""Demo script showing custom profiling usage."""

import os
import time

# Enable profiling
os.environ["EQUIREC2PERSPEC_PROFILE"] = "1"

from equirec2perspec import (
    Equirectangular,
    get_profiling_stats,
    profile,
    profile_block,
    reset_profiling_stats,
)

# Reset stats
reset_profiling_stats()


# Example 1: Using @profile decorator for custom functions
@profile("custom_preprocessing")
def preprocess_panorama(image_path: str) -> Equirectangular:
    """Simulate some preprocessing before loading."""
    time.sleep(0.01)  # Simulate preprocessing work
    return Equirectangular(image_path)


# Example 2: Using profile_block context manager
def batch_process_views(equ: Equirectangular) -> list:
    """Process multiple views with granular profiling."""
    results = []

    with profile_block("generate_cardinal_views"):
        # Generate cardinal direction views
        for angle in [0, 90, 180, -90]:
            view = equ.get_perspective(60, angle, 0, 480, 640)
            results.append(view)

    with profile_block("generate_vertical_views"):
        # Generate up/down views
        for phi in [-45, 45]:
            view = equ.get_perspective(60, 0, phi, 480, 640)
            results.append(view)

    return results


print("=" * 80)
print("Custom Profiling Demo")
print("=" * 80)
print()

# Run custom profiled operations
print("Running custom profiled operations...")
equ = preprocess_panorama("images/image.jpg")
views = batch_process_views(equ)

print(f"Generated {len(views)} perspective views")
print()

# Display profiling results
stats = get_profiling_stats()
print(stats.summary())
print()

# Highlight custom operations
print("Custom Operations Highlighted:")
print("-" * 80)
custom_ops = [
    "custom_preprocessing",
    "generate_cardinal_views",
    "generate_vertical_views",
]
for op_name in custom_ops:
    op_stats = stats.get_stats(op_name)
    if op_stats["count"] > 0:
        print(f"  {op_name}:")
        print(f"    Time: {op_stats['total'] * 1000:.3f}ms")
print()
print("=" * 80)
