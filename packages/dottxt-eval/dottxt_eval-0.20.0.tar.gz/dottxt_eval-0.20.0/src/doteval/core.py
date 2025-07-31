import asyncio
import functools
import itertools
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    TypedDict,
    Union,
)

import pytest
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from doteval.concurrency import (
    Adaptive,
    AsyncConcurrencyStrategy,
    Sequential,
    SyncConcurrencyStrategy,
)
from doteval.datasets import _registry
from doteval.models import EvaluationSummary, Record, Result
from doteval.progress import BaseProgressManager, SingleProgress, get_dataset_info
from doteval.sessions import SessionManager
from doteval.storage import Storage

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # Initial delay in seconds
DEFAULT_MAX_DELAY = 30.0  # Maximum delay between retries


class DatasetInfo(TypedDict, total=False):
    """Type for dataset information dictionary."""

    name: str
    total_rows: Optional[int]


CONNECTION_ERRORS = (
    ConnectionError,
    ConnectionResetError,
    ConnectionAbortedError,
    ConnectionRefusedError,
    TimeoutError,
    OSError,
)


class ForEach:
    def __init__(
        self,
        retries: Optional[AsyncRetrying] = None,
        concurrency: Optional[object] = None,
        storage: Optional[Storage] = None,
    ):
        """Initialize ForEach decorator with optional configuration.

        Args:
            name: Optional name for the evaluation
            retries: Optional AsyncRetrying instance for retry configuration
            concurrency: Optional concurrency strategy
            storage: Optional storage backend
        """
        self.retries = retries
        self.concurrency = concurrency
        self.storage = storage

    def __call__(self, column_spec: str, dataset: Iterable) -> Callable:
        def core_foreach(column_spec: str, dataset: Iterable) -> Callable:
            """
            Decorator that marks a function for running against each item in a dataset.

            When used with `pytest`, the decorated function will be automatically
            executed against all dataset items as part of the evaluation suite.
            Functions decorated by `foreach` can also be executed as normal Python
            functions.

            The decorated function inherits retry, concurrency, and storage configuration
            from the ForEach instance that created it.

            Args:
                column_spec: Comma-separated list of column names
                dataset: An iterator of tuples or lists, each representing a row of data

            Returns:
                A decorated function that can be used as a regular function or as a `pytest` test

            """

            def decorator(eval_fn: Callable) -> Callable:
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(
                        evaluation_name,
                        experiment_name,
                        samples,
                        progress_manager=None,
                        **kwargs,
                    ):
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset,
                            evaluation_name,
                            experiment_name,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            storage=self.storage,
                            progress_manager=progress_manager,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    async_wrapper._column_names = [col.strip() for col in column_spec.split(",")]  # type: ignore

                    return pytest.mark.doteval(async_wrapper)
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def sync_wrapper(
                        evaluation_name,
                        experiment_name,
                        samples,
                        progress_manager=None,
                        **kwargs,
                    ):
                        return asyncio.run(
                            run_evaluation(
                                eval_fn,
                                column_spec,
                                dataset,
                                evaluation_name,
                                experiment_name,
                                samples,
                                retries=self.retries,
                                concurrency=self.concurrency,
                                storage=self.storage,
                                progress_manager=progress_manager,
                                **kwargs,
                            )
                        )

                    # Store parsed column names for plugin
                    sync_wrapper._column_names = [col.strip() for col in column_spec.split(",")]  # type: ignore

                    return pytest.mark.doteval(sync_wrapper)

            return decorator

        return core_foreach(column_spec, dataset)

    def __getattr__(self, dataset_name: str) -> Callable:
        def dataset_foreach(split: Optional[str] = None, **kwargs) -> Callable:
            dataset_class = _registry.get_dataset_class(dataset_name)
            dataset_instance = (
                dataset_class(split, **kwargs)
                if split is not None
                else dataset_class(**kwargs)
            )
            column_spec = ",".join(dataset_class.columns)

            def decorator(eval_fn: Callable):
                if asyncio.iscoroutinefunction(eval_fn):
                    # Create async wrapper for async eval functions
                    @functools.wraps(eval_fn)
                    async def async_wrapper(
                        evaluation_name, experiment_name, samples, **kwargs
                    ):
                        return await run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            evaluation_name,
                            experiment_name,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            storage=self.storage,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    async_wrapper._column_names = [col.strip() for col in column_spec.split(",")]  # type: ignore

                    return pytest.mark.doteval(async_wrapper)
                else:
                    # Create sync wrapper for sync eval functions
                    @functools.wraps(eval_fn)
                    def sync_wrapper(
                        evaluation_name, experiment_name, samples, **kwargs
                    ):
                        return run_evaluation(
                            eval_fn,
                            column_spec,
                            dataset_instance,
                            evaluation_name,
                            experiment_name,
                            samples,
                            retries=self.retries,
                            concurrency=self.concurrency,
                            storage=self.storage,
                            **kwargs,
                        )

                    # Store parsed column names for plugin
                    sync_wrapper._column_names = [col.strip() for col in column_spec.split(",")]  # type: ignore

                    return pytest.mark.doteval(sync_wrapper)

            decorator._dataset_name = dataset_name  # type: ignore
            decorator._split = split  # type: ignore
            return decorator

        return dataset_foreach


