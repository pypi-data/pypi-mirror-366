# How to Evaluate Structured Generation

Structured generation is doteval's defining capability. This guide shows you how to evaluate JSON schemas, function calls, structured outputs, and custom formats beyond simple text matching.

## Problem: Text Matching Isn't Enough

Traditional evaluation approaches fail with structured outputs (see [Tutorial 4: Building Custom Evaluators](../tutorials/04-building-custom-evaluators.md) for basic evaluator concepts):

```python
# ❌ This doesn't work well for structured data
model_output = '{"name": "John", "age": 25, "city": "NYC"}'
expected = '{"name":"John","age":25,"city":"NYC"}'
exact_match(model_output, expected)  # False due to formatting differences
```

You need semantic validation, not string comparison.

## Solution 1: JSON Schema Validation

Validate that your model produces valid JSON with the correct structure:

```python
import json
from jsonschema import validate, ValidationError
from doteval import foreach, Result
from doteval.evaluators import evaluator

# Define your expected schema
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer", "minimum": 0},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age", "email"]
}

@evaluator
def json_schema_match(response: str, schema: dict) -> bool:
    """Validate JSON response against schema."""
    try:
        data = json.loads(response)
        validate(instance=data, schema=schema)
        return True
    except (json.JSONDecodeError, ValidationError):
        return False

@foreach("prompt,expected_schema", user_data)
def eval_user_extraction(prompt, expected_schema, model):
    """Evaluate structured user data extraction."""
    response = model.generate(prompt)

    return Result(
        json_schema_match(response, expected_schema),
        prompt=prompt,
        response=response,
        scores={
            "schema_valid": json_schema_match(response, expected_schema)
        }
    )
```

## Solution 2: Function Call Evaluation

Evaluate models that generate function calls or tool usage:

```python
import json
from doteval import foreach, Result
from doteval.evaluators import evaluator

@evaluator
def function_call_match(response: str, expected_function: str, expected_args: dict) -> dict:
    """Evaluate function call accuracy."""
    try:
        data = json.loads(response)

        # Check function name
        function_correct = data.get("function") == expected_function

        # Check required arguments
        args_correct = all(
            data.get("arguments", {}).get(key) == value
            for key, value in expected_args.items()
        )

        return {
            "function_correct": function_correct,
            "args_correct": args_correct,
            "overall_correct": function_correct and args_correct
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "function_correct": False,
            "args_correct": False,
            "overall_correct": False
        }

function_call_data = [
    (
        "What's the weather in Paris?",
        "get_weather",
        {"location": "Paris", "units": "celsius"}
    ),
]

@foreach("prompt,expected_function,expected_args", function_call_data)
def eval_function_calls(prompt, expected_function, expected_args, model):
    """Evaluate function call generation."""
    response = model.generate(prompt)
    scores = function_call_match(response, expected_function, expected_args)

    return Result(
        scores["overall_correct"],
        prompt=prompt,
        response=response,
        scores=scores
    )
```

## Solution 3: Custom Structured Evaluators

Create domain-specific evaluators for your structured outputs:

```python
from typing import Dict, Any
import re
from doteval.evaluators import evaluator

@evaluator
def sql_query_evaluator(response: str, expected_tables: list, expected_operations: list) -> dict:
    """Evaluate generated SQL queries."""
    response = response.strip().upper()

    # Check for required tables
    tables_present = all(
        table.upper() in response for table in expected_tables
    )

    # Check for required operations
    operations_present = all(
        op.upper() in response for op in expected_operations
    )

    # Check SQL syntax basics
    valid_syntax = (
        response.startswith('SELECT') and
        'FROM' in response and
        response.endswith(';')
    )

    return {
        "tables_correct": tables_present,
        "operations_correct": operations_present,
        "syntax_valid": valid_syntax,
        "overall_correct": tables_present and operations_present and valid_syntax
    }

@evaluator
def code_structure_evaluator(response: str, expected_functions: list, expected_imports: list) -> dict:
    """Evaluate generated code structure."""

    # Check for required function definitions
    functions_present = all(
        f"def {func}(" in response for func in expected_functions
    )

    # Check for required imports
    imports_present = all(
        f"import {imp}" in response or f"from {imp}" in response
        for imp in expected_imports
    )

    # Basic syntax check (can be parsed)
    try:
        compile(response, '<string>', 'exec')
        syntax_valid = True
    except SyntaxError:
        syntax_valid = False

    return {
        "functions_present": functions_present,
        "imports_present": imports_present,
        "syntax_valid": syntax_valid,
        "overall_correct": functions_present and imports_present and syntax_valid
    }
```

