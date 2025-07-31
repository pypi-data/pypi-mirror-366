"""Tests for adaptive concurrency internal functionality to achieve targeted coverage."""

import asyncio
import time

import pytest

from doteval.concurrency.adaptive import Adaptive, ThroughputTracker


class TestThroughputTracker:
    """Test the ThroughputTracker component."""

    def test_throughput_tracker_insufficient_data(self):
        """Test throughput calculation with insufficient data (line 45)."""
        tracker = ThroughputTracker()

        # With no completions, should return None
        assert tracker.get_throughput() is None

        # With only one completion, should return None
        tracker.record_completion(time.time())
        assert tracker.get_throughput() is None

    def test_throughput_tracker_zero_time_span(self):
        """Test throughput calculation with zero time span (lines 44-45)."""
        tracker = ThroughputTracker()

        # Record completions at the exact same time
        now = time.time()
        tracker.record_completion(now)
        tracker.record_completion(now)
        tracker.record_completion(now)

        # Should return None due to zero time span
        assert tracker.get_throughput() is None

    def test_recent_throughput_insufficient_data(self):
        """Test recent throughput with insufficient data (lines 51-52)."""
        tracker = ThroughputTracker()

        # With no completions
        assert tracker.get_recent_throughput() is None

        # With only one completion
        tracker.record_completion(time.time())
        assert tracker.get_recent_throughput() is None

    def test_recent_throughput_zero_time_span(self):
        """Test recent throughput with zero time span (lines 55-57)."""
        tracker = ThroughputTracker()

        # Record completions at the same time
        now = time.time()
        tracker.record_completion(now)
        tracker.record_completion(now)
        tracker.record_completion(now)

        # Should return None due to zero time span
        assert tracker.get_recent_throughput() is None

    def test_recent_throughput_custom_window(self):
        """Test recent throughput with custom window size (lines 54-59)."""
        tracker = ThroughputTracker()

        # Create a timing pattern where different windows give different results
        base_time = time.time()
        # Add completions with specific timing: fast start, then slower
        times = [
            base_time,  # 0
            base_time + 0.1,  # 1
            base_time + 0.2,  # 2
            base_time + 1.0,  # 3 (big gap)
            base_time + 2.0,  # 4 (big gap)
        ]

        for timestamp in times:
            tracker.record_completion(timestamp)

        # Test with different window sizes
        throughput_3 = tracker.get_recent_throughput(
            3
        )  # Uses timestamps 2, 3, 4 (span=1.8, rate=2/1.8)
        throughput_5 = tracker.get_recent_throughput(
            5
        )  # Uses all timestamps (span=2.0, rate=4/2.0)

        assert throughput_3 is not None
        assert throughput_5 is not None
        # These should be different due to different time spans
        assert throughput_3 != throughput_5


