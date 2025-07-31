# Command Line Interface

The doteval CLI provides powerful tools for managing evaluation sessions, viewing results, and monitoring progress.

## Installation

The CLI is included when you install doteval:

```bash
pip install doteval
```

Verify installation:

```bash
doteval --help
```

## Core Commands

### `doteval list`

List all available evaluation sessions.

```bash
doteval list
```

**Options:**

- `--name TEXT` - Filter experiments by name (partial match)
- `--storage TEXT` - Storage backend path (default: `json://.doteval`)

**Examples:**

```bash
# List all sessions
doteval list

# Filter by name
doteval list --name "gsm8k"

# Use custom storage location
doteval list --storage "json://my_evals"
```

**Sample Output:**

```
Named Experiments
┌─────────────────────┬─────────────┐
│ Experiment Name     │ Evaluations │
├─────────────────────┼─────────────┤
│ gsm8k_baseline      │ 1           │
│ gsm8k_improved      │ 2           │
│ gpqa_evaluation     │ 1           │
└─────────────────────┴─────────────┘

Ephemeral Experiments
┌─────────────────────┬─────────────┐
│ Timestamp           │ Evaluations │
├─────────────────────┼─────────────┤
│ 20240115_143022_abc │ 1           │
│ 20240114_091533_def │ 1           │
└─────────────────────┴─────────────┘
```

### `doteval show`

Display detailed information about a specific experiment.

```bash
doteval show EXPERIMENT_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.doteval`)
- `--evaluation TEXT` - Show specific evaluation results
- `--full` - Show complete session data in JSON format
- `--errors` - Show detailed error information

**Examples:**

```bash
# Show session summary
doteval show gsm8k_baseline

# Show full session details
doteval show gsm8k_baseline --full

# Show session from custom storage
doteval show my_eval --storage "json://custom_path"
```

**Sample Output (Summary):**

```
Summary of gsm8k_baseline :: eval_gsm8k
┌────────────┬──────────┬───────┬────────┐
│ Evaluator  │ Metric   │ Score │ Errors │
├────────────┼──────────┼───────┼────────┤
│ exact_match│ accuracy │  0.73 │ 0/100  │
└────────────┴──────────┴───────┴────────┘
```

**Sample Output (Full):**

```json
{
  "name": "gsm8k_baseline",
  "status": "Completed",
  "created_at": 1705325422.123,
  "results": {
    "eval_gsm8k": [
      {
        "scores": [
          {
            "name": "exact_match",
            "value": true,
            "metrics": ["accuracy"],
            "metadata": {"value": "42", "expected": "42"}
          }
        ],
        "item_id": 0,
        "input_data": {"question": "What is 6*7?", "answer": "42"}
      }
    ]
  }
}
```

### `doteval rename`

Rename an existing experiment.

```bash
doteval rename OLD_NAME NEW_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.doteval`)

**Examples:**

```bash
# Rename a session
doteval rename old_experiment new_experiment

# Rename with custom storage
doteval rename exp1 experiment_v2 --storage "json://my_evals"
```

### `doteval delete`

Delete an experiment permanently.

```bash
doteval delete EXPERIMENT_NAME
```

**Options:**

- `--storage TEXT` - Storage backend path (default: `json://.doteval`)

**Examples:**

```bash
# Delete a session
doteval delete failed_experiment

# Delete from custom storage
doteval delete old_eval --storage "json://archived_evals"
```

!!! warning "Permanent Deletion"
    This action cannot be undone. All evaluation results for the experiment will be permanently lost.

### `doteval datasets`

List available datasets that can be used with the `@foreach` decorator.

```bash
doteval datasets
```

**Options:**

- `--verbose`, `-v` - Show detailed information for each dataset
- `--name TEXT`, `-n TEXT` - Filter datasets by name (case-insensitive partial match)

**Examples:**

```bash
# List all available datasets
doteval datasets

# Show detailed information for each dataset
doteval datasets --verbose

# Filter datasets by name
doteval datasets --name gsm

# Combine options
doteval datasets -v -n bfcl
```

**Sample Output (Summary):**

```
Available Datasets
┌─────────┬────────────────┬───────────────────────────────────┬──────────┐
│ Dataset │ Splits         │ Columns                           │     Rows │
├─────────┼────────────────┼───────────────────────────────────┼──────────┤
│ bfcl    │ simple,        │ question, schema, answer          │ streaming│
│         │ multiple,      │                                   │          │
│         │ parallel       │                                   │          │
│ gsm8k   │ train, test    │ question, reasoning, answer       │    8,792 │
│ sroie   │ train, test    │ images, address, company, date,   │    1,000 │
│         │                │ total                             │          │
└─────────┴────────────────┴───────────────────────────────────┴──────────┘

Use --verbose for detailed information and usage examples
```

**Sample Output (Verbose):**

```
╭─────────────────────────────────────────────────────────────────────╮
│ Dataset: gsm8k                                                      │
├────────────┬────────────────────────────────────────────────────────┤
│ Property   │ Value                                                  │
├────────────┼────────────────────────────────────────────────────────┤
│ Name       │ gsm8k                                                  │
│ Splits     │ train, test                                            │
│ Columns    │ question, reasoning, answer                            │
│ Rows       │ 8,792                                                  │
╰────────────┴────────────────────────────────────────────────────────╯

Usage:
  @foreach.gsm8k("test")
  def eval_gsm8k(question, reasoning, answer, model):
      # Your evaluation logic here
      pass
```

!!! info "Dataset Plugins"
    If no datasets are found, you need to install a dataset plugin:
    ```bash
    pip install doteval-datasets
    ```

    You can also create custom dataset plugins. See [How to Create a Dataset Plugin](../how-to/create-dataset-plugin.md).

