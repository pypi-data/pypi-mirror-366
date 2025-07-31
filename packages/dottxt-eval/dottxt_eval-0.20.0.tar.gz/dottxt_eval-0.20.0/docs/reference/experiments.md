# Experiments

Experiments in doteval provide robust state management for evaluations, enabling progress tracking, interruption recovery, and result persistence. They ensure that no evaluation work is ever lost, even in the face of system crashes or network failures.

## Overview

An experiment represents a complete evaluation run with:

- **Unique identification** via experiment names
- **Progress tracking** of which items have been processed
- **Result persistence** across process restarts
- **Automatic resumption** from where evaluations left off
- **Error recovery** with selective retry of failed items

## Experiment Lifecycle

Experiments progress through distinct states that determine their behavior:

### Experiment States

#### Running
- **Description**: Evaluation is currently in progress by an active process
- **CLI Display**: "Running"
- **Resumable**: No (already active)
- **Lock Status**: Locked

```bash
# Active evaluation in progress
pytest eval_math.py --experiment math_eval
# Experiment shows as "Running" while pytest is executing
```

#### Interrupted
- **Description**: Process crashed or was killed before evaluation completed
- **CLI Display**: "Interrupted"
- **Resumable**: Yes (resumes from last completed item)
- **Lock Status**: Locked (stale lock from crashed process)

```bash
# Process was killed mid-evaluation
doteval list
# Shows: math_eval | Interrupted | 2024-01-15 14:30:22

# Resume from where it left off
pytest eval_math.py --experiment math_eval
```

#### Has errors
- **Description**: Evaluation finished but some items failed with errors
- **CLI Display**: "Has errors"
- **Resumable**: Yes (retries only failed items)
- **Lock Status**: Locked (available for retry)

```bash
# Some items failed during evaluation
doteval list
# Shows: math_eval | Has errors | 2024-01-15 14:30:22

# Retry only the failed items
pytest eval_math.py --experiment math_eval
```

#### Completed
- **Description**: Evaluation finished successfully with all items processed
- **CLI Display**: "Completed"
- **Resumable**: No (evaluation is finished)
- **Lock Status**: Unlocked

```bash
# All items processed successfully
doteval list
# Shows: math_eval | Completed | 2024-01-15 14:30:22

# Cannot resume completed experiments
pytest eval_math.py --experiment math_eval
# Error: Experiment 'math_eval' is already completed
```

## Experiment Management

### Creating Experiments

Experiments are created automatically when you run an evaluation (see [@foreach Decorator](foreach.md) for evaluation setup):

```python
@foreach("question,answer", dataset)
def eval_math(question, answer):
    response = model.generate(question)
    return exact_match(response, answer)

# Run with experiment - creates experiment if it doesn't exist
pytest eval_math.py --experiment math_baseline
```

### Resuming Experiments

Resumption works automatically by using the same experiment name:

```python
# Original run (gets interrupted)
pytest eval_large.py --experiment large_eval --samples 500

# Resume later - continues from item 501
pytest eval_large.py --experiment large_eval --samples 1000
```

### Experiment Data

Each experiment stores:

```python
from doteval.sessions import SessionManager

manager = SessionManager("json://evals")
session = manager.get_session("my_evaluation")

print(f"Experiment: {session.name}")
print(f"Status: {session.status}")
print(f"Created: {session.created_at}")
print(f"Results: {len(session.results)} evaluations")

# Access specific evaluation results
math_results = session.results["eval_math"]
print(f"Math eval: {len(math_results)} items")
```

## Advanced Experiment Management

### Incremental Processing with `--samples`

The `--samples` CLI parameter enables incremental processing of large datasets by controlling how many items to process in each run.

**Parameter Behavior:**
- `--samples N`: Process exactly N items total, keeping evaluation "Running" for continuation
- No `--samples`: Process entire dataset and mark as "Completed"

**Usage Examples:**
```bash
# Process first 1000 items
pytest eval_massive.py --experiment massive_eval --samples 1000
# Status: "Running" (allows continuation)

# Later: process 2000 more items (total 3000)
pytest eval_massive.py --experiment massive_eval --samples 3000
# Processes items 1001-3000 only

# Finally: process entire dataset
pytest eval_massive.py --experiment massive_eval
# Processes remaining items and marks as "Completed"
```

**Incremental Processing Logic:**
1. **First run**: `--samples 1000` processes items 0-999, status remains "Running"
2. **Second run**: `--samples 3000` processes items 1000-2999, status remains "Running"
3. **Final run**: No `--samples` processes all remaining items, status becomes "Completed"

!!! info "Experiment Completion Logic"
    - **With `--samples`**: Experiment stays "Running" for continuation
    - **Without `--samples`**: Experiment marked "Completed" when done
    - **Resumption**: Always continues from the last completed item, regardless of `--samples` value

### Error Recovery

