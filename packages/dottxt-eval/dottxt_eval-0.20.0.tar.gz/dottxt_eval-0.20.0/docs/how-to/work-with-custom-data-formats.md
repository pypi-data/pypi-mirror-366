# How to Work with Custom Data Formats

Most real-world datasets don't come in the simple list format shown in tutorials. This guide shows you how to work with CSV files, JSONL, databases, APIs, and other data sources in your evaluations.

## Problem: Real Data Isn't in Tutorial Format

Tutorials show simple data structures:

```python
# ❌ Tutorial format - not how real data looks
simple_data = [
    ("What is 2+2?", "4"),
    ("What is 3+3?", "6"),
]
```

But your data is in CSV files, databases, APIs, or complex nested structures.

## Solution 1: Working with CSV Files

Transform CSV data into evaluation format:

```python
import csv
import pandas as pd
from doteval import foreach, Result
from typing import Generator, Tuple

# Option 1: Using csv module (memory efficient for large files)
def csv_dataset(filepath: str) -> Generator[Tuple[str, str], None, None]:
    """Stream CSV data row by row."""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Transform your CSV columns to evaluation format
            prompt = row['question']  # Adjust column names as needed
            expected = row['answer']
            yield (prompt, expected)

# Option 2: Using pandas (easier for complex transformations)
def pandas_csv_dataset(filepath: str) -> Generator[Tuple[str, str], None, None]:
    """Load CSV with pandas and yield rows."""
    df = pd.read_csv(filepath)

    # Clean and transform data
    df = df.dropna(subset=['question', 'answer'])  # Remove rows with missing data
    df['question'] = df['question'].str.strip()   # Clean whitespace
    df['answer'] = df['answer'].str.strip()

    for _, row in df.iterrows():
        yield (row['question'], row['answer'])

@foreach("question,answer", csv_dataset("data/my_dataset.csv"))
def eval_csv_data(question, answer, model):
    """Evaluate data from CSV file."""
    response = model.generate(question)
    return exact_match(response, answer)

# For very large CSV files, use chunking
def chunked_csv_dataset(filepath: str, chunk_size: int = 1000) -> Generator[Tuple[str, str], None, None]:
    """Process large CSV files in chunks."""
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        chunk = chunk.dropna(subset=['question', 'answer'])
        for _, row in chunk.iterrows():
            yield (row['question'], row['answer'])
```

## Solution 2: Working with JSONL Files

Handle JSON Lines format (one JSON object per line):

```python
import json
from typing import Dict, Any

def jsonl_dataset(filepath: str) -> Generator[Tuple[str, str], None, None]:
    """Load JSONL file line by line."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())

                # Extract fields from your JSON structure
                prompt = data['prompt']  # Adjust field names as needed
                expected = data['expected']

                yield (prompt, expected)

            except json.JSONDecodeError as e:
                print(f"Skipping invalid JSON on line {line_num}: {e}")
                continue
            except KeyError as e:
                print(f"Missing field on line {line_num}: {e}")
                continue

# For complex JSON structures
def complex_jsonl_dataset(filepath: str) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """Handle complex JSONL with nested data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())

            # Build prompt from multiple fields
            prompt = f"Context: {data['context']}\nQuestion: {data['question']}"

            # Keep full expected data for complex evaluation
            expected = {
                'answer': data['answer'],
                'reasoning': data.get('reasoning', ''),
                'category': data.get('category', 'general')
            }

            yield (prompt, expected)

@foreach("prompt,expected", complex_jsonl_dataset("data/complex.jsonl"))
def eval_complex_jsonl(prompt, expected, model):
    """Evaluate complex JSONL data."""
    response = model.generate(prompt)

    # Use the additional context for evaluation
    basic_score = exact_match(response, expected['answer'])
    category_bonus = 1.1 if expected['category'] == 'math' else 1.0

    return Result(
        basic_score,
        prompt=prompt,
        response=response,
        scores={
            "basic_accuracy": basic_score,
            "category": expected['category'],
            "weighted_score": basic_score * category_bonus
        }
    )
```

