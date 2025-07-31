"""Integration tests for complete doteval workflows."""

import tempfile
from pathlib import Path

from doteval import ForEach
from doteval.evaluators import exact_match
from doteval.models import Result
from doteval.sessions import SessionManager


def test_complete_evaluation_workflow():
    """Test the full user workflow end-to-end."""
    # Create temporary directory for test storage
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        # Simple test dataset
        test_data = [
            ("What is 2+2?", "4"),
            ("What is 3+3?", "6"),
            ("What is 5+5?", "10"),
        ]

        # Create ForEach instance with storage
        foreach = ForEach(storage=f"json://{storage_path}")

        # Define evaluation function
        @foreach("question,answer", test_data)
        def eval_math(question, answer):
            # Create prompt
            prompt = f"Question: {question}"
            # Simulate some processing
            result = "4" if "2+2" in question else "wrong"
            # Return Result with prompt and scores
            return Result(exact_match(result, answer), prompt=prompt)

        # Run the evaluation with the new API
        result = eval_math(
            evaluation_name="eval_math", experiment_name="test_experiment", samples=None
        )

        # Verify results
        assert len(result.results) == 3
        assert (
            result.summary["exact_match"]["accuracy"] == 1 / 3
        )  # Only first item matches

        # Create session manager to verify storage
        session_manager = SessionManager(
            storage=f"json://{storage_path}", experiment_name="test_experiment"
        )

        # Verify experiment was created and evaluation persisted
        experiments = session_manager.storage.list_experiments()
        assert "test_experiment" in experiments

        # Verify we can retrieve the evaluation results
        results = session_manager.storage.get_results("test_experiment", "eval_math")
        assert len(results) == 3


def test_session_persistence_across_runs():
    """Test that session state persists across multiple runs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir)

        test_data = [("Q1", "A1"), ("Q2", "A2")]

        # Create ForEach instance with storage
        foreach = ForEach(storage=f"json://{storage_path}")

        @foreach("question,answer", test_data)
        def eval_test(question, answer):
            prompt = f"Q: {question}"
            return Result(exact_match(answer, "A1"), prompt=prompt)

        # First run
        result1 = eval_test(
            evaluation_name="eval_test",
            experiment_name="persistence_test",
            samples=None,
        )
        assert len(result1.results) == 2  # Verify first run processed items

        # Second run with new session manager (simulates new process)
        session_manager2 = SessionManager(
            storage=f"json://{storage_path}", experiment_name="persistence_test"
        )

        # Should be able to retrieve the same evaluation results
        results = session_manager2.storage.get_results("persistence_test", "eval_test")
        assert len(results) == 2

        # Experiments should be the same
        experiments = session_manager2.storage.list_experiments()
        assert "persistence_test" in experiments


def test_progress_tracker_with_errors():
    """Test progress tracking when some evaluations have errors."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create ForEach instance with isolated storage
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("test1", "answer1"), ("test2", "answer2"), ("test3", "answer3")]

        error_on_item = "test2"

        @foreach_instance("input,expected", dataset)
        def eval_with_errors(input, expected):
            if input == error_on_item:
                raise ValueError(f"Intentional error on {input}")
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should complete despite errors
        result = eval_with_errors(
            evaluation_name="test_eval", experiment_name="test_exp", samples=None
        )

        # Should have 3 results, with one containing an error
        assert len(result.results) == 3
        error_results = [r for r in result.results if r.error]
        assert len(error_results) == 1
        assert "Intentional error on test2" in error_results[0].error


