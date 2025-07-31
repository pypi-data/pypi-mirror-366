# How to Create a Dataset Plugin

This guide walks you through creating a custom dataset plugin for doteval, from implementation to distribution.

## Overview

Dataset plugins allow you to:
- Package evaluation datasets for easy distribution
- Share datasets with the community
- Integrate custom data formats with doteval's evaluation framework
- Maintain datasets independently from doteval core

## Prerequisites

- Basic Python knowledge
- Understanding of doteval's `@foreach` decorator
- Familiarity with Python packaging (helpful but not required)

## Step 1: Set Up Your Project

Create a new directory for your dataset plugin:

```bash
mkdir my-eval-dataset
cd my-eval-dataset
```

Set up the project structure:

```
my-eval-dataset/
├── pyproject.toml
├── README.md
├── src/
│   └── my_eval_dataset/
│       ├── __init__.py
│       └── dataset.py
├── tests/
│   └── test_dataset.py
└── data/  # Optional: for bundled data files
    ├── train.jsonl
    └── test.jsonl
```

## Step 2: Create the Dataset Class

In `src/my_eval_dataset/dataset.py`:

```python
from doteval.datasets import Dataset
from typing import Iterator, Tuple, Optional
import json
import os
from pathlib import Path


class MyEvalDataset(Dataset):
    """A custom dataset for evaluating specific model capabilities."""

    # Required class attributes
    name = "my_eval"  # This is what users will use: @foreach.my_eval()
    splits = ["train", "test", "validation"]
    columns = ["input", "expected_output", "task_type"]

    def __init__(self, split: str, subset: Optional[str] = None, max_samples: Optional[int] = None):
        """Initialize the dataset.

        Args:
            split: Which data split to load ("train", "test", or "validation")
            subset: Optional subset of the data (e.g., "easy", "hard")
            max_samples: Limit the number of samples (useful for debugging)
        """
        if split not in self.splits:
            raise ValueError(
                f"Invalid split '{split}'. "
                f"Available splits: {', '.join(self.splits)}"
            )

        self.split = split
        self.subset = subset
        self.max_samples = max_samples

        # Store configuration but don't load data yet (lazy loading)
        self._data_path = self._get_data_path(split)

        # Set num_rows if it can be determined efficiently
        # Leave as None for streaming datasets
        self.num_rows = self._count_rows() if max_samples is None else max_samples

    def __iter__(self) -> Iterator[Tuple]:
        """Yield dataset items as tuples matching the columns specification."""
        count = 0

        with open(self._data_path, 'r') as f:
            for line in f:
                if self.max_samples and count >= self.max_samples:
                    break

                item = json.loads(line)

                # Filter by subset if specified
                if self.subset and item.get("subset") != self.subset:
                    continue

                # Yield tuple in the order specified by columns
                yield (
                    item["input"],
                    item["expected_output"],
                    item["task_type"]
                )
                count += 1

    def _get_data_path(self, split: str) -> Path:
        """Get the path to the data file for the given split."""
        # This example assumes data is bundled with the package
        package_dir = Path(__file__).parent
        data_file = package_dir / "data" / f"{split}.jsonl"

        if not data_file.exists():
            raise FileNotFoundError(
                f"Data file not found: {data_file}. "
                f"Please ensure the dataset is properly installed."
            )

        return data_file

    def _count_rows(self) -> Optional[int]:
        """Count the number of rows in the dataset."""
        try:
            with open(self._data_path, 'r') as f:
                return sum(1 for _ in f)
        except:
            return None
```

## Step 3: Configure Package Metadata

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-eval-dataset"
version = "0.1.0"
description = "A custom evaluation dataset for doteval"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "doteval>=0.1.0",  # Adjust version as needed
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

# This is the key part - register your dataset as an entry point
[project.entry-points."doteval.datasets"]
my_eval = "my_eval_dataset.dataset:MyEvalDataset"

[project.urls]
Homepage = "https://github.com/yourusername/my-eval-dataset"
Repository = "https://github.com/yourusername/my-eval-dataset.git"
Issues = "https://github.com/yourusername/my-eval-dataset/issues"
```

## Step 4: Add Tests

Create `tests/test_dataset.py`:

```python
import pytest
from my_eval_dataset.dataset import MyEvalDataset


class TestMyEvalDataset:
    def test_dataset_attributes(self):
        """Test that the dataset has required attributes."""
        assert MyEvalDataset.name == "my_eval"
        assert MyEvalDataset.splits == ["train", "test", "validation"]
        assert MyEvalDataset.columns == ["input", "expected_output", "task_type"]

    def test_init_valid_split(self):
        """Test initialization with valid split."""
        dataset = MyEvalDataset(split="test")
        assert dataset.split == "test"

    def test_init_invalid_split(self):
        """Test initialization with invalid split."""
        with pytest.raises(ValueError, match="Invalid split 'invalid'"):
            MyEvalDataset(split="invalid")

    def test_iteration(self):
        """Test that dataset yields correct tuple structure."""
        dataset = MyEvalDataset(split="test", max_samples=5)
        items = list(dataset)

        assert len(items) <= 5
        if items:  # If dataset has data
            assert len(items[0]) == len(MyEvalDataset.columns)
            assert all(isinstance(item, tuple) for item in items)

    def test_max_samples(self):
        """Test that max_samples limits the dataset size."""
        dataset = MyEvalDataset(split="test", max_samples=3)
        items = list(dataset)
        assert len(items) <= 3

    def test_subset_filtering(self):
        """Test that subset filtering works correctly."""
        dataset = MyEvalDataset(split="test", subset="easy")
        # Items should only include those with subset="easy"
        # Implementation depends on your data format