# Create default instance for usability
foreach = ForEach()


async def run_evaluation(
    eval_fn: Callable,
    column_spec: str,
    dataset: Iterable,
    evaluation_name: str,
    experiment_name: Optional[str] = None,
    samples: Optional[int] = None,
    retries: Optional[AsyncRetrying] = None,
    concurrency: Optional[
        Union[SyncConcurrencyStrategy, AsyncConcurrencyStrategy]
    ] = None,
    storage: Optional[Storage] = None,
    progress_manager: Optional[BaseProgressManager] = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run an evaluation function against each item in a dataset.

    Args:
        eval_fn: The function to run for each dataset item
        column_spec: Comma-separated list of column names
        dataset: An iterator of tuples or lists, each representing a row of data
        experiment_name: Optional experiment name (used when creating SessionManager)
        evaluation_name: The name of the evaluation being run
        samples: Maximum number of dataset samples to evaluate (None for all)
        retries: Retry strategy (AsyncRetrying for async, Retrying for sync)
        concurrency: Concurrency strategy (AsyncConcurrencyStrategy or SyncConcurrencyStrategy)
        storage: Storage backend for results
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    session_manager = SessionManager(storage=storage, experiment_name=experiment_name)
    session_manager.start_evaluation(evaluation_name)

    columns = [col.strip() for col in column_spec.split(",")]

    dataset_info = get_dataset_info(dataset)

    completed_items = session_manager.storage.completed_items(
        session_manager.current_experiment, evaluation_name
    )
    completed_ids = set(completed_items)

    all_results = session_manager.storage.get_results(
        session_manager.current_experiment, evaluation_name
    )
    all_item_ids = {r.item_id for r in all_results}
    items_to_retry = all_item_ids - completed_ids

    # Batch remove from storage all the items that errored out in the
    # previous run since we're going to re-try them.
    if items_to_retry:
        session_manager.storage.remove_error_results_batch(
            session_manager.current_experiment,
            evaluation_name,
            list(items_to_retry),
        )

    # Filter the dataset to only keep items that were not completed
    dataset = (
        (item_id, row_data)
        for item_id, row_data in enumerate(dataset)
        if item_id not in completed_ids
    )

    # Limit the dataset to `num_samples` items
    dataset = itertools.islice(dataset, None, samples)

    try:
        if asyncio.iscoroutinefunction(eval_fn):
            # For async functions, pass only AsyncConcurrencyStrategy
            async_concurrency = (
                concurrency
                if concurrency is None or hasattr(concurrency, "execute")
                else None
            )
            result = await _run_evaluation_async(
                evaluation_name,
                eval_fn,
                columns,
                dataset,
                async_concurrency,  # type: ignore
                retries,
                session_manager,
                samples,
                dataset_info,
                storage,
                progress_manager=progress_manager,
                **kwargs,
            )
        else:
            # For sync functions, pass only SyncConcurrencyStrategy
            sync_concurrency = (
                concurrency
                if concurrency is None or hasattr(concurrency, "execute")
                else None
            )
            result = _run_evaluation_sync(
                evaluation_name,
                eval_fn,
                columns,
                dataset,
                sync_concurrency,  # type: ignore
                retries,
                session_manager,
                samples,
                dataset_info,
                storage,
                progress_manager=progress_manager,
                **kwargs,
            )

        session_manager.finish_evaluation(evaluation_name, success=True)

        return result
    except Exception:
        session_manager.finish_evaluation(evaluation_name, success=False)
        raise


def _run_evaluation_sync(
    evaluation_name: str,
    eval_fn: Callable,
    columns: List[str],
    dataset: Iterable,
    concurrency: Optional[SyncConcurrencyStrategy],
    retries: Optional[Retrying],
    session_manager: "SessionManager",
    samples: Optional[int],
    dataset_info: DatasetInfo,
    storage: Optional["Storage"],
    progress_manager: Optional[BaseProgressManager] = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run the evaluation when `eval_fn` is a Python function, against
    each item in the dataset.

    Args:
        evaluation_name: The name of the evaluation currently being run
        eval_fn: The function to run for each dataset item
        columns: List of column names that map to dataset fields
        dataset: An iterator of tuples or lists, each representing a row of data
        concurrency: Concurrency strategy for sync execution (defaults to Sequential())
        retries: Retry strategy for handling failures (defaults to Retrying with 3 attempts)
        samples: Maximum number of samples to evaluate
        dataset_info: Optional dataset information (name, split, size)
        session_manager: The current session's session manager
        storage: Storage backend for results (defaults to JSONStorage)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if concurrency is None:
        concurrency = Sequential()

    if retries is None:
        retries = Retrying(
            retry=retry_if_exception_type(CONNECTION_ERRORS),
            stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_DELAY, max=DEFAULT_MAX_DELAY
            ),
            reraise=True,
        )

    # When the library is used programmatically we automatically instantiate the
    # `SingleProgress` otherwise we use the one provided by the pytest runner.
    if progress_manager is None:
        progress_manager = SingleProgress()

    def create_tasks() -> Generator[Callable[[], Record], None, None]:
        """Create an iterator over evaluation tasks."""
        for item_id, row_data in dataset:
            row_dict = _format_data(row_data, columns)

            def task(
                item_id: int = item_id, row_dict: Dict[str, Any] = row_dict
            ) -> Record:
                try:
                    wrapped_fn = retries.wraps(eval_fn) if retries else eval_fn
                    result = wrapped_fn(**row_dict, **kwargs)

                    if not isinstance(result, Result):
                        raise ValueError(
                            "Evaluation functions must return a Result object"
                        )

                    # If the Result contains an error we propagate it to Record.
                    #
                    # A result can contain an error when it is specified by the
                    # user. For instance if we expect a result to be valid JSON,
                    # we would parse it between try/except and return a `Record`
                    # with the error in case the parsing fails.
                    if result.error is not None:
                        return Record(result, item_id, row_dict, result.error)
                    else:
                        return Record(result, item_id, row_dict)
                except Exception as e:
                    error_result = Result(prompt="")
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    return Record(error_result, item_id, row_dict, error_msg)

            yield task

    # Run the evaluation.
    #
    # When the library is used programmatically we automatically instantiate the
    # `ProgressManager` otherwise we use the one provided by the pytest runner.
    with progress_manager:
        dataset_size = dataset_info.get("total_rows")
        progress_manager.start_evaluation(evaluation_name, dataset_size)
        progress_callback = lambda result: progress_manager.update_evaluation_progress(
            evaluation_name, result=result
        )

        for result in concurrency.execute(create_tasks(), progress_callback):
            session_manager.add_results(evaluation_name, [result])

    results = session_manager.get_results(evaluation_name)

    return EvaluationSummary(results)


async def _run_evaluation_async(
    evaluation_name: str,
    eval_fn: Callable,
    columns: List[str],
    dataset: Iterable,
    concurrency: Optional[AsyncConcurrencyStrategy],
    retries: Optional[AsyncRetrying],
    session_manager: "SessionManager",
    samples: Optional[int],
    dataset_info: DatasetInfo,
    storage: Optional["Storage"],
    progress_manager: Optional[BaseProgressManager] = None,
    **kwargs: Any,
) -> EvaluationSummary:
    """
    Run the evaluation when `eval_fn` is a coroutine, against each item in the
    dataset.

    Args:
        evaluation_name: The name of the current evaluation
        eval_fn: The function to run for each dataset item
        columns: List of column names that map to dataset fields
        dataset: An iterator of tuples or lists, each representing a row of data
        concurrency: Concurrency strategy for async execution (defaults to SlidingWindowStrategy)
        retries: Retry strategy for handling failures (defaults to AsyncRetrying with connection error handling)
        samples: Maximum number of samples to evaluate
        dataset_info: Optional dataset information (name, split, size)
        session_manager: The current session's session manager
        samples: Maximum number of dataset samples to evaluate (None for all)
        storage: Storage backend for results (defaults to JSONStorage)
        **kwargs: Additional arguments to pass to the evaluation function

    Returns:
        An EvaluationSummary containing all results

    """
    if concurrency is None:
        concurrency = Adaptive()

    if retries is None:
        retries = AsyncRetrying(
            retry=retry_if_exception_type(CONNECTION_ERRORS),
            stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
            wait=wait_exponential_jitter(
                initial=DEFAULT_RETRY_DELAY, max=DEFAULT_MAX_DELAY
            ),
        )

    # When the library is used programmatically we automatically instantiate the
    # `SingleProgress` otherwise we use the one provided by the pytest runner.
    if progress_manager is None:
        progress_manager = SingleProgress()

    def create_tasks() -> Generator[Callable[[], Any], None, None]:
        """Create an async iterator of evaluation tasks."""
        for item_id, row_data in dataset:
            row_dict = _format_data(row_data, columns)

            async def task(
                item_id: int = item_id, row_dict: Dict[str, Any] = row_dict
            ) -> Record:
                try:
                    wrapped_fn = retries.wraps(eval_fn) if retries else eval_fn
                    result = await wrapped_fn(**row_dict, **kwargs)

                    if not isinstance(result, Result):
                        raise ValueError(
                            "Evaluation functions must return a Result object"
                        )

                    # If the Result contains an error we propagate it to Record.
                    #
                    # A result can contain an error when it is specified by the
                    # user. For instance if we expect a result to be valid JSON,
                    # we would parse it between try/except and return a `Record`
                    # with the error in case the parsing fails.
                    if result.error is not None:
                        return Record(result, item_id, row_dict, result.error)
                    else:
                        return Record(result, item_id, row_dict)
                except Exception as e:
                    # Create empty Result for error cases
                    empty_result = Result(prompt="")
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    return Record(empty_result, item_id, row_dict, error_msg)

            yield task

    # Run the evaluation
    with progress_manager:
        dataset_size = dataset_info.get("total_rows")
        progress_manager.start_evaluation(evaluation_name, dataset_size)
        progress_callback = lambda result: progress_manager.update_evaluation_progress(
            evaluation_name, result=result
        )

        async for result in concurrency.execute(create_tasks(), progress_callback):
            session_manager.add_results(evaluation_name, [result])

    results = session_manager.get_results(evaluation_name)

    return EvaluationSummary(results)


def _format_data(row_data: Union[Iterable, dict], columns: List[str]) -> Dict[str, Any]:
    """Handle different data formats for the datasets."""
    if len(columns) == 1 and not (
        isinstance(row_data, (tuple, list)) and len(row_data) == 1
    ):
        # Single column with non-tuple data: pass the data item directly
        # (handles dicts, objects, etc.)
        return {columns[0]: row_data}
    else:
        # Multiple columns OR single column with single-element tuple: use zip logic
        return {col: data for col, data in zip(columns, row_data)}
