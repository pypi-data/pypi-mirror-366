# Tutorial 6: Share Expensive Resources

In this tutorial, you'll learn to efficiently pool expensive model instances and API connections using pytest fixtures.

## What you'll learn

- How pytest fixture scopes affect resource lifecycle
- How to pool expensive model instances with session-scoped fixtures
- How to share API connections across evaluations
- How to implement caching for cost savings
- How to track usage statistics and optimize performance

## Step 1: Understanding Fixture Scopes

Pytest fixtures can have different lifespans. Let's see the difference:

```python title="eval_fixture_scopes.py"
import time
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

# Function-scoped fixture (default) - created for each test
@pytest.fixture
def function_scoped_model():
    """New model instance for each evaluation function."""
    print("🔄 Creating function-scoped model...")

    class SlowModel:
        def __init__(self):
            time.sleep(2)  # Simulate expensive model loading
            self.load_time = time.time()

        def classify(self, text):
            return "positive" if "good" in text.lower() else "negative"

    model = SlowModel()
    yield model
    print("🗑️  Cleaning up function-scoped model")

# Session-scoped fixture - created once for entire test session
@pytest.fixture(scope="session")
def session_scoped_model():
    """Single model instance shared across all evaluations."""
    print("🚀 Creating session-scoped model...")

    class SharedModel:
        def __init__(self):
            time.sleep(2)  # Expensive setup, but only once!
            self.load_time = time.time()
            self.usage_count = 0

        def classify(self, text):
            self.usage_count += 1
            return "positive" if "good" in text.lower() else "negative"

        def get_stats(self):
            return f"Model loaded at {self.load_time}, used {self.usage_count} times"

    model = SharedModel()
    yield model
    print(f"🗑️  Cleaning up session model: {model.get_stats()}")

# Test data
test_data = [
    ("This is good", "positive"),
    ("This is bad", "negative"),
    ("Really good stuff", "positive"),
]

# Evaluation using function-scoped fixture (slow)
@foreach("text,expected", test_data)
def eval_with_function_fixture(text, expected, function_scoped_model):
    """Each call creates a new model instance."""
    prediction = function_scoped_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)

# Evaluation using session-scoped fixture (fast)
@foreach("text,expected", test_data)
def eval_with_session_fixture(text, expected, session_scoped_model):
    """All calls share the same model instance."""
    prediction = session_scoped_model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

Run both to see the performance difference:

```bash
# This takes ~6 seconds (2s setup × 3 evaluations)
time pytest eval_fixture_scopes.py::eval_with_function_fixture --experiment function_scoped -v

# This takes ~2 seconds (2s setup × 1 time)
time pytest eval_fixture_scopes.py::eval_with_session_fixture --experiment session_scoped -v
```

## Step 2: Real Model Connection Pooling

Apply fixture scopes to real model connections:

```python title="eval_model_pooling.py"
import os
import pytest
from openai import OpenAI
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture(scope="session")
def openai_client():
    """Shared OpenAI client for all evaluations."""
    print("🔗 Creating shared OpenAI client...")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Test connection
    try:
        # Make a small test call to verify connection
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        print("✅ OpenAI connection verified")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        pytest.skip("OpenAI API not available")

    yield client
    print("🗑️  Cleaning up OpenAI client")

@pytest.fixture(scope="session")
def model_pool(openai_client):
    """Pool of model instances with shared client."""
    print("🏊 Creating model pool...")

    class ModelPool:
        def __init__(self, client):
            self.client = client
            self.request_count = 0
            self.cache = {}  # Simple response cache

        def classify_sentiment(self, text, use_cache=True):
            """Classify with optional caching."""
            if use_cache and text in self.cache:
                return self.cache[text]

            self.request_count += 1

            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Classify sentiment as positive, negative, or neutral. One word only."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=5,
                    temperature=0
                )

                result = response.choices[0].message.content.strip().lower()

                if use_cache:
                    self.cache[text] = result

                return result

            except Exception as e:
                print(f"API error: {e}")
                return "neutral"

        def get_stats(self):
            return {
                "requests": self.request_count,
                "cache_size": len(self.cache),
                "cache_hit_rate": (len(self.cache) / max(self.request_count, 1)) * 100
            }

    pool = ModelPool(openai_client)
    yield pool

    stats = pool.get_stats()
    print(f"🗑️  Model pool stats: {stats}")

# Test data with some duplicates to show caching benefits
evaluation_data = [
    ("I love this product!", "positive"),
    ("This is terrible", "negative"),
    ("I love this product!", "positive"),  # Duplicate - will use cache
    ("Pretty good overall", "positive"),
    ("This is terrible", "negative"),  # Duplicate - will use cache
    ("It's okay", "neutral"),
]

@foreach("text,expected", evaluation_data)
def eval_with_pooled_model(text, expected, model_pool):
    """Evaluation using pooled model with caching."""
    prediction = model_pool.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )

def test_show_pool_stats(model_pool):
    """Display final pool statistics."""
    stats = model_pool.get_stats()
    print(f"\n📊 Final Pool Statistics:")
    print(f"Total API requests: {stats['requests']}")
    print(f"Cache entries: {stats['cache_size']}")
    print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