Experiments with errors can be selectively retried:

```python
@foreach("question,answer", dataset)
def eval_with_possible_errors(question, answer):
    try:
        response = unreliable_model.generate(question)
        return exact_match(response, answer)
    except APIError:
        raise  # This item will be marked as failed
```

```bash
# Initial run - some items fail
pytest eval_unreliable.py --experiment recovery_test
# Experiment status: "Has errors"

# View which items failed
doteval show recovery_test --full | grep '"error"'

# Retry only failed items
pytest eval_unreliable.py --experiment recovery_test
# Only items with errors are retried
```

### Progress Tracking

Experiments track completion at the item level:

```python
from doteval.sessions import SessionManager

manager = SessionManager("json://evals")
session = manager.get_session("my_experiment")

# Get completed item IDs for specific evaluation
completed_ids = session.get_completed_item_ids("eval_math")
print(f"Completed items: {completed_ids}")

# Check if specific item was completed
if 42 in completed_ids:
    print("Item 42 was successfully processed")
```

## Experiment Configuration

### Storage Location

Configure where experiments are stored:

```bash
# Default location
pytest eval.py --experiment test  # Uses json://.doteval

# Custom location
pytest eval.py --experiment test --storage "json://my_evaluations"

# Absolute path
pytest eval.py --experiment test --storage "json:///home/user/experiments"
```

### Experiment Naming

Choose meaningful experiment names for organization:

```bash
# Include date/version in name
pytest eval.py --experiment "gpt4_baseline_2024_01_15"

# Use environment/config info
pytest eval.py --experiment "prod_config_gsm8k_v2"

# Experiment tracking
pytest eval.py --experiment "exp_${EXPERIMENT_ID}_temperature_0_7"
```

### Concurrent Access

Experiments are protected against concurrent access:

```bash
# Terminal 1
pytest eval.py --experiment shared_experiment
# Acquires lock

# Terminal 2 (same time)
pytest eval.py --experiment shared_experiment
# Error: Experiment is currently being used by another process
```


## Experiment Storage Format

Experiments are stored in JSON format with the following structure:

```json
{
  "name": "math_evaluation",
  "status": "Completed",
  "created_at": 1705325422.123,
  "metadata": {
    "git_commit": "a1b2c3d4"
  },
  "results": {
    "eval_math": [
      {
        "scores": [
          {
            "name": "exact_match",
            "value": true,
            "metrics": ["accuracy"],
            "metadata": {"prediction": "42", "expected": "42"}
          }
        ],
        "item_id": 0,
        "item_data": {"question": "What is 6*7?", "answer": "42"},
        "error": null,
        "timestamp": 1705325422.456
      }
    ]
  }
}
```

## Lock Files

Lock files prevent concurrent access and detect interruptions:

```bash
# Lock file created when experiment starts
ls evals/
# math_eval.json      # Experiment data
# math_eval.lock      # Lock file (only while running)
```

Lock file behavior:

- **Created**: When experiment starts
- **Removed**: When experiment completes successfully
- **Kept**: When experiment fails or is interrupted
- **Detected**: Used to identify interrupted experiments

## Common Issues

- **Experiment not found**: Use `doteval list` to check available experiments
- **Cannot resume completed experiment**: Completed experiments cannot be resumed, use a new name
- **Experiment locked**: Another process is using the experiment, wait or check for stale locks
- **Corrupted data**: Delete corrupted experiment with `doteval delete <name>` and restart
- **Stale locks**: Resume the experiment to clear stale locks automatically

## Usage Tips

- Use descriptive experiment names: `gpt4_gsm8k_baseline` not `test1`
- Include dates: `model_eval_2024_01_15`
- Use `--samples` for incremental processing of large datasets
- Experiments automatically handle interruptions and errors

## See Also

### Core Concepts
- **[@foreach Decorator](foreach.md)** - Learn how `@foreach` automatically creates and manages evaluation experiments
- **[Storage Backends](storage.md)** - Understand the storage systems that persist experiment data
- **[CLI Reference](cli.md)** - Master command-line tools for managing and viewing experiments

### Integration Guides
- **[Pytest Integration](pytest.md)** - See how pytest integrates with experiment management for test execution
- **[Async Evaluations](async.md)** - Understand experiment behavior with concurrent async evaluations

### Advanced Usage
- **[Evaluators](evaluators.md)** - Learn how evaluator results are stored within experiments
- **[Metrics](metrics.md)** - See how aggregated metrics are computed and stored in experiments

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with basic experiment creation and management
- **[Build a Production Evaluation Pipeline](../tutorials/09-build-production-evaluation-pipeline.md)** - Design robust experiment workflows for production systems
- **[Pytest Fixtures and Resource Pooling](../tutorials/06-pytest-fixtures-and-resource-pooling.md)** - Manage experiments with expensive resources efficiently