def test_progress_tracker_completion_count():
    """Test progress tracking with explicit completion count."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("test1", "answer1"), ("test2", "answer2")]

        @foreach_instance("input,expected", dataset)
        def eval_completion_count(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        result = eval_completion_count(
            evaluation_name="test_eval", experiment_name="test_exp", samples=None
        )

        assert len(result.results) == 2


def test_sequential_runner_empty_items():
    """Test sequential runner with empty evaluation items."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        # Empty dataset
        dataset = []

        @foreach_instance("input,expected", dataset)
        def eval_empty(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        result = eval_empty(
            evaluation_name="test_eval", experiment_name="test_exp", samples=None
        )

        assert len(result.results) == 0


def test_is_running_under_pytest():
    """Test the _is_running_under_pytest helper function."""
    from doteval.progress import _is_running_under_pytest

    # Since we're running this in pytest, this should return True
    assert _is_running_under_pytest() is True


def test_concurrent_runner_with_empty_items():
    """Test concurrent runner behavior with empty evaluation items."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        # Empty dataset
        dataset = []

        @foreach_instance("input,expected", dataset)
        async def eval_empty_concurrent(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        result = asyncio.run(
            eval_empty_concurrent(
                evaluation_name="test_eval", experiment_name="test_exp", samples=None
            )
        )

        assert len(result.results) == 0


def test_concurrent_runner_multiple_async_evaluations():
    """Test concurrent runner with multiple async evaluations."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("test1", "test1"), ("test2", "test2"), ("test3", "test3")]

        @foreach_instance("input,expected", dataset)
        async def eval_concurrent_multi(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        result = asyncio.run(
            eval_concurrent_multi(
                evaluation_name="test_eval",
                experiment_name="test_exp",
                samples=None,
                max_concurrency=2,  # Force concurrent execution
            )
        )

        assert len(result.results) == 3


def test_sequential_runner_with_progress_finishing():
    """Test sequential runner progress finishing in finally block."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("test1", "answer1"), ("test2", "answer2")]

        @foreach_instance("input,expected", dataset)
        def eval_sequential_progress(input, expected):
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should exercise the finally block in SequentialRunner
        result = eval_sequential_progress(
            evaluation_name="test_eval", experiment_name="test_exp", samples=None
        )

        assert len(result.results) == 2


def test_concurrent_runner_with_progress_finishing():
    """Test concurrent runner progress finishing in finally block."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("test1", "test1"), ("test2", "test2")]

        @foreach_instance("input,expected", dataset)
        async def eval_concurrent_progress(input, expected):
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Q: {input}")

        # This should exercise the finally block in ConcurrentRunner
        result = asyncio.run(
            eval_concurrent_progress(
                evaluation_name="test_eval",
                experiment_name="test_exp",
                samples=None,
                max_concurrency=2,
            )
        )

        assert len(result.results) == 2


def test_concurrent_runner_task_creation():
    """Test concurrent runner task creation and evaluation processing."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [
            ("item1", "expected1"),
            ("item2", "expected2"),
            ("item3", "expected3"),
        ]

        @foreach_instance("input,expected", dataset)
        async def eval_task_creation(input, expected):
            # Simulate some async work
            await asyncio.sleep(0.002)
            return Result(exact_match(input, expected), prompt=f"Processing: {input}")

        # This should exercise task creation, gathering, and progress management
        result = asyncio.run(
            eval_task_creation(
                evaluation_name="test_eval",
                experiment_name="test_exp",
                samples=None,
                max_concurrency=3,  # Allow all tasks to run concurrently
            )
        )

        assert len(result.results) == 3


def test_concurrent_runner_single_evaluation_method():
    """Test the concurrent runner's single evaluation method."""
    import asyncio
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        foreach_instance = ForEach(storage=f"json://{temp_dir}")

        dataset = [("single_test", "single_expected")]

        @foreach_instance("input,expected", dataset)
        async def eval_single_method(input, expected):
            # Test the run_single_evaluation method specifically
            await asyncio.sleep(0.001)
            return Result(exact_match(input, expected), prompt=f"Single eval: {input}")

        result = asyncio.run(
            eval_single_method(
                evaluation_name="test_eval",
                experiment_name="test_exp",
                samples=None,
                max_concurrency=1,  # Forces single evaluation path
            )
        )

        assert len(result.results) == 1
