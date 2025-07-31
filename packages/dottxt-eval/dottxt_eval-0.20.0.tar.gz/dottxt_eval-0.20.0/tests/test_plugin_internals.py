"""Tests for internal plugin functionality to achieve targeted coverage."""

import multiprocessing
from unittest.mock import MagicMock, patch

from doteval.plugin import _is_async_evaluation, pytest_configure, pytest_sessionfinish


class MockConfig:
    """Mock pytest config object."""

    def __init__(self):
        self._options = {}
        self._doteval_concurrent = None
        self._doteval_items = []

    def getoption(self, name, default=None):
        return self._options.get(name, default)

    def setoption(self, name, value):
        self._options[name] = value

    def addinivalue_line(self, name, value):
        """Mock addinivalue_line method."""
        pass


class MockSession:
    """Mock pytest session object."""

    def __init__(self, config=None):
        self.config = config if config else MockConfig()


class MockItem:
    """Mock pytest item object."""

    def __init__(self, function, name="test_item"):
        self.function = function
        self.name = name


def test_pytest_configure_auto_concurrent():
    """Test plugin configuration with --concurrent auto (line 92)."""
    config = MockConfig()
    config.setoption("concurrent", "auto")

    # This should trigger multiprocessing.cpu_count() on line 92
    pytest_configure(config)

    assert config._doteval_concurrent == multiprocessing.cpu_count()


def test_pytest_configure_invalid_concurrent_int():
    """Test plugin configuration with invalid integer concurrent option (lines 94-97)."""
    config = MockConfig()
    config.setoption("concurrent", "not_an_integer")

    # This should trigger the ValueError exception path on lines 94-97
    pytest_configure(config)

    assert config._doteval_concurrent is None


def test_pytest_configure_valid_concurrent_int():
    """Test plugin configuration with valid integer concurrent option."""
    config = MockConfig()
    config.setoption("concurrent", "4")

    pytest_configure(config)

    assert config._doteval_concurrent == 4


def test_pytest_configure_no_concurrent():
    """Test plugin configuration with no concurrent option."""
    config = MockConfig()
    # No concurrent option set

    pytest_configure(config)

    assert config._doteval_concurrent is None


def test_is_async_evaluation_with_coroutine_function():
    """Test async function detection (line 241)."""

    async def async_eval():
        return "result"

    item = MockItem(async_eval)

    assert _is_async_evaluation(item) is True


def test_is_async_evaluation_with_wrapped_function():
    """Test async function detection with __wrapped__ (lines 239-241)."""

    async def original_async():
        return "result"

    def wrapper():
        return "wrapped"

    # Simulate a decorated function with __wrapped__
    wrapper.__wrapped__ = original_async

    item = MockItem(wrapper)

    assert _is_async_evaluation(item) is True


def test_is_async_evaluation_with_sync_function():
    """Test sync function detection."""

    def sync_eval():
        return "result"

    item = MockItem(sync_eval)

    assert _is_async_evaluation(item) is False


@patch("doteval.runners.ConcurrentRunner")
@patch("asyncio.run")
def test_pytest_sessionfinish_with_concurrent_items(
    mock_asyncio_run, mock_concurrent_runner
):
    """Test pytest session finish with concurrent items (lines 232-234)."""
    # Setup mock
    mock_runner_instance = MagicMock()
    mock_concurrent_runner.return_value = mock_runner_instance

    # Create mock config with concurrent enabled
    config = MockConfig()
    config._doteval_concurrent = 2

    # Create mock async evaluation item
    async def async_eval():
        return "result"

    async_item = MockItem(async_eval, "async_eval")
    config._doteval_items = [async_item]

    # Create session with the config
    session = MockSession(config)

    # This should trigger lines 232-234
    pytest_sessionfinish(session, 0)

    # Verify concurrent runner was created and used
    mock_concurrent_runner.assert_called_once_with(config)
    mock_asyncio_run.assert_called_once_with(
        mock_runner_instance.run_evaluations([async_item])
    )


def test_pytest_sessionfinish_no_concurrent_items():
    """Test pytest session finish with no concurrent items (line 214)."""
    config = MockConfig()
    config._doteval_concurrent = 2

    # Create mock sync evaluation item
    def sync_eval():
        return "result"

    sync_item = MockItem(sync_eval, "sync_eval")
    config._doteval_items = [sync_item]

    # This should NOT trigger the concurrent path (line 232 should be skipped)
    with patch("doteval.runners.ConcurrentRunner") as mock_concurrent_runner:
        with patch("doteval.runners.SequentialRunner") as mock_sequential_runner:
            mock_seq_instance = MagicMock()
            mock_sequential_runner.return_value = mock_seq_instance

            session = MockSession(config)
            pytest_sessionfinish(session, 0)

            # Concurrent runner should not be called since no async items
            mock_concurrent_runner.assert_not_called()
            # Sequential runner should be called with sync items
            mock_sequential_runner.assert_called_once_with(config)
            mock_seq_instance.run_evaluations.assert_called_once_with([sync_item])


def test_pytest_sessionfinish_no_doteval_items():
    """Test pytest session finish with no doteval items at all (line 214)."""
    config = MockConfig()
    config._doteval_concurrent = 2
    config._doteval_items = []  # Empty list

    # This should trigger early return on line 214
    with patch("doteval.runners.ConcurrentRunner") as mock_concurrent_runner:
        session = MockSession(config)
        pytest_sessionfinish(session, 0)

        # Nothing should be called
        mock_concurrent_runner.assert_not_called()


def test_pytest_sessionfinish_mixed_items():
    """Test pytest session finish with mixed sync and async items (line 222)."""
    config = MockConfig()
    config._doteval_concurrent = 2

    # Create mixed items
    def sync_eval():
        return "sync"

    async def async_eval():
        return "async"

    sync_item = MockItem(sync_eval, "sync_eval")
    async_item = MockItem(async_eval, "async_eval")
    config._doteval_items = [sync_item, async_item]

    with patch("doteval.runners.ConcurrentRunner") as mock_concurrent_runner:
        with patch("doteval.runners.SequentialRunner") as mock_sequential_runner:
            with patch("asyncio.run") as mock_asyncio_run:
                mock_runner_instance = MagicMock()
                mock_concurrent_runner.return_value = mock_runner_instance
                mock_seq_instance = MagicMock()
                mock_sequential_runner.return_value = mock_seq_instance

                session = MockSession(config)
                pytest_sessionfinish(session, 0)

                # Should pass async items to concurrent runner
                mock_concurrent_runner.assert_called_once_with(config)
                mock_asyncio_run.assert_called_once_with(
                    mock_runner_instance.run_evaluations([async_item])
                )
                # Should pass sync items to sequential runner
                mock_sequential_runner.assert_called_once_with(config)
                mock_seq_instance.run_evaluations.assert_called_once_with([sync_item])
