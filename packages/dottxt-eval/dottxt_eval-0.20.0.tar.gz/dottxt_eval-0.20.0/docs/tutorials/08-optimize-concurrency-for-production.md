# Tutorial 8: Master Async Evaluation Patterns

In this tutorial, you'll learn advanced async evaluation patterns by exploring different concurrency strategies. By the end, you'll understand how to choose and configure the right approach for your evaluation needs.

## What you'll learn

- The 5 different concurrency strategies doteval provides
- How to choose the right strategy for your use case
- How the Adaptive strategy automatically optimizes performance
- When and why each strategy works best

## Step 1: Start with a Simple Async Model

Build on Tutorial 5's async foundation with a realistic model:

```python title="eval_concurrency_strategies.py"
import asyncio
import pytest
from doteval import ForEach, Result
from doteval.evaluators import exact_match
from doteval.concurrency import SlidingWindow

@pytest.fixture
def async_model():
    """Mock async model with realistic latency."""
    class MockAsyncModel:
        async def classify(self, text):
            # Simulate realistic API latency (300-500ms)
            await asyncio.sleep(0.3 + (0.2 * len(text) / 100))

            # Simple sentiment classification
            if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                return "positive"
            elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                return "negative"
            else:
                return "neutral"
    return MockAsyncModel()

# Start with a basic sliding window strategy
foreach_sliding = ForEach(concurrency=SlidingWindow(max_concurrency=5))

# Test dataset
sentiment_data = [
    ("This movie is absolutely amazing!", "positive"),
    ("Terrible plot with awful acting", "negative"),
    ("It was an okay film", "neutral"),
    ("Great cinematography and excellent story", "positive"),
    ("Bad writing with terrible development", "negative"),
    ("Average movie with decent performances", "neutral"),
    ("Amazing visuals and great soundtrack", "positive"),
    ("Awful script and bad direction", "negative"),
] * 2  # 16 samples for testing

@foreach_sliding("text,expected", sentiment_data)
async def eval_sliding_window(text, expected, async_model):
    """Evaluation using sliding window concurrency."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text[:30] + "..."
    )
```

Run it to see the baseline:

```bash
time pytest eval_concurrency_strategies.py::eval_sliding_window --experiment sliding_baseline
```

Note the total time - we'll compare this with other strategies.

## Step 2: Understanding Concurrency Strategy Trade-offs

Before diving into specific strategies, let's understand the trade-offs you'll face:

| Strategy | Speed | Resource Control | Predictability | Best For |
|----------|-------|------------------|----------------|----------|
| **Sequential** | Slowest | Complete | Very High | Debugging, strict ordering |
| **Batch** | Medium | Good | High | Balanced throughput & control |
| **SlidingWindow** | Fastest* | Fair | Medium | Maximum throughput |
| **Adaptive** | Smart | Dynamic | Low | Unknown optimal settings |

*When configured correctly for your system

### Key Decision Factors

**Choose Sequential when:**
- Debugging evaluations or need predictable execution order
- Working with very limited resources or rate-limited APIs
- Order of execution matters for your evaluation logic

**Choose Batch when:**
- You want balanced performance with predictable resource usage
- Processing large datasets where you want to control memory usage
- Your system has known capacity limits you don't want to exceed

**Choose SlidingWindow when:**
- You know the optimal concurrency level for your system
- Maximum throughput is critical and your resources can handle it
- Your evaluation tasks are uniform in execution time

**Choose Adaptive when:**
- You're unsure what concurrency level works best
- Your system conditions vary (network, API limits, resource availability)
- You want automatic optimization without manual tuning

## Step 3: Explore All 5 Concurrency Strategies

Now let's see these strategies in action to understand their differences:

