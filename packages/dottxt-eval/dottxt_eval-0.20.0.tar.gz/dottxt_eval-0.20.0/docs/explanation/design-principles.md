# Design Principles

The philosophical foundations that guide doteval's approach to LLM evaluation.

## Simplicity Over Complexity

doteval is built on the principle that **evaluation should be as simple as writing a test**. This guides every design decision:

**Write evaluations like tests:**
```python
@foreach("text,expected", dataset)
def eval_sentiment(text, expected):
    prediction = model.classify(text)
    return Result(exact_match(prediction, expected), prompt=text)
```

Rather than complex evaluation frameworks with custom DSLs or configuration files, doteval leverages familiar testing patterns that developers already understand.

## Composability Through Small Pieces

Each component in doteval serves a single, well-defined purpose:

- **Result objects** encapsulate individual evaluation outcomes
- **Score objects** represent specific metrics applied to outcomes
- **Evaluators** are pure functions that compute boolean or numeric results
- **Metrics** aggregate scores across multiple evaluations

This modular design enables flexible composition without tight coupling.

## Immediate Feedback Over Batch Processing

doteval prioritizes fast feedback loops:

```python
# Start seeing results immediately
pytest eval_tests.py -v

# Resume from failures without re-running successes
pytest eval_tests.py --experiment continued_run
```

Results are stored as they're computed, enabling interruption and resumption without data loss.

## Transparency Over Magic

Every step of the evaluation process is explicit and inspectable:

- **Clear data flow**: Dataset → Evaluation Function → Result → Storage
- **Visible progress**: Real-time progress bars and result streaming
- **Debuggable execution**: Standard Python debugging tools work naturally
- **Explicit configuration**: No hidden defaults or implicit behaviors

## Separation of Concerns

doteval maintains clear boundaries between different responsibilities:

- **Evaluation logic** is separate from **execution orchestration**
- **Data models** are separate from **storage backends**
- **Testing framework** is separate from **model deployment**
- **Result collection** is separate from **metric computation**

This separation enables each component to evolve independently while maintaining system coherence.
