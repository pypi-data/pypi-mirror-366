# Tutorial 2: Connect to Real Models

In this tutorial, you'll connect your evaluations to actual language models instead of mock functions. By the end, you'll understand the basic patterns for integrating with APIs and local models.

## What you'll learn

- How to connect evaluations to OpenAI GPT models
- How to integrate local models via Ollama
- Basic patterns for working with real model APIs
- How to compare API vs local model results

## Step 1: Set Up OpenAI Integration

First, install the OpenAI client and set up your API key:

```bash
pip install openai
export OPENAI_API_KEY="your-api-key-here"
```

Create your first real model evaluation:

```python title="eval_openai_sentiment.py"
import os
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match
from openai import OpenAI

@pytest.fixture
def openai_model():
    """OpenAI model client."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    class OpenAIModel:
        def __init__(self, client):
            self.client = client

        def classify_sentiment(self, text):
            """Classify sentiment using GPT."""
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Classify the sentiment as: positive, negative, or neutral. Respond with only one word."},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0  # Deterministic responses
            )
            return response.choices[0].message.content.strip().lower()

    return OpenAIModel(client)

# Test dataset
sentiment_data = [
    ("I absolutely love this product!", "positive"),
    ("This is terrible and disappointing", "negative"),
    ("It's an okay product, nothing special", "neutral"),
    ("Amazing quality and great value!", "positive"),
    ("Completely useless and broken", "negative"),
]

@foreach("text,expected", sentiment_data)
def eval_openai_sentiment(text, expected, openai_model):
    """Evaluate sentiment classification with OpenAI."""
    prediction = openai_model.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run your first real model evaluation:

```bash
pytest eval_openai_sentiment.py --experiment openai_sentiment_test
```

## Step 2: Add Basic Error Handling

Real APIs can occasionally fail, so add simple error handling:

```python title="eval_simple_openai.py"
import os
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match
from openai import OpenAI

@pytest.fixture
def simple_openai_model():
    """Simple OpenAI model with basic error handling."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    class SimpleOpenAIModel:
        def __init__(self, client):
            self.client = client

        def classify_sentiment(self, text):
            """Classify sentiment with basic error handling."""
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=5,
                    temperature=0
                )

                result = response.choices[0].message.content.strip().lower()

                # Validate response
                if result in ["positive", "negative", "neutral"]:
                    return result
                else:
                    return "neutral"  # Default fallback

            except Exception as e:
                print(f"API error: {e}")
                return "neutral"  # Safe fallback

    return SimpleOpenAIModel(client)

@foreach("text,expected", sentiment_data)
def eval_simple_openai(text, expected, simple_openai_model):
    """Simple OpenAI evaluation with basic error handling."""
    prediction = simple_openai_model.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the basic version:

```bash
pytest eval_simple_openai.py --experiment simple_openai_test
```

## Step 3: Try Local Models

Use Ollama for local models that don't require API costs:

```bash
# Install and start Ollama
# Download from https://ollama.ai/
ollama pull llama2  # or another model
```

```python title="eval_local_models.py"
import requests
import json
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match

@pytest.fixture
def ollama_model():
    """Local Ollama model client."""

    class OllamaModel:
        def __init__(self, model_name="llama2", base_url="http://localhost:11434"):
            self.model_name = model_name
            self.base_url = base_url

        def classify_sentiment(self, text):
            """Classify sentiment using local Ollama model."""
            try:
                prompt = f"""Classify the sentiment of this text as either "positive", "negative", or "neutral".

Text: {text}

Sentiment:"""

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0,
                            "num_predict": 10
                        }
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()["response"].strip().lower()

                    # Extract sentiment from response
                    if "positive" in result:
                        return "positive"
                    elif "negative" in result:
                        return "negative"
                    else:
                        return "neutral"
                else:
                    print(f"Ollama API error: {response.status_code}")
                    return "neutral"

            except requests.exceptions.ConnectionError:
                print("Could not connect to Ollama. Make sure it's running on localhost:11434")
                return "neutral"
            except Exception as e:
                print(f"Error with Ollama: {e}")
                return "neutral"

    return OllamaModel()

@foreach("text,expected", sentiment_data)
def eval_ollama_sentiment(text, expected, ollama_model):
    """Evaluate sentiment with local Ollama model."""
    prediction = ollama_model.classify_sentiment(text)

    return Result(
        exact_match(prediction, expected),
        prompt=text
    )
```

Run the local model evaluation:

```bash
pytest eval_local_models.py --experiment ollama_test
```

## Step 4: Compare Different Models

Create a side-by-side comparison:

```python title="eval_model_comparison.py"
import os
import pytest
from doteval import foreach, Result
from doteval.evaluators import exact_match
from openai import OpenAI
import requests

# Simple comparison evaluation
@pytest.fixture
def comparison_models():
    """Both OpenAI and Ollama models for comparison."""
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    class ModelComparison:
        def __init__(self):
            self.openai_client = openai_client

        def classify_with_openai(self, text):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Classify sentiment as: positive, negative, or neutral. One word only."},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=5,
                    temperature=0
                )
                return response.choices[0].message.content.strip().lower()
            except:
                return "neutral"

        def classify_with_ollama(self, text):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": f"Classify sentiment as positive, negative, or neutral: {text}\nSentiment:",
                        "stream": False,
                        "options": {"temperature": 0, "num_predict": 5}
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()["response"].strip().lower()
                    if "positive" in result:
                        return "positive"
                    elif "negative" in result:
                        return "negative"
                    else:
                        return "neutral"
                return "neutral"
            except:
                return "neutral"

    return ModelComparison()

# Compare both models on the same data
@foreach("text,expected", sentiment_data)
def eval_model_comparison(text, expected, comparison_models):
    """Compare OpenAI and local model performance."""

    # Get predictions from both models
    openai_prediction = comparison_models.classify_with_openai(text)
    ollama_prediction = comparison_models.classify_with_ollama(text)

    return Result(
        exact_match(openai_prediction, expected, name="openai_accuracy"),
        exact_match(ollama_prediction, expected, name="ollama_accuracy"),
        prompt=text,
        model_response=f"OpenAI: {openai_prediction}, Ollama: {ollama_prediction}"
    )
```

Run the comparison:

```bash
pytest eval_model_comparison.py --experiment model_comparison
```

View the results:

```bash
doteval show model_comparison
```

## What you've learned

You now understand:

1. **Basic API integration** - How to connect evaluations to OpenAI models
2. **Local model setup** - Using Ollama for cost-free evaluation
3. **Simple error handling** - Basic patterns for handling API failures
4. **Model comparison** - Running the same evaluation on different models
5. **API vs local tradeoffs** - Understanding the differences between approaches

## Key takeaways

- Set `temperature=0` for consistent evaluation results
- Always include basic error handling for API calls
- Local models are free but may need more setup
- Comparing models helps you understand their strengths
- Start simple - you can always add more sophistication later

## Next Steps

**[Tutorial 3: Working with Real Datasets](03-working-with-real-datasets.md)** - Load and work with real evaluation datasets from multiple sources.
