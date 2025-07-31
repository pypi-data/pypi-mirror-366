# The @foreach Decorator

The `@foreach` decorator is the heart of doteval. It transforms a regular Python function into an evaluation that automatically runs across an entire dataset, handling data iteration, error management, progress tracking, and session management.

## Basic Usage

```python
from doteval import foreach
from doteval.evaluators import exact_match  # See Evaluators reference for more options
from doteval.models import Result

@foreach("question,answer", dataset)
def eval_model(question, answer, model):
    """Evaluate model on question-answer pairs."""
    response = model.generate(question)
    return Result(exact_match(response, answer), prompt=question)
```

## Function Signature

The `@foreach` decorator can be used in two ways:

### 1. Direct Usage (Default)

```python
def foreach(column_spec: str, dataset: Iterator) -> Callable
```

**Parameters:**

- **column_spec** (`str`): Comma-separated list of column names that map to dataset fields
- **dataset** (`Iterator`): An iterator of tuples/lists representing dataset rows

**Returns:** A decorated function that can be used as a regular function or integrated with testing frameworks

### 2. Configured Instance

```python
from doteval import ForEach

foreach = ForEach(
    retries: Optional[AsyncRetrying] = None,
    concurrency: Optional[object] = None,
    storage: Optional[Storage] = None
)
```

**Parameters:**

- **retries** (`Optional[AsyncRetrying]`): Custom retry strategy using tenacity
- **concurrency** (`Optional[object]`): Custom concurrency strategy (AsyncConcurrencyStrategy or SyncConcurrencyStrategy)
- **storage** (`Optional[Storage]`): Custom storage backend

**Returns:** A configured ForEach instance with custom behavior

## Registered Dataset Syntax

For built-in datasets, you can use the simplified `@foreach.dataset_name()` syntax:

```python
from doteval import foreach
from doteval.models import Result

@foreach.gsm8k("test")
def eval_math_reasoning(question, answer, model):
    """Evaluate on GSM8K dataset."""
    response = model.solve(question)
    return Result(exact_match(response, answer), prompt=question)
```

This is equivalent to manually loading the dataset but provides:

- Automatic dataset loading and preprocessing
- Progress bars with dataset names and sizes
- Consistent column naming across datasets

### Available Registered Datasets

Currently available datasets:

- `gsm8k`: Grade school math problems (columns: `question`, `reasoning`, `answer`)
- `bfcl`: Berkeley Function Calling Leaderboard (columns: `question`, `schema`, `answer`)
- `sroie`: Receipt information extraction (columns: `image`, `expected_info`)