## Solution 4: Handling Malformed Outputs

Robust evaluation handles cases where models produce invalid structured data:

```python
from doteval.evaluators import evaluator
import json
import logging

@evaluator
def robust_json_evaluator(response: str, required_fields: list) -> dict:
    """Robustly evaluate JSON with fallback parsing."""

    # First, try standard JSON parsing
    try:
        data = json.loads(response)
        json_valid = True
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                json_valid = True
            except json.JSONDecodeError:
                data = {}
                json_valid = False
        else:
            data = {}
            json_valid = False

    # Check required fields
    if json_valid:
        fields_present = all(field in data for field in required_fields)
        fields_non_empty = all(
            data.get(field) not in [None, "", []] for field in required_fields
        )
    else:
        fields_present = fields_non_empty = False

    return {
        "json_valid": json_valid,
        "fields_present": fields_present,
        "fields_non_empty": fields_non_empty,
        "overall_correct": json_valid and fields_present and fields_non_empty,
        "extracted_data": data
    }

@foreach("prompt,required_fields", extraction_data)
def eval_robust_extraction(prompt, required_fields, model):
    """Robust evaluation of structured extraction."""
    response = model.generate(prompt)
    scores = robust_json_evaluator(response, required_fields)

    return Result(
        scores["overall_correct"],
        prompt=prompt,
        response=response,
        scores=scores
    )
```

## Advanced: Multi-Level Structured Validation

For complex nested structures, create hierarchical evaluators:

```python
@evaluator
def nested_structure_evaluator(response: str, schema: dict) -> dict:
    """Evaluate complex nested JSON structures."""
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return {"valid": False, "errors": ["Invalid JSON"]}

    errors = []
    scores = {}

    def validate_nested(obj, schema_part, path=""):
        if schema_part["type"] == "object":
            if not isinstance(obj, dict):
                errors.append(f"{path}: Expected object, got {type(obj).__name__}")
                return False

            # Check required properties
            valid = True
            for prop, prop_schema in schema_part.get("properties", {}).items():
                prop_path = f"{path}.{prop}" if path else prop
                if prop in obj:
                    if not validate_nested(obj[prop], prop_schema, prop_path):
                        valid = False
                elif prop in schema_part.get("required", []):
                    errors.append(f"{prop_path}: Required field missing")
                    valid = False

            return valid

        elif schema_part["type"] == "array":
            if not isinstance(obj, list):
                errors.append(f"{path}: Expected array, got {type(obj).__name__}")
                return False

            return all(
                validate_nested(item, schema_part["items"], f"{path}[{i}]")
                for i, item in enumerate(obj)
            )

        else:  # primitive types
            expected_type = {"string": str, "integer": int, "number": (int, float), "boolean": bool}
            if not isinstance(obj, expected_type[schema_part["type"]]):
                errors.append(f"{path}: Expected {schema_part['type']}, got {type(obj).__name__}")
                return False
            return True

    overall_valid = validate_nested(data, schema)

    return {
        "valid": overall_valid,
        "errors": errors,
        "error_count": len(errors),
        "structure_score": max(0, 1 - len(errors) / 10)  # Penalty per error
    }
```

## Running Structured Evaluations

```bash
# Run with experiment tracking
pytest eval_structured.py --experiment structured_baseline

# View detailed results
doteval show structured_baseline --full

# Compare structured vs unstructured approaches
pytest eval_structured.py --experiment structured_v1
pytest eval_unstructured.py --experiment unstructured_v1
```

## Key Takeaways

1. **Semantic validation over string matching** - Use JSON parsing and validation
2. **Handle malformed outputs gracefully** - Models sometimes produce invalid JSON
3. **Create domain-specific evaluators** - SQL, code, API calls need custom validation
4. **Use hierarchical scoring** - Break down complex structures into component scores
5. **Test your evaluators** - Ensure they correctly identify both valid and invalid outputs

Structured generation evaluation is about validating meaning and format, not exact string matches. This approach scales to any structured output format your models need to produce.

## See Also

- **[Tutorial 4: Building Custom Evaluators](../tutorials/04-building-custom-evaluators.md)** - Learn to create domain-specific evaluators
- **[How to Work with Custom Data Formats](work-with-custom-data-formats.md)** - Handle complex nested data structures
- **[Reference: Evaluators](../reference/evaluators.md)** - Complete API documentation for evaluators
- **[Tutorial 2: Using Real Models](../tutorials/02-using-real-models.md)** - Connect to APIs that generate structured outputs
