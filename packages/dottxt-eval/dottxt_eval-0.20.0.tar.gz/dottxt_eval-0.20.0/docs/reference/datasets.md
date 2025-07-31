# Data Handling

doteval provides flexible data handling capabilities for various dataset formats and sources.

## Streaming-First Architecture

**doteval is streaming-first** - it processes datasets one item at a time without loading everything into memory. This means you can evaluate on datasets that don't fit in memory, including:

- Multi-gigabyte datasets streamed from disk
- Live data from APIs or databases
- Infinite generators that produce data on-demand
- Large HuggingFace datasets with streaming enabled

## Overview

doteval supports:

- Multiple dataset formats (lists, tuples, iterators, generators)
- Built-in registered datasets with `@foreach.dataset_name()` syntax
- HuggingFace Datasets integration with streaming
- Custom column mappings

## Basic Dataset Formats

### Lists and Tuples

```python
import doteval
from doteval.evaluators import exact_match

# Simple question-answer pairs
dataset = [
    ("What is 2+2?", "4"),
    ("What is 3+3?", "6")
]

@doteval.foreach("question,answer", dataset)
def eval_simple(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)
```

### Single Column Datasets

```python
prompts = [("Write a poem",), ("Explain gravity",)]

@doteval.foreach("prompt", prompts)
def eval_single_column(prompt, model):
    result = model.generate(prompt)
    return quality_score(result)
```

### Multi-Column Datasets

```python
dataset = [
    ("context1", "question1", "answer1"),
    ("context2", "question2", "answer2")
]

@doteval.foreach("context,question,answer", dataset)
def eval_multi_column(context, question, answer, model):
    prompt = f"Context: {context}\nQuestion: {question}"
    result = model.generate(prompt)
    return exact_match(result, answer)
```

## Registered Datasets

doteval includes built-in support for popular evaluation datasets using the `@foreach.dataset_name()` syntax.

### GSM8K Dataset

Grade school math problems with step-by-step reasoning.

**Columns**: `question`, `reasoning`, `answer`
**Splits**: `train`, `test`

```python
from doteval import foreach
from doteval.evaluators import numeric_match

@foreach.gsm8k("test")
def eval_gsm8k(question, reasoning, answer, model):
    response = model.solve(question)
    return numeric_match(response, answer)
```

#### GSM8K Parameters

```python
@foreach.gsm8k(split: str)
```
**Parameters:**
- `split` (str): Dataset split to use. Must be one of: `"train"`, `"test"`

### BFCL Dataset

Berkeley Function Calling Leaderboard dataset for evaluating function calling capabilities.

**Columns**: `question`, `schema`, `answer`
**Variants**: `simple`, `multiple`, `parallel`

```python
from doteval import foreach
from doteval.evaluators import exact_match
import json

@foreach.bfcl("simple")
def eval_bfcl(question, schema, answer, model):
    available_functions = json.loads(schema)
    response = model.generate_function_call(question, functions=available_functions)
    expected_calls = json.loads(answer)
    return exact_match(response, expected_calls)
```

#### BFCL Parameters

```python
@foreach.bfcl(variant: str = "simple")
```
**Parameters:**
- `variant` (str, default="simple"): BFCL variant to use. Must be one of: `"simple"`, `"multiple"`, `"parallel"`
  - `"simple"`: Single function calls
  - `"multiple"`: Multiple sequential function calls
  - `"parallel"`: Multiple parallel function calls

### SROIE Dataset

Scanned Receipts OCR and Information Extraction dataset for testing information extraction from receipt images.

**Columns**: `images`, `address`, `company`, `date`, `total`

```python
from doteval import foreach
from doteval.evaluators import exact_match, valid_json
import json

@foreach.sroie()
def eval_sroie(images, address, company, date, total, multimodal_model):
    prompt = "Extract company, date, address, and total as JSON."
    response = multimodal_model.generate(prompt, image=images)

    if not valid_json(response):
        return Score(value=0.0, passed=False)

    # Compare extracted info with ground truth
    extracted = json.loads(response)
    expected = {
        "company": company,
        "date": date,
        "address": address,
        "total": total
    }
    return exact_match(extracted, expected)
```

