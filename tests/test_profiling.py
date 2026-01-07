"""Tests for the profiling module."""

import os
import time
from unittest.mock import patch

import pytest

from equirec2perspec.profiling import (
    ProfileEntry,
    ProfilingStats,
    get_profiling_stats,
    is_profiling_enabled,
    profile,
    profile_block,
    reset_profiling_stats,
)


class TestProfilingEnabled:
    """Tests for profiling enabled detection."""

    def test_is_profiling_enabled_when_set_to_1(self) -> None:
        """Test profiling is enabled when environment variable is '1'."""
        with patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "1"}):
            assert is_profiling_enabled() is True

    def test_is_profiling_enabled_when_set_to_true(self) -> None:
        """Test profiling is enabled when environment variable is 'true'."""
        with patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "true"}):
            assert is_profiling_enabled() is True

    def test_is_profiling_enabled_when_set_to_yes(self) -> None:
        """Test profiling is enabled when environment variable is 'yes'."""
        with patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "yes"}):
            assert is_profiling_enabled() is True

    def test_is_profiling_enabled_when_not_set(self) -> None:
        """Test profiling is disabled when environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_profiling_enabled() is False

    def test_is_profiling_enabled_when_set_to_0(self) -> None:
        """Test profiling is disabled when environment variable is '0'."""
        with patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "0"}):
            assert is_profiling_enabled() is False


class TestProfileEntry:
    """Tests for ProfileEntry dataclass."""

    def test_profile_entry_creation(self) -> None:
        """Test ProfileEntry can be created with required fields."""
        entry = ProfileEntry(name="test_op", duration=1.23, timestamp=123456.0)
        assert entry.name == "test_op"
        assert entry.duration == 1.23
        assert entry.timestamp == 123456.0


class TestProfilingStats:
    """Tests for ProfilingStats class."""

    def test_add_entry_when_enabled(self) -> None:
        """Test adding entry when profiling is enabled."""
        stats = ProfilingStats(enabled=True)
        stats.add_entry("test_op", 1.5)

        assert len(stats.entries) == 1
        assert stats.entries[0].name == "test_op"
        assert stats.entries[0].duration == 1.5

    def test_add_entry_when_disabled(self) -> None:
        """Test adding entry when profiling is disabled doesn't record."""
        stats = ProfilingStats(enabled=False)
        stats.add_entry("test_op", 1.5)

        assert len(stats.entries) == 0

    def test_clear(self) -> None:
        """Test clearing all entries."""
        stats = ProfilingStats(enabled=True)
        stats.add_entry("op1", 1.0)
        stats.add_entry("op2", 2.0)

        stats.clear()
        assert len(stats.entries) == 0

    def test_get_stats_for_existing_operation(self) -> None:
        """Test getting statistics for an operation with entries."""
        stats = ProfilingStats(enabled=True)
        stats.add_entry("test_op", 1.0)
        stats.add_entry("test_op", 2.0)
        stats.add_entry("test_op", 3.0)

        result = stats.get_stats("test_op")
        assert result["count"] == 3
        assert result["total"] == 6.0
        assert result["mean"] == 2.0
        assert result["min"] == 1.0
        assert result["max"] == 3.0

    def test_get_stats_for_nonexistent_operation(self) -> None:
        """Test getting statistics for an operation with no entries."""
        stats = ProfilingStats(enabled=True)
        result = stats.get_stats("nonexistent")

        assert result["count"] == 0
        assert result["total"] == 0.0
        assert result["mean"] == 0.0
        assert result["min"] == 0.0
        assert result["max"] == 0.0

    def test_get_all_stats(self) -> None:
        """Test getting statistics for all operations."""
        stats = ProfilingStats(enabled=True)
        stats.add_entry("op1", 1.0)
        stats.add_entry("op1", 2.0)
        stats.add_entry("op2", 3.0)

        all_stats = stats.get_all_stats()
        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["count"] == 2
        assert all_stats["op2"]["count"] == 1

    def test_summary_with_no_data(self) -> None:
        """Test summary when no profiling data exists."""
        stats = ProfilingStats(enabled=True)
        summary = stats.summary()

        assert "No profiling data collected" in summary

    def test_summary_with_data(self) -> None:
        """Test summary with profiling data."""
        stats = ProfilingStats(enabled=True)
        stats.add_entry("test_op", 1.5)

        summary = stats.summary()
        assert "Profiling Summary" in summary
        assert "test_op" in summary
        assert "Count: 1" in summary
        assert "Total:" in summary
        assert "Mean:" in summary


