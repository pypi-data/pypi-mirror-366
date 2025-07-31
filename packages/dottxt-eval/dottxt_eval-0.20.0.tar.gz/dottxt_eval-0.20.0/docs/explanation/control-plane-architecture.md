# Control Plane Architecture

Why doteval uses single-machine control with remote inference.

## The Core Philosophy

doteval is built around a fundamental insight: **testing and deploying models are separate concerns**.

Most evaluation frameworks try to solve both model deployment and evaluation orchestration. doteval takes a different approach: **assume models are already deployed and accessible**, then focus exclusively on efficient evaluation orchestration.

This leads to a simple architectural principle: **LLM evaluation is fundamentally IO-bound, not compute-bound**.

## Why Single-Machine Control Works

In LLM evaluation, the bottleneck is not local processing but rather:

- **Network latency** to model APIs (50-500ms per request)
- **Model inference time** (100ms-10s depending on complexity)
- **API rate limits** (requests per minute/second constraints)

The actual evaluation logic—comparing outputs, computing metrics—consumes negligible resources compared to waiting for model responses.

Adding more machines doesn't solve the bottleneck since the constraint is API throughput, not local compute capacity.

## The Architecture

doteval's approach is straightforward:

```
┌─────────────────┐
│ doteval Process │
│                 │
│ • Async HTTP    │
│ • Rate limiting │
│ • Result storage│
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Model APIs      │
│ • OpenAI        │
│ • Anthropic     │
│ • Local servers │
└─────────────────┘
```

A single Python process orchestrates all evaluation tasks, managing concurrency and API communication efficiently.

## How It Scales

Instead of adding more machines, doteval scales through intelligent concurrency:

```python
# Automatically tune concurrency to API limits
foreach_optimized = ForEach(
    concurrency=SlidingWindow(max_concurrency=50)
)
```

Key techniques:

- **Async request handling** to maximize API utilization
- **Automatic rate limiting** that adapts to API responses
- **Connection pooling** to minimize overhead
- **Smart retry logic** with exponential backoff

This delivers 10-100x speedup over sequential evaluation while remaining simple to deploy and debug.

## Benefits

This simple architecture provides several advantages:

**No Coordination Overhead**: Single process means no distributed system complexity, immediate error handling, and instant startup.

**Resource Efficiency**: Shared connections, pooled authentication, and optimal memory usage across all evaluations.

**Easy Development**: Local development works exactly like production. Standard Python debugging tools work naturally.

**Simple Deployment**: Just run `pytest`. No orchestration, no cluster management, no service discovery.

## Example Usage

Running evaluations is as simple as running tests:

```bash
# Install and run
pip install doteval
pytest eval_suite.py --experiment production
```

CI/CD integration is straightforward:

```yaml
# GitHub Actions example
- name: Run Evaluations
  run: |
    pip install doteval
    pytest evaluations/ --experiment "ci-${{ github.sha }}"
    doteval show "ci-${{ github.sha }}" --format json > results.json
```

The single-process design means local development works exactly like production, making debugging and iteration fast and predictable.

## When This Approach Works

This architecture works well when:

- **Models are accessible via API** (OpenAI, Anthropic, local servers)
- **Evaluation logic is lightweight** compared to model inference
- **API quotas and rate limits** are the primary scaling constraint

These constraints match the reality of modern LLM evaluation, where the bottleneck is model inference, not evaluation orchestration.

## Summary

doteval's architecture reflects the principle that **testing and deploying models are separate concerns**. By assuming models are already deployed, doteval can focus on what an evaluation framework should do: efficiently orchestrate API calls and collect results.

The result is simple, fast, and reliable evaluation that scales with your API quotas rather than your infrastructure complexity.