#### SROIE Parameters

```python
@foreach.sroie(split: str = "test")
```
**Parameters:**
- `split` (str, default="test"): Dataset split to use. Must be one of: `"train"`, `"test"`

### Available Registered Datasets

- **gsm8k**: Grade school math problems
  - Columns: `question`, `reasoning`, `answer`
  - Splits: `train`, `test`
- **bfcl**: Berkeley Function Calling Leaderboard
  - Columns: `question`, `schema`, `answer`
  - Variants: `simple`, `multiple`, `parallel`
- **sroie**: Receipt information extraction
  - Columns: `images`, `address`, `company`, `date`, `total`
  - Splits: `train`, `test`

### Dataset Discovery

```python
from doteval.datasets import list_available, get_dataset_info

# List all registered datasets
available_datasets = list_available()
print(available_datasets)  # ['bfcl', 'gsm8k', 'sroie']

# Get dataset information
info = get_dataset_info('gsm8k')
print(f"Columns: {info['columns']}")  # ['question', 'reasoning', 'answer']
print(f"Splits: {info['splits']}")    # ['train', 'test']
```

#### Dataset Discovery Functions

```python
def list_available() -> list[str]
```
**Returns:** List of all registered dataset names that can be used with `@foreach.dataset_name()` syntax.

```python
def get_dataset_info(name: str) -> dict
```
**Parameters:**
- `name` (str): Name of the registered dataset to get information about

**Returns:** Dictionary containing:
- `name` (str): Dataset name
- `splits` (list[str]): Available splits for the dataset (e.g., ['train', 'test'])
- `columns` (list[str]): Column names that will be passed to evaluation functions
- `num_rows` (int or None): Total number of rows if determinable, None for streaming datasets

## Dataset Plugin System

doteval uses a plugin-based architecture for datasets, allowing third-party packages to provide custom datasets that integrate seamlessly with the `@foreach` decorator. This system enables:

- Dynamic dataset discovery without modifying doteval core
- Easy distribution of custom datasets as separate packages
- Lazy loading of dataset implementations
- Standardized dataset interface through the Dataset ABC

### How the Plugin System Works

1. **Entry Points**: Datasets are registered via Python entry points in the `"doteval.datasets"` group
2. **Discovery**: The DatasetRegistry automatically discovers installed plugins when needed
3. **Loading**: Dataset classes are loaded only when first accessed
4. **Registration**: Once loaded, datasets are available via `@foreach.dataset_name()` syntax

### Creating Custom Dataset Plugins

To create a custom dataset plugin, you need to:

1. Implement the `Dataset` abstract base class
2. Register your dataset via entry points in your package

#### Step 1: Implement the Dataset Class

```python
from doteval.datasets import Dataset
from typing import Iterator, Tuple

class MyCustomDataset(Dataset):
    """Custom dataset for my specific use case."""

    name = "my_dataset"
    splits = ["train", "validation", "test"]
    columns = ["input", "expected_output", "metadata"]

    def __init__(self, split: str, **kwargs):
        if split not in self.splits:
            raise ValueError(f"Invalid split: {split}. Must be one of {self.splits}")

        self.split = split
        self.data = self._load_data(split, **kwargs)
        self.num_rows = len(self.data)

    def __iter__(self) -> Iterator[Tuple]:
        for item in self.data:
            yield (
                item["input"],
                item["expected_output"],
                item["metadata"]
            )

    def _load_data(self, split: str, **kwargs):
        # Your data loading logic here
        # This could load from files, APIs, databases, etc.
        pass
```

#### Step 2: Register via Entry Points

In your package's `pyproject.toml`:

```toml
[project.entry-points."doteval.datasets"]
my_dataset = "my_package.datasets:MyCustomDataset"
```

Or if using `setup.py`:

```python
setup(
    name="my-dataset-plugin",
    # ... other setup parameters ...
    entry_points={
        "doteval.datasets": [
            "my_dataset = my_package.datasets:MyCustomDataset",
        ],
    },
)
```

#### Step 3: Use Your Dataset

Once installed, your dataset is automatically available:

```python
from doteval import foreach

@foreach.my_dataset("test")
def evaluate_my_dataset(input, expected_output, metadata, model):
    result = model.process(input, context=metadata)
    return compare_outputs(result, expected_output)
```

### Best Practices for Dataset Plugins

1. **Streaming Support**: For large datasets, implement streaming to avoid loading everything into memory:

```python
def __iter__(self) -> Iterator[Tuple]:
    # Stream from file instead of loading all at once
    with open(self.file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            yield (data["input"], data["output"])
```

2. **Lazy Loading**: Load data only when iteration begins:

```python
def __init__(self, split: str, **kwargs):
    self.split = split
    self.config = kwargs
    # Don't load data here

def __iter__(self) -> Iterator[Tuple]:
    # Load data when iteration starts
    data = self._load_data(self.split, **self.config)
    for item in data:
        yield self._process_item(item)
```

3. **Configuration Options**: Accept keyword arguments for flexibility:

```python
def __init__(self, split: str, subset: str = "default", max_samples: int = None):
    self.split = split
    self.subset = subset
    self.max_samples = max_samples
```

4. **Error Handling**: Provide clear error messages:

```python
def __init__(self, split: str, **kwargs):
    if split not in self.splits:
        raise ValueError(
            f"Invalid split '{split}'. "
            f"Available splits: {', '.join(self.splits)}"
        )
```

### Publishing Dataset Plugins

To publish your dataset plugin:

1. Package your dataset implementation
2. Include proper entry points in your package configuration
3. Publish to PyPI or your preferred package index
4. Users can install with: `pip install your-dataset-plugin`

Example package structure:
```
my-dataset-plugin/
├── pyproject.toml
├── README.md
├── src/
│   └── my_dataset_plugin/
│       ├── __init__.py
│       └── datasets.py
└── tests/
    └── test_dataset.py
```

### Testing Dataset Plugins

```python
import pytest
from my_dataset_plugin.datasets import MyCustomDataset

def test_dataset_attributes():
    assert MyCustomDataset.name == "my_dataset"
    assert MyCustomDataset.splits == ["train", "validation", "test"]
    assert MyCustomDataset.columns == ["input", "expected_output", "metadata"]

def test_dataset_iteration():
    dataset = MyCustomDataset(split="test")
    items = list(dataset)

    assert len(items) > 0
    assert len(items[0]) == len(MyCustomDataset.columns)

def test_invalid_split():
    with pytest.raises(ValueError, match="Invalid split"):
        MyCustomDataset(split="invalid")
```

For a detailed step-by-step guide on creating dataset plugins, see [How to Create a Dataset Plugin](../how-to/create-dataset-plugin.md).

## HuggingFace Datasets Integration

Install the `datasets` library for HuggingFace integration:

```bash
pip install datasets
```

### Loading Datasets

```python
import datasets
import itertools

def load_hf_dataset(dataset_name: str, split: str, limit: int = None):
    dataset = datasets.load_dataset(dataset_name, split=split, streaming=True)
    samples = ((sample["input"], sample["output"]) for sample in dataset)

    if limit:
        samples = itertools.islice(samples, limit)

    return samples

@doteval.foreach("input,output", load_hf_dataset("my_dataset", "test", 100))
def eval_hf_dataset(input_text, output, model):
    result = model.generate(input_text)
    return exact_match(result, output)
```

#### HuggingFace Dataset Loading Function

