#!/usr/bin/env python3
"""Demo script showing how to use profiling for performance analysis."""

import os

# Enable profiling
os.environ["EQUIREC2PERSPEC_PROFILE"] = "1"

from equirec2perspec import Equirectangular, get_profiling_stats, reset_profiling_stats

# Reset stats
reset_profiling_stats()

print("=" * 80)
print("Performance Analysis Demo")
print("=" * 80)
print()

# Test different resolutions to see performance impact
resolutions = [
    (360, 540, "Low"),
    (720, 1080, "Medium"),
    (1080, 1920, "High"),
]

print("Testing performance across different resolutions...")
print()

equ = Equirectangular("images/image.jpg")

for height, width, label in resolutions:
    reset_profiling_stats()
    print(f"{label} resolution ({height}x{width}):")

    # Generate a single perspective view
    view = equ.get_perspective(60, 0, 0, height, width)

    # Analyze the performance
    stats = get_profiling_stats()
    all_stats = stats.get_all_stats()

    # Get key operation times
    total_time = all_stats.get("get_perspective", {}).get("total", 0)
    coord_gen = all_stats.get("generate_3d_coordinates", {}).get("total", 0)
    remap = all_stats.get("apply_transformations_and_remap", {}).get("total", 0)

    print(f"  Total time:        {total_time * 1000:.2f}ms")
    print(
        f"  Coord generation:  {coord_gen * 1000:.2f}ms ({coord_gen / total_time * 100:.1f}%)"
    )
    print(
        f"  Remap operation:   {remap * 1000:.2f}ms ({remap / total_time * 100:.1f}%)"
    )
    print()

print("-" * 80)

# Analyze bottlenecks
reset_profiling_stats()
print()
print("Bottleneck Analysis - Processing 5 views at 720x1080...")
print()

equ = Equirectangular("images/image.jpg")

# Generate 5 views
for i in range(5):
    equ.get_perspective(60, i * 30, 0, 720, 1080)

stats = get_profiling_stats()
all_stats = stats.get_all_stats()

# Calculate what percentage of time each operation takes
total_entries = len(stats.entries)
operations_sorted = sorted(all_stats.items(), key=lambda x: x[1]["total"], reverse=True)

print("Time Distribution:")
print("-" * 80)

# Calculate total time across all operations
total_time_all = sum(s["total"] for s in all_stats.values())

for op_name, op_stats in operations_sorted:
    percentage = (op_stats["total"] / total_time_all) * 100
    bar_length = int(percentage / 2)
    bar = "█" * bar_length

    print(f"{op_name:35s} {bar} {percentage:5.1f}% ({op_stats['total'] * 1000:6.1f}ms)")

print("-" * 80)
print()
print("Key Insights:")
print("  • Most expensive operations are identified above")
print("  • generate_3d_coordinates and apply_transformations_and_remap are typically")
print("    the main performance bottlenecks")
print("  • These operations scale with output resolution")
print("  • load_image is a one-time cost per panorama")
print()
print("=" * 80)
