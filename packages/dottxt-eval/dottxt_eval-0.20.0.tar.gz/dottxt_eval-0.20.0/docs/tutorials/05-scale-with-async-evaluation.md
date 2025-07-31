# Tutorial 5: Scale with Async Evaluation

In this tutorial, you'll learn to transform slow synchronous evaluations into fast asynchronous ones.

## What you'll learn

- The difference between sync and async evaluation approaches
- How to convert synchronous evaluations to async
- How to enable concurrent execution with `SlidingWindow`
- When async evaluation provides the biggest benefits
- How to measure and compare performance improvements

## Understanding the Problem: Why Evaluations Are Slow

Before diving into async, let's understand **why** evaluations are slow and **when** async helps.

Most LLM evaluations are **I/O bound** - they spend time waiting for:
- API calls to language models (OpenAI, Anthropic, etc.)
- Database queries for datasets
- File system operations for loading data

**The key insight**: While one evaluation waits for an API response, your CPU could be processing other evaluations concurrently.

### CPU vs I/O Bound Tasks

```python
# CPU-bound: Your computer does the work
def cpu_intensive_calculation(n):
    return sum(i**2 for i in range(n))  # Computer calculates this

# I/O-bound: Your computer waits for external systems
def api_call_to_model(prompt):
    response = requests.post("https://api.openai.com/...", ...)  # Wait for network
    return response.json()
```

**Async helps with I/O-bound tasks** (like API calls) but won't speed up CPU-intensive calculations.

## Step 1: Create a Slow Sync Evaluation

Start with a deliberately slow evaluation to see the baseline:

```python title="eval_slow_sync.py"
import time
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture
def model():
    """Slow mock model for baseline testing."""
    class SlowModel:
        def classify(self, text):
            time.sleep(1)  # Simulate API latency
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return SlowModel()

def slow_sentiment_model(text):
    """Mock slow model that takes 1 second per call."""
    time.sleep(1)  # Simulate API latency

    # Simple sentiment logic
    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Test dataset
sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach("text,expected", sentiment_data)
def eval_sync_sentiment(text, expected, model):
    """Slow synchronous sentiment evaluation."""
    prediction = model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run and time the sync version:

```bash
time pytest eval_slow_sync.py --experiment sync_baseline
```

You'll see it takes about 8 seconds (8 samples × 1 second each). Note the total time.

## Understanding Async: The Foundation

Before converting to async, let's understand what `async` and `await` actually do.

### Synchronous Execution (What We Just Ran)
```python
# Synchronous: Each operation blocks until complete
def sync_process():
    result1 = slow_operation_1()  # Wait 1 second
    result2 = slow_operation_2()  # Wait 1 second
    result3 = slow_operation_3()  # Wait 1 second
    # Total: 3 seconds
```

### Asynchronous Execution (What We're Building Toward)
```python
# Asynchronous: Operations can overlap
async def async_process():
    task1 = async_operation_1()  # Start immediately
    task2 = async_operation_2()  # Start immediately
    task3 = async_operation_3()  # Start immediately

    result1 = await task1  # Wait for completion
    result2 = await task2  # Wait for completion
    result3 = await task3  # Wait for completion
    # Total: ~1 second (all run concurrently)
```

### Key Async Concepts

**`async def`**: Declares a function that can be paused and resumed
**`await`**: Pauses the function until the awaited operation completes
**Concurrency**: Multiple operations in progress at the same time (but not necessarily simultaneously)

```python
# This is NOT concurrent - still runs one at a time
async def not_concurrent():
    result1 = await slow_call()  # Wait 1 second
    result2 = await slow_call()  # Wait 1 second
    # Total: 2 seconds

# This IS concurrent - both run at the same time
async def concurrent():
    task1 = slow_call()      # Start immediately
    task2 = slow_call()      # Start immediately
    result1 = await task1    # Wait for both
    result2 = await task2
    # Total: ~1 second
```

## Step 2: Convert to Async

Now create an async version of the same evaluation:

```python title="eval_async_sentiment.py"
import asyncio
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture
def async_model():
    """Async mock model for testing."""
    class AsyncModel:
        async def classify(self, text):
            await asyncio.sleep(1)  # Simulate async API call
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return AsyncModel()