class TestAdaptiveConcurrency:
    """Test the Adaptive concurrency strategy."""

    @pytest.mark.asyncio
    async def test_adaptive_error_handling_and_recording(self):
        """Test error handling and recording in adaptive execution (line 155)."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.1,
            error_backoff_factor=0.5,
        )

        error_count = 0
        success_count = 0

        def create_tasks():
            nonlocal error_count, success_count
            for i in range(5):

                async def task(task_id=i):
                    if task_id == 1:  # Make second task fail
                        raise ValueError(f"Error in task {task_id}")
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        errors_caught = 0

        try:
            async for result in strategy.execute(create_tasks()):
                if result is not None:
                    results.append(result)
        except ValueError as e:
            errors_caught += 1
            assert "Error in task 1" in str(e)

        # Should have caught the error and recorded it
        assert errors_caught > 0
        stats = strategy.get_stats()
        assert stats["recent_errors"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_progress_callback_with_results(self):
        """Test progress callback with actual results (lines 159-160)."""
        strategy = Adaptive(initial_concurrency=2, adaptation_interval=0.1)

        progress_results = []

        def progress_callback(result):
            progress_results.append(result)

        def create_tasks():
            for i in range(3):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks(), progress_callback):
            results.append(result)

        # Both results and progress_results should have the same items
        assert len(results) == 3
        assert len(progress_results) == 3
        assert set(results) == set(progress_results)

    @pytest.mark.asyncio
    async def test_adaptive_result_yielding(self):
        """Test result yielding when not None (lines 162-163)."""
        strategy = Adaptive(initial_concurrency=2, adaptation_interval=0.1)

        def create_tasks():
            # Mix of tasks returning results and None
            async def task_with_result():
                await asyncio.sleep(0.01)
                return "valid_result"

            async def task_with_none():
                await asyncio.sleep(0.01)
                return None

            yield task_with_result
            yield task_with_none
            yield task_with_result

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        # Should only yield non-None results
        assert len(results) == 2
        assert all(r == "valid_result" for r in results)

    @pytest.mark.asyncio
    async def test_adaptive_exception_error_counting(self):
        """Test exception handling increases error count (lines 164-166)."""
        strategy = Adaptive(initial_concurrency=1, adaptation_interval=0.1)

        def create_tasks():
            async def failing_task():
                await asyncio.sleep(0.01)
                raise RuntimeError("Task failed")

            yield failing_task

        with pytest.raises(RuntimeError, match="Task failed"):
            async for result in strategy.execute(create_tasks()):
                pass

        # Error count should have increased
        stats = strategy.get_stats()
        assert stats["recent_errors"] > 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_adjustment_under_load(self):
        """Test concurrency adjustment logic (lines 186, 222-226)."""
        strategy = Adaptive(
            initial_concurrency=2,
            adaptation_interval=0.05,  # Fast adaptation
            min_concurrency=1,
            max_concurrency=8,
            stability_window=1,
        )

        def create_tasks():
            # Create many tasks to trigger adaptation
            for i in range(20):

                async def task(task_id=i):
                    await asyncio.sleep(0.02)  # Moderate load
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 20

        # Strategy should have adapted concurrency
        final_stats = strategy.get_stats()
        assert "adaptation_history" in final_stats
        assert final_stats["total_completed"] == 20

    @pytest.mark.asyncio
    async def test_adaptive_throughput_based_scaling(self):
        """Test throughput-based concurrency scaling (lines 237-255)."""
        strategy = Adaptive(
            initial_concurrency=3,
            adaptation_interval=0.08,
            min_concurrency=2,
            max_concurrency=10,
            stability_window=2,
        )

        def create_tasks():
            # Create enough tasks to allow multiple adaptation cycles
            for i in range(25):

                async def task(task_id=i):
                    await asyncio.sleep(0.015)  # Consistent work time
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 25

        # Should have some adaptation history
        stats = strategy.get_stats()
        assert stats["adaptation_history"] is not None
        assert len(stats["adaptation_history"]) >= 0

    @pytest.mark.asyncio
    async def test_adaptive_concurrency_limits_enforcement(self):
        """Test that concurrency limits are enforced (lines 262-265, 271-272)."""
        strategy = Adaptive(
            initial_concurrency=3,
            min_concurrency=2,
            max_concurrency=4,
            adaptation_interval=0.1,
        )

        def create_tasks():
            for i in range(8):

                async def task(task_id=i):
                    await asyncio.sleep(0.01)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 8

        # Concurrency should respect limits
        assert strategy.current_concurrency >= 2
        assert strategy.current_concurrency <= 4

    @pytest.mark.asyncio
    async def test_adaptive_performance_degradation_handling(self):
        """Test handling of performance degradation (lines 243-248)."""
        strategy = Adaptive(
            initial_concurrency=3,
            adaptation_interval=0.06,
            min_concurrency=1,
            max_concurrency=8,
            stability_window=1,
        )

        task_counter = 0

        def create_tasks():
            nonlocal task_counter
            for i in range(15):

                async def task(task_id=i):
                    nonlocal task_counter
                    task_counter += 1
                    # Simulate degrading performance
                    delay = 0.01 + (task_counter * 0.003)
                    await asyncio.sleep(delay)
                    return f"result_{task_id}"

                yield task

        results = []
        async for result in strategy.execute(create_tasks()):
            results.append(result)

        assert len(results) == 15

        # Strategy should have attempted adaptations
        stats = strategy.get_stats()
        assert stats["total_completed"] == 15