```

Run the pooled evaluation:

```bash
pytest eval_model_pooling.py --experiment pooled_models -v -s
```

## Step 3: Local Model Pooling

Pool expensive local model instances:

```python title="eval_local_model_pooling.py"
import time
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture(scope="session")
def local_model_pool():
    """Shared pool of local model instances."""
    print("🤖 Setting up local model pool...")

    class LocalModelPool:
        def __init__(self):
            self.models = {}
            self.usage_stats = {}
            self._setup_models()

        def _setup_models(self):
            """Initialize model instances."""
            print("🔄 Loading sentiment model...")
            time.sleep(1)  # Simulate expensive model loading

            class SentimentModel:
                def __init__(self):
                    self.call_count = 0

                def classify(self, text):
                    self.call_count += 1
                    if any(word in text.lower() for word in ["great", "amazing", "excellent"]):
                        return "positive"
                    elif any(word in text.lower() for word in ["terrible", "awful", "bad"]):
                        return "negative"
                    else:
                        return "neutral"

            self.models["sentiment"] = SentimentModel()
            self.usage_stats["sentiment"] = 0

        def get_sentiment_model(self):
            """Get sentiment model instance."""
            self.usage_stats["sentiment"] += 1
            return self.models["sentiment"]

        def get_stats(self):
            """Get usage statistics."""
            return {
                "models_loaded": list(self.models.keys()),
                "usage_count": self.usage_stats,
                "model_call_counts": {
                    name: model.call_count
                    for name, model in self.models.items()
                    if hasattr(model, 'call_count')
                }
            }

    pool = LocalModelPool()
    yield pool

    stats = pool.get_stats()
    print(f"🗑️  Model pool cleanup: {stats}")

# Test data
local_test_data = [
    ("This is great!", "positive"),
    ("Terrible quality", "negative"),
    ("It's okay", "neutral"),
    ("Amazing product!", "positive"),
    ("Awful experience", "negative"),
]

@foreach("text,expected", local_test_data)
def eval_with_pooled_local_model(text, expected, local_model_pool):
    """Evaluation using pooled local model."""
    model = local_model_pool.get_sentiment_model()
    prediction = model.classify(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )

def test_local_model_stats(local_model_pool):
    """Display local model pool statistics."""
    stats = local_model_pool.get_stats()
    print(f"\n📊 Local Model Pool Stats:")
    print(f"Models loaded: {stats['models_loaded']}")
    print(f"Pool usage: {stats['usage_count']}")
    print(f"Model calls: {stats['model_call_counts']}")
```

## Step 4: Performance Comparison

Compare different fixture strategies:

```python title="eval_fixture_performance.py"
import time
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

# Expensive setup function
def create_expensive_model():
    """Simulate expensive model creation."""
    print("💰 Creating expensive model...")
    time.sleep(0.5)  # Simulate loading time

    class ExpensiveModel:
        def __init__(self):
            self.creation_time = time.time()
            self.call_count = 0

        def predict(self, text):
            self.call_count += 1
            return "positive" if "good" in text else "negative"

    return ExpensiveModel()

# Different fixture scopes for comparison
@pytest.fixture  # Function scope (default)
def function_model():
    model = create_expensive_model()
    yield model

@pytest.fixture(scope="module")  # Module scope
def module_model():
    model = create_expensive_model()
    yield model
    print(f"🗑️  Module model used {model.call_count} times")

@pytest.fixture(scope="session")  # Session scope
def session_model():
    model = create_expensive_model()
    yield model
    print(f"🗑️  Session model used {model.call_count} times")

# Test dataset
perf_data = [("good", "positive"), ("bad", "negative")] * 3

# Benchmarks for each scope
@foreach("text,expected", perf_data)
def eval_function_scope(text, expected, function_model):
    prediction = function_model.predict(text)
    return Result(exact_match(prediction, expected), prompt=text)

@foreach("text,expected", perf_data)
def eval_module_scope(text, expected, module_model):
    prediction = module_model.predict(text)
    return Result(exact_match(prediction, expected), prompt=text)

@foreach("text,expected", perf_data)
def eval_session_scope(text, expected, session_model):
    prediction = session_model.predict(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

Run performance comparison:

```bash
echo "Function scope (slowest):"
time pytest eval_fixture_performance.py::eval_function_scope --experiment func_scope -q

echo -e "\nModule scope (medium):"
time pytest eval_fixture_performance.py::eval_module_scope --experiment mod_scope -q

echo -e "\nSession scope (fastest):"
time pytest eval_fixture_performance.py::eval_session_scope --experiment sess_scope -q
```

## What you've learned

You now understand:

1. **Fixture scoping** - How function vs session scopes affect resource lifecycle
2. **Model pooling** - Sharing expensive model instances efficiently across tests
3. **Connection reuse** - Pooling API clients and implementing caching
4. **Performance optimization** - Choosing appropriate fixture scopes for your needs
5. **Resource management** - Proper setup, usage tracking, and cleanup patterns

## Best Practices

- ✅ Use **session scope** for expensive model loading and API clients
- ✅ Use **function scope** only when test isolation is required
- ✅ **Cache API responses** when appropriate to reduce costs
- ✅ Track **usage statistics** for optimization insights
- ✅ Always include **cleanup logic** in fixtures
- ✅ Handle **connection failures** gracefully

## Next Steps

**[Tutorial 7: Comparing Multiple Models](07-comparing-multiple-models.md)** - Use fixtures with parametrized model comparisons to test multiple models efficiently.
