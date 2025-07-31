# Tutorial 7: Compare Multiple Models

In this tutorial, you'll learn to evaluate multiple models on the same dataset using pytest parametrization.

## What you'll learn

- How to use `@pytest.mark.parametrize` with `indirect=True` for model comparison
- How to create pooled model instances for efficient testing
- How to generate test parameters dynamically
- How to evaluate models across different task categories
- How to analyze and compare results across models

## Step 1: Understanding pytest Parametrization Basics

Before jumping into model comparison, let's understand how pytest parametrization works with fixtures.

### Simple Parametrization

First, let's see basic parametrization without models:

```python
import pytest

# Simple values parametrization
@pytest.mark.parametrize("number", [1, 2, 3])
def test_simple_numbers(number):
    """Basic parametrization - one test per parameter value."""
    assert number > 0
    print(f"Testing number: {number}")

# Multiple parameters
@pytest.mark.parametrize("text,expected", [
    ("hello", 5),
    ("world", 5),
    ("pytest", 6)
])
def test_string_lengths(text, expected):
    """Test with multiple parameter values."""
    assert len(text) == expected
```

### The `indirect=True` Pattern

When you use `indirect=True`, pytest passes the parameter values to a fixture instead of directly to the test:

```python
@pytest.fixture
def processed_data(request):
    """Fixture that processes the parameter value."""
    raw_value = request.param  # Get the parameter passed from parametrize

    # Process the raw value
    if raw_value == "simple":
        return {"type": "basic", "complexity": 1}
    elif raw_value == "advanced":
        return {"type": "complex", "complexity": 10}
    else:
        return {"type": "unknown", "complexity": 5}

@pytest.mark.parametrize("processed_data", ["simple", "advanced", "unknown"], indirect=True)
def test_with_indirect(processed_data):
    """Test using indirect parametrization."""
    assert "type" in processed_data
    assert processed_data["complexity"] > 0
    print(f"Processing: {processed_data}")
```

The key insight: `indirect=True` lets you transform parameter values through fixtures before they reach your test.

## Step 2: Basic Model Parametrization

Now let's apply this pattern to model comparison:

```python title="eval_model_comparison.py"
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

# Define model configurations
model_configs = [
    "gpt-3.5-turbo",
    "gpt-4o-mini",
    "local_llama"
]

@pytest.fixture
def model(request):
    """Model fixture that creates different models based on parameter."""
    model_name = request.param

    if model_name == "gpt-3.5-turbo":
        from openai import OpenAI
        import os

        class GPT35Model:
            def __init__(self):
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.name = "gpt-3.5-turbo"

            def classify_sentiment(self, text):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                            {"role": "user", "content": text}
                        ],
                        max_tokens=5,
                        temperature=0
                    )
                    return response.choices[0].message.content.strip().lower()
                except:
                    return "neutral"

        return GPT35Model()

    elif model_name == "gpt-4o-mini":
        from openai import OpenAI
        import os

        class GPT4Mini:
            def __init__(self):
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.name = "gpt-4o-mini"

            def classify_sentiment(self, text):
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                            {"role": "user", "content": text}
                        ],
                        max_tokens=5,
                        temperature=0
                    )
                    return response.choices[0].message.content.strip().lower()
                except:
                    return "neutral"

        return GPT4Mini()

    else:  # local_llama
        class LocalLlama:
            def __init__(self):
                self.name = "local_llama"

            def classify_sentiment(self, text):
                # Mock local model - replace with actual Ollama integration
                if any(word in text.lower() for word in ["great", "amazing", "excellent", "love"]):
                    return "positive"
                elif any(word in text.lower() for word in ["terrible", "awful", "bad", "hate"]):
                    return "negative"
                else:
                    return "neutral"

        return LocalLlama()

# Test dataset
sentiment_data = [
    ("I love this product!", "positive"),
    ("This is terrible quality", "negative"),
    ("It's an okay product", "neutral"),
    ("Amazing experience!", "positive"),
    ("Awful customer service", "negative"),
]

@pytest.mark.parametrize("model", model_configs, indirect=True)
@foreach("text,expected", sentiment_data)
def eval_sentiment_comparison(text, expected, model):
    """Compare sentiment classification across different models."""
    prediction = model.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text,
        metadata={"model_name": model.name}
    )
```

