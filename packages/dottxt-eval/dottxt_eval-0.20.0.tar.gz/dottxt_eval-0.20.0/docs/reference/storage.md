# Storage Backends

Storage backends in doteval handle the persistence of evaluation sessions, results, and metadata. They provide a consistent interface for saving and loading evaluation data while supporting different storage mechanisms.

## Overview

Storage backends implement the `Storage` abstract base class and provide session persistence. The storage system is extensible, allowing you to implement custom backends for your specific needs.

## Built-in Storage Backends

### JSON Storage (Default)

The JSON storage backend stores each session as a separate JSON file in a directory.

#### `class JSONStorage(Storage)`

File-based JSON storage backend that stores each evaluation as a separate JSONL file.

**Constructor:**
```python
JSONStorage(storage_path: str)
```

**Parameters:**
- `storage_path` (`str`): Directory path where evaluation files will be stored
  - Directory will be created if it doesn't exist
  - Can be relative or absolute path
  - Each experiment becomes a subdirectory
  - Each evaluation becomes a `.jsonl` file within the experiment directory

**Usage:**
```python
from doteval.storage import JSONStorage

# Create JSON storage in default location
storage = JSONStorage("evals")

# Custom path
storage = JSONStorage("/path/to/my/evaluations")

# Relative path
storage = JSONStorage("../shared_evaluations")
```

**Directory Structure:**
```
evals/
├── gsm8k_baseline.json      # Session data
├── gsm8k_baseline.lock      # Lock file (if running)
├── sentiment_eval.json
└── math_reasoning.json
```

**Features:**

- Human-readable JSON format
- File-based locking
- Automatic directory creation
- Cross-platform compatibility

**Usage via URL:**
```bash
# Default JSON storage
doteval list --storage "json://evals"

# Custom path
doteval list --storage "json:///absolute/path/to/storage"

# Relative path
doteval list --storage "json://relative/path"
```

### SQLite Storage

The SQLite storage backend stores evaluation data in a relational database, enabling powerful querying capabilities.

#### `class SQLiteStorage(Storage)`

Relational database storage backend using SQLite for efficient querying and analysis.

**Constructor:**
```python
SQLiteStorage(db_path: str)
```

**Parameters:**
- `db_path` (`str`): Path to SQLite database file
  - File will be created if it doesn't exist
  - Can be relative or absolute path
  - Database schema is initialized automatically
  - Supports concurrent reads, serialized writes

**Usage:**
```python
from doteval.storage import SQLiteStorage

# Create SQLite storage
storage = SQLiteStorage("evaluations.db")

# Custom path
storage = SQLiteStorage("/path/to/my/database.db")

# Memory database (for testing)
storage = SQLiteStorage(":memory:")
```

**Features:**

- Efficient storage for large datasets
- Query capabilities for error analysis
- ACID transactions
- Built-in support for finding failed evaluations

**Additional Query Methods:**

**`get_failed_results(experiment_name: str, evaluation_name: Optional[str] = None, evaluator_name: Optional[str] = None) -> list[dict]`**

Query helper to find all failed results (score = False or 0) for analysis.

- `experiment_name` (`str`): Name of the experiment to query
- `evaluation_name` (`Optional[str]`): Filter by specific evaluation name
- `evaluator_name` (`Optional[str]`): Filter by specific evaluator name
- **Returns:** `list[dict]` - List of failed result records with metadata

**`get_error_results(experiment_name: str, evaluation_name: Optional[str] = None) -> list[dict]`**

Query helper to find all results that encountered errors during evaluation.

- `experiment_name` (`str`): Name of the experiment to query
- `evaluation_name` (`Optional[str]`): Filter by specific evaluation name
- **Returns:** `list[dict]` - List of error result records with exception details

**Usage:**
```python
# Find all failed evaluations
failed_results = storage.get_failed_results("math_experiment")

# Find errors in specific evaluation
error_results = storage.get_error_results("math_experiment", "addition_test")

# Find failures for specific evaluator
failed_exact_match = storage.get_failed_results(
    "math_experiment", evaluator_name="exact_match"
)
```

**Usage via URL:**
```bash
# SQLite storage
doteval list --storage "sqlite://evaluations.db"

# Custom path
doteval list --storage "sqlite:///absolute/path/to/database.db"
```

## Custom Storage Backends

You can implement your own storage backend by inheriting from the `Storage` abstract base class and registering it.

## Storage API Reference

### Core Functions

#### `get_storage(storage_path: Optional[str] = None) -> Storage`

Factory function to create storage instances from URL paths.

**Parameters:**
- `storage_path` (`Optional[str]`): Storage URL in format `backend://path`. Defaults to `"json://.doteval"` if `None`.
  - Format: `"backend://path"` (e.g., `"json://evals"`, `"sqlite://db.sqlite"`)
  - For backward compatibility, paths without `://` default to JSON backend

**Returns:**
- `Storage`: Storage instance of the appropriate backend type

**Raises:**
- `ValueError`: If the backend is not registered

**Examples:**
```python
from doteval.storage import get_storage

# Default storage
storage = get_storage()  # Uses json://.doteval

# JSON storage
storage = get_storage("json://my_evals")

# SQLite storage
storage = get_storage("sqlite://evaluations.db")

# Legacy format (defaults to JSON)
storage = get_storage("my_evals")  # Same as json://my_evals
```

#### `register(name: str, storage_class: Type[Storage]) -> None`

Register a custom storage backend in the global registry.

**Parameters:**
- `name` (`str`): Unique name for the backend (e.g., `"redis"`, `"s3"`)
- `storage_class` (`Type[Storage]`): Class implementing the `Storage` interface

