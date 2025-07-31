# How to Resume Failed Evaluations Properly

Long-running evaluations fail for many reasons: network issues, power outages, crashes, or manual interruption. This guide shows you how to properly resume evaluations and manage session state.

## Problem: Evaluation Interrupted and You Don't Know Where You Are

```bash
# Your evaluation was running for 2 hours...
pytest eval_large.py --experiment long_eval
# Progress: 1247/5000 samples completed (24.9%)
# ^C  <- You hit Ctrl+C or computer crashed

# Now what? How do you resume from sample 1247?
```

Without proper session management, you lose progress and have to start over.

## Solution 1: Understanding doteval Sessions

doteval automatically saves progress, but you need to understand how it works:

```python
from doteval import foreach, Result

@foreach("prompt,expected", large_dataset)
def eval_resumable(prompt, expected, model):
    """Evaluation that can be resumed."""
    response = model.generate(prompt)
    score = exact_match(response, expected)

    # doteval automatically saves:
    # - Which samples have been completed
    # - Results for each completed sample
    # - Session metadata and progress

    return Result(score, prompt=prompt, response=response)
```

## Solution 2: Resume Basic Evaluations

Simply re-run the same command to resume:

```bash
# Original command that was interrupted
pytest eval_large.py --experiment long_eval

# Resume by running the exact same command
pytest eval_large.py --experiment long_eval
# doteval will automatically skip completed samples and continue from where it left off
```

Key points:
- **Use the same experiment name** - This is how doteval identifies the session
- **Use the same dataset** - Order must be consistent for proper resumption
- **Use the same evaluation function name** - Changes break resumption

## Solution 3: Check Session Status Before Resuming

Always check what state your evaluation is in:

```bash
# List all experiments to see status
doteval list

# Check specific experiment details
doteval show long_eval

# See if it's completed, running, or failed
doteval show long_eval --full | grep -E "(Status|Progress|Samples)"
```

Example output:
```
Session: long_eval
Status: Interrupted
Samples: 1247/5000 (24.9%)
Duration: 2h 15m
Last updated: 2024-01-15 14:30:22
```

## Solution 4: Handle Different Resumption Scenarios

### Scenario 1: Clean Interruption (Ctrl+C)

```bash
# This usually resumes cleanly
pytest eval_large.py --experiment clean_interrupted
```

### Scenario 2: Process Killed/System Crash

```bash
# Check for corruption first
doteval show crashed_eval

# If session looks good, resume normally
pytest eval_large.py --experiment crashed_eval

# If session is corrupted, you may need to reset (loses progress)
doteval delete crashed_eval
pytest eval_large.py --experiment crashed_eval_v2
```

### Scenario 3: Code Changes During Evaluation

If you changed your evaluation code:

```python
# ❌ This breaks resumption
@foreach("prompt,expected", dataset)
def eval_modified(prompt, expected, model):
    # You added new logic here - this changes the evaluation signature
    response = model.generate(prompt, temperature=0.5)  # New parameter
    return advanced_evaluator(response, expected)       # New evaluator

# ✅ Better: Use a new experiment name
@foreach("prompt,expected", dataset)
def eval_modified_v2(prompt, expected, model):
    response = model.generate(prompt, temperature=0.5)
    return advanced_evaluator(response, expected)
```

```bash
# Start new experiment instead of trying to resume modified one
pytest eval_large.py::eval_modified_v2 --experiment long_eval_v2
```

### Scenario 4: Dataset Changes

If your dataset changed:

```python
# ❌ This can cause issues
def modified_dataset():
    # You added/removed/reordered items - breaks resumption
    for item in load_data_with_new_filter():
        yield item

# ✅ Better approaches:

# Option 1: Use a new experiment name
@foreach("prompt,expected", modified_dataset())
def eval_new_data(prompt, expected, model):
    return evaluate(prompt, expected, model)

# Option 2: Preserve order and add new items at the end
def safe_dataset_extension():
    # Yield original items in same order
    for item in original_dataset():
        yield item

    # Add new items at the end
    for item in new_items():
        yield item
```

## Solution 5: Manual Session Management