Run the comparison:

```bash
pytest eval_model_comparison.py --experiment model_comparison_basic
```

## Step 3: Pooled Model Comparison

Optimize with shared model instances using fixtures from Tutorial 6:

```python title="eval_pooled_comparison.py"
import os
import pytest
from openai import OpenAI
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture(scope="session")
def model_pool():
    """Session-scoped pool of all model instances."""
    print("🏊 Creating model pool...")

    class ModelPool:
        def __init__(self):
            self.models = {}
            self.usage_stats = {}
            self._initialize_models()

        def _initialize_models(self):
            """Initialize all model instances once."""

            # GPT-3.5-turbo
            try:
                print("🔗 Loading GPT-3.5-turbo...")
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                class GPT35Model:
                    def __init__(self, client):
                        self.client = client
                        self.name = "gpt-3.5-turbo"
                        self.call_count = 0

                    def classify_sentiment(self, text):
                        self.call_count += 1
                        response = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Classify sentiment: positive, negative, or neutral. One word."},
                                {"role": "user", "content": text}
                            ],
                            max_tokens=5,
                            temperature=0
                        )
                        return response.choices[0].message.content.strip().lower()

                self.models["gpt-3.5-turbo"] = GPT35Model(client)
                print("✅ GPT-3.5-turbo ready")

            except Exception as e:
                print(f"❌ GPT-3.5-turbo failed: {e}")
                self.models["gpt-3.5-turbo"] = None

            # GPT-4o-mini
            try:
                print("🔗 Loading GPT-4o-mini...")

                class GPT4Mini:
                    def __init__(self, client):
                        self.client = client
                        self.name = "gpt-4o-mini"
                        self.call_count = 0

                    def classify_sentiment(self, text):
                        self.call_count += 1
                        response = self.client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Classify sentiment: positive, negative, or neutral. One word."},
                                {"role": "user", "content": text}
                            ],
                            max_tokens=5,
                            temperature=0
                        )
                        return response.choices[0].message.content.strip().lower()

                # Reuse the same OpenAI client
                self.models["gpt-4o-mini"] = GPT4Mini(self.models["gpt-3.5-turbo"].client if self.models["gpt-3.5-turbo"] else OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
                print("✅ GPT-4o-mini ready")

            except Exception as e:
                print(f"❌ GPT-4o-mini failed: {e}")
                self.models["gpt-4o-mini"] = None

            # Local model
            print("🤖 Loading local model...")

            class LocalModel:
                def __init__(self):
                    self.name = "local_model"
                    self.call_count = 0

                def classify_sentiment(self, text):
                    self.call_count += 1
                    # Mock local model logic
                    positive_words = ["great", "amazing", "excellent", "love", "fantastic"]
                    negative_words = ["terrible", "awful", "bad", "hate", "horrible"]

                    text_lower = text.lower()
                    if any(word in text_lower for word in positive_words):
                        return "positive"
                    elif any(word in text_lower for word in negative_words):
                        return "negative"
                    else:
                        return "neutral"

            self.models["local_model"] = LocalModel()
            print("✅ Local model ready")

            # Initialize usage stats
            for model_name in self.models:
                self.usage_stats[model_name] = 0

        def get_model(self, model_name):
            """Get model instance and track usage."""
            if model_name in self.models and self.models[model_name] is not None:
                self.usage_stats[model_name] += 1
                return self.models[model_name]
            else:
                raise ValueError(f"Model {model_name} not available")

        def get_available_models(self):
            """Get list of successfully loaded models."""
            return [name for name, model in self.models.items() if model is not None]

        def get_stats(self):
            """Get usage statistics for all models."""
            stats = {
                "usage": self.usage_stats,
                "available_models": self.get_available_models()
            }

            # Add call counts if available
            for name, model in self.models.items():
                if model and hasattr(model, 'call_count'):
                    stats[f"{name}_calls"] = model.call_count

            return stats

    pool = ModelPool()
    yield pool

    # Print final statistics
    stats = pool.get_stats()
    print(f"🗑️  Model pool cleanup: {stats}")

@pytest.fixture
def comparison_model(request, model_pool):
    """Fixture that provides specific model from the pool."""
    model_name = request.param
    return model_pool.get_model(model_name)

# Get available models dynamically
def pytest_generate_tests(metafunc):
    """Dynamically generate test parameters based on available models."""
    if "comparison_model" in metafunc.fixturenames:
        # This will be populated when the model_pool fixture is created
        # For now, we'll use all possible models
        available_models = ["gpt-3.5-turbo", "gpt-4o-mini", "local_model"]
        metafunc.parametrize("comparison_model", available_models, indirect=True)

# Evaluation dataset
comparison_data = [
    ("I absolutely love this product!", "positive"),
    ("This is terrible and disappointing", "negative"),
    ("It's an okay product, nothing special", "neutral"),
    ("Amazing quality and great value!", "positive"),
    ("Completely useless and broken", "negative"),
    ("Pretty good overall experience", "positive"),
    ("Not bad, but could be better", "neutral"),
    ("Fantastic service and support!", "positive"),
]

@foreach("text,expected", comparison_data)
def eval_pooled_model_comparison(text, expected, comparison_model):
    """Compare models using shared pool."""
    try:
        prediction = comparison_model.classify_sentiment(text)

        return Result(
            exact_match(prediction, expected),
            prompt=text,
            metadata={"model_name": comparison_model.name}
        )
    except Exception as e:
        return Result(
            exact_match("neutral", expected),  # Fallback
            prompt=text,
            error=str(e),
            metadata={"model_name": getattr(comparison_model, 'name', 'unknown')}
        )

def test_model_pool_stats(model_pool):
    """Display final model pool statistics."""
    stats = model_pool.get_stats()
    print(f"\n📊 Model Pool Final Stats:")
    print(f"Available models: {stats['available_models']}")
    print(f"Usage per model: {stats['usage']}")
    for key, value in stats.items():
        if key.endswith('_calls'):
            print(f"{key}: {value}")
```