## Solution 3: Working with Databases

Connect to databases and stream evaluation data:

```python
import sqlite3
import psycopg2
from typing import Iterator

def sqlite_dataset(db_path: str, query: str) -> Generator[Tuple[str, str], None, None]:
    """Load data from SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        for row in cursor.fetchall():
            # Assumes query returns (prompt, expected) columns
            yield (row[0], row[1])

    finally:
        conn.close()

def postgres_dataset(connection_params: dict, query: str) -> Generator[Tuple[str, str], None, None]:
    """Load data from PostgreSQL database."""
    conn = psycopg2.connect(**connection_params)
    cursor = conn.cursor()

    try:
        cursor.execute(query)

        # Use server-side cursor for large datasets
        while True:
            rows = cursor.fetchmany(1000)  # Fetch in batches
            if not rows:
                break

            for row in rows:
                yield (row[0], row[1])

    finally:
        conn.close()

# Example usage
database_config = {
    'host': 'localhost',
    'database': 'evaluations',
    'user': 'eval_user',
    'password': 'password'
}

query = """
SELECT
    question_text,
    correct_answer
FROM evaluation_data
WHERE dataset_name = 'math_problems'
    AND difficulty = 'medium'
ORDER BY id
"""

@foreach("question,answer", postgres_dataset(database_config, query))
def eval_database_data(question, answer, model):
    """Evaluate data from database."""
    response = model.generate(question)
    return exact_match(response, answer)
```

## Solution 4: Working with APIs

Fetch evaluation data from REST APIs:

```python
import requests
from typing import List, Dict
import time

def api_dataset(api_url: str, headers: dict = None, params: dict = None) -> Generator[Tuple[str, str], None, None]:
    """Fetch data from REST API with pagination."""
    page = 1
    per_page = 100

    while True:
        # Build request parameters
        request_params = {'page': page, 'per_page': per_page}
        if params:
            request_params.update(params)

        try:
            response = requests.get(api_url, headers=headers, params=request_params)
            response.raise_for_status()

            data = response.json()

            # Handle different API response formats
            items = data.get('data', data.get('items', data))

            if not items:  # No more data
                break

            for item in items:
                prompt = item['question']
                expected = item['answer']
                yield (prompt, expected)

            page += 1

            # Be respectful to APIs
            time.sleep(0.1)

        except requests.RequestException as e:
            print(f"API request failed: {e}")
            break

# For APIs requiring authentication
def authenticated_api_dataset(api_url: str, api_key: str) -> Generator[Tuple[str, str], None, None]:
    """Fetch data from authenticated API."""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    yield from api_dataset(api_url, headers=headers)

# For GraphQL APIs
def graphql_dataset(graphql_url: str, query: str, variables: dict = None) -> Generator[Tuple[str, str], None, None]:
    """Fetch data from GraphQL API."""
    headers = {'Content-Type': 'application/json'}

    payload = {
        'query': query,
        'variables': variables or {}
    }

    response = requests.post(graphql_url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()

    for item in data['data']['evaluationQuestions']:
        yield (item['text'], item['expectedAnswer'])
```

## Solution 5: Working with Hugging Face Datasets

Integrate with the Hugging Face datasets library:

```python
from datasets import load_dataset, Dataset
from typing import Union

def huggingface_dataset(dataset_name: str, split: str = 'test', streaming: bool = True) -> Generator[Tuple[str, str], None, None]:
    """Load data from Hugging Face datasets."""
    dataset = load_dataset(dataset_name, split=split, streaming=streaming)

    for item in dataset:
        # Transform HF dataset format to evaluation format
        # This depends on the specific dataset structure
        if dataset_name == 'gsm8k':
            question = item['question']
            # Extract answer from solution format
            answer = item['answer'].split('#### ')[-1]
            yield (question, answer)

        elif dataset_name == 'squad':
            context = item['context']
            question = item['question']
            prompt = f"Context: {context}\nQuestion: {question}"
            answer = item['answers']['text'][0] if item['answers']['text'] else ""
            yield (prompt, answer)

        else:
            # Generic handling
            yield (str(item.get('input', item.get('question', ''))),
                   str(item.get('output', item.get('answer', ''))))

def custom_huggingface_transform(dataset_name: str, transform_func) -> Generator[Tuple[str, str], None, None]:
    """Apply custom transformation to HF dataset."""
    dataset = load_dataset(dataset_name, split='test', streaming=True)

    for item in dataset:
        prompt, expected = transform_func(item)
        yield (prompt, expected)

# Example custom transform
def gsm8k_transform(item):
    """Custom transform for GSM8K dataset."""
    question = item['question']

    # Extract numerical answer from step-by-step solution
    solution = item['answer']
    answer_match = re.search(r'#### (\d+(?:\.\d+)?)', solution)
    answer = answer_match.group(1) if answer_match else ""

    return question, answer

@foreach("question,answer", custom_huggingface_transform('gsm8k', gsm8k_transform))
def eval_gsm8k(question, answer, model):
    """Evaluate GSM8K with custom transform."""
    response = model.generate(f"Solve: {question}")
    return exact_match(extract_number(response), answer)
```

## Solution 6: Working with Nested/Complex Data

Handle complex nested structures:

```python
import json
from typing import Any, Dict, List

def nested_json_dataset(filepath: str) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """Handle complex nested JSON data."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Navigate nested structure
    for category in data['evaluation_sets']:
        for subcategory in category['subcategories']:
            for item in subcategory['questions']:

                # Build comprehensive prompt
                prompt = f"""
Category: {category['name']}
Subcategory: {subcategory['name']}
Difficulty: {item['difficulty']}

Question: {item['question']}
"""

                # Keep full context for evaluation
                expected = {
                    'answer': item['answer'],
                    'explanation': item.get('explanation', ''),
                    'category': category['name'],
                    'difficulty': item['difficulty'],
                    'scoring_rubric': item.get('rubric', {})
                }

                yield (prompt.strip(), expected)

@foreach("prompt,expected", nested_json_dataset("data/complex_eval.json"))
def eval_nested_data(prompt, expected, model):
    """Evaluate with complex nested data context."""
    response = model.generate(prompt)

    # Use rubric for sophisticated scoring
    rubric = expected['scoring_rubric']
    base_score = exact_match(response, expected['answer'])

    # Apply difficulty multiplier
    difficulty_multiplier = {
        'easy': 1.0,
        'medium': 1.2,
        'hard': 1.5
    }.get(expected['difficulty'], 1.0)

    return Result(
        base_score,
        prompt=prompt,
        response=response,
        scores={
            "base_accuracy": base_score,
            "category": expected['category'],
            "difficulty": expected['difficulty'],
            "weighted_score": base_score * difficulty_multiplier
        }
    )
```

## Solution 7: Combining Multiple Data Sources

Merge data from different sources:

```python
from itertools import chain
from typing import Iterator

def combined_dataset(*datasets) -> Generator[Tuple[str, str], None, None]:
    """Combine multiple data sources."""
    for dataset in datasets:
        yield from dataset

# Example: Combine CSV, API, and HF data
combined_data = combined_dataset(
    csv_dataset("data/custom.csv"),
    api_dataset("https://api.example.com/questions"),
    huggingface_dataset("gsm8k")
)

@foreach("question,answer", combined_data)
def eval_combined_sources(question, answer, model):
    """Evaluate data from multiple sources."""
    response = model.generate(question)
    return exact_match(response, answer)

# Weighted combination with source tracking
def weighted_combined_dataset() -> Generator[Tuple[str, str, str], None, None]:
    """Combine datasets with source tracking."""

    # Add source labels
    for prompt, expected in csv_dataset("data/custom.csv"):
        yield (prompt, expected, "custom")

    for prompt, expected in api_dataset("https://api.example.com/questions"):
        yield (prompt, expected, "api")

    for prompt, expected in huggingface_dataset("gsm8k"):
        yield (prompt, expected, "gsm8k")

@foreach("question,answer,source", weighted_combined_dataset())
def eval_with_source_tracking(question, answer, source, model):
    """Evaluate with source-specific handling."""

    # Adjust prompt based on source
    if source == "gsm8k":
        prompt = f"Solve this math problem step by step: {question}"
    else:
        prompt = question

    response = model.generate(prompt)
    score = exact_match(response, answer)

    return Result(
        score,
        prompt=prompt,
        response=response,
        scores={
            "accuracy": score,
            "source": source,
            "source_weight": 1.5 if source == "custom" else 1.0
        }
    )
```

