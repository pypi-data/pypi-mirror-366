# The @foreach Decorator

Deep dive into doteval's central abstraction that transforms simple functions into powerful evaluation pipelines.

## Basic Mechanics

The `@foreach` decorator is doteval's core abstraction:

```python
@foreach("text,expected", dataset)
def eval_example(text, expected):
    # Function runs once per dataset item
    return Result(...)
```

Under the hood, `@foreach` performs several transformations:

### Dataset Binding and Column Mapping

```python
# The decorator parses column specifications
columns = ["text", "expected"]  # from "text,expected"

# Maps dataset rows to function parameters
for item_id, row_data in enumerate(dataset):
    row_dict = {"text": row_data[0], "expected": row_data[1]}
    result = eval_example(**row_dict)
```

### Pytest Integration

```python
# Functions get marked for pytest discovery
return pytest.mark.doteval(wrapper_function)

# This enables standard pytest commands:
pytest eval_tests.py --experiment my_eval
```

### Async/Sync Handling

The decorator automatically detects function type and applies appropriate execution strategies:

```python
if asyncio.iscoroutinefunction(eval_fn):
    # Use async concurrency strategies
    concurrency = Adaptive()  # Default for async
else:
    # Use sync strategies
    concurrency = Sequential()  # Default for sync
```

## Advanced Features

### Dataset Registry Integration

```python
# Automatic dataset loading via attribute access
@foreach.imdb(split="test")
def eval_movie_sentiment(text, label):
    return Result(...)

# Equivalent to:
dataset = ImdbDataset(split="test")
@foreach("text,label", dataset)
def eval_movie_sentiment(text, label):
    return Result(...)
```

The registry system enables dynamic dataset discovery and automatic column mapping.

### Configuration Inheritance

```python
# Create configured decorator instances
foreach_fast = ForEach(
    concurrency=SlidingWindow(max_concurrency=20),
    storage=SQLiteStorage("fast_evals.db")
)

@foreach_fast("input,output", dataset)
def eval_with_config(input, output):
    # Inherits concurrency and storage settings
    return Result(...)
```

### Error Handling and Retries

```python
from tenacity import AsyncRetrying, stop_after_attempt

foreach_robust = ForEach(
    retries=AsyncRetrying(stop=stop_after_attempt(5))
)

@foreach_robust("text,expected", dataset)
async def eval_with_retries(text, expected):
    # Automatic retry on connection errors
    response = await api_call(text)
    return Result(exact_match(response, expected), prompt=text)
```

## Execution Flow

When an evaluation runs, `@foreach` orchestrates this flow:

```
1. Session Creation
   └── experiment_name → SessionManager → Storage setup

2. Dataset Processing
   └── column_spec parsing → row iteration → parameter mapping

3. Evaluation Execution
   └── function calls → Result validation → Record creation

4. Storage and Progress
   └── Result storage → Progress tracking → Summary computation

5. Completion
   └── Status updates → Cleanup → Return EvaluationSummary
```

## Design Philosophy

The `@foreach` decorator embodies several key design principles:

**Declarative over Imperative**: You declare what you want to evaluate, not how to execute it.

**Convention over Configuration**: Sensible defaults that work out of the box, with explicit configuration when needed.

**Progressive Enhancement**: Start simple, add complexity (concurrency, retries, custom storage) as requirements grow.

**Tool Integration**: Works naturally with existing Python tooling (pytest, debuggers, profilers).