Run the pooled comparison:

```bash
pytest eval_pooled_comparison.py --experiment pooled_model_comparison -v -s
```

## Step 4: Advanced Model Comparison with Categories

Compare models across different types of tasks:

```python title="eval_categorized_comparison.py"
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

# Define test categories
evaluation_categories = {
    "simple_sentiment": [
        ("I love it", "positive"),
        ("I hate it", "negative"),
        ("It's okay", "neutral"),
    ],
    "complex_sentiment": [
        ("While the product has some flaws, overall I'm quite satisfied with the quality", "positive"),
        ("Despite a few good features, the numerous issues make this disappointing", "negative"),
        ("The product is functional but nothing extraordinary - meets basic expectations", "neutral"),
    ],
    "edge_cases": [
        ("", "neutral"),  # Empty text
        ("Good bad good bad", "neutral"),  # Mixed signals
        ("This is NOT good", "negative"),  # Negation
    ]
}

@pytest.fixture(scope="session")
def category_model_pool():
    """Model pool optimized for categorized testing."""

    class CategoryModelPool:
        def __init__(self):
            self.models = {}
            self.category_stats = {}
            self._setup_models()

        def _setup_models(self):
            """Setup models with category tracking."""

            # Simple rule-based model
            class RuleBasedModel:
                def __init__(self):
                    self.name = "rule_based"
                    self.category_performance = {}

                def classify_sentiment(self, text, category=None):
                    if category not in self.category_performance:
                        self.category_performance[category] = {"correct": 0, "total": 0}

                    if not text.strip():
                        return "neutral"

                    positive_words = ["love", "good", "great", "satisfied", "quality"]
                    negative_words = ["hate", "bad", "flaws", "issues", "disappointing"]

                    # Handle negation
                    if "not" in text.lower():
                        if any(word in text.lower() for word in positive_words):
                            return "negative"

                    pos_count = sum(1 for word in positive_words if word in text.lower())
                    neg_count = sum(1 for word in negative_words if word in text.lower())

                    if pos_count > neg_count:
                        return "positive"
                    elif neg_count > pos_count:
                        return "negative"
                    else:
                        return "neutral"

            # Advanced model (mock)
            class AdvancedModel:
                def __init__(self):
                    self.name = "advanced_model"
                    self.category_performance = {}

                def classify_sentiment(self, text, category=None):
                    if category not in self.category_performance:
                        self.category_performance[category] = {"correct": 0, "total": 0}

                    # More sophisticated logic for complex cases
                    if not text.strip():
                        return "neutral"

                    # Better handling of complex sentiment
                    if category == "complex_sentiment":
                        if "satisfied" in text.lower() or "overall" in text.lower():
                            return "positive"
                        elif "disappointing" in text.lower() or "issues" in text.lower():
                            return "negative"
                        elif "functional" in text.lower() and "meets" in text.lower():
                            return "neutral"

                    # Better negation handling
                    if "not" in text.lower() and "good" in text.lower():
                        return "negative"

                    # Fallback to simple logic
                    positive_indicators = ["love", "good", "great", "satisfied", "quality"]
                    negative_indicators = ["hate", "bad", "flaws", "issues", "disappointing"]

                    pos_score = sum(1 for word in positive_indicators if word in text.lower())
                    neg_score = sum(1 for word in negative_indicators if word in text.lower())

                    if pos_score > neg_score:
                        return "positive"
                    elif neg_score > pos_score:
                        return "negative"
                    else:
                        return "neutral"

            self.models["rule_based"] = RuleBasedModel()
            self.models["advanced_model"] = AdvancedModel()

        def get_model(self, model_name):
            return self.models[model_name]

        def get_available_models(self):
            return list(self.models.keys())

        def record_result(self, model_name, category, is_correct):
            """Record evaluation result for analysis."""
            if model_name not in self.category_stats:
                self.category_stats[model_name] = {}
            if category not in self.category_stats[model_name]:
                self.category_stats[model_name][category] = {"correct": 0, "total": 0}

            self.category_stats[model_name][category]["total"] += 1
            if is_correct:
                self.category_stats[model_name][category]["correct"] += 1

        def get_category_stats(self):
            """Get performance breakdown by category."""
            results = {}
            for model_name, categories in self.category_stats.items():
                results[model_name] = {}
                for category, stats in categories.items():
                    accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                    results[model_name][category] = {
                        "accuracy": accuracy,
                        "correct": stats["correct"],
                        "total": stats["total"]
                    }
            return results

    pool = CategoryModelPool()
    yield pool

    # Print category performance breakdown
    stats = pool.get_category_stats()
    print(f"\n📊 Category Performance Breakdown:")
    for model_name, categories in stats.items():
        print(f"\n{model_name}:")
        for category, perf in categories.items():
            print(f"  {category}: {perf['accuracy']:.2%} ({perf['correct']}/{perf['total']})")

@pytest.fixture
def categorized_model(request, category_model_pool):
    """Fixture providing model with category context."""
    model_name, category = request.param
    model = category_model_pool.get_model(model_name)
    model._current_category = category  # Add category context
    model._pool = category_model_pool
    return model

def pytest_generate_tests(metafunc):
    """Generate test parameters for model and category combinations."""
    if "categorized_model" in metafunc.fixturenames:
        models = ["rule_based", "advanced_model"]
        categories = list(evaluation_categories.keys())

        # Create all combinations of models and categories
        combinations = []
        for model in models:
            for category in categories:
                combinations.append((model, category))

        metafunc.parametrize("categorized_model", combinations, indirect=True)

def get_category_data(category_name):
    """Helper to get data for a specific category."""
    return evaluation_categories[category_name]

@foreach("text,expected", get_category_data)
def eval_categorized_comparison(text, expected, categorized_model):
    """Evaluate models across different categories."""
    category = categorized_model._current_category

    try:
        # Pass category context to model if it supports it
        if hasattr(categorized_model, 'classify_sentiment'):
            prediction = categorized_model.classify_sentiment(text, category=category)
        else:
            prediction = categorized_model.classify_sentiment(text)

        is_correct = prediction == expected

        # Record result for category analysis
        categorized_model._pool.record_result(
            categorized_model.name,
            category,
            is_correct
        )

        return Result(
            exact_match(prediction, expected),
            prompt=text,
            metadata={
                "model_name": categorized_model.name,
                "category": category
            }
        )

    except Exception as e:
        return Result(
            exact_match("neutral", expected),
            prompt=text,
            error=str(e),
            metadata={
                "model_name": categorized_model.name,
                "category": category
            }
        )
```

