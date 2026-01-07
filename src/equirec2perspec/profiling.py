"""Performance profiling utilities for equirec2perspec.

This module provides decorators and context managers for profiling the performance
of image transformation operations. Profiling can be enabled/disabled via the
EQUIREC2PERSPEC_PROFILE environment variable.

Example:
    >>> import os
    >>> os.environ['EQUIREC2PERSPEC_PROFILE'] = '1'
    >>> from equirec2perspec import Equirectangular
    >>> from equirec2perspec.profiling import get_profiling_stats
    >>> equ = Equirectangular('panorama.jpg')
    >>> perspective = equ.get_perspective(60, 0, 0, 720, 1080)
    >>> stats = get_profiling_stats()
    >>> print(stats.summary())

"""

import functools
import logging
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic function decoration
F = TypeVar("F", bound=Callable[..., Any])


def is_profiling_enabled() -> bool:
    """Check if profiling is enabled via environment variable.

    Returns:
        True if EQUIREC2PERSPEC_PROFILE environment variable is set to '1', 'true', or 'yes'

    """
    return os.getenv("EQUIREC2PERSPEC_PROFILE", "").lower() in ("1", "true", "yes")


@dataclass
class ProfileEntry:
    """A single profiling measurement entry.

    Attributes:
        name: Name of the profiled operation
        duration: Duration in seconds
        timestamp: Unix timestamp when the measurement was taken

    """

    name: str
    duration: float
    timestamp: float


@dataclass
class ProfilingStats:
    """Collection of profiling statistics.

    Attributes:
        entries: List of all profiling entries
        enabled: Whether profiling is currently enabled

    """

    entries: list[ProfileEntry] = field(default_factory=list)
    enabled: bool = field(default_factory=is_profiling_enabled)

    def add_entry(self, name: str, duration: float) -> None:
        """Add a profiling entry.

        Args:
            name: Name of the profiled operation
            duration: Duration in seconds

        """
        if self.enabled:
            entry = ProfileEntry(name=name, duration=duration, timestamp=time.time())
            self.entries.append(entry)
            logger.debug(f"Profile [{name}]: {duration:.6f}s")

    def clear(self) -> None:
        """Clear all profiling entries."""
        self.entries.clear()

    def get_stats(self, name: str) -> dict[str, float]:
        """Get statistics for a specific operation.

        Args:
            name: Name of the operation to get stats for

        Returns:
            Dictionary containing 'count', 'total', 'mean', 'min', 'max' statistics

        """
        matching = [e for e in self.entries if e.name == name]
        if not matching:
            return {
                "count": 0,
                "total": 0.0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        durations = [e.duration for e in matching]
        return {
            "count": len(durations),
            "total": sum(durations),
            "mean": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
        }

    def get_all_stats(self) -> dict[str, dict[str, float]]:
        """Get statistics for all operations.

        Returns:
            Dictionary mapping operation names to their statistics

        """
        operation_names = set(e.name for e in self.entries)
        return {name: self.get_stats(name) for name in sorted(operation_names)}

    def summary(self) -> str:
        """Generate a human-readable summary of profiling statistics.

        Returns:
            Formatted string containing profiling summary

        """
        if not self.entries:
            return "No profiling data collected."

        lines = ["Profiling Summary", "=" * 80]

        all_stats = self.get_all_stats()
        for name, stats in all_stats.items():
            lines.append(f"\n{name}:")
            lines.append(f"  Count: {stats['count']}")
            lines.append(f"  Total: {stats['total']:.6f}s")
            lines.append(f"  Mean:  {stats['mean']:.6f}s")
            lines.append(f"  Min:   {stats['min']:.6f}s")
            lines.append(f"  Max:   {stats['max']:.6f}s")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


# Global profiling stats instance
_global_stats = ProfilingStats()


def get_profiling_stats() -> ProfilingStats:
    """Get the global profiling statistics instance.

    Returns:
        Global ProfilingStats instance

    """
    return _global_stats


def reset_profiling_stats() -> None:
    """Reset the global profiling statistics."""
    _global_stats.clear()


def profile(name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator to profile function execution time.

    Args:
        name: Optional custom name for the profiled operation.
              If not provided, uses the function's qualified name.

    Returns:
        Decorated function that records execution time

    Example:
        >>> @profile()
        ... def my_function():
        ...     pass
        >>> @profile("custom_name")
        ... def another_function():
        ...     pass

    """

    def decorator(func: F) -> F:
        operation_name = name or f"{func.__module__}.{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _global_stats.enabled:
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start_time
                _global_stats.add_entry(operation_name, duration)

        return wrapper  # type: ignore[return-value]

    return decorator


@contextmanager
def profile_block(name: str) -> Iterator[None]:
    """Context manager to profile a block of code.

    Args:
        name: Name for the profiled code block

    Yields:
        None

    Example:
        >>> with profile_block("my_operation"):
        ...     # code to profile
        ...     pass

    """
    if not _global_stats.enabled:
        yield
        return

    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        _global_stats.add_entry(name, duration)
