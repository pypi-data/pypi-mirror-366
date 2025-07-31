# Pytest Integration

doteval integrates seamlessly with pytest, allowing you to run LLM evaluations as part of your test suite.

## Overview

When you install doteval, it automatically registers a pytest plugin that:

- Collects evaluation files (`eval_*.py`) and functions (`eval_*`)
- Integrates with pytest fixtures and parametrization
- Provides evaluation-specific markers and configuration

## Installation

The pytest plugin is automatically available when you install doteval:

```bash
uv add doteval
```

## File and Function Collection

doteval extends pytest's collection to include evaluation files and functions alongside your regular tests:

- **Files**: `eval_*.py`
- **Functions**: `eval_*`

```python
# eval_math.py - This file will be collected by pytest

import doteval
from doteval.evaluators import exact_match

dataset = [("2+2", "4"), ("3+3", "6")]

@doteval.foreach("question,answer", dataset)
def eval_arithmetic(question, answer):
    result = model.generate(question)
    return exact_match(result, answer)
```

## Pytest Fixtures Integration

doteval evaluations work seamlessly with pytest fixtures:

```python
import pytest
import doteval
from doteval.evaluators import exact_match

@pytest.fixture
def model():
    """Initialize model once for all tests."""
    return YourModel()

@pytest.fixture
def template():
    """Create a prompt template."""
    return "Q: {question}\nA:"

dataset = [("What is 2+2?", "4"), ("What is 3+3?", "6")]

@doteval.foreach("question,answer", dataset)
def eval_math_with_fixtures(question, answer, model, template):
    prompt = template.format(question=question)
    result = model.generate(prompt)
    return exact_match(result, answer)
```

## Markers

All doteval evaluations are automatically marked with `@pytest.mark.doteval`:

```bash
# Run only doteval evaluations
pytest -m doteval

# Skip doteval evaluations
pytest -m "not doteval"
```

## Parametrized Tests

doteval works with pytest parametrization:

```python
import pytest
import doteval

@pytest.mark.parametrize("model_name", ["gpt-3.5", "gpt-4"])
@doteval.foreach("question,answer", dataset)
def eval_multiple_models(question, answer, model_name):
    model = load_model(model_name)
    result = model.generate(question)
    return exact_match(result, answer)
```

## Error Handling

The plugin provides robust error handling:

- Individual evaluation failures don't stop the entire test suite
- Errors are captured and stored in the evaluation results
- Detailed error reporting in test output

## Configuration

You can configure the plugin behavior in `pytest.ini`:

```ini
[tool:pytest]
# Collect only evaluation files
python_files = eval_*.py
python_functions = eval_*

# Set default markers
markers =
    doteval: LLM evaluation tests
    slow: tests that take a long time
```

## Best Practices

### File Organization

```
tests/
├── eval_math.py        # Math evaluations
├── eval_reasoning.py   # Reasoning evaluations
└── fixtures/
    ├── conftest.py     # Shared fixtures
    └── models.py       # Model fixtures
```

### Fixture Scope

Use appropriate fixture scopes for expensive resources:

```python
@pytest.fixture(scope="session")
def expensive_model():
    """Load model once per test session."""
    return load_large_model()

@pytest.fixture(scope="module")
def dataset():
    """Load dataset once per module."""
    return load_dataset()
```

### Session Naming

Use descriptive session names:

```bash
pytest eval_math.py --experiment "baseline_gpt35_v1"
pytest eval_math.py --experiment "improved_prompt_v2"
```

## See Also

### Core Concepts
- **[@foreach Decorator](foreach.md)** - How `@foreach` decorated functions work with pytest
- **[Experiments](experiments.md)** - Experiment tracking and resumption
- **[Running Evaluations](running-evaluations.md)** - Command-line options for pytest-based evaluations

### Integration Guides
- **[Async Evaluations](async.md)** - Run async evaluations with pytest
- **[Data Handling](datasets.md)** - Use pytest fixtures for dataset management

### Advanced Usage
- **[Evaluators](evaluators.md)** - Integrate custom evaluators with pytest fixtures
- **[Storage Backends](storage.md)** - Configure storage for pytest runs
- **[Metrics](metrics.md)** - View results from pytest evaluations

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with pytest evaluations
- **[Pytest Fixtures and Resource Pooling](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Advanced pytest integration
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Use pytest parametrization for model comparisons
