# Running Evaluations

How to execute doteval evaluations using different methods and control their behavior.

## Execution Methods

### 1. pytest (Recommended)

The primary way to run evaluations is through pytest:

```bash
# Run a specific evaluation
uv pytest eval_model.py::eval_function --experiment my_eval

# Run all evaluations in a file
uv pytest eval_model.py --experiment my_eval

# Run with custom parameters
uv pytest eval_model.py --experiment my_eval --samples 100 --concurrent 10
```

### 2. Programmatic Execution

Run evaluations directly in Python:

```python
from doteval.core import run_evaluation

# Run evaluation function directly
results = await run_evaluation(
    eval_function=eval_model,
    dataset=my_dataset,
    experiment_name="my_eval",
    concurrent=5
)
```


## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--experiment` | Experiment name for session management | `--experiment my_eval` |
| `--samples` | Limit number of samples to process | `--samples 100` |
| `--concurrent` | Maximum concurrent executions | `--concurrent 20` |
| `--storage` | Storage backend configuration | `--storage json://custom/` |
| `-k` | Run evaluations matching keyword patterns | `-k "math or accuracy"` |
| `-m` | Run evaluations matching markers | `-m "not doteval"` |

## Execution Patterns

### Development Testing

```bash
# Quick test with limited samples (ephemeral experiment)
uv pytest eval_model.py --samples 10

# Test with different concurrency (no experiment persistence)
uv pytest eval_model.py --concurrent 5
```

**Ephemeral experiments:** When you omit `--experiment`, doteval creates a temporary experiment that appears in a separate list from your named experiments. This keeps your main experiment history clean while still allowing you to view results from development runs.

### Production Runs

```bash
# Full evaluation with session management
uv pytest eval_model.py --experiment "prod_$(date +%Y%m%d)"

# Resume interrupted evaluation
uv pytest eval_model.py --experiment prod_20241201  # Automatically resumes
```

### Filtering Evaluations

```bash
# Run only evaluations matching a keyword
uv pytest -k "math" --experiment math_only

# Run evaluations with specific names
uv pytest -k "eval_accuracy or eval_speed" --experiment filtered_run

# Run only evaluations (skip regular tests)
uv pytest -m doteval --experiment eval_only

# Skip all evaluations (run only regular tests)
uv pytest -m "not doteval"
```

**Note:** doteval automatically marks all `@foreach` decorated functions with the `doteval` marker, making it easy to include or exclude them from test runs.

### File Discovery

pytest automatically discovers evaluation files and functions:

- **Files**: `eval_*.py` (in addition to standard `test_*.py`)
- **Functions**: `eval_*` (in addition to standard `test_*`)

```python
# This file will be automatically discovered
# eval_math.py

@foreach("question,answer", dataset)
def eval_arithmetic(question, answer, model):
    response = model.generate(question)
    return Result(exact_match(response, answer), prompt=question)
```

## Session Management

### Automatic Resumption

Evaluations automatically resume from where they left off:

```bash
# Start evaluation
uv pytest eval_large.py --experiment large_eval

# If interrupted, resume by running same command
uv pytest eval_large.py --experiment large_eval  # Continues from last checkpoint
```

### Incremental Evaluation

Add more samples to existing experiments:

```bash
# Initial run
uv pytest eval_model.py --experiment incremental --samples 500

# Add more samples
uv pytest eval_model.py --experiment incremental --samples 1000

# Process any remaining
uv pytest eval_model.py --experiment incremental
```

## Error Handling

### Error Recovery

When evaluations fail due to API errors, network issues, or other transient problems, doteval provides several recovery mechanisms:

**Automatic resumption:** Experiments that fail partway through can be resumed by running the same command. Only failed items will be retried:

```bash
# If this fails partway through
uv pytest eval_api.py --experiment api_test

# Resume by running the same command - skips successful items
uv pytest eval_api.py --experiment api_test
```

**Graceful error handling in code:** Handle expected errors within your evaluation function:

```python
@foreach("question,answer", dataset)
def eval_with_error_handling(question, answer, model):
    try:
        response = model.generate(question)
        return exact_match(response, answer)
    except APIError as e:
        # Record the failure but continue evaluation
        return Result(
            exact_match(False, True, name="api_failed"),
            error=f"API Error: {e}",
            prompt=question
        )
    except Exception as e:
        # Handle unexpected errors
        return Result(
            exact_match(False, True, name="failed"),
            error=str(e),
            prompt=question
        )
```

## Performance Optimization

### Concurrency Control

**For API-based models:** Configure concurrency strategy in your evaluation setup, not via `--concurrent`. This provides proper rate limiting and shared throttling:

```python
from doteval import ForEach
from doteval.concurrency import RateLimitedConcurrency

# Configure rate-limited concurrency strategy
foreach = ForEach(
    concurrency=RateLimitedConcurrency(
        max_concurrent=5,
        rate_limit=10,  # requests per second
        burst_limit=20
    )
)

@foreach("question,answer", dataset)
async def eval_openai(question, answer, openai_client):
    # Proper rate limiting across all evaluations
    response = await openai_client.chat.completions.create(...)
    return exact_match(response.choices[0].message.content, answer)
```

**For independent processes:** Use `--concurrent` when you can launch separate instances:

```bash
# Each evaluation gets its own model process
uv pytest eval_ollama.py --experiment ollama_eval --concurrent 4
```

**When to avoid `--concurrent`:**

- API calls (use concurrency strategy instead for proper rate limiting)
- Single shared model instance (most local model setups)
- CPU-bound evaluations where cores are already saturated

### Memory Management

Use streaming datasets for large evaluations:

```python
def streaming_dataset():
    with open("large_dataset.jsonl") as f:
        for line in f:
            data = json.loads(line)
            yield (data["question"], data["answer"])

@foreach("question,answer", streaming_dataset())
def eval_streaming(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

## Viewing Results

After running evaluations, view results using the CLI:

```bash
# View experiment results
doteval show my_eval

# List all experiments
doteval list

# View detailed results with full data
doteval show my_eval --full
```

## See Also

- **[CLI Reference](cli.md)** - Complete command-line options reference
- **[Experiments](experiments.md)** - Session management and state handling
- **[Pytest Integration](pytest.md)** - Deep dive into pytest-specific features
- **[@foreach Decorator](foreach.md)** - Decorator API and configuration options