For more control over session state:

```python
from doteval.session import get_session, SessionStatus
import os

def check_and_resume_evaluation():
    """Check session status and handle resumption logic."""
    experiment_name = "my_long_eval"

    # Get session info
    session = get_session(experiment_name)

    if session is None:
        print(f"No existing session '{experiment_name}' found. Starting fresh.")
        return True

    elif session.status == SessionStatus.COMPLETED:
        print(f"Session '{experiment_name}' already completed.")
        print("Use a new experiment name or delete this session.")
        return False

    elif session.status == SessionStatus.RUNNING:
        print(f"Session '{experiment_name}' appears to be running.")
        print("If it's actually stopped, resumption will continue from last checkpoint.")
        return True

    elif session.status == SessionStatus.FAILED:
        print(f"Session '{experiment_name}' failed previously.")
        completed = session.completed_count
        total = session.total_count
        print(f"Progress was: {completed}/{total} samples")

        response = input("Resume from last checkpoint? (y/n): ")
        return response.lower() == 'y'

    return True

# Use in your evaluation script
if __name__ == "__main__":
    if check_and_resume_evaluation():
        # Run evaluation
        os.system("pytest eval_large.py --experiment my_long_eval")
```

## Solution 6: Robust Evaluation Pattern

Design evaluations to be naturally resumable:

```python
import logging
from datetime import datetime
from doteval import foreach, Result

# Set up logging to track progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log'),
        logging.StreamHandler()
    ]
)

@foreach("prompt,expected", large_deterministic_dataset())
def robust_eval(prompt, expected, model):
    """Evaluation designed for reliable resumption."""

    # Log progress periodically
    if hasattr(robust_eval, 'call_count'):
        robust_eval.call_count += 1
    else:
        robust_eval.call_count = 1

    if robust_eval.call_count % 100 == 0:
        logging.info(f"Processed {robust_eval.call_count} samples")

    try:
        # Make evaluation deterministic
        response = model.generate(prompt, temperature=0.0, seed=42)
        score = exact_match(response, expected)

        return Result(
            score,
            prompt=prompt,
            response=response,
            scores={
                "accuracy": score,
                "timestamp": datetime.now().isoformat(),
                "sample_id": robust_eval.call_count
            }
        )

    except Exception as e:
        logging.error(f"Failed on sample {robust_eval.call_count}: {e}")
        # Return failure result instead of crashing
        return Result(
            False,
            prompt=prompt,
            response=f"ERROR: {str(e)}",
            scores={"error": True, "sample_id": robust_eval.call_count}
        )

def large_deterministic_dataset():
    """Dataset that yields items in consistent order."""
    # Sort or use deterministic ordering to ensure resumption works
    items = load_all_items()
    items.sort(key=lambda x: x['id'])  # Consistent ordering

    for item in items:
        yield (item['prompt'], item['expected'])
```

## Solution 7: Advanced Session Recovery

For complex recovery scenarios:

```python
from doteval.storage import get_storage_backend
import json

def analyze_session_state(experiment_name: str):
    """Analyze session state for debugging."""
    storage = get_storage_backend()
    session_data = storage.load_session(experiment_name)

    if not session_data:
        print(f"No session data found for '{experiment_name}'")
        return

    print(f"Session Analysis for '{experiment_name}':")
    print(f"- Status: {session_data.get('status', 'unknown')}")
    print(f"- Total samples: {session_data.get('total_count', 'unknown')}")
    print(f"- Completed: {session_data.get('completed_count', 'unknown')}")
    print(f"- Success rate: {session_data.get('success_rate', 'unknown')}")
    print(f"- Last update: {session_data.get('last_updated', 'unknown')}")

    # Check for common issues
    results = session_data.get('results', [])
    if results:
        print(f"- First result: {results[0] if results else 'None'}")
        print(f"- Last result: {results[-1] if results else 'None'}")

        # Check for errors
        errors = [r for r in results if r.get('scores', {}).get('error', False)]
        print(f"- Error count: {len(errors)}")

        if errors:
            print("- Recent errors:")
            for error in errors[-3:]:  # Show last 3 errors
                print(f"  * {error.get('response', 'No error message')}")

def force_session_recovery(experiment_name: str, checkpoint_sample: int):
    """Force recovery from a specific checkpoint."""
    storage = get_storage_backend()
    session_data = storage.load_session(experiment_name)

    if not session_data:
        print(f"Cannot recover - no session data for '{experiment_name}'")
        return

    # Truncate results to checkpoint
    results = session_data.get('results', [])
    truncated_results = results[:checkpoint_sample]

    # Update session data
    session_data['results'] = truncated_results
    session_data['completed_count'] = len(truncated_results)
    session_data['status'] = 'interrupted'

    # Save modified session
    storage.save_session(experiment_name, session_data)

    print(f"Session '{experiment_name}' reset to sample {checkpoint_sample}")
    print("You can now resume the evaluation normally")

# Usage
if __name__ == "__main__":
    # Analyze before resuming
    analyze_session_state("problematic_eval")

    # Force recovery if needed
    # force_session_recovery("problematic_eval", 1000)
```