class TestProfileDecorator:
    """Tests for profile decorator."""

    def test_profile_decorator_when_enabled(self) -> None:
        """Test profile decorator records execution time when enabled."""
        stats = ProfilingStats(enabled=True)
        reset_profiling_stats()

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "1"}),
        ):

            @profile("test_function")
            def slow_function() -> str:
                time.sleep(0.01)
                return "done"

            result = slow_function()

            assert result == "done"
            assert len(stats.entries) == 1
            assert stats.entries[0].name == "test_function"
            assert stats.entries[0].duration >= 0.01

    def test_profile_decorator_when_disabled(self) -> None:
        """Test profile decorator doesn't record when disabled."""
        stats = ProfilingStats(enabled=False)

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {}, clear=True),
        ):

            @profile("test_function")
            def fast_function() -> str:
                return "done"

            result = fast_function()

            assert result == "done"
            assert len(stats.entries) == 0

    def test_profile_decorator_with_default_name(self) -> None:
        """Test profile decorator uses function name when name not provided."""
        stats = ProfilingStats(enabled=True)

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "1"}),
        ):

            @profile()
            def my_function() -> str:
                return "done"

            my_function()

            assert len(stats.entries) == 1
            assert "my_function" in stats.entries[0].name

    def test_profile_decorator_preserves_function_metadata(self) -> None:
        """Test profile decorator preserves function name and docstring."""

        @profile("test")
        def documented_function() -> None:
            """This is a docstring."""
            pass

        assert documented_function.__name__ == "documented_function"
        assert documented_function.__doc__ == "This is a docstring."


class TestProfileBlock:
    """Tests for profile_block context manager."""

    def test_profile_block_when_enabled(self) -> None:
        """Test profile_block records execution time when enabled."""
        stats = ProfilingStats(enabled=True)

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "1"}),
        ):
            with profile_block("test_block"):
                time.sleep(0.01)

            assert len(stats.entries) == 1
            assert stats.entries[0].name == "test_block"
            assert stats.entries[0].duration >= 0.01

    def test_profile_block_when_disabled(self) -> None:
        """Test profile_block doesn't record when disabled."""
        stats = ProfilingStats(enabled=False)

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {}, clear=True),
        ):
            with profile_block("test_block"):
                pass

            assert len(stats.entries) == 0

    def test_profile_block_records_even_with_exception(self) -> None:
        """Test profile_block records time even when exception occurs."""
        stats = ProfilingStats(enabled=True)

        with (
            patch("equirec2perspec.profiling._global_stats", stats),
            patch.dict(os.environ, {"EQUIREC2PERSPEC_PROFILE": "1"}),
        ):
            with pytest.raises(ValueError):
                with profile_block("test_block"):
                    raise ValueError("test error")

            # Should still record the timing
            assert len(stats.entries) == 1
            assert stats.entries[0].name == "test_block"


class TestGlobalProfilingStats:
    """Tests for global profiling statistics functions."""

    def test_get_profiling_stats_returns_global_instance(self) -> None:
        """Test get_profiling_stats returns the global stats instance."""
        stats1 = get_profiling_stats()
        stats2 = get_profiling_stats()

        assert stats1 is stats2

    def test_reset_profiling_stats_clears_entries(self) -> None:
        """Test reset_profiling_stats clears all entries."""
        stats = get_profiling_stats()
        stats.enabled = True
        stats.add_entry("test", 1.0)

        reset_profiling_stats()

        assert len(stats.entries) == 0


class TestProfilingIntegration:
    """Integration tests for profiling with actual library usage."""

    def test_profiling_with_actual_operations(self) -> None:
        """Test profiling works with actual equirec2perspec operations."""
        reset_profiling_stats()
        stats = get_profiling_stats()
        stats.enabled = True

        from equirec2perspec.perspective_helpers import (
            build_camera_matrix,
            generate_3d_coordinates,
        )

        # Call some actual functions
        K, K_inv = build_camera_matrix(60.0, 1920, 1080)
        xyz = generate_3d_coordinates(100, 100, K_inv)

        # Should have recorded these operations
        all_stats = stats.get_all_stats()
        assert "build_camera_matrix" in all_stats
        assert "generate_3d_coordinates" in all_stats
        assert all_stats["build_camera_matrix"]["count"] == 1
        assert all_stats["generate_3d_coordinates"]["count"] == 1

        # Clean up
        reset_profiling_stats()
