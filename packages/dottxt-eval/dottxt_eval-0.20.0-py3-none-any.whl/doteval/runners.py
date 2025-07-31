"""Execution runners for doteval evaluations."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Coroutine, Dict, List, Union

from pytest import Config, Item


class BaseRunner(ABC):
    """Base class for all evaluation runners."""

    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    def run_evaluations(
        self, evaluation_items: List[Item]
    ) -> Union[None, Coroutine[Any, Any, None]]:
        """Run all the evaluation items."""

    @abstractmethod
    def run_single_evaluation(
        self, item: Item
    ) -> Union[None, Coroutine[Any, Any, None]]:
        """Run a single evaluation item"""

    def _get_evaluation_params(self, item: Item) -> Dict[str, Any]:
        """Extract common evaluation parameters from item and config."""
        # Use captured fixture kwargs from pytest_runtest_call
        fixture_kwargs = getattr(item, "_doteval_fixture_kwargs", {})

        return {
            "evaluation_name": item.name,
            "experiment_name": self.config.getoption("--experiment"),
            "samples": self.config.getoption("--samples"),
            "fixture_kwargs": fixture_kwargs,
        }


class SequentialRunner(BaseRunner):
    """Handles sequential execution of both sync and async evaluations."""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        from doteval.progress import MultiProgress

        self.progress_manager = MultiProgress()

    def run_evaluations(self, evaluation_items: List[Any]) -> None:
        """Run multiple evaluations sequentially."""
        if not evaluation_items:
            return

        # Start progress display
        self.progress_manager.start(len(evaluation_items))

        try:
            for item in evaluation_items:
                self.run_single_evaluation(item)
        finally:
            self.progress_manager.finish()

    def run_single_evaluation(self, item: Any) -> None:
        """Execute a single evaluation item sequentially."""
        eval_fn = item.function
        params = self._get_evaluation_params(item)

        result = eval_fn(
            evaluation_name=params["evaluation_name"],
            experiment_name=params["experiment_name"],
            samples=params["samples"],
            progress_manager=self.progress_manager,
            **params["fixture_kwargs"],
        )

        if asyncio.iscoroutine(result):
            result = asyncio.run(result)

        self.config._evaluation_results[params["evaluation_name"]] = result


class ConcurrentRunner(BaseRunner):
    """Handles concurrent execution of async evaluations without global state."""

    def __init__(self, config: Config) -> None:
        super().__init__(config)
        from doteval.progress import MultiProgress

        self.progress_manager = MultiProgress()

    async def run_evaluations(self, evaluation_items: List[Any]) -> None:
        """Run multiple async evaluations concurrently."""
        if not evaluation_items:
            return

        # Keep all parametrized variations as separate evaluations
        evaluations = [(item.name, item) for item in evaluation_items]

        # Create tasks for concurrent execution
        tasks = []
        for eval_name, item in evaluations:
            coro = self.run_single_evaluation(item)
            tasks.append(coro)

        # Start progress display
        self.progress_manager.start(len(tasks))

        try:
            await asyncio.gather(*tasks)
        finally:
            self.progress_manager.finish()

    async def run_single_evaluation(self, item: Any) -> None:
        """Execute a single evaluation item asynchronously with common logic."""
        eval_fn = item.function
        params = self._get_evaluation_params(item)

        result = await eval_fn(
            evaluation_name=params["evaluation_name"],
            experiment_name=params["experiment_name"],
            samples=params["samples"],
            progress_manager=self.progress_manager,
            **params["fixture_kwargs"],
        )

        self.config._evaluation_results[params["evaluation_name"]] = result