Run the categorized comparison:

```bash
pytest eval_categorized_comparison.py --experiment categorized_comparison -v -s
```

## Step 5: Analyze Results Across Models

Create analysis tools to compare results:

```python title="analyze_model_results.py"
import json
from doteval.sessions import SessionManager

def analyze_model_comparison(experiment_name, storage_path="json://.doteval"):
    """Analyze and compare model performance from experiment results."""

    manager = SessionManager(storage_path=storage_path)
    session = manager.get_session(experiment_name)

    if not session:
        print(f"❌ Experiment '{experiment_name}' not found")
        return

    # Group results by model
    model_results = {}

    for result in session.results:
        model_name = result.metadata.get("model_name", "unknown")
        category = result.metadata.get("category", "general")

        if model_name not in model_results:
            model_results[model_name] = {"total": 0, "correct": 0, "categories": {}}

        if category not in model_results[model_name]["categories"]:
            model_results[model_name]["categories"][category] = {"total": 0, "correct": 0}

        # Check if the result was successful
        is_correct = any(score.value for score in result.scores if hasattr(score, 'value'))

        model_results[model_name]["total"] += 1
        model_results[model_name]["categories"][category]["total"] += 1

        if is_correct:
            model_results[model_name]["correct"] += 1
            model_results[model_name]["categories"][category]["correct"] += 1

    # Print comparison report
    print(f"\n📊 Model Comparison Report: {experiment_name}")
    print("=" * 60)

    # Overall performance
    print("\n🏆 Overall Performance:")
    for model_name, stats in model_results.items():
        accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        print(f"{model_name:20}: {accuracy:.2%} ({stats['correct']}/{stats['total']})")

    # Category breakdown
    if any("categories" in stats for stats in model_results.values()):
        print("\n📂 Performance by Category:")

        # Get all unique categories
        all_categories = set()
        for stats in model_results.values():
            all_categories.update(stats["categories"].keys())

        for category in sorted(all_categories):
            print(f"\n  {category}:")
            for model_name, stats in model_results.items():
                if category in stats["categories"]:
                    cat_stats = stats["categories"][category]
                    accuracy = cat_stats["correct"] / cat_stats["total"] if cat_stats["total"] > 0 else 0
                    print(f"    {model_name:18}: {accuracy:.2%} ({cat_stats['correct']}/{cat_stats['total']})")

    # Best performing model
    best_model = max(model_results.items(), key=lambda x: x[1]["correct"] / x[1]["total"] if x[1]["total"] > 0 else 0)
    best_accuracy = best_model[1]["correct"] / best_model[1]["total"] if best_model[1]["total"] > 0 else 0

    print(f"\n🥇 Best Overall: {best_model[0]} ({best_accuracy:.2%})")

if __name__ == "__main__":
    # Analyze different experiment results
    experiments = [
        "model_comparison_basic",
        "pooled_model_comparison",
        "categorized_comparison"
    ]

    for exp in experiments:
        try:
            analyze_model_comparison(exp)
        except Exception as e:
            print(f"❌ Failed to analyze {exp}: {e}")
```

Run the analysis:

```bash
python analyze_model_results.py
```

## What you've learned

You now understand:

1. **Model parametrization** - Using `@pytest.mark.parametrize` with `indirect=True`
2. **Resource efficiency** - Pooling model instances across multiple comparisons
3. **Dynamic testing** - Generating test parameters programmatically
4. **Categorized evaluation** - Testing models across different task types
5. **Result analysis** - Comparing and analyzing performance across models

## Best Practices

- ✅ Use **session-scoped fixtures** for expensive model instances
- ✅ **Pool shared resources** (API clients) across models
- ✅ **Categorize evaluations** to understand model strengths/weaknesses
- ✅ **Handle failures gracefully** with fallback responses
- ✅ **Track metadata** for detailed analysis
- ✅ **Generate parameters dynamically** for flexible model sets

## Next Steps

**[Tutorial 8: Optimize Concurrency for Production](08-optimize-concurrency-for-production.md)** - Scale model comparisons with production-ready async evaluation strategies.
