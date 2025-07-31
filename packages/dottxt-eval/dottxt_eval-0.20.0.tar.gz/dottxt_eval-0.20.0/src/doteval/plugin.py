"""Pytest plugin for doteval - LLM evaluation framework integration.

This module provides seamless integration between doteval's evaluation system and pytest's
test discovery and execution framework. It allows evaluation functions decorated with
@foreach to be collected and executed as pytest tests.

The plugin uses a unified collection system where ALL doteval functions are collected
during pytest's collection phase and executed at session end using appropriate runners:

1. **Collection Phase** (pytest_collection_modifyitems):
   - All functions with @foreach decorators are marked with 'doteval' marker
   - All doteval items are collected into config._doteval_items for deferred execution

2. **Test Execution Phase** (pytest_runtest_call):
   - All doteval functions are SKIPPED during normal test execution
   - Fixture values are captured and stored for later use (when pytest's fixture system is active)
   - This ensures doteval functions don't interfere with normal pytest test flow

3. **Session End** (pytest_sessionfinish):
   - Collected doteval items are executed using appropriate runners:
     * SequentialRunner: For sync functions and async functions in non-concurrent mode
     * ConcurrentRunner: For async functions when --concurrent flag is used
   - Results are stored in config._evaluation_results for retrieval
"""

import asyncio
import inspect
import multiprocessing
from typing import Any, Dict, Optional, Union

import pytest
from pytest import Config, Function, Item, Metafunc, Parser, Session


@pytest.hookimpl
def pytest_addoption(parser: Parser) -> None:
    """Add command line options that are specific to doteval.

    This hook registers custom CLI options that doteval users can pass to pytest:
    - --samples: Limit the number of dataset samples to evaluate
    - --experiment: Name the experiment for result storage
    - --concurrent: Number of concurrent evaluations to run (similar to pytest-xdist syntax)

    Args:
        parser: Pytest's argument parser for adding custom command line options.
                This is a pytest.config.argparsing.Parser instance.

    Note:
        This is a pytest hook implementation that gets called during pytest initialization.
        The parser parameter is automatically provided by pytest.
    """
    parser.addoption(
        "--samples", type=int, help="Maximum number of dataset samples to evaluate"
    )
    parser.addoption("--experiment", type=str, help="Name of the experiment")
    parser.addoption(
        "-C",
        "--concurrent",
        dest="concurrent",
        default=None,
        help="Number of concurrent evaluations to run. Use 'auto' for CPU count.",
    )


@pytest.hookimpl
def pytest_configure(config: Config) -> None:
    """Configure pytest for doteval integration.

    This hook extends pytest's collection patterns to include doteval evaluation files:
    - Collects files named `eval_*.py` (in addition to `test_*.py`)
    - Collects functions named `eval_*` (in addition to `test_*`)
    - Registers the 'doteval' marker for filtering evaluations vs tests
    - Initializes storage for evaluation results
    - Configures concurrent execution if requested

    Args:
        config: Pytest configuration object that holds command line options,
                ini-file values, and other configuration data.

    Note:
        This hook is called once per pytest session after command line options
        have been parsed but before test collection begins.
    """
    config.addinivalue_line("markers", "doteval: mark test as LLM evaluation")
    config.addinivalue_line("python_files", "eval_*.py")
    config.addinivalue_line("python_functions", "eval_*")
    config._evaluation_results = {}

    # Check if concurrent execution is requested
    concurrent_option = config.getoption("concurrent", None)
    if concurrent_option == "auto":
        config._doteval_concurrent = multiprocessing.cpu_count()
    elif concurrent_option:
        try:
            config._doteval_concurrent = int(concurrent_option)
        except ValueError:
            config._doteval_concurrent = None
    else:
        config._doteval_concurrent = None

    # Store evaluation items that pass marker filtering for deferred execution
    config._doteval_items = []


@pytest.hookimpl
def pytest_pyfunc_call(pyfuncitem: Function) -> Optional[bool]:
    """Intercept function calls for doteval functions.

    This hook prevents pytest from trying to call doteval functions directly.
    Instead, we handle the execution in pytest_runtest_call where we can:
    - Pass the proper evaluation parameters (evaluation_name, experiment_name, samples)
    - Handle fixture resolution correctly
    - Run the actual evaluation logic

    Args:
        pyfuncitem: A pytest Function item representing a Python function to be executed.

    Returns:
        bool or None: True if we handled the call (for doteval functions),
                      None to let pytest handle it normally (for regular test functions).

    Note:
        Returning True indicates to pytest that we handled the call and it should
        not attempt to execute the function itself.
    """
    if pyfuncitem.get_closest_marker("doteval"):
        # For doteval functions, return True to indicate we handled the call
        return True

    return None