```

## Step 5: Package Data Files

If your dataset includes data files, ensure they're included in the package. Create `src/my_eval_dataset/data/` and add your data files.

Update `pyproject.toml` to include data files:

```toml
[tool.setuptools.package-data]
my_eval_dataset = ["data/*.jsonl"]
```

## Step 6: Create Documentation

Create a comprehensive `README.md`:

```markdown
# My Eval Dataset

A custom evaluation dataset for testing model capabilities in [specific domain].

## Installation

```bash
pip install my-eval-dataset
```

## Usage

```python
from doteval import foreach
from doteval.evaluators import exact_match

@foreach.my_eval("test")
def evaluate_my_task(input, expected_output, task_type, model):
    result = model.generate(input, task_type=task_type)
    return exact_match(result, expected_output)
```

## Dataset Structure

The dataset contains the following columns:
- `input`: The input text/prompt for the model
- `expected_output`: The expected model output
- `task_type`: The type of task (e.g., "classification", "generation")

### Splits

- `train`: X samples for training/few-shot examples
- `test`: Y samples for evaluation
- `validation`: Z samples for development

### Subsets

Optional subsets available:
- `easy`: Simple examples
- `hard`: Challenging examples

## License

This dataset is released under [LICENSE].
```

## Step 7: Test Locally

Before publishing, test your dataset locally:

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Test integration with doteval
python -c "from doteval.datasets import list_available; print(list_available())"
```

## Step 8: Publish to PyPI

1. Build the package:
```bash
pip install build
python -m build
```

2. Upload to PyPI (or TestPyPI first):
```bash
pip install twine
twine upload dist/*
```

## Best Practices

### 1. Memory Efficiency

For large datasets, implement streaming:

```python
def __iter__(self) -> Iterator[Tuple]:
    # Don't load all data at once
    with open(self.data_file, 'r') as f:
        for line in f:
            yield self._process_line(line)
```

### 2. Remote Data Support

Support downloading data from remote sources:

```python
import requests
from pathlib import Path

def _download_data(self, url: str, dest: Path):
    """Download data if not present locally."""
    if not dest.exists():
        response = requests.get(url, stream=True)
        response.raise_for_status()

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
```

### 3. Caching

Cache processed data for faster subsequent loads:

```python
import pickle
from pathlib import Path

def _get_cached_data(self):
    cache_path = Path.home() / ".cache" / "my_eval" / f"{self.split}.pkl"

    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            return pickle.load(f)

    # Process and cache data
    data = self._process_raw_data()
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'wb') as f:
        pickle.dump(data, f)

    return data
```

### 4. Version Management

Include dataset version in your class:

```python
class MyEvalDataset(Dataset):
    name = "my_eval"
    version = "1.0.0"  # Semantic versioning
    splits = ["train", "test"]
    columns = ["input", "output"]
```

### 5. Validation

Add data validation in `__init__`:

```python
def __init__(self, split: str, **kwargs):
    # Validate split
    if split not in self.splits:
        raise ValueError(f"Invalid split: {split}")

    # Validate kwargs
    valid_kwargs = {"subset", "max_samples", "random_seed"}
    invalid = set(kwargs.keys()) - valid_kwargs
    if invalid:
        raise TypeError(f"Unexpected keyword arguments: {invalid}")
```

## Troubleshooting

### Dataset Not Found

If your dataset doesn't appear in `list_available()`:

1. Check the entry point name matches exactly
2. Ensure the package is installed (`pip list | grep my-eval`)
3. Try forcing rediscovery:
   ```python
   from doteval.datasets import _registry
   _registry.discover_plugins(force=True)
   ```

### Import Errors

If you get import errors when loading the dataset:

1. Check that all dependencies are installed
2. Ensure the module path in entry points is correct
3. Test the import directly:
   ```python
   from my_eval_dataset.dataset import MyEvalDataset
   ```

## Next Steps

- Add more sophisticated data preprocessing
- Implement data versioning
- Add download progress bars for remote data
- Create subset variants for different evaluation scenarios
- Add data statistics and analysis tools

## See Also

- [Dataset API Reference](../reference/datasets.md)
- [Using Datasets with @foreach](../reference/foreach.md)
- [Working with Real Datasets Tutorial](../tutorials/03-working-with-real-datasets.md)