See the [datasets reference](datasets.md#registered-datasets) for complete details.

## Column Specification

The `column_spec` parameter defines how dataset items map to function arguments:

### Simple Mapping

```python
from doteval.models import Result

# Dataset: [("What is 2+2?", "4"), ("What is 3+3?", "6")]
@foreach("question,answer", math_dataset)
def eval_math(question, answer, model):
    # question gets "What is 2+2?"
    # answer gets "4"
    result = model.solve(question)
    return Result(exact_match(result, answer), prompt=question)
```

### Complex Data Structures

```python
# Dataset with nested data
dataset = [
    {"text": "Hello world", "metadata": {"difficulty": "easy"}, "expected": "greeting"},
    {"text": "Complex text", "metadata": {"difficulty": "hard"}, "expected": "complex"}
]

@foreach("text,expected", dataset)
def eval_classification(text, expected, model):
    # Only extracts 'text' and 'expected' fields
    prediction = model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

### Multiple Column Formats

```python
from doteval.models import Result

# Single column
@foreach("text,expected", text_dataset)
def eval_single(text, expected, model):
    result = model.process(text)
    return Result(exact_match(result, expected), prompt=text)

# Many columns
@foreach("input,expected,context,difficulty", complex_dataset)
def eval_complex(input, expected, context, difficulty, model):
    response = model.generate(input, context=context)
    return Result(context_aware_match(response, expected, difficulty), prompt=input)
```

## Dataset Formats

The `@foreach` decorator works with various dataset formats:

### Python Lists

```python
from doteval.models import Result

dataset = [
    ("What is the capital of France?", "Paris"),
    ("What is 2+2?", "4"),
    ("Name a color", "red")
]

@foreach("question,answer", dataset)
def eval_qa(question, answer, model):
    return Result(exact_match(model.answer(question), answer), prompt=question)
```

### Generators

```python
import json
from doteval.models import Result

def load_data():
    """Generator that yields data items."""
    with open("dataset.jsonl") as f:
        for line in f:
            item = json.loads(line)
            yield (item["question"], item["answer"])

@foreach("question,answer", load_data())
def eval_from_file(question, answer, model):
    return Result(exact_match(model.answer(question), answer), prompt=question)
```

### Hugging Face Datasets

```python
from datasets import load_dataset
from doteval.models import Result

def gsm8k_data():
    """Load and format GSM8K dataset."""
    dataset = load_dataset("gsm8k", "main", split="test", streaming=True)
    for item in dataset:
        question = item["question"]
        # Extract answer from solution text
        answer = extract_answer(item["answer"])
        yield (question, answer)

@foreach("question,answer", gsm8k_data())
def eval_gsm8k(question, answer, model):
    response = model.solve(question)
    return Result(exact_match(response, answer), prompt=question)
```

### Custom Iterators

```python
import json
from doteval.models import Result

class CustomDataset:
    def __init__(self, data_path):
        self.data_path = data_path

    def __iter__(self):
        with open(self.data_path) as f:
            for line in f:
                data = json.loads(line)
                yield (data["input"], data["output"])

dataset = CustomDataset("my_data.jsonl")

@foreach("input,output", dataset)
def eval_custom(input, output, model):
    result = model.process(input)
    return Result(exact_match(result, output), prompt=input)
```

## Function Arguments

Decorated functions receive dataset columns plus any additional arguments:

### Dependencies and Resources

```python
from doteval.models import Result

def load_model():
    """Load model once for all evaluations."""
    return load_expensive_model()

def load_tokenizer():
    """Load tokenizer."""
    return load_tokenizer()

@foreach("text,label", dataset)
def eval_with_dependencies(text, label, model, tokenizer):
    """Function receives dataset columns + additional dependencies."""
    tokens = tokenizer.encode(text)
    prediction = model.classify(tokens)
    return Result(exact_match(prediction, label), prompt=text)

# Call with dependencies
model = load_model()
tokenizer = load_tokenizer()
eval_with_dependencies(model=model, tokenizer=tokenizer)
```

### Additional Parameters

```python
from doteval.models import Result

@foreach("question,answer", dataset)
def eval_with_params(question, answer, model, temperature=0.7, max_tokens=100):
    """Pass additional parameters to control generation."""
    response = model.generate(
        question,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return Result(exact_match(response, answer), prompt=question)

# Call with custom parameters
eval_with_params(model=my_model, temperature=0.5, max_tokens=50)
```



## Configuration Options

### Custom Retry Configuration

Configure retry behavior for handling transient failures:

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type
from doteval import ForEach
from doteval.models import Result
import aiohttp

# Custom retry strategy for API calls
api_retries = AsyncRetrying(
    retry=retry_if_exception_type((aiohttp.ClientError, TimeoutError)),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)

# Create ForEach instance with custom retries
foreach = ForEach(retries=api_retries)

@foreach("prompt,expected", dataset)
async def eval_api_model(prompt, expected, api_model):
    """Evaluation with automatic retries on API errors."""
    response = await api_model.generate(prompt)
    return Result(exact_match(response, expected), prompt=prompt)
```

### Custom Concurrency Strategies

Configure concurrency behavior for the decorator:

```python
from doteval import ForEach
from doteval.concurrency import SlidingWindow, Batch, Sequential, Adaptive

# Adaptive concurrency (default for async)
adaptive = Adaptive()
foreach_async = ForEach(concurrency=adaptive)

# Sliding window concurrency
sliding_window = SlidingWindow(max_concurrency=20)
foreach_sliding = ForEach(concurrency=sliding_window)

# Batch processing (for sync functions)
batch_strategy = Batch(batch_size=50)
foreach_batch = ForEach(concurrency=batch_strategy)

# Sequential processing (default for sync)
sequential = Sequential()
foreach_seq = ForEach(concurrency=sequential)
```

### Complete Configuration Example

```python
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed
from doteval import ForEach
from doteval.concurrency import SlidingWindow
from doteval.models import Result

foreach = ForEach(
    retries=AsyncRetrying(stop=stop_after_attempt(3), wait=wait_fixed(2)),
    concurrency=SlidingWindow(max_concurrency=10)
)

@foreach("prompt,expected", test_prompts)
async def eval_configured(prompt, expected, api_client):
    response = await api_client.complete(prompt)
    return Result(exact_match(response, expected), prompt=prompt)
```

### Async Functions

The decorator supports async functions:

```python
from doteval.models import Result

@foreach("prompt,expected", dataset)
async def eval_async(prompt, expected, async_model):
    response = await async_model.generate_async(prompt)
    return Result(exact_match(response, expected), prompt=prompt)
```

### Error Handling

```python
from doteval.models import Result

@foreach("question,answer", dataset)
def eval_with_errors(question, answer, model):
    try:
        response = model.generate(question)
        return Result(exact_match(response, answer), prompt=question)
    except Exception as e:
        # Errors are captured automatically
        raise e
```

### Multiple Return Values

```python
from doteval.models import Result

@foreach("text,expected_sentiment,expected_topic", dataset)
def eval_multi_task(text, expected_sentiment, expected_topic, model):
    result = model.analyze(text)

    sentiment_score = exact_match(result.sentiment, expected_sentiment)
    topic_score = exact_match(result.topic, expected_topic)

    return Result(sentiment_score, topic_score, prompt=text)
```

## Session Management

The decorator automatically integrates with doteval's session management, providing automatic resume capabilities for interrupted evaluations:

```python
from doteval.models import Result

@foreach("question,answer", large_dataset)
def eval_large_dataset(question, answer, model):
    """Evaluation with automatic session management."""
    response = model.generate(question)
    return Result(exact_match(response, answer), prompt=question)
```


## See Also

### Core Concepts
- **[Evaluators](evaluators.md)** - Learn how to create and use evaluators within `@foreach` decorated functions
- **[Experiments](experiments.md)** - Understand how `@foreach` automatically creates and manages evaluation experiments
- **[Data Handling](datasets.md)** - Explore dataset formats, column specifications, and registered datasets compatible with `@foreach`

### Integration Guides
- **[Running Evaluations](running-evaluations.md)** - Complete guide on executing `@foreach` functions, including pytest integration, CLI options, and programmatic execution
- **[Async Evaluations](async.md)** - Scale your evaluations with async `@foreach` functions and concurrency control

### Advanced Usage
- **[Metrics](metrics.md)** - Configure custom metrics that aggregate results from `@foreach` evaluations
- **[Storage Backends](storage.md)** - Customize where `@foreach` sessions store evaluation results

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with basic `@foreach` usage
- **[Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)** - Transform sync evaluations to async for better performance
- **[Pytest Fixtures and Resource Pooling](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Use pytest fixtures with `@foreach` functions