```python
def load_hf_dataset(
    dataset_name: str,
    split: str,
    limit: int = None,
    **kwargs
) -> Iterator[Tuple]
```

**Parameters:**
- `dataset_name` (str): Name of the HuggingFace dataset to load (e.g., `"squad"`, `"glue"`)
- `split` (str): Dataset split to use (e.g., `"train"`, `"test"`, `"validation"`)
- `limit` (int, optional): Maximum number of samples to load. If None, loads entire dataset
- `**kwargs`: Additional arguments passed to `datasets.load_dataset()`

**Returns:** Iterator yielding tuples of dataset samples for use with `@foreach`

**Note:** Always use `streaming=True` to enable memory-efficient processing of large datasets.

## Generators and Streaming

### Generator Functions

```python
def generate_dataset(count: int):
    for i in range(count):
        yield (f"Question {i}", f"Answer {i}")

@doteval.foreach("question,answer", generate_dataset(1000))
def eval_generated(question, answer, model):
    result = model.generate(question)
    return exact_match(result, answer)
```

### File Streaming

```python
def stream_from_file(file_path: str):
    import csv
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield (row["input"], row["expected"])

@doteval.foreach("input,expected", stream_from_file("dataset.csv"))
def eval_streamed(input_text, expected, model):
    result = model.generate(input_text)
    return exact_match(result, expected)
```

## Column Specification

Column names in the `@foreach` decorator must match the dataset structure:

```python
# Dataset: (context, question, answer)
dataset = [
    ("The sky is blue.", "What color is the sky?", "blue"),
    ("E=mc²", "What is Einstein's equation?", "E=mc²")
]

@doteval.foreach("context,question,answer", dataset)
def eval_with_context(context, question, answer, model):
    prompt = f"Context: {context}\nQuestion: {question}"
    result = model.generate(prompt)
    return exact_match(result, answer)
```

## Dataset Iterator Requirements

Any dataset provided to `@foreach` must satisfy these requirements:

### Iterator Protocol
```python
def custom_dataset() -> Iterator[Tuple]:
    """Custom dataset generator function"""
    pass
```

**Requirements:**
- Must implement the iterator protocol (`__iter__` and `__next__`)
- Each iteration must yield a tuple with consistent structure
- Tuple length must match the number of columns specified in `@foreach`
- Can be finite (list, tuple) or infinite (generator, stream)

### Tuple Structure
```python
# Single column: each item is a 1-tuple
dataset = [("prompt1",), ("prompt2",)]

# Multiple columns: each item is an n-tuple
dataset = [("input1", "output1"), ("input2", "output2")]

# Dict-like access (convert to tuple)
def dict_to_tuple_dataset(dict_dataset):
    for item in dict_dataset:
        yield (item["input"], item["output"])
```

**Requirements:**
- All tuples must have the same length within a dataset
- Tuple order must match the column order in `@foreach("col1,col2,col3", dataset)`
- Values can be any Python object (strings, images, complex structures)


## See Also

### Core Concepts
- **[@foreach Decorator](foreach.md)** - Master column specifications and dataset integration with `@foreach`
- **[Evaluators](evaluators.md)** - Apply data validation patterns and preprocessing for robust evaluations

### Integration Guides
- **[Experiments](experiments.md)** - Understand how dataset processing integrates with experiment management
- **[Async Evaluations](async.md)** - Process large datasets efficiently with async evaluation patterns

### Advanced Usage
- **[Storage Backends](storage.md)** - Optimize storage for different dataset sizes and formats
- **[Pytest Integration](pytest.md)** - Use pytest fixtures for dataset loading and management

### Tutorials
- **[Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Get started with simple dataset formats
- **[Working with Real Datasets](../tutorials/03-working-with-real-datasets.md)** - Load and process real-world datasets effectively
- **[Build a Production Evaluation Pipeline](../tutorials/09-build-production-evaluation-pipeline.md)** - Design robust data pipelines for production systems
