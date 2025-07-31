# How to Debug Slow Evaluations

When evaluations run slower than expected, you need to identify the bottleneck. This guide shows you how to profile, diagnose, and optimize evaluation performance.

## Problem: Evaluation Taking Too Long

```bash
# This evaluation is crawling...
pytest eval_large.py --experiment slow_eval
# Progress: 50/1000 samples completed (5.0%) - ETA: 3 hours
```

You need to identify if the slowdown is from the model, data loading, doteval overhead, or something else.

## Solution 1: Profile Your Evaluation

First, add timing and profiling to understand where time is spent:

```python
import time
import cProfile
import pstats
from doteval import foreach, Result
from contextlib import contextmanager

@contextmanager
def timer(description: str):
    """Simple timing context manager."""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description}: {elapsed:.2f}s")

@foreach("prompt,expected", large_dataset)
def eval_with_profiling(prompt, expected, model):
    """Evaluation with detailed timing."""

    with timer("Model generation"):
        response = model.generate(prompt, max_tokens=100)

    with timer("Evaluation logic"):
        score = custom_evaluator(response, expected)

    with timer("Result creation"):
        result = Result(
            score,
            prompt=prompt,
            response=response,
            scores={"accuracy": score}
        )

    return result
```

Run with profiling:

```python
# Create a profiled version of your evaluation
def profile_evaluation():
    """Run evaluation with detailed profiling."""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run your evaluation here
    # pytest eval_large.py --experiment profiled --samples 10

    profiler.disable()

    # Save and view results
    profiler.dump_stats('evaluation_profile.prof')
    stats = pstats.Stats('evaluation_profile.prof')
    stats.sort_stats('cumulative').print_stats(20)

if __name__ == "__main__":
    profile_evaluation()
```

## Solution 2: Identify Common Bottlenecks

### Bottleneck 1: Model API Calls

Most common issue - each model call is slow (covered in detail in [Tutorial 5: Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)):

```python
import asyncio
from doteval import foreach

# ❌ Slow: Synchronous calls
@foreach("prompt,expected", dataset)
def eval_sync_slow(prompt, expected, model):
    response = model.generate(prompt)  # Blocks for 1-2 seconds
    return evaluate_response(response, expected)

# ✅ Fast: Async calls with concurrency
@foreach("prompt,expected", dataset)
async def eval_async_fast(prompt, expected, async_model):
    response = await async_model.generate_async(prompt)
    return evaluate_response(response, expected)
```

Run with controlled concurrency:

```bash
# Control concurrent requests to avoid overwhelming APIs
pytest eval_async.py --experiment fast_eval --concurrent 10
```

### Bottleneck 2: Data Loading

Large datasets loaded inefficiently:

```python
# ❌ Slow: Loading entire dataset into memory
def slow_dataset():
    data = load_entire_csv("huge_file.csv")  # 10GB file loaded at once
    return [(row.prompt, row.expected) for row in data]

# ✅ Fast: Streaming/lazy loading
def fast_dataset():
    """Stream data lazily to avoid memory issues."""
    with open("huge_file.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (row["prompt"], row["expected"])

@foreach("prompt,expected", fast_dataset())
def eval_with_streaming(prompt, expected, model):
    # Data is loaded one row at a time
    response = model.generate(prompt)
    return evaluate_response(response, expected)
```

### Bottleneck 3: Complex Evaluators

Expensive evaluation logic:

```python
import functools

# ❌ Slow: Expensive operations repeated
def slow_evaluator(response: str, expected: str) -> bool:
    # This regex compilation happens for every evaluation
    pattern = re.compile(r'complex_pattern_here')
    return pattern.match(response) is not None

# ✅ Fast: Cache expensive operations
@functools.lru_cache(maxsize=1000)
def fast_evaluator(response: str, expected: str) -> bool:
    # Regex compiled once and cached
    pattern = re.compile(r'complex_pattern_here')
    return pattern.match(response) is not None

# ✅ Even faster: Pre-compile patterns
COMPILED_PATTERN = re.compile(r'complex_pattern_here')

def fastest_evaluator(response: str, expected: str) -> bool:
    return COMPILED_PATTERN.match(response) is not None
```

## Solution 3: Optimize Model Calls

### Use Connection Pooling

Reuse HTTP connections for API calls:

```python
import pytest
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@pytest.fixture(scope="session")
def optimized_client():
    """HTTP client with connection pooling and retries."""
    session = requests.Session()

    # Connection pooling
    adapter = HTTPAdapter(
        pool_connections=20,
        pool_maxsize=100,
        max_retries=Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session

@foreach("prompt,expected", dataset)
def eval_with_pooling(prompt, expected, optimized_client):
    """Use connection pooling for better performance."""
    response = optimized_client.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
    )

    return evaluate_response(response.json(), expected)
```

### Batch API Calls When Possible

Some APIs support batching:

```python
from typing import List, Tuple

def batch_evaluate_openai(prompts_and_expected: List[Tuple[str, str]], batch_size: int = 10):
    """Batch multiple prompts when API supports it."""
    results = []

    for i in range(0, len(prompts_and_expected), batch_size):
        batch = prompts_and_expected[i:i + batch_size]

        # Create batch request
        batch_messages = [
            {"role": "user", "content": prompt}
            for prompt, _ in batch
        ]

        # Send batch (if API supports it)
        batch_responses = send_batch_request(batch_messages)

        # Evaluate batch results
        for (prompt, expected), response in zip(batch, batch_responses):
            score = evaluate_response(response, expected)
            results.append(Result(score, prompt=prompt, response=response))

    return results
```

## Solution 4: Monitor Performance in Real-Time

Add real-time performance monitoring:

```python
import time
from collections import defaultdict, deque
from threading import Lock

class PerformanceMonitor:
    """Monitor evaluation performance in real-time."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.times = deque(maxlen=window_size)
        self.counters = defaultdict(int)
        self.lock = Lock()

    def record_time(self, operation: str, duration: float):
        with self.lock:
            self.times.append(duration)
            self.counters[operation] += 1

    def get_stats(self) -> dict:
        with self.lock:
            if not self.times:
                return {}

            return {
                "avg_time": sum(self.times) / len(self.times),
                "max_time": max(self.times),
                "min_time": min(self.times),
                "samples": len(self.times),
                "ops_per_second": len(self.times) / sum(self.times) if sum(self.times) > 0 else 0
            }

# Global monitor instance
monitor = PerformanceMonitor()

@foreach("prompt,expected", dataset)
def eval_with_monitoring(prompt, expected, model):
    """Evaluation with performance monitoring."""
    start_time = time.time()

    try:
        response = model.generate(prompt)
        score = evaluate_response(response, expected)

        duration = time.time() - start_time
        monitor.record_time("total", duration)

        # Print stats every 50 evaluations
        if monitor.counters["total"] % 50 == 0:
            stats = monitor.get_stats()
            print(f"Performance: {stats['avg_time']:.2f}s avg, {stats['ops_per_second']:.1f} ops/s")

        return Result(score, prompt=prompt, response=response)

    except Exception as e:
        monitor.record_time("error", time.time() - start_time)
        raise
```

## Solution 5: Use Sampling for Quick Iteration

Test performance optimizations on smaller samples:

```bash
# Test with small sample first
pytest eval_optimized.py --experiment quick_test --samples 50

# If fast, run full evaluation
pytest eval_optimized.py --experiment full_test --samples 1000

# Compare performance
doteval show quick_test
doteval show full_test
```

## Solution 6: Parallel Processing

For CPU-bound evaluations, use multiprocessing:

```python
from multiprocessing import Pool
from functools import partial

def evaluate_single_item(item_and_model, evaluator_func):
    """Evaluate a single item (for multiprocessing)."""
    (prompt, expected), model_config = item_and_model

    # Initialize model in worker process
    model = initialize_model(model_config)
    response = model.generate(prompt)
    return evaluator_func(response, expected)

def parallel_evaluation(dataset, model_config, evaluator_func, num_processes=4):
    """Run evaluation in parallel processes."""

    # Prepare data for multiprocessing
    items_with_config = [
        ((prompt, expected), model_config)
        for prompt, expected in dataset
    ]

    # Create partial function with evaluator
    worker_func = partial(evaluate_single_item, evaluator_func=evaluator_func)

    # Run in parallel
    with Pool(processes=num_processes) as pool:
        results = pool.map(worker_func, items_with_config)

    return results
```

## Quick Performance Checklist

When your evaluation is slow, check these in order:

1. **✅ Use async/await** - Enable concurrent API calls
2. **✅ Set appropriate concurrency** - Start with `--concurrent 10`, adjust based on API limits
3. **✅ Stream large datasets** - Don't load everything into memory
4. **✅ Cache expensive operations** - Use `@lru_cache` for repeated computations
5. **✅ Monitor in real-time** - Add timing to identify bottlenecks
6. **✅ Test with samples** - Use `--samples N` for quick iteration
7. **✅ Use connection pooling** - Reuse HTTP connections
8. **✅ Profile systematically** - Use `cProfile` to find hotspots

## Debugging Commands

```bash
# Profile with small sample
pytest eval.py --experiment profile_test --samples 10

# Monitor memory usage
pytest eval.py --experiment memory_test --samples 100 &
top -p $(pgrep -f pytest)

# Test different concurrency levels
pytest eval.py --experiment conc_5 --concurrent 5
pytest eval.py --experiment conc_20 --concurrent 20

# Compare timing
doteval show conc_5 | grep "Duration"
doteval show conc_20 | grep "Duration"
```

Most performance issues come from inefficient API usage or data loading. Start with async evaluation and appropriate concurrency levels before optimizing other components.

## See Also

- **[Tutorial 5: Scale with Async Evaluation](../tutorials/05-scale-with-async-evaluation.md)** - Learn async patterns for better performance
- **[Tutorial 8: Optimize Concurrency for Production](../tutorials/08-optimize-concurrency-for-production.md)** - Advanced concurrency strategies
- **[How to Handle Rate Limits and API Errors](handle-rate-limits-and-api-errors.md)** - Avoid performance issues from API failures
- **[Reference: Async Evaluations](../reference/async.md)** - Technical details on async implementation
- **[Tutorial 6: pytest Fixtures and Resource Pooling](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Efficient resource management