```python
from doteval.concurrency import Sequential, Batch, SlidingWindow, Adaptive

# Strategy 1: Sequential (no concurrency - one at a time)
foreach_sequential = ForEach(concurrency=Sequential())

@foreach_sequential("text,expected", sentiment_data[:8])  # Smaller set for comparison
async def eval_sequential(text, expected, async_model):
    """Sequential execution - one request at a time."""
    prediction = await async_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text[:25] + "...")

# Strategy 2: Batch processing - process in groups
foreach_batch = ForEach(concurrency=Batch(batch_size=4))

@foreach_batch("text,expected", sentiment_data[:8])
async def eval_batch(text, expected, async_model):
    """Batch processing - groups of 4 at a time."""
    prediction = await async_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text[:25] + "...")

# Strategy 3: Sliding Window - maintain constant concurrency
foreach_sliding_window = ForEach(concurrency=SlidingWindow(max_concurrency=4))

@foreach_sliding_window("text,expected", sentiment_data[:8])
async def eval_sliding_window_demo(text, expected, async_model):
    """Sliding window - always 4 requests running."""
    prediction = await async_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text[:25] + "...")
```

Run each strategy and compare the timing patterns:

```bash
echo "Sequential (slowest):" && time pytest eval_concurrency_strategies.py::eval_sequential --experiment sequential_demo
echo "Batch processing:" && time pytest eval_concurrency_strategies.py::eval_batch --experiment batch_demo
echo "Sliding window:" && time pytest eval_concurrency_strategies.py::eval_sliding_window_demo --experiment sliding_demo
```

You should see:
- **Sequential**: ~3.2 seconds (8 × 0.4s each)
- **Batch**: ~1.6 seconds (2 batches × 0.8s each)
- **Sliding Window**: ~0.8 seconds (4 concurrent × 0.8s)

## Step 4: Try the Adaptive Strategy

The Adaptive strategy is special - it automatically finds the optimal concurrency level:

```python
from doteval.concurrency import Adaptive

# Adaptive strategy that learns the optimal concurrency
adaptive_strategy = Adaptive(
    initial_concurrency=2,      # Start with 2 concurrent requests
    min_concurrency=1,          # Never go below 1
    max_concurrency=8,          # Don't exceed 8 concurrent
    adaptation_interval=1.0,    # Check performance every second
    increase_threshold=0.90,    # Increase if throughput is good
    decrease_threshold=0.70     # Decrease if throughput drops
)

foreach_adaptive = ForEach(concurrency=adaptive_strategy)

@foreach_adaptive("text,expected", sentiment_data)
async def eval_adaptive_learning(text, expected, async_model):
    """Adaptive strategy that learns optimal concurrency."""
    prediction = await async_model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text[:30] + "..."
    )
```

Run the adaptive strategy:

```bash
pytest eval_concurrency_strategies.py::eval_adaptive_learning --experiment adaptive_demo
```

Watch the output - you'll see it start with 2 concurrent requests and automatically adjust as it learns what works best for your system.

## Step 5: Understanding Strategy Performance

Let's create a simple comparison to understand when each strategy works best:

```python
# Test all strategies on the same data for comparison
strategies = {
    "sequential": Sequential(),
    "batch_4": Batch(batch_size=4),
    "sliding_4": SlidingWindow(max_concurrency=4),
    "adaptive": Adaptive(initial_concurrency=2, max_concurrency=6)
}

# Create evaluations for each strategy
for name, strategy in strategies.items():
    foreach_strategy = ForEach(concurrency=strategy)

    @foreach_strategy("text,expected", sentiment_data[:12])  # Use 12 samples
    async def eval_strategy_comparison(text, expected, async_model, strategy_name=name):
        f"""Compare {strategy_name} strategy performance."""
        prediction = await async_model.classify(text)

        return Result(
            exact_match(prediction, expected),
            prompt=f"[{strategy_name}] {text[:20]}..."
        )

    # Dynamically name the evaluation function
    eval_strategy_comparison.__name__ = f"eval_{name}_strategy"
    globals()[f"eval_{name}_strategy"] = eval_strategy_comparison
```

Run all strategies and compare:

```bash
echo "Testing all strategies..."
for strategy in sequential batch_4 sliding_4 adaptive; do
    echo "\n=== $strategy Strategy ==="
    time pytest eval_concurrency_strategies.py::eval_${strategy}_strategy --experiment ${strategy}_comparison
done
```

This shows you the real-world performance differences between strategies.

## Step 6: Learn When to Use Each Strategy

Now let's understand when each strategy works best:

```python
# Create a summary evaluation showing strategy characteristics
def analyze_strategy_behavior():
    """Understand when to use each concurrency strategy."""

    strategies_guide = {
        "Sequential": {
            "best_for": "Debugging, when order matters, or very limited resources",
            "pattern": "One request at a time: Request1 -> Request2 -> Request3",
            "speed": "Slowest but most predictable"
        },
        "Batch": {
            "best_for": "Predictable resource usage, balanced approach",
            "pattern": "Groups: [Req1,Req2,Req3] -> wait -> [Req4,Req5,Req6]",
            "speed": "Medium speed, good for controlled load"
        },
        "SlidingWindow": {
            "best_for": "Maximum throughput when you know optimal concurrency",
            "pattern": "Always N running: Req1,Req2,Req3 start -> Req1 finishes -> Req4 starts",
            "speed": "Fastest when configured correctly"
        },
        "Adaptive": {
            "best_for": "Unknown optimal concurrency, variable conditions",
            "pattern": "Starts low, learns and adjusts: 2 -> 4 -> 6 -> back to 4",
            "speed": "Smart optimization, finds best speed automatically"
        }
    }

    print("\n📚 Concurrency Strategy Guide:")
    print("=" * 50)

    for strategy, info in strategies_guide.items():
        print(f"\n🔧 {strategy}:")
        print(f"   Best for: {info['best_for']}")
        print(f"   Pattern: {info['pattern']}")
        print(f"   Speed: {info['speed']}")

    return strategies_guide

# Add this as a test to see the guide
def test_strategy_guide():
    """Display the strategy selection guide."""
    analyze_strategy_behavior()
```

Run the guide:

```bash
pytest eval_concurrency_strategies.py::test_strategy_guide -s
```

## Step 7: See Your Results

Compare all the strategies you've tested:

```bash
# List all your experiments
doteval list

# Compare the results
echo "\n=== Strategy Comparison ==="
doteval show sliding_baseline
doteval show sequential_demo
doteval show batch_demo
doteval show sliding_demo
doteval show adaptive_demo
```

Look at the timing and success rates to understand how each strategy performed in your environment.

## What you've learned

You now understand:

1. **The 5 concurrency strategies** - Sequential, Batch, SlidingWindow, and Adaptive
2. **Performance patterns** - How each strategy affects timing and resource usage
3. **Strategy selection** - When to use each approach based on your needs
4. **Adaptive learning** - How the Adaptive strategy automatically optimizes
5. **Real-world tradeoffs** - Speed vs predictability vs resource control

## Strategy Quick Reference

- **Sequential**: Predictable, slow, good for debugging
- **Batch**: Balanced speed and resource control
- **SlidingWindow**: Maximum speed when you know optimal concurrency
- **Adaptive**: Smart optimization when you don't know the best settings

## Key insights

- Concurrency isn't always faster - it depends on your bottlenecks
- The Adaptive strategy is often the best starting point
- Different strategies work better for different types of models and APIs
- Always measure performance in your specific environment

## Next Steps

**[Tutorial 9: Build a Production Evaluation Pipeline](09-build-production-evaluation-pipeline.md)** - Set up CI/CD automation and performance tracking for complete evaluation workflows.

## See Also

- **[How to Debug Slow Evaluations](../how-to/debug-slow-evaluations.md)** - Identify and fix performance bottlenecks
- **[How to Handle Rate Limits and API Errors](../how-to/handle-rate-limits-and-api-errors.md)** - Robust error handling for production
- **[Tutorial 5: Scale with Async Evaluation](05-scale-with-async-evaluation.md)** - Foundation async concepts
- **[Reference: Async Evaluations](../reference/async.md)** - Technical details on async implementation
