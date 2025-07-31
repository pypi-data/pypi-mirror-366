# Tutorial 1: Your First Evaluation

In this tutorial, you'll create and run your first LLM evaluation with doteval in about 10 minutes.

## What you'll learn

- How to install and set up doteval
- How to create a basic evaluation with `@foreach`
- How to run evaluations and view results
- How to manage experiments for tracking progress

## Install doteval

```bash
pip install dottxt-eval
```

## Create Your First Evaluation

Create a file called `eval_math.py`:

```python title="eval_math.py"
from doteval import foreach, Result
from doteval.evaluators import exact_match

# Simple math problems dataset
math_data = [
    ("What is 2 + 3?", "5"),
    ("What is 10 - 4?", "6"),
    ("What is 3 * 2?", "6"),
]

@foreach("question,answer", math_data)
def eval_basic_math(question, answer):
    """Test basic math problem solving."""
    # Simulate a model that gets most answers right
    if "2 + 3" in question:
        prediction = "5"
    elif "10 - 4" in question:
        prediction = "6"
    else:
        prediction = "7"  # Wrong answer for 3 * 2

    return Result(
        exact_match(prediction, answer),
        prompt=question
    )
```

## Run the Evaluation

```bash
pytest eval_math.py --experiment my_first_eval
```

You'll see output like:

```
doteval session: my_first_eval
Progress: 3/3 samples completed (100.0%)
Success rate: 2/3 (66.7%)
```

## View Results

```bash
doteval show my_first_eval
```

This shows detailed results:

```
Session: my_first_eval
Status: Completed
Samples: 3/3 (100.0%)
Success Rate: 2/3 (66.7%)

Results:
┌─────────────────┬─────────┬────────────────┐
│ Prompt          │ Success │ Score          │
├─────────────────┼─────────┼────────────────┤
│ What is 2 + 3?  │ ✓       │ exact_match: 1 │
│ What is 10 - 4? │ ✓       │ exact_match: 1 │
│ What is 3 * 2?  │ ✗       │ exact_match: 0 │
└─────────────────┴─────────┴────────────────┘
```

## Understanding the Code

- **`@foreach`**: Turns your function into an evaluation that runs on each data item
- **`Result`**: Wraps your evaluation output with the prompt and scores
- **`exact_match`**: Built-in evaluator that checks if two strings are identical
- **Experiments**: Named evaluations (like `my_first_eval`) that save your results

## Managing Experiments

List all your experiments:

```bash
doteval list
```

Run a new experiment:

```bash
pytest eval_math.py --experiment math_v2
```

Compare results by viewing different experiments.

## Next Steps

**[Tutorial 2: Using Real Models](02-using-real-models.md)** - Connect to OpenAI, local models, and handle real APIs

The key insight: doteval makes LLM evaluation as simple as writing pytest tests.

## See Also

- **[How-To Guides](../how-to/index.md)** - Problem-focused guides for specific challenges
- **[How to Work with Custom Data Formats](../how-to/work-with-custom-data-formats.md)** - Move beyond simple list data
- **[Reference: Experiments](../reference/experiments.md)** - Technical details on experiment management
- **[Reference: CLI](../reference/cli.md)** - Complete `doteval` command reference
