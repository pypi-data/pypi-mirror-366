# Tutorial 4: Build Custom Evaluators

In this tutorial, you'll build a custom LLM judge evaluator that scores creative writing on multiple criteria.

## What you'll learn

- How to create custom evaluators with `@evaluator`
- How to design effective LLM judge prompts
- How to parse and structure LLM responses
- How to return multi-metric evaluation results
- How to iterate and improve evaluator reliability

## Step 1: Understanding Prompt Engineering Principles

Before creating LLM judges, let's understand the key principles of effective prompt engineering.

### Core Prompt Design Principles

**1. Be Specific and Clear**
```python
# ❌ Vague prompt
"Rate this story."

# ✅ Specific prompt
"Rate this creative writing story on a scale of 1-10 for creativity, coherence, and grammar."
```

**2. Provide Structure and Format**
```python
# ❌ Unstructured output
"Tell me what you think about this story."

# ✅ Structured output
"Provide ratings in this exact format:
creativity: [score], coherence: [score], grammar: [score]"
```

**3. Include Examples**
```python
# ❌ No examples
"Rate the story."

# ✅ With examples
"Rate the story like this example:
creativity: 8, coherence: 7, grammar: 9"
```

**4. Define Your Criteria**
```python
# ❌ Undefined criteria
"Rate creativity."

# ✅ Defined criteria
"CREATIVITY (1=cliché, 10=highly original):
- Unique ideas, unexpected elements, imaginative concepts"
```

### Response Parsing Patterns

When working with LLM outputs, you'll encounter these common patterns:

```python
def parse_key_value_pairs(response: str) -> dict:
    """Parse 'key: value' format responses."""
    result = {}
    for line in response.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip()
    return result

def parse_comma_separated(response: str) -> dict:
    """Parse 'key1: value1, key2: value2' format."""
    result = {}
    for part in response.split(','):
        if ':' in part:
            key, value = part.split(':')
            result[key.strip()] = value.strip()
    return result

def safe_int_conversion(value: str, default: int = 0) -> int:
    """Safely convert strings to integers."""
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return default
```

## Step 2: Create the Judge Prompt

Now let's apply these principles to build a simple evaluation file:

```python title="eval_story_judge.py"
import pytest
from doteval import foreach, Result
from doteval.evaluators import evaluator
from doteval.metrics import accuracy

@pytest.fixture
def judge_model():
    """Simple mock judge - replace with your actual LLM."""
    class MockJudge:
        def generate(self, prompt):
            # Mock judge that varies responses
            if "dragon" in prompt.lower():
                return "creativity: 8, coherence: 7, grammar: 9"
            elif "cat" in prompt.lower():
                return "creativity: 6, coherence: 9, grammar: 8"
            else:
                return "creativity: 5, coherence: 6, grammar: 7"
    return MockJudge()
```

Create the judging prompt:

```python
def create_judge_prompt(story: str) -> str:
    """Create a structured prompt for the LLM judge."""
    return f"""
You are evaluating a creative writing story. Rate each aspect from 1-10:

Story:
{story}

Provide ratings in this exact format:
creativity: [score], coherence: [score], grammar: [score]

Example: creativity: 8, coherence: 7, grammar: 9
"""
```

## Step 3: Build the Evaluator

Create your custom evaluator:

```python
@evaluator(metrics=accuracy())
def story_judge(story: str, judge_model) -> dict:
    """Judge story quality using an LLM."""
    prompt = create_judge_prompt(story)
    response = judge_model.generate(prompt)

    # Parse the response
    scores = {}
    for part in response.split(","):
        if ":" in part:
            criterion, score = part.split(":")
            criterion = criterion.strip()
            try:
                scores[criterion] = int(score.strip())
            except ValueError:
                scores[criterion] = 0

    # Return whether all scores are above threshold
    threshold = 7
    return {
        "high_quality": all(score >= threshold for score in scores.values()),
        "creativity_score": scores.get("creativity", 0),
        "coherence_score": scores.get("coherence", 0),
        "grammar_score": scores.get("grammar", 0)
    }
```

## Step 4: Test Your Evaluator

Create test stories:

