# Result Models and Scoring

How doteval structures evaluation outcomes and applies measurements across datasets.

## Result Architecture

```python
@dataclass
class Result:
    prompt: Optional[str]           # Input that produced this result
    scores: List[Score]             # Evaluation outcomes
    error: Optional[str] = None     # Error message if evaluation failed
    model_response: Optional[str] = None  # Raw model output
```

This structure captures everything needed for analysis and debugging.

## Score Design Philosophy

Scores separate **what happened** from **how we measure it**:

```python
@dataclass
class Score:
    name: str                    # Identifier for this evaluation aspect
    value: Any                   # The actual result (bool, float, dict, etc.)
    metrics: List[Metric]        # How to aggregate this across the dataset
    metadata: Dict[str, Any]     # Additional context for debugging
```

### Why This Design?

**Flexibility**: The same evaluation can be measured multiple ways:

```python
# Single evaluation, multiple metrics
def semantic_similarity(text1, text2):
    similarity = compute_similarity(text1, text2)
    return Score(
        name="semantic_sim",
        value=similarity,
        metrics=[accuracy(), mean(), std_dev()]  # Different aggregations
    )
```

**Debuggability**: Metadata preserves evaluation context:

```python
score = exact_match("hello", "hello", name="greeting_test")
# score.metadata = {"result": "hello", "expected": "hello"}
```

**Composability**: Multiple scores per result:

```python
return Result(
    exact_match(prediction, expected, name="exact"),
    fuzzy_match(prediction, expected, name="fuzzy"),
    prompt=input_text
)
```

## The Evaluator Pattern

Evaluators transform functions into reusable, composable evaluation components:

```python
@evaluator(metrics=accuracy())
def exact_match(result, expected) -> bool:
    return result == expected

# Usage creates Score objects automatically
score = exact_match("hello", "world")
# Returns: Score(name="exact_match", value=False, metrics=[accuracy()])
```

### Why Decorators?

**Automatic Score Creation**: No manual Score object construction

**Metadata Extraction**: Function parameters become metadata automatically

**Reusability**: Same evaluator works across different contexts

```python
# Built-in evaluators handle common cases
@evaluator(metrics=accuracy())
def numeric_match(result, expected) -> bool:
    # Handles "1,234" == "1234", scientific notation, etc.

@evaluator(metrics=accuracy())
def valid_json(result, schema=None) -> bool:
    # JSON validation with optional schema checking
```

## Aggregation Philosophy

Results aggregate through a two-phase process:

### Phase 1: Score Collection

```python
# Each evaluation produces Record objects
Record(
    result=Result(...),
    item_id=42,
    dataset_row={"text": "input", "expected": "output"},
    error=None,
    timestamp=time.time()
)
```

### Phase 2: Metric Application

```python
# EvaluationSummary aggregates by evaluator and metric
summary = EvaluationSummary(all_records)

# Produces structure like:
{
    "exact_match": {
        "accuracy": 0.85,
        "count": 1000
    },
    "fuzzy_match": {
        "accuracy": 0.92,
        "count": 1000
    }
}
```

This design separates data collection from analysis, enabling multiple analysis perspectives on the same evaluation run.

## Error Handling

The Result model gracefully handles evaluation failures:

```python
# Successful evaluation
return Result(
    exact_match(prediction, expected),
    prompt=input_text,
    model_response=raw_output
)

# Failed evaluation
return Result(
    prompt=input_text,
    error="API timeout after 30 seconds"
)
```

Errors are tracked and included in summary statistics, providing visibility into evaluation reliability.

## Practical Examples

### Simple Boolean Evaluation

```python
@foreach("question,answer", qa_dataset)
def eval_qa_accuracy(question, answer):
    response = model.generate(question)
    return Result(
        exact_match(response.strip(), answer),
        prompt=question,
        model_response=response
    )
```

### Multi-Metric Evaluation

```python
@foreach("text,sentiment", sentiment_dataset)
def eval_sentiment_analysis(text, sentiment):
    prediction = model.classify_sentiment(text)
    confidence = model.get_confidence()

    return Result(
        exact_match(prediction, sentiment, name="accuracy"),
        Score("confidence", confidence, metrics=[mean(), std_dev()]),
        prompt=text,
        model_response=f"{prediction} (confidence: {confidence})"
    )
```

### Complex Structured Evaluation

```python
@foreach("instruction,expected_json", code_dataset)
def eval_code_generation(instruction, expected_json):
    generated_code = model.generate_code(instruction)

    try:
        result = execute_code(generated_code)
        parsed_expected = json.loads(expected_json)

        return Result(
            exact_match(result, parsed_expected, name="output_match"),
            valid_json(generated_code, name="syntax_valid"),
            Score("execution_time", result.execution_time, metrics=[mean()]),
            prompt=instruction,
            model_response=generated_code
        )
    except Exception as e:
        return Result(
            prompt=instruction,
            model_response=generated_code,
            error=str(e)
        )
```

This flexible model supports everything from simple accuracy measurements to complex, multi-dimensional evaluation scenarios.
