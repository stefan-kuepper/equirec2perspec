# Performance Profiling Demos

This directory contains demonstration scripts showing how to use the performance profiling system in equirec2perspec.

## Demo Scripts

### 1. Basic Profiling (`demo_profiling.py`)
Shows basic profiling usage with the library's built-in profiling.

**Run:**
```bash
uv run python demo_profiling.py
```

**What it does:**
- Loads a panorama image
- Extracts 4 different perspective views
- Displays comprehensive profiling statistics
- Shows execution counts, mean/min/max times for each operation

**Sample Output:**
```
apply_transformations_and_remap:
  Count: 4
  Total: 0.214750s
  Mean:  0.053687ms
  Min:   0.043512ms
  Max:   0.076582ms
```

### 2. Custom Profiling (`demo_custom_profiling.py`)
Demonstrates how to add profiling to your own code using decorators and context managers.

**Run:**
```bash
uv run python demo_custom_profiling.py
```

**What it does:**
- Shows `@profile()` decorator usage for custom functions
- Shows `profile_block()` context manager for code blocks
- Demonstrates profiling custom preprocessing and batch operations
- Highlights how to extract stats for specific custom operations

**Key Features:**
```python
@profile("custom_operation")
def my_function():
    # Your code here
    pass

with profile_block("my_code_block"):
    # Your code here
    pass
```

### 3. Performance Analysis (`demo_performance_analysis.py`)
Advanced demo showing how to use profiling for performance analysis and optimization.

**Run:**
```bash
uv run python demo_performance_analysis.py
```

**What it does:**
- Tests performance across different output resolutions
- Identifies performance bottlenecks with percentage breakdown
- Shows visual distribution of time spent in each operation
- Provides actionable insights for optimization

**Sample Output:**
```
Time Distribution:
--------------------------------------------------------------------------------
get_perspective                     ██████████████████  37.8% ( 293.0ms)
load_image                          ████████████  24.5% ( 189.8ms)
apply_transformations_and_remap     ███████████  23.5% ( 181.9ms)
generate_3d_coordinates             ███████  14.1% ( 109.6ms)
```

## Using Profiling in Your Code

### Enable Profiling

Set the environment variable before running your code:

```bash
export EQUIREC2PERSPEC_PROFILE=1
```

Or in Python:
```python
import os
os.environ['EQUIREC2PERSPEC_PROFILE'] = '1'
```

### Get Statistics

```python
from equirec2perspec import get_profiling_stats

# ... run your code ...

stats = get_profiling_stats()
print(stats.summary())  # Human-readable summary

# Or get specific operation stats
op_stats = stats.get_stats("get_perspective")
print(f"Mean time: {op_stats['mean']:.4f}s")

# Or get all stats programmatically
all_stats = stats.get_all_stats()
```

### Reset Statistics

```python
from equirec2perspec import reset_profiling_stats

reset_profiling_stats()  # Clear all profiling data
```

### Check if Profiling is Enabled

```python
from equirec2perspec import is_profiling_enabled

if is_profiling_enabled():
    print("Profiling is active")
```

## Performance Insights

Based on the profiling demos, here are typical performance characteristics:

1. **Image Loading** (`load_image`): One-time cost, ~190ms for a 2.6MB image
2. **Coordinate Generation** (`generate_3d_coordinates`): Scales with output resolution
3. **Transformation & Remap** (`apply_transformations_and_remap`): Scales with output resolution
4. **Camera Matrix** (`build_camera_matrix`): Negligible cost (~0.2ms)
5. **Rotation Matrices** (`compute_rotation_matrices`): Negligible cost (~0.2ms)

### Resolution Impact

- **Low (360x540)**: ~55ms per view
- **Medium (720x1080)**: ~120ms per view
- **High (1080x1920)**: ~325ms per view

The main bottlenecks are coordinate generation and remapping operations, which both scale with the output resolution.

## Zero-Overhead When Disabled

When profiling is disabled (default), there is **zero runtime overhead**. The profiling decorators check the enabled flag and immediately return without timing.

```python
# Profiling disabled (default)
@profile("my_operation")
def my_function():
    # No overhead - function runs at normal speed
    pass
```
