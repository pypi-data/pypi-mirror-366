import time
import uuid
from datetime import datetime
from typing import Optional, Union

from doteval.models import Evaluation, EvaluationStatus, Record
from doteval.storage import Storage, get_storage


class EvaluationProgress:
    """Runtime progress tracking for an evaluation.

    Used for progress bars.

    """

    def __init__(self, evaluation_name: str):
        self.evaluation_name = evaluation_name
        self.completed_count = 0
        self.error_count = 0
        self.start_time = time.time()


class SessionManager:
    """Manages experiment lifecycle and storage"""

    def __init__(
        self,
        storage: Optional[Union[Storage, str]] = None,
        experiment_name: Optional[str] = None,
    ):
        # Handle storage parameter - can be Storage instance or path string
        if isinstance(storage, Storage):
            self.storage = storage
        else:
            self.storage = get_storage(storage)

        self.evaluation_progress: EvaluationProgress | None = None
        self.active_evaluations: set[str] = set()

        # If no experiment name provided, create ephemeral one with timestamp
        if experiment_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            short_uuid = str(uuid.uuid4())[:8]
            experiment_name = f"{timestamp}_{short_uuid}"

        self.current_experiment: str = experiment_name
        self.storage.create_experiment(experiment_name)

    def start_evaluation(self, evaluation_name: str) -> None:
        """Start or resume an evaluation within the current experiment.

        This method either creates a new evaluation or resumes an existing one.
        If resuming, it reports the number of already completed samples and
        continues from where it left off.

        Args:
            evaluation_name: Unique name for the evaluation within the experiment.
                           Used for storage, progress tracking, and result retrieval.

        Side Effects:
            - Creates new evaluation in storage if it doesn't exist
            - Adds Git commit hash to metadata for reproducibility tracking
            - Initializes progress tracking for the evaluation
            - Prints resume message if continuing existing evaluation
        """
        evaluation = self.storage.load_evaluation(
            self.current_experiment, evaluation_name
        )

        if evaluation:
            completed_items = self.storage.completed_items(
                self.current_experiment, evaluation_name
            )
            print(
                f"{evaluation_name}: Resuming from {len(completed_items)} completed samples"
            )
        else:
            git_commit = get_git_commit()
            metadata = {"git_commit": git_commit} if git_commit else {}
            evaluation = Evaluation(
                evaluation_name=evaluation_name,
                status=EvaluationStatus.RUNNING,
                started_at=time.time(),
                metadata=metadata,
            )
            self.storage.create_evaluation(self.current_experiment, evaluation)

        self.evaluation_progress = EvaluationProgress(evaluation_name)
        self.active_evaluations.add(evaluation_name)

    def add_results(self, evaluation_name: str, results: list[Record]) -> None:
        """Add evaluation results to storage and update progress tracking.

        Args:
            evaluation_name: Name of the evaluation to add results to
            results: List of Record objects containing evaluation results
        """
        self.storage.add_results(self.current_experiment, evaluation_name, results)

        if self.evaluation_progress:
            for result in results:
                self.evaluation_progress.completed_count += 1
                if result.error is not None:
                    self.evaluation_progress.error_count += 1

    def get_results(self, evaluation_name: str) -> list[Record]:
        """Retrieve all results for a specific evaluation.

        Args:
            evaluation_name: Name of the evaluation to get results for

        Returns:
            List of Record objects containing all results for the evaluation
        """
        return self.storage.get_results(self.current_experiment, evaluation_name)

    def finish_evaluation(self, evaluation_name: str, success: bool = True) -> None:
        """Mark an evaluation as completed or failed in storage.

        Args:
            evaluation_name: Name of the evaluation to finish
            success: Whether the evaluation completed successfully (True) or failed (False)
        """
        status = EvaluationStatus.COMPLETED if success else EvaluationStatus.FAILED
        self.storage.update_evaluation_status(
            self.current_experiment, evaluation_name, status
        )

    def finish_all(self, success: bool = True) -> None:
        """Finish all active evaluations with the specified status.

        This is a convenience method to mark all currently active evaluations
        as either completed or failed in bulk.

        Args:
            success: Whether all evaluations completed successfully (True) or failed (False)
        """
        for evaluation_name in self.active_evaluations:
            self.finish_evaluation(evaluation_name, success)


def get_git_commit() -> Optional[str]:
    """Get the short Git commit hash of the current repository.

    This function attempts to retrieve the current Git commit hash using
    the git command line tool. It returns the first 8 characters of the
    commit hash for brevity, which is typically sufficient for identification.

    Returns:
        Optional[str]: The first 8 characters of the current Git commit hash,
                      or None if Git is not available or not in a Git repository.

    Examples:
        ```python
        >>> get_git_commit()
        'a1b2c3d4'  # If in a Git repository

        >>> get_git_commit()
        None  # If not in a Git repository or Git not available
        ```

    Note:
        This function is used to track which version of the code was used
        for evaluations, enabling reproducibility and debugging.
    """
    try:
        import subprocess

        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()[:8]
        )
    except subprocess.CalledProcessError:
        return None
