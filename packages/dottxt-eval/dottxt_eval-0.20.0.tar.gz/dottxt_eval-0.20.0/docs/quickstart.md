# Quickstart

Get your first evaluation running in under 5 minutes.

## Prerequisites

- Python 3.8+
- doteval installed: `pip install dottxt-eval`

## 30-Second Example

Create a file called `eval_simple.py`:

```python
from doteval import foreach
from doteval.evaluators import exact_match

# Simple test data
math_problems = [
    ("What is 2+2?", "4"),
    ("What is 5+3?", "8"),
    ("What is 10-7?", "3"),
]

@foreach("question,answer", math_problems)
def eval_math(question, answer):
    """Simple math evaluation - replace with your model."""
    # For demo: just return the expected answer
    # Replace this with your actual model call
    model_response = answer  # Simulated perfect model

    return exact_match(model_response, answer)
```

## Run Your Evaluation

```bash
# Run the evaluation
uv pytest eval_simple.py::eval_math --experiment my_first_eval

# View results
doteval show my_first_eval
```

You should see output showing 3/3 correct answers.

## With a Real Model

Replace the simulation with an actual model call. We use a pytest fixture to efficiently manage the OpenAI client:

```python
import pytest
from openai import OpenAI

@pytest.fixture
def openai_client():
    """OpenAI client fixture (requires OPENAI_API_KEY)."""
    return OpenAI()

@foreach("question,answer", math_problems)
def eval_math(question, answer, openai_client):
    """Math evaluation with real model."""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}]
    )

    model_response = response.choices[0].message.content.strip()
    return exact_match(model_response, answer)
```

**Why use a fixture?** The `openai_client` fixture creates the OpenAI client once and reuses it across all evaluation runs, rather than creating a new client for each question. This is more efficient and follows pytest best practices.

## Next Steps

Ready for more? **[Tutorial 1: Your First Evaluation](tutorials/01-your-first-evaluation.md)** walks through a complete evaluation with real datasets.

## See Also

- **[How to Work with Custom Data Formats](how-to/work-with-custom-data-formats.md)** - Move beyond simple list data
- **[How to Evaluate Structured Generation](how-to/evaluate-structured-generation.md)** - Validate JSON, function calls, and structured outputs
- **[Tutorial 2: Using Real Models](tutorials/02-using-real-models.md)** - Connect to OpenAI and other APIs
- **[Reference: CLI](reference/cli.md)** - Complete command-line reference