## Storage Backends

doteval supports different storage backends for evaluation data:

### JSON Storage (Default)

```bash
# Default location
doteval list --storage "json://.doteval"

# Custom directory
doteval list --storage "json://my_custom_path"

# Absolute path
doteval list --storage "json:///home/user/evaluations"
```

The JSON storage backend stores each session as a separate JSON file in the specified directory.

## Working with pytest

The CLI integrates seamlessly with pytest for running evaluations (see [Pytest Integration](pytest.md) for detailed setup):

### Basic Evaluation

```bash
# Run evaluation with experiment name
pytest eval_gsm8k.py --experiment my_gsm8k_eval

# Run with custom storage
pytest eval_gsm8k.py --experiment my_eval --storage json://custom_path
```

### Resuming Interrupted Evaluations

If an evaluation is interrupted, it can be resumed by running the same command:

```bash
# This will automatically resume from where it left off
pytest eval_gsm8k.py --experiment my_gsm8k_eval
```

### Resuming Sessions with Errors

Sessions that finished with errors can also be resumed to retry only the failed items:

```bash
# Resume the experiment - will only retry items that failed
pytest eval_gsm8k.py --experiment my_gsm8k_eval
```

When resuming an error session:

- ✅ Items that completed successfully are skipped
- 🔄 Items that failed are retried
- 📊 All results (old and new) are preserved in the same session

### Concurrent Evaluations

Control concurrency for async evaluations:

```bash
pytest eval_async.py --experiment async_eval --concurrent 20
```

### Retry Configuration

Configure retry behavior for handling transient failures:

```bash
# Set maximum retry attempts (default: 3)
pytest eval_api.py --experiment api_eval --max-retries 5

# Set retry delay in seconds (default: 1.0)
pytest eval_api.py --experiment api_eval --retry-delay 2.0

# Combine retry options
pytest eval_api.py --experiment api_eval --max-retries 10 --retry-delay 5.0
```

**Note**: These options apply to the default retry behavior for connection errors. For more advanced retry configuration, use the `ForEach` class with custom `AsyncRetrying` instances.

### Sample Limits

Limit the number of samples for testing or incremental processing:

```bash
# Process only 100 items for quick testing
pytest eval_gsm8k.py --experiment test_run --samples 100

# Process 500 items, then later continue with more
pytest eval_large_dataset.py --experiment incremental_eval --samples 500
# Later: resume and process more items
pytest eval_large_dataset.py --experiment incremental_eval --samples 1000
```

!!! info "Session Completion with Samples"
    When using `--samples`, the session remains in "Running" status and can be resumed to process more items. Only evaluations that process the complete dataset (without `--samples`) are marked as "Completed".

## Usage Examples

```bash
# Run evaluation with experiment name
pytest eval_model.py --experiment "model_baseline"

# Check results
doteval show "model_baseline"

# Run batch evaluations
for dataset in gsm8k gpqa; do
    pytest "eval_${dataset}.py" --experiment "${dataset}_eval"
done

# Development testing with limited samples
pytest eval_test.py --experiment dev_test --samples 10
```

## Configuration

### Environment Variables

You can set default values using environment variables:

```bash
export DOTEVAL_STORAGE="json://my_default_path"
export DOTEVAL_MAX_CONCURRENCY=50

# Now these are the defaults
doteval list  # Uses json://my_default_path
pytest eval.py --experiment test  # Uses 50 max concurrency
```

### Config Files

Create a `.doteval.toml` config file in your project root:

```toml
[doteval]
storage = "json://evaluations"
max_concurrency = 25

[doteval.sessions]
auto_cleanup_days = 30
```

## Troubleshooting

### Common Issues

#### Session Not Found
```bash
doteval show my_session
# Error: Session 'my_session' not found
```
**Solution**: Check available sessions with `doteval list` and verify the session name.

#### Storage Access Error
```bash
doteval list --storage "json://restricted_path"
# Error: Permission denied
```
**Solution**: Ensure you have read/write permissions to the storage directory.

#### Interrupted Session
```bash
doteval list
# Shows session as "Interrupted"
```
**Solution**: Resume by running the original pytest command again.

### Debug Mode

Enable verbose output for debugging:

```bash
# Enable debug logging
export DOTEVAL_DEBUG=1
doteval show my_session

# Or use pytest verbose mode
pytest eval.py --experiment test -v
```

### Getting Help

```bash
# General help
doteval --help

# Command-specific help
doteval list --help
doteval show --help
doteval rename --help
doteval delete --help
doteval datasets --help
```

## See Also

### Core Concepts
- **[Experiments](experiments.md)** - Understand the experiment lifecycle that CLI commands manage
- **[Storage Backends](storage.md)** - Learn about storage configuration options available via CLI

### Integration Guides
- **[Pytest Integration](pytest.md)** - See how CLI options integrate with pytest-based evaluation execution
- **[@foreach Decorator](foreach.md)** - Understand how CLI parameters affect `@foreach` evaluation behavior
- **[Async Evaluations](async.md)** - Control async evaluation execution with CLI concurrency options

### Advanced Usage
- **[Evaluators](evaluators.md)** - View evaluator results through CLI display tools
- **[Metrics](metrics.md)** - Access computed metrics via CLI session viewing commands

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with basic CLI usage for running evaluations
- **[Build a Production Evaluation Pipeline](../tutorials/09-build-production-evaluation-pipeline.md)** - Master CLI workflow patterns for production systems
- **[Comparing Multiple Models](../tutorials/07-comparing-multiple-models.md)** - Use CLI commands to organize and compare evaluation results
