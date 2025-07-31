# Evaluators Module

Built-in evaluators and decorators for creating custom evaluators.

## Built-in Evaluators

Ready-to-use evaluators for common evaluation tasks. These functions can be used directly in your evaluations or as building blocks for custom evaluators.

### exact_match

The most commonly used evaluator for exact string comparisons.

::: doteval.evaluators.exact_match

### numeric_match

Compare numeric values with optional tolerance, handling various formats like commas, spaces, and scientific notation.

::: doteval.evaluators.numeric_match

### valid_json

Validate if response is valid JSON and optionally matches a schema.

::: doteval.evaluators.valid_json

### All Evaluators

::: doteval.evaluators
    options:
      filters:
        - "!evaluator"
        - "!get_metadata"

## @evaluator Decorator

Create custom evaluators with automatic metric computation and result aggregation.

**Usage**: `@evaluator(metrics=[accuracy(), mean()])`

::: doteval.evaluators.evaluator

## Helper Functions

### get_metadata

Extract metadata from evaluator functions.

::: doteval.evaluators.get_metadata
