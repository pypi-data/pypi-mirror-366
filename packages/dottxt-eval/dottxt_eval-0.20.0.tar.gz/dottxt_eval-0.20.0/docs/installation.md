# Installation

This guide will walk you through installing doteval and setting up your environment for LLM evaluation.

## Prerequisites

doteval requires **Python 3.10** or higher. Check your Python version:

```bash
python --version
```

!!! tip "Python Version Manager"
    We recommend using [pyenv](https://github.com/pyenv/pyenv) or [conda](https://docs.conda.io/en/latest/) to manage Python versions if you need to install a newer version.

## Basic Installation

### Install from PyPI

The simplest way to install doteval is using pip:

```bash
pip install dottxt-eval
```

### Install from Source

For the latest development version:

```bash
git clone https://github.com/dottxt-ai/doteval.git
cd doteval
pip install -e .
```

## Optional: Dataset Plugins

doteval uses a plugin system for datasets. To use built-in evaluation datasets like GSM8K, BFCL, or SROIE, install the official dataset plugin:

```bash
pip install doteval-datasets
```

This enables using registered datasets with the `@foreach` decorator:

```python
from doteval import foreach

@foreach.gsm8k("test")
def eval_math(question, reasoning, answer, model):
    # Your evaluation logic here
    pass
```

You can also create and install custom dataset plugins. See [How to Create a Dataset Plugin](how-to/create-dataset-plugin.md) for details.

## Development Installation

If you plan to contribute to doteval or need the development dependencies:

```bash
git clone https://github.com/dottxt-ai/doteval.git
cd doteval
pip install -e ".[test,docs]"
```

This installs doteval in editable mode with additional dependencies for:

- **test**: pytest, coverage, and other testing tools
- **docs**: mkdocs, mkdocs-material, and documentation tools

## Verify Installation

After installing doteval, run these commands to verify everything is working correctly:

### 1. Basic Import Test

Test that doteval can be imported successfully:

```bash
python -c "import doteval; print('✓ doteval imported successfully')"
```

Expected output:
```
✓ doteval imported successfully
```

### 2. Version Check

Check the installed version:

```bash
python -c "import doteval._version; print(f'doteval version: {doteval._version.__version__}')"
```

Expected output (version may vary):
```
doteval version: 0.18.2
```

### 3. CLI Availability

Test that the command-line interface is available:

```bash
doteval --help
```

Expected output:
```
Usage: doteval [OPTIONS] COMMAND [ARGS]...

  doteval CLI to manage experiments and evaluations.

Options:
  --help  Show this message and exit.

Commands:
  delete  Delete an experiment.
  list    List available experiments
  rename  Rename an experiment.
  show    Show results of an experiment.
```

### 4. Simple Functionality Test

Run a minimal evaluation example to test core functionality:

**Create a test file** (`test_installation.py`):

```python
from doteval import foreach, Result

@foreach("question,expected", [
    ("What is 2+2?", "4"),
    ("What color is grass?", "green"),
])
def eval_verification_test(question, expected):
    """Simple verification evaluation."""
    responses = {
        "What is 2+2?": "4",
        "What color is grass?": "green"
    }

    answer = responses.get(question, "unknown")
    is_correct = answer == expected

    return Result(
        prompt=question,
        response=answer,
        scores={"correct": is_correct}
    )
```

**Run the test:**

```bash
pytest test_installation.py -v
```

Expected output (similar to):
```
======================= test session starts =======================
collected 1 item

test_installation.py::eval_verification_test[None-None] PASSED [100%]

======================== 1 passed in 0.2s ========================
```

### Alternative: Using uv

If you're using [uv](https://docs.astral.sh/uv/) for Python management, prefix the commands with `uv run`:

```bash
# Import test
uv run python -c "import doteval; print('✓ doteval imported successfully')"

# Version check
uv run python -c "import doteval._version; print(f'doteval version: {doteval._version.__version__}')"

# CLI test
uv run doteval --help

# Functionality test
uv run pytest test_installation.py -v
```

## Troubleshooting

If you encounter issues during verification:

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'doteval'`

**Solutions**:
- Ensure you installed the correct package: `pip install dottxt-eval`
- Check you're using the right Python environment
- Try reinstalling: `pip uninstall dottxt-eval && pip install dottxt-eval`

### Python Version Issues

**Problem**: Compatibility errors or installation failures

**Solutions**:
- Verify Python version: `python --version` (requires Python 3.10+)
- Use a version manager like [pyenv](https://github.com/pyenv/pyenv) or [conda](https://docs.conda.io/en/latest/)
- Create a fresh virtual environment

### Permission Errors

**Problem**: Permission denied during installation

**Solutions**:
- Use a virtual environment: `python -m venv doteval-env && source doteval-env/bin/activate`
- Install for user only: `pip install --user dottxt-eval`
- On Windows, try running as administrator

### CLI Not Found

**Problem**: `doteval: command not found`

**Solutions**:
- Ensure the installation directory is in your PATH
- Try using: `python -c "import doteval.cli; doteval.cli.cli(['--help'])"`
- Reinstall in a virtual environment

## Next Steps

Now that you have doteval installed, you can:

1. **[Try the quickstart guide](tutorials/01-your-first-evaluation.md)** - Build your first evaluation
2. **[Explore examples](tutorials/01-your-first-evaluation.md)** - See real-world evaluation setups
3. **[Learn about the CLI](reference/cli.md)** - Manage evaluation sessions

### Getting Help

If you encounter issues during installation or verification:

1. **Check the [troubleshooting section](#troubleshooting)** above for common solutions
2. **Search [existing issues](https://github.com/dottxt-ai/doteval/issues)** for similar problems
3. **Create a [new issue](https://github.com/dottxt-ai/doteval/issues/new)** with details about your environment and the error