async def async_sentiment_model(text):
    """Mock async model that simulates API latency."""
    await asyncio.sleep(1)  # Simulate async API call

    # Same sentiment logic
    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Same test dataset
sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach("text,expected", sentiment_data)
async def eval_async_sentiment(text, expected, async_model):
    """Async sentiment evaluation."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the async version:

```bash
time pytest eval_async_sentiment.py --experiment async_basic
```

Still takes about 8 seconds! Why? Because doteval runs async functions sequentially by default.

### Why Async Alone Doesn't Help

This is a common confusion point. Let's understand what just happened:

```python
# What we wrote (async function)
async def eval_async_sentiment(text, expected, async_model):
    prediction = await async_model.classify(text)  # Pauses here
    return Result(exact_match(prediction, expected), prompt=text)

# How doteval executed it (sequential by default)
for sample in dataset:
    result = await eval_async_sentiment(sample[0], sample[1], model)
    # Each evaluation waits for the previous one to complete
```

**The problem**: Even though our function is `async`, doteval is still calling them one at a time. We get:

1. Call sample 1 → wait 1 second → get result
2. Call sample 2 → wait 1 second → get result
3. Call sample 3 → wait 1 second → get result
4. ...and so on

**The solution**: We need to tell doteval to run multiple evaluations **concurrently**.

## Step 3: Add Concurrency

Enable concurrent execution with a concurrency strategy:

```python title="eval_concurrent_sentiment.py"
import asyncio
import pytest
from doteval import ForEach, Result
from doteval.evaluators import exact_match
from doteval.concurrency import SlidingWindow

@pytest.fixture
def async_model():
    """Async mock model for concurrent testing."""
    class AsyncModel:
        async def classify(self, text):
            await asyncio.sleep(1)
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return AsyncModel()

async def async_sentiment_model(text):
    """Mock async model with API latency."""
    await asyncio.sleep(1)

    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
        return "positive"
    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
        return "negative"
    else:
        return "neutral"

# Configure concurrent execution
foreach_concurrent = ForEach(concurrency=SlidingWindow(max_concurrency=4))

sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot and awful acting", "negative"),
    ("It was an okay film, nothing special", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing and terrible direction", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad character development", "negative"),
]

@foreach_concurrent("text,expected", sentiment_data)
async def eval_concurrent_sentiment(text, expected, async_model):
    """Concurrent async sentiment evaluation."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the concurrent version:

```bash
time pytest eval_concurrent_sentiment.py --experiment concurrent_test
```

Now it should take about 2 seconds (8 samples ÷ 4 concurrent = 2 batches × 1 second each)!

### Understanding What Just Happened

The `SlidingWindow(max_concurrency=4)` changed how doteval executes our evaluations:

```python
# Without concurrency (what we had before)
await eval_sample_1()  # 1 second
await eval_sample_2()  # 1 second
await eval_sample_3()  # 1 second
await eval_sample_4()  # 1 second
# Total: 4 seconds for 4 samples

# With SlidingWindow(max_concurrency=4)
await asyncio.gather(
    eval_sample_1(),  # All start together
    eval_sample_2(),  # All start together
    eval_sample_3(),  # All start together
    eval_sample_4(),  # All start together
)
# Total: ~1 second for 4 samples
```

**Key insight**: The `ForEach(concurrency=SlidingWindow(...))` tells doteval:
- "Run up to 4 evaluations at the same time"
- "When one finishes, start the next one"
- "Keep 4 running concurrently until all are done"

So for 8 samples with concurrency=4:
- **Batch 1**: Samples 1-4 run together (1 second)
- **Batch 2**: Samples 5-8 run together (1 second)
- **Total**: ~2 seconds instead of 8!

## Step 4: Measure Performance Improvements

Compare all three approaches:

```bash
# View timing results
doteval show sync_baseline
doteval show async_basic
doteval show concurrent_test
```

You should see:

- **Sync**: ~8 seconds (baseline)
- **Async without concurrency**: ~8 seconds (no improvement)
- **Async with concurrency**: ~2 seconds (4x improvement!)