```python
stories = [
    "Once upon a time, a magical dragon discovered it could code in Python. It used its newfound skills to debug the kingdom's software problems.",
    "The cat sat on the mat. It was a normal day. The cat was happy.",
    "In a world where gravity worked backwards, Maria learned to walk on clouds and swim through air to reach her floating school.",
]

@foreach("story", stories)
def eval_creative_writing(story, judge_model):
    """Evaluate creative writing using LLM judge."""
    return Result(
        story_judge(story, judge_model),
        prompt=story[:50] + "..."
    )
```

## Step 5: Run and Test

Run your evaluation:

```bash
pytest eval_story_judge.py --experiment story_quality
```

View the results:

```bash
doteval show story_quality
```

You should see scores for each story showing the creativity, coherence, and grammar ratings.

## Step 6: Improve the Prompt

Let's make the judging more reliable:

```python
def create_improved_prompt(story: str) -> str:
    """Improved prompt with clearer criteria."""
    return f"""
Evaluate this creative writing story on three criteria (1-10 scale):

CREATIVITY (1=cliché, 10=highly original):

- Unique ideas, unexpected elements, imaginative concepts

COHERENCE (1=confusing, 10=perfectly logical):

- Story makes sense, events connect logically, clear narrative

GRAMMAR (1=many errors, 10=perfect):

- Proper spelling, punctuation, sentence structure

Story to evaluate:
{story}

Respond with ONLY these three lines:
creativity: [number]
coherence: [number]
grammar: [number]
"""
```

Update your evaluator to use the improved prompt:

```python
@evaluator(metrics=accuracy())
def improved_story_judge(story: str, judge_model) -> dict:
    """Improved story judge with better prompt."""
    prompt = create_improved_prompt(story)
    response = judge_model.generate(prompt)

    # More robust parsing
    scores = {}
    for line in response.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            try:
                scores[key.strip()] = int(value.strip())
            except ValueError:
                scores[key.strip()] = 0

    return {
        "high_quality": all(score >= 7 for score in scores.values()),
        "avg_score": sum(scores.values()) / len(scores) if scores else 0,
        **scores
    }
```

## Step 7: Test Multiple Stories

Create a more comprehensive test:

```python
story_dataset = [
    "The time-traveling librarian accidentally returned the wrong century's books, causing Shakespeare to write science fiction.",
    "I went to store. Bought milk. Came home.",
    "As the last star died, the cosmic janitor swept up the universe's debris, humming an ancient tune that would birth new galaxies.",
    "There was a dog named Rex. Rex was good dog. Rex played fetch every day.",
]

@foreach("story", story_dataset)
def eval_story_quality_final(story, judge_model):
    """Final story quality evaluation."""
    return Result(
        improved_story_judge(story, judge_model),
        prompt=story[:60] + "..." if len(story) > 60 else story
    )
```

Run the improved evaluation:

```bash
pytest eval_story_judge.py::eval_story_quality_final --experiment improved_stories
```

## What you've learned

You now understand (for advanced structured evaluation patterns, see [How to Evaluate Structured Generation](../how-to/evaluate-structured-generation.md)):

1. **LLM judge design** - Creating prompts with clear criteria and output formats
2. **Response parsing** - Robustly extracting structured data from LLM outputs
3. **Multi-metric evaluation** - Returning multiple scores from one evaluator
4. **Iterative improvement** - How to refine prompts for better reliability
5. **Edge case handling** - Dealing with unexpected LLM responses

## Next Steps

**[Tutorial 5: Scale with Async Evaluation](05-scale-with-async-evaluation.md)** - Make your evaluations run 10x faster with async and concurrency.

## See Also

- **[How to Evaluate Structured Generation](../how-to/evaluate-structured-generation.md)** - Advanced patterns for structured outputs and validation
- **[Reference: Evaluators](../reference/evaluators.md)** - Complete API documentation for evaluators
- **[How to Handle Rate Limits and API Errors](../how-to/handle-rate-limits-and-api-errors.md)** - Robust LLM judge implementations
- **[Tutorial 7: Comparing Multiple Models](07-comparing-multiple-models.md)** - Use custom evaluators to compare model performance