## Solution 8: Preventing Common Resumption Issues

### Issue 1: Non-Deterministic Datasets

```python
# ❌ Bad: Random order breaks resumption
def bad_dataset():
    items = load_items()
    random.shuffle(items)  # Different order each time!
    for item in items:
        yield item

# ✅ Good: Deterministic order
def good_dataset():
    items = load_items()
    items.sort(key=lambda x: x['id'])  # Same order every time
    for item in items:
        yield item
```

### Issue 2: Non-Deterministic Model Calls

```python
# ❌ Bad: Random outputs break evaluation consistency
def bad_model_call(prompt):
    return model.generate(prompt, temperature=1.0)  # Random each time

# ✅ Good: Deterministic outputs
def good_model_call(prompt):
    return model.generate(prompt, temperature=0.0, seed=42)
```

### Issue 3: Time-Dependent Data

```python
# ❌ Bad: Dataset changes based on when you run it
def bad_time_dependent_dataset():
    cutoff_date = datetime.now()  # Changes each run!
    return load_data_before(cutoff_date)

# ✅ Good: Fixed cutoff for consistency
def good_fixed_dataset():
    cutoff_date = datetime(2024, 1, 1)  # Fixed cutoff
    return load_data_before(cutoff_date)
```

## Resumption Best Practices

1. **Use consistent experiment names** - Same name = resume, different name = fresh start
2. **Keep datasets deterministic** - Same order every time
3. **Make model calls deterministic** - Use temperature=0.0 and fixed seeds
4. **Check session status** before resuming
5. **Log progress regularly** for debugging
6. **Handle errors gracefully** - Don't crash the entire evaluation
7. **Use new experiment names** when you change evaluation logic
8. **Back up important sessions** before making changes

## Quick Resumption Commands

```bash
# Check all experiments
doteval list

# Check specific experiment
doteval show my_experiment

# Resume evaluation (run same command)
pytest eval_script.py --experiment my_experiment

# Start fresh with new name if resumption fails
pytest eval_script.py --experiment my_experiment_v2

# Delete corrupted session
doteval delete corrupted_experiment
```

## Recovery Checklist

When resumption isn't working:

1. ✅ **Same experiment name?**
2. ✅ **Same dataset order?**
3. ✅ **Same evaluation function?**
4. ✅ **Session not corrupted?** (`doteval show experiment_name`)
5. ✅ **No code changes?** (Use new experiment name if changed)
6. ✅ **Deterministic model calls?**

If all else fails, start a new experiment with a different name. It's better to lose some progress than to have inconsistent results.

## See Also

- **[How to Handle Rate Limits and API Errors](handle-rate-limits-and-api-errors.md)** - Prevent failures that require resumption
- **[Reference: Experiments](../reference/experiments.md)** - Technical details on session management
- **[Tutorial 1: Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Learn basic experiment concepts
- **[Reference: CLI](../reference/cli.md)** - Complete guide to `doteval` command-line tools
- **[Tutorial 9: Build Production Evaluation Pipeline](../tutorials/09-build-production-evaluation-pipeline.md)** - Robust production patterns