## Step 5: Test Different Concurrency Levels

Try different concurrency settings:

```python
# Higher concurrency
foreach_high = ForEach(concurrency=SlidingWindow(max_concurrency=8))

@foreach_high("text,expected", sentiment_data)
async def eval_high_concurrency(text, expected, async_model):
    """High concurrency evaluation."""
    prediction = await async_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

```bash
time pytest eval_concurrent_sentiment.py::eval_high_concurrency --experiment high_concurrency
```

With 8 concurrent calls, all 8 samples should complete in about 1 second!

### Choosing the Right Concurrency Level

How do you pick the right `max_concurrency`? Consider these factors:

**Too Low (concurrency=1-2)**:
- Safe but slow
- Underutilizes your connection capacity

**Just Right (concurrency=4-20)**:
- Balances speed with stability
- Most APIs can handle this range
- Good starting point: `concurrency = min(dataset_size, 10)`

**Too High (concurrency=100+)**:
- May hit API rate limits
- Can overwhelm servers
- Diminishing returns after optimal point

**Real-world guidelines**:
- **OpenAI API**: Start with 10-20, increase based on your tier
- **Local models**: Can handle 50-100+ depending on GPU memory
- **Anthropic API**: Start with 5-10 concurrent requests
- **Custom APIs**: Test incrementally to find the sweet spot

## Step 6: Real-World Async Model

Here's how to integrate with real async APIs:

```python title="eval_real_async.py"
import asyncio
import aiohttp
from doteval import ForEach, Result
from doteval.evaluators import exact_match
from doteval.concurrency import SlidingWindow

async def openai_sentiment(text, session):
    """Example async OpenAI API call."""
    # Mock API call - replace with real OpenAI async client
    await asyncio.sleep(0.5)  # Realistic API latency

    # Mock response parsing
    if "amazing" in text.lower():
        return "positive"
    elif "terrible" in text.lower():
        return "negative"
    else:
        return "neutral"

# Configure for API rate limits
foreach_api = ForEach(concurrency=SlidingWindow(max_concurrency=10))

@foreach_api("text,expected", sentiment_data)
async def eval_real_api(text, expected):
    """Evaluation with real async API calls."""
    async with aiohttp.ClientSession() as session:
        prediction = await openai_sentiment(text, session)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

## What you've learned

You now understand the **three-step pattern** for async evaluation optimization:

### 1. Identify I/O Bound Operations
- API calls to language models (OpenAI, Anthropic, etc.)
- Database queries
- File system operations
- Network requests

### 2. Convert Functions to Async
```python
# Before: Synchronous
def eval_sync(prompt, model):
    result = model.generate(prompt)  # Blocks
    return exact_match(result, expected)

# After: Asynchronous
async def eval_async(prompt, model):
    result = await model.generate(prompt)  # Can pause/resume
    return exact_match(result, expected)
```

### 3. Configure Concurrency
```python
# Enable concurrent execution
foreach_concurrent = ForEach(concurrency=SlidingWindow(max_concurrency=10))
```

## Key Insights

**🚫 Common Misconception**: "Making my function `async` will speed it up"
**✅ Reality**: Async functions run sequentially by default - you need concurrency configuration

**🚫 Common Mistake**: Setting concurrency too high initially
**✅ Best Practice**: Start with 10, increase gradually while monitoring performance

**🚫 Wrong Use Case**: Using async for CPU-intensive calculations
**✅ Right Use Case**: Using async for I/O operations (API calls, database queries, file access)

## The Mental Model

Think of async evaluation like a restaurant:

- **Synchronous**: One waiter takes one order, waits for the kitchen, serves the food, then takes the next order
- **Asynchronous with concurrency**: Multiple waiters take orders simultaneously, kitchen works on multiple dishes at once
- **Concurrency level**: How many waiters you hire (too few = slow service, too many = chaos)

## Next Steps

**[Tutorial 6: Pytest Fixtures and Resource Pooling](06-pytest-fixtures-and-resource-pooling.md)** - Manage expensive resources efficiently with proper fixture scoping.
