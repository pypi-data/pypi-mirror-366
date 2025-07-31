# API Reference

Complete API documentation organized by module. If you're new to doteval, start with the [tutorials](../tutorials/01-your-first-evaluation.md) before diving into the API details.

## Modules

### Core Components

- **[Core](core.md)** - The `@foreach` decorator and core evaluation functions
- **[Models](models.md)** - Data models for results, sessions, and experiments
- **[Evaluators](evaluators.md)** - Built-in evaluators and the `@evaluator` decorator
- **[Metrics](metrics.md)** - Metrics for aggregating evaluation results

### Data and Sessions

- **[Datasets](datasets.md)** - Dataset plugin system and registry
- **[Sessions](sessions.md)** - Session management and experiment tracking

### Tools and Utilities

- **[CLI](cli.md)** - Command-line interface
- **[Plugin](plugin.md)** - pytest integration

## Quick Navigation

### Common Patterns

Quick reference for the most frequently used doteval patterns.

#### Basic Evaluation

```python
from doteval import foreach
from doteval.evaluators import exact_match

@foreach("question,answer", dataset)
def eval_basic(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

#### Custom Evaluator with Multiple Metrics

```python
from doteval import foreach, Result
from doteval.evaluators import evaluator
from doteval.metrics import accuracy, mean

@evaluator(metrics=[accuracy(), mean()])
def custom_score(response: str, expected: str) -> float:
    # Your scoring logic here
    return similarity_score(response, expected)

@foreach("prompt,expected", dataset)
def eval_custom(prompt, expected, model):
    response = model.generate(prompt)
    return custom_score(response, expected)
```

#### Async Evaluation

```python
@foreach("prompt,expected", dataset)
async def eval_async(prompt, expected, async_model):
    response = await async_model.generate_async(prompt)
    return exact_match(response, expected)
```

#### Multiple Scores per Result

```python
@foreach("prompt,expected", dataset)
def eval_multi_score(prompt, expected, model):
    response = model.generate(prompt)

    return Result(
        exact_match(response, expected),  # Primary score
        prompt=prompt,
        response=response,
        scores={
            "exact_match": exact_match(response, expected),
            "length": len(response),
            "contains_keyword": "important" in response.lower()
        }
    )
```

### Common CLI Workflows

```bash
# Run evaluation with experiment tracking
pytest eval_script.py --experiment my_eval

# Resume interrupted evaluation
pytest eval_script.py --experiment my_eval

# View results
doteval show my_eval

# List all experiments
doteval list

# List available datasets
doteval datasets --verbose

# Clean up old experiments
doteval delete old_experiment
```

## See Also

- **[How-To Guides](../how-to/index.md)** - Problem-focused solutions using these APIs
- **[Tutorial Series](../tutorials/01-your-first-evaluation.md)** - Step-by-step guides with practical examples
- **[Reference Documentation](../reference/index.md)** - Conceptual documentation and usage patterns