@pytest.hookimpl
def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Prevent fixture resolution errors for doteval functions.

    The problem: When pytest sees a function like `def eval_func(input, expected)`,
    it thinks 'input' and 'expected' are fixtures that need to be resolved. Pytest
    fixture resolution happens before our plugin is called.

    The solution: We pre-parametrize dataset column names with dummy values [None]
    to satisfy pytest's fixture resolution.

    Later, in pytest_runtest_call, our wrapper function will filter out these
    dummy values and only pass real fixture values to the evaluation.

    Args:
        metafunc: Pytest's Metafunc object that provides access to the test function
                  and allows parametrization of its arguments.

    Note:
        This hook is called for every test function during collection phase.
        Only doteval functions (those with _column_names attribute) are processed.
    """
    if hasattr(metafunc.function, "_column_names"):
        column_names = metafunc.function._column_names

        # Only parametrize dataset columns that pytest thinks are fixtures
        for column in column_names:
            if column in metafunc.fixturenames:
                metafunc.parametrize(column, [None])


@pytest.hookimpl
def pytest_runtest_call(item: Item) -> None:
    """Skip doteval functions and capture fixture state for deferred execution.

    All doteval functions are executed at session end using the appropriate runner.
    This hook just captures fixture state that will be needed later.

    Args:
        item: Pytest test item to be executed. For doteval functions, this contains
              the evaluation function and its associated metadata.

    Note:
        This is called for every test item during the execution phase.
        For doteval functions, we skip execution and only capture fixture values.
        For regular test functions, pytest continues with normal execution.
    """
    if item.get_closest_marker("doteval"):
        config = item.session.config
        config._doteval_items.append(item)
        # Capture fixture values for later use.
        item._doteval_fixture_kwargs = _extract_fixture_kwargs(item)

        return None


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(
    session: Session, exitstatus: Union[int, pytest.ExitCode]
) -> None:
    """Run all collected doteval items using appropriate runners.

    This handles both sequential and concurrent execution:
    - Sequential items are run one by one with SequentialRunner
    - Concurrent-eligible items are run together with ConcurrentRunner (if concurrent mode enabled)

    Args:
        session: Pytest session object containing information about the test run.
        exitstatus: Exit status of the test session (0 for success, non-zero for failures).

    Note:
        The trylast=True ensures this runs after all other session finish hooks.
        This is where all doteval functions are actually executed using captured fixtures.
    """
    from doteval.runners import ConcurrentRunner, SequentialRunner

    config = session.config

    # Exit early if no doteval items were selected for execution
    # (e.g., when running -m "not doteval")
    if not getattr(config, "_doteval_items", []):
        return

    # Separate items by execution strategy
    sequential_items = []
    concurrent_items = []

    for item in config._doteval_items:
        if config._doteval_concurrent and _is_async_evaluation(item):
            concurrent_items.append(item)
        else:
            sequential_items.append(item)

    # Run sequential items
    if sequential_items:
        sequential_runner = SequentialRunner(config)
        sequential_runner.run_evaluations(sequential_items)

    # Run concurrent items together
    if concurrent_items:
        runner = ConcurrentRunner(config)
        asyncio.run(runner.run_evaluations(concurrent_items))


def _is_async_evaluation(item: Item) -> bool:
    """Check if an evaluation item is async and can be run concurrently."""
    eval_fn = item.function
    original_func = getattr(eval_fn, "__wrapped__", eval_fn)
    return asyncio.iscoroutinefunction(original_func)


def _extract_fixture_kwargs(item: Item) -> Dict[str, Any]:
    """Extract fixture kwargs from a pytest item.

    This function inspects the evaluation function signature to identify
    which parameters are fixtures (vs dataset columns) and extracts their
    values from the pytest item.

    Args:
        item: Pytest test item containing the evaluation function and fixture values.

    Returns:
        dict: Dictionary mapping fixture parameter names to their resolved values.
              Only includes parameters that are actual fixtures (not dataset columns).

    Examples:
        For a function `def eval_math(question, answer, model_client)` where
        'question' and 'answer' are dataset columns and 'model_client' is a fixture:

        ```python
        # Returns: {'model_client': <fixture_value>}
        ```
    """
    eval_fn = item.function
    original_func = getattr(eval_fn, "__wrapped__", eval_fn)

    # Get expected parameters
    sig = inspect.signature(original_func)
    expected_params = set(sig.parameters.keys())
    column_names = eval_fn._column_names
    columns = set(column_names)
    expected_fixture_params = expected_params - columns

    fixture_kwargs = {}
    if hasattr(item, "funcargs") and item.funcargs:
        for param_name in expected_fixture_params:
            if param_name in item.funcargs:
                fixture_kwargs[param_name] = item.funcargs[param_name]

    return fixture_kwargs
