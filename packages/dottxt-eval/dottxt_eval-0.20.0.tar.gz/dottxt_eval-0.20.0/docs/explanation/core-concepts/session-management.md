# Session Management

How doteval manages experiment lifecycle, storage, and resumability.

## Experiment-Centric Design

```python
# Experiments group related evaluations
SessionManager(experiment_name="model_comparison_v2")

# Multiple evaluations per experiment
start_evaluation("sentiment_analysis")
start_evaluation("named_entity_recognition")
start_evaluation("text_classification")
```

This design reflects real-world evaluation workflows where you want to compare multiple evaluation types within a single research iteration or model release.

## Resumable by Default

Every evaluation is automatically resumable:

```python
# First run - processes all 1000 samples
pytest eval_sentiment.py --experiment prod_eval

# Second run - skips 850 completed, retries 150 failed
pytest eval_sentiment.py --experiment prod_eval
```

Implementation details:

```python
# Session manager tracks completion per item
completed_items = storage.completed_items(experiment, evaluation)
completed_ids = set(completed_items)

# Filter dataset to skip completed items
dataset = (
    (item_id, row_data)
    for item_id, row_data in enumerate(dataset)
    if item_id not in completed_ids
)
```

This enables long-running evaluations to be interrupted and resumed without losing progress.

## Reproducibility Through Metadata

Sessions automatically capture context for reproducibility:

```python
class SessionManager:
    def start_evaluation(self, evaluation_name: str):
        git_commit = get_git_commit()
        metadata = {"git_commit": git_commit} if git_commit else {}

        evaluation = Evaluation(
            evaluation_name=evaluation_name,
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
            metadata=metadata
        )
```

This enables tracking exactly which code version produced which results.

## Storage Abstraction

Sessions work with pluggable storage backends:

```python
# JSON for development
SessionManager(storage="json://./evals")

# SQLite for production
SessionManager(storage="sqlite://./production.db")

# Custom implementations
SessionManager(storage=RedisStorage("redis://localhost"))
```

The storage abstraction enables different use cases without changing evaluation code.

## Lifecycle Management

### Session Creation

```python
# Automatic experiment naming if none provided
if experiment_name is None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    experiment_name = f"{timestamp}_{short_uuid}"

self.current_experiment = experiment_name
self.storage.create_experiment(experiment_name)
```

### Evaluation Tracking

```python
def start_evaluation(self, evaluation_name: str):
    # Check for existing evaluation
    evaluation = self.storage.load_evaluation(
        self.current_experiment, evaluation_name
    )

    if evaluation:
        # Resume existing evaluation
        completed_items = self.storage.completed_items(
            self.current_experiment, evaluation_name
        )
        print(f"Resuming from {len(completed_items)} completed samples")
    else:
        # Create new evaluation
        evaluation = Evaluation(
            evaluation_name=evaluation_name,
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
            metadata=get_metadata()
        )
        self.storage.create_evaluation(self.current_experiment, evaluation)
```

### Progress Tracking

```python
class EvaluationProgress:
    def __init__(self, evaluation_name: str):
        self.evaluation_name = evaluation_name
        self.completed_count = 0
        self.error_count = 0
        self.start_time = time.time()

def add_results(self, evaluation_name: str, results: list[Record]):
    self.storage.add_results(self.current_experiment, evaluation_name, results)

    # Update progress tracking
    if self.evaluation_progress:
        for result in results:
            self.evaluation_progress.completed_count += 1
            if result.error is not None:
                self.evaluation_progress.error_count += 1
```

### Completion Handling

```python
def finish_evaluation(self, evaluation_name: str, success: bool = True):
    status = EvaluationStatus.COMPLETED if success else EvaluationStatus.FAILED
    self.storage.update_evaluation_status(
        self.current_experiment, evaluation_name, status
    )
```

## Error Recovery

The session manager handles various failure scenarios:

### Partial Completion

```python
# Identify items that errored in previous runs
all_results = storage.get_results(experiment, evaluation)
all_item_ids = {r.item_id for r in all_results}
items_to_retry = all_item_ids - completed_ids

# Remove error results for retry
if items_to_retry:
    storage.remove_error_results_batch(
        experiment, evaluation, list(items_to_retry)
    )
```

### Graceful Degradation

```python
try:
    session_manager.finish_evaluation(evaluation_name, success=True)
    return result
except Exception:
    session_manager.finish_evaluation(evaluation_name, success=False)
    raise
```

## Design Philosophy

Session management balances **simplicity** with **enterprise requirements**:

**Simple Default Behavior**: Works out of the box with minimal configuration

**Explicit Control When Needed**: Full control over experiment naming, storage backends, and lifecycle

**Automatic Best Practices**: Git tracking, timestamps, and error handling built-in

**Production Ready**: Handles failures, supports resumption, enables monitoring

The result is a system that works seamlessly for quick experiments while providing the robustness needed for production evaluation pipelines.
