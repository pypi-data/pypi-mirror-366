# Registry Architecture

How doteval enables extensibility and discovery through registry patterns.

## Dataset Registry

The dataset registry enables attribute-based access to registered datasets:

```python
# Registration happens at import time
@dataclass
class ImdbDataset(Dataset):
    name = "imdb"
    columns = ["text", "label"]
    splits = ["train", "test"]

_registry.register(ImdbDataset)

# Usage through attribute access
@foreach.imdb(split="test")
def eval_sentiment(text, label):
    return Result(...)
```

### Implementation Details

```python
class ForEach:
    def __getattr__(self, dataset_name: str):
        # Dynamic attribute access triggers dataset lookup
        dataset_class = _registry.get_dataset_class(dataset_name)

        def dataset_foreach(split=None, **kwargs):
            # Create dataset instance with parameters
            dataset_instance = dataset_class(split, **kwargs)
            column_spec = ",".join(dataset_class.columns)

            # Return configured decorator
            return self(column_spec, dataset_instance)

        return dataset_foreach
```

### Benefits

**Discoverability**: `foreach.` + tab completion shows available datasets

**Type Safety**: Registered datasets must implement the Dataset interface

**Flexibility**: Registration enables plugin architectures and custom datasets

## Registry Pattern Philosophy

Registries in doteval follow consistent principles:

### Dynamic Discovery with Type Safety

```python
class DatasetRegistry:
    def register(self, dataset_class: Type[Dataset]):
        name = dataset_class.name
        if name in self._dataset_classes:
            if self._dataset_classes[name] is dataset_class:
                return  # Idempotent re-registration
            raise ValueError(f"Dataset {name} already registered")
        self._dataset_classes[name] = dataset_class

    def get_dataset_class(self, name: str) -> Type[Dataset]:
        if name not in self._dataset_classes:
            raise ValueError(
                f"Dataset '{name}' not found. "
                f"Available datasets: {self.list_datasets()}"
            )
        return self._dataset_classes[name]
```

### Convention-Based Configuration

```python
# Datasets define their own metadata
class CustomDataset(Dataset):
    name = "custom"           # Registry key
    columns = ["input", "output"]  # Column mapping
    splits = ["train", "test"]     # Available splits

    def __init__(self, split: str, **kwargs):
        # Implementation details...
```

## Concurrency Strategy Registry

While not explicitly a registry pattern, concurrency strategies follow similar principles:

```python
# Strategies are classes that implement common interfaces
class SlidingWindow(AsyncConcurrencyStrategy):
    def execute(self, tasks, callback):
        # Implementation details...

class Adaptive(AsyncConcurrencyStrategy):
    def execute(self, tasks, callback):
        # Different implementation...

# Usage through configuration
foreach_concurrent = ForEach(
    concurrency=SlidingWindow(max_concurrency=10)
)
```

This enables pluggable concurrency strategies without changing evaluation code.

## Storage Backend Registry

Storage backends follow a similar pattern through the `get_storage()` function:

```python
def get_storage(storage_config: Optional[str]) -> Storage:
    if storage_config is None:
        return JSONStorage()  # Default

    if storage_config.startswith("sqlite://"):
        return SQLiteStorage(storage_config)
    elif storage_config.startswith("json://"):
        return JSONStorage(storage_config)
    # ... other backends
```

This URL-based configuration enables different storage backends without code changes.

## Extensibility Examples

### Custom Dataset Registration

```python
from doteval.datasets.base import Dataset, _registry

class MyCustomDataset(Dataset):
    name = "mycustom"
    columns = ["question", "answer", "difficulty"]
    splits = ["easy", "medium", "hard"]

    def __init__(self, split: str = "easy"):
        self.split = split
        self.data = load_my_data(split)

    def __iter__(self):
        for item in self.data:
            yield (item.question, item.answer, item.difficulty)

# Register for global use
_registry.register(MyCustomDataset)

# Now available everywhere
@foreach.mycustom(split="hard")
def eval_hard_questions(question, answer, difficulty):
    return Result(...)
```

### Custom Storage Backend

```python
from doteval.storage.base import Storage

class RedisStorage(Storage):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    def create_experiment(self, name: str):
        # Implementation...

    def add_results(self, experiment: str, evaluation: str, results: List[Record]):
        # Implementation...

# Usage
session = SessionManager(storage=RedisStorage("redis://localhost:6379"))
```

### Custom Concurrency Strategy

```python
from doteval.concurrency import AsyncConcurrencyStrategy

class RateLimitedStrategy(AsyncConcurrencyStrategy):
    def __init__(self, requests_per_second: int):
        self.rate_limit = requests_per_second

    async def execute(self, tasks, progress_callback):
        # Implementation with rate limiting...

# Usage
foreach_limited = ForEach(
    concurrency=RateLimitedStrategy(requests_per_second=10)
)
```

## Design Benefits

The registry architecture provides several key benefits:

**Plugin Architecture**: Easy to add new datasets, storage backends, and strategies

**Zero Configuration Discovery**: Available options are discoverable through code completion

**Type Safety**: Interfaces ensure compatible implementations

**Backwards Compatibility**: New registrations don't break existing code

**Testability**: Easy to register mock implementations for testing

**Separation of Concerns**: Registration is separate from usage, enabling clean modular design

This approach makes doteval extensible while maintaining simplicity for common use cases.