**Examples:**
```python
from doteval.storage import Storage, register

class RedisStorage(Storage):
    def __init__(self, redis_url: str):
        # Implementation...
        pass
    # ... implement all Storage methods

# Register the backend
register("redis", RedisStorage)

# Now usable via get_storage
storage = get_storage("redis://localhost:6379")
```

#### `list_backends() -> list[str]`

List all registered storage backend names.

**Returns:**
- `list[str]`: List of backend names (e.g., `["json", "sqlite"]`)

**Examples:**
```python
from doteval.storage import list_backends

available = list_backends()
print(f"Available backends: {available}")
# Output: Available backends: ['json', 'sqlite']
```

### Storage Abstract Base Class

#### `class Storage(ABC)`

Abstract base class defining the storage interface. All storage backends must implement these methods.

##### Experiment Management

**`create_experiment(experiment_name: str) -> None`**

Create a new experiment. Idempotent - does nothing if experiment already exists.

- `experiment_name` (`str`): Unique name for the experiment

**`delete_experiment(experiment_name: str) -> None`**

Delete an experiment and all its associated data.

- `experiment_name` (`str`): Name of experiment to delete
- **Raises:** `ValueError` if experiment not found

**`rename_experiment(old_name: str, new_name: str) -> None`**

Rename an existing experiment.

- `old_name` (`str`): Current experiment name
- `new_name` (`str`): New experiment name
- **Raises:** `ValueError` if old experiment not found or new name already exists

**`list_experiments() -> list[str]`**

List all experiment names, typically ordered by creation time (newest first).

- **Returns:** `list[str]` - List of experiment names

##### Evaluation Management

**`create_evaluation(experiment_name: str, evaluation: Evaluation) -> None`**

Create a new evaluation within an experiment.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation` (`Evaluation`): Evaluation object with metadata and configuration

**`load_evaluation(experiment_name: str, evaluation_name: str) -> Optional[Evaluation]`**

Load an evaluation's metadata and configuration.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation to load
- **Returns:** `Optional[Evaluation]` - Evaluation object or `None` if not found

**`update_evaluation_status(experiment_name: str, evaluation_name: str, status: EvaluationStatus) -> None`**

Update the status of an evaluation (running, completed, failed, etc.).

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation to update
- `status` (`EvaluationStatus`): New status for the evaluation

**`list_evaluations(experiment_name: str) -> list[str]`**

List all evaluation names within an experiment.

- `experiment_name` (`str`): Name of the parent experiment
- **Returns:** `list[str]` - List of evaluation names

##### Results Management

**`add_results(experiment_name: str, evaluation_name: str, results: list[Record]) -> None`**

Add evaluation results to storage.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation
- `results` (`list[Record]`): List of evaluation records to store

**`get_results(experiment_name: str, evaluation_name: str) -> list[Record]`**

Retrieve all results for an evaluation.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation
- **Returns:** `list[Record]` - List of all evaluation records

**`completed_items(experiment_name: str, evaluation_name: str) -> list[int]`**

Get list of successfully completed item IDs for resumption logic.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation
- **Returns:** `list[int]` - List of completed item IDs (excluding errored items)

##### Error Recovery

**`remove_error_result(experiment_name: str, evaluation_name: str, item_id: int) -> None`**

Remove an errored result for a specific item that will be retried.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation
- `item_id` (`int`): ID of the item whose error result should be removed

**`remove_error_results_batch(experiment_name: str, evaluation_name: str, item_ids: list[int]) -> None`**

Remove multiple errored results efficiently. Default implementation calls `remove_error_result` for each item, but backends should override for better performance.

- `experiment_name` (`str`): Name of the parent experiment
- `evaluation_name` (`str`): Name of the evaluation
- `item_ids` (`list[int]`): List of item IDs whose error results should be removed

### Implementing a Custom Backend

Implement the `Storage` abstract base class and register your backend:

```python
from doteval.storage import Storage, register

class MyCustomStorage(Storage):
    def __init__(self, connection_string: str):
        # Initialize your storage connection
        pass

    # Implement all required methods from Storage ABC
    def create_experiment(self, experiment_name: str):
        pass

    def list_experiments(self) -> list[str]:
        pass

    # ... implement remaining Storage methods

# Register the backend
register("mycustom", MyCustomStorage)
```

### Using Your Custom Backend

```python
from my_storage import MyCustomStorage  # Triggers registration
from doteval.sessions import SessionManager

manager = SessionManager(storage="mycustom://connection_string")
```

```bash
pytest eval_test.py --experiment my_eval --storage mycustom://config
```

## Error Handling

Common error scenarios:

```bash
# Unknown backend
$ doteval list --storage "unknown://localhost"
Error: Unknown storage backend: unknown

# Permission issues
$ doteval list --storage "json:///restricted/path"
Error: Permission denied
```

List available backends:
```python
from doteval.storage import list_backends
print(list_backends())  # ['json', 'sqlite']
```

## See Also

### Core Concepts
- **[Experiments](experiments.md)** - Understand how experiments use storage backends for data persistence
- **[CLI Reference](cli.md)** - Learn command-line options for configuring storage backends

### Integration Guides
- **[@foreach Decorator](foreach.md)** - See how `@foreach` evaluations automatically use configured storage
- **[Pytest Integration](pytest.md)** - Configure storage for pytest-based evaluation runs

### Advanced Usage
- **[Evaluators](evaluators.md)** - Understand how evaluator results are persisted across storage systems
- **[Metrics](metrics.md)** - See how metric computations are stored and retrieved
- **[Async Evaluations](async.md)** - Handle storage with concurrent async evaluation workloads

### Tutorials
- **[Build a Production Evaluation Pipeline](../tutorials/09-build-production-evaluation-pipeline.md)** - Choose and configure storage backends for production systems
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Organize storage for multi-model evaluation experiments
