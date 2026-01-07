#!/usr/bin/env python3
"""Demo script to showcase the profiling functionality."""

import os

# Enable profiling
os.environ["EQUIREC2PERSPEC_PROFILE"] = "1"

from equirec2perspec import Equirectangular, get_profiling_stats, reset_profiling_stats

# Reset stats to start fresh
reset_profiling_stats()

print("=" * 80)
print("Performance Profiling Demo")
print("=" * 80)
print()

# Load image and extract multiple perspective views
print("Loading panorama and extracting perspective views...")
print("  - Front view (60° FOV, 720x1080)")
print("  - Right view (90° FOV, 720x1080)")
print("  - Left view (90° FOV, 720x1080)")
print("  - Up view (45° FOV, 720x1080)")
print()

equ = Equirectangular("images/image.jpg")

# Extract different views
front_view = equ.get_perspective(60, 0, 0, 720, 1080)
right_view = equ.get_perspective(90, 90, 0, 720, 1080)
left_view = equ.get_perspective(90, -90, 0, 720, 1080)
up_view = equ.get_perspective(45, 0, -30, 720, 1080)

# Get and display profiling statistics
stats = get_profiling_stats()
print(stats.summary())
print()
print("Total operations profiled:", len(stats.entries))
print()

# Show individual operation breakdown
all_stats = stats.get_all_stats()
print("Performance Breakdown:")
print("-" * 80)
for name, stat in all_stats.items():
    print(f"  {name}:")
    print(f"    Executions: {stat['count']}")
    print(f"    Avg time:   {stat['mean'] * 1000:.3f}ms")
    if stat["count"] > 1:
        print(f"    Total time: {stat['total'] * 1000:.3f}ms")
print("=" * 80)