## Solution 8: Data Validation and Cleaning

Ensure data quality before evaluation:

```python
import re
from typing import Optional

def validate_and_clean_dataset(raw_dataset) -> Generator[Tuple[str, str], None, None]:
    """Validate and clean dataset entries."""

    for prompt, expected in raw_dataset:
        # Skip invalid entries
        if not prompt or not expected:
            continue

        if len(prompt.strip()) < 10:  # Too short to be meaningful
            continue

        if len(expected.strip()) < 1:  # No expected answer
            continue

        # Clean the data
        clean_prompt = clean_text(prompt)
        clean_expected = clean_text(expected)

        # Validate cleaned data
        if clean_prompt and clean_expected:
            yield (clean_prompt, clean_expected)

def clean_text(text: str) -> Optional[str]:
    """Clean and normalize text."""
    if not text:
        return None

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove or fix common encoding issues
    text = text.replace('\u00a0', ' ')  # Non-breaking space
    text = text.replace('\u2019', "'")  # Smart quote
    text = text.replace('\u201c', '"')  # Smart quote
    text = text.replace('\u201d', '"')  # Smart quote

    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize numbers
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# Example usage
raw_csv_data = csv_dataset("data/messy_data.csv")
clean_data = validate_and_clean_dataset(raw_csv_data)

@foreach("question,answer", clean_data)
def eval_clean_data(question, answer, model):
    """Evaluate cleaned dataset."""
    response = model.generate(question)
    return exact_match(response, answer)
```

## Performance Tips for Large Datasets

1. **Use generators** instead of loading everything into memory
2. **Stream data** rather than loading full files
3. **Process in chunks** for very large datasets
4. **Cache transformed data** if you'll use it multiple times
5. **Use database indexes** for complex queries
6. **Add progress indicators** for long-running data loading

```python
from tqdm import tqdm

def progress_dataset(dataset, description="Loading data"):
    """Add progress bar to dataset loading."""
    for item in tqdm(dataset, desc=description):
        yield item

@foreach("question,answer", progress_dataset(large_csv_dataset("huge_file.csv")))
def eval_with_progress(question, answer, model):
    response = model.generate(question)
    return exact_match(response, answer)
```

## Common Data Format Patterns

```python
# Pattern 1: Key-value extraction
def extract_qa_pairs(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, dict) and 'question' in value and 'answer' in value:
            yield (value['question'], value['answer'])

# Pattern 2: Flattening nested lists
def flatten_nested_qa(nested_list):
    for category in nested_list:
        for item in category.get('items', []):
            yield (item['q'], item['a'])

# Pattern 3: Multi-column to single prompt
def combine_columns(row):
    prompt = f"Context: {row['context']}\nInput: {row['input']}\nTask: {row['task']}"
    return prompt, row['expected_output']
```

The key is to transform your data format into the `(prompt, expected)` tuple format that doteval expects, while preserving important metadata for evaluation.

## See Also

- **[Tutorial 3: Working with Real Datasets](../tutorials/03-working-with-real-datasets.md)** - Learn to work with Hugging Face and other dataset sources
- **[How to Evaluate Structured Generation](evaluate-structured-generation.md)** - Handle complex nested outputs from your custom data
- **[Reference: Data Handling](../reference/datasets.md)** - Technical details on dataset integration
- **[Tutorial 1: Your First Evaluation](../tutorials/01-your-first-evaluation.md)** - Start with simple data formats before moving to complex ones
- **[How to Debug Slow Evaluations](debug-slow-evaluations.md)** - Optimize data loading for large datasets
