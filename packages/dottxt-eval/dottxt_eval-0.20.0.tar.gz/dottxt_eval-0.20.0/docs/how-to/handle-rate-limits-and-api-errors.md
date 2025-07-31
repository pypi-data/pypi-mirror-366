# How to Handle Rate Limits and API Errors

API calls fail for many reasons: rate limits, network issues, server errors, and quota exhaustion. This guide shows you how to build robust evaluations that handle these issues gracefully.

## Problem: Evaluations Failing Due to API Issues

```bash
pytest eval_large.py --experiment api_test
# APIError: Rate limit exceeded. Please try again in 60 seconds.
# ConnectionError: Unable to connect to API server
# 429 Too Many Requests
```

Without proper error handling, these failures stop your entire evaluation.

## Solution 1: Implement Retry Logic with Exponential Backoff

Add automatic retries with increasing delays:

```python
import time
import random
from typing import Callable, Any
from functools import wraps
import requests
from doteval import foreach, Result

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    """Decorator for retrying API calls with exponential backoff."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except (requests.exceptions.RequestException,
                       ConnectionError,
                       TimeoutError) as e:
                    last_exception = e

                    if attempt == max_retries:
                        print(f"Failed after {max_retries} retries: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                    # Add jitter to avoid thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)

                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator

@retry_with_backoff(max_retries=5, base_delay=1.0, max_delay=30.0)
def robust_api_call(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Make API call with automatic retries."""
    import openai

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        timeout=30  # Set timeout to avoid hanging
    )

    return response.choices[0].message.content.strip()

@foreach("prompt,expected", dataset)
def eval_with_retries(prompt, expected):
    """Evaluation with automatic retry logic."""
    try:
        response = robust_api_call(prompt)
        score = evaluate_response(response, expected)

        return Result(
            score,
            prompt=prompt,
            response=response,
            scores={"accuracy": score}
        )

    except Exception as e:
        # Log failure but don't crash the evaluation
        print(f"Failed to evaluate prompt after retries: {e}")
        return Result(
            False,
            prompt=prompt,
            response=f"ERROR: {str(e)}",
            scores={"accuracy": 0, "error": True}
        )
```

## Solution 2: Handle Specific Error Types

Different errors need different handling strategies:

```python
import openai
from requests.exceptions import RequestException, HTTPError
import json

class APIErrorHandler:
    """Centralized API error handling."""

    @staticmethod
    def handle_openai_error(error, prompt: str, attempt: int) -> dict:
        """Handle OpenAI-specific errors."""

        if hasattr(error, 'response') and error.response:
            status_code = error.response.status_code

            if status_code == 429:  # Rate limit
                # Extract retry-after header if available
                retry_after = error.response.headers.get('retry-after', 60)
                return {
                    "should_retry": True,
                    "delay": int(retry_after),
                    "reason": f"Rate limited (attempt {attempt})"
                }

            elif status_code in [500, 502, 503, 504]:  # Server errors
                return {
                    "should_retry": True,
                    "delay": min(2 ** attempt, 60),  # Exponential backoff
                    "reason": f"Server error {status_code} (attempt {attempt})"
                }

            elif status_code == 400:  # Bad request
                return {
                    "should_retry": False,
                    "delay": 0,
                    "reason": f"Bad request - check prompt: {prompt[:100]}..."
                }

            elif status_code == 401:  # Authentication
                return {
                    "should_retry": False,
                    "delay": 0,
                    "reason": "Authentication failed - check API key"
                }

        # Default for unknown errors
        return {
            "should_retry": attempt < 3,
            "delay": min(2 ** attempt, 30),
            "reason": f"Unknown error: {str(error)}"
        }

def robust_openai_call(prompt: str, max_retries: int = 5) -> dict:
    """Make OpenAI call with sophisticated error handling."""

    for attempt in range(max_retries + 1):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                timeout=30
            )

            return {
                "success": True,
                "response": response.choices[0].message.content.strip(),
                "usage": response.usage.dict() if response.usage else {},
                "attempts": attempt + 1
            }

        except Exception as e:
            error_info = APIErrorHandler.handle_openai_error(e, prompt, attempt)

            if not error_info["should_retry"] or attempt == max_retries:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "reason": error_info["reason"],
                    "attempts": attempt + 1
                }

            print(f"API call failed: {error_info['reason']}. Waiting {error_info['delay']}s...")
            time.sleep(error_info["delay"])

    return {"success": False, "error": "Max retries exceeded"}

@foreach("prompt,expected", dataset)
def eval_with_error_handling(prompt, expected):
    """Evaluation with comprehensive error handling."""
    api_result = robust_openai_call(prompt)

    if api_result["success"]:
        response = api_result["response"]
        score = evaluate_response(response, expected)

        return Result(
            score,
            prompt=prompt,
            response=response,
            scores={
                "accuracy": score,
                "api_attempts": api_result["attempts"],
                "tokens_used": api_result.get("usage", {}).get("total_tokens", 0)
            }
        )
    else:
        # Record the failure but continue evaluation
        return Result(
            False,
            prompt=prompt,
            response=f"API_ERROR: {api_result['error']}",
            scores={
                "accuracy": 0,
                "error": True,
                "error_type": api_result.get("error_type", "unknown"),
                "api_attempts": api_result["attempts"]
            }
        )
```

## Solution 3: Implement Rate Limiting

Control your request rate to stay within API limits:

```python
import asyncio
from asyncio import Semaphore
import time
from typing import AsyncGenerator

class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 60, calls_per_second: int = 10):
        self.calls_per_minute = calls_per_minute
        self.calls_per_second = calls_per_second

        # Track calls for rate limiting
        self.minute_calls = []
        self.second_calls = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Wait until it's safe to make an API call."""
        await self.lock.acquire()

        try:
            now = time.time()

            # Clean old records
            self.minute_calls = [t for t in self.minute_calls if now - t < 60]
            self.second_calls = [t for t in self.second_calls if now - t < 1]

            # Check if we need to wait
            if len(self.minute_calls) >= self.calls_per_minute:
                wait_time = 60 - (now - self.minute_calls[0]) + 0.1
                await asyncio.sleep(wait_time)

            elif len(self.second_calls) >= self.calls_per_second:
                wait_time = 1 - (now - self.second_calls[0]) + 0.1
                await asyncio.sleep(wait_time)

            # Record this call
            current_time = time.time()
            self.minute_calls.append(current_time)
            self.second_calls.append(current_time)

        finally:
            self.lock.release()

# Global rate limiter
rate_limiter = RateLimiter(calls_per_minute=50, calls_per_second=5)

async def rate_limited_api_call(prompt: str) -> str:
    """API call with rate limiting."""
    await rate_limiter.acquire()

    # Make the actual API call
    response = await async_openai_call(prompt)
    return response

@foreach("prompt,expected", dataset)
async def eval_with_rate_limiting(prompt, expected):
    """Async evaluation with rate limiting."""
    try:
        response = await rate_limited_api_call(prompt)
        score = evaluate_response(response, expected)

        return Result(score, prompt=prompt, response=response)

    except Exception as e:
        return Result(False, prompt=prompt, response=f"ERROR: {e}")
```

## Solution 4: Circuit Breaker Pattern

Prevent cascading failures by temporarily stopping API calls when error rates are high:

```python
import time
from enum import Enum
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking all calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker for API calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - too many recent failures")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should try to reset the circuit."""
        return (
            self.last_failure_time is not None and
            time.time() - self.last_failure_time >= self.timeout
        )

    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Global circuit breaker
api_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=120.0,  # Wait 2 minutes before trying again
    expected_exception=(requests.RequestException, openai.OpenAIError)
)

def protected_api_call(prompt: str) -> str:
    """API call protected by circuit breaker."""

    def _make_call():
        return openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content.strip()

    return api_circuit_breaker.call(_make_call)

@foreach("prompt,expected", dataset)
def eval_with_circuit_breaker(prompt, expected):
    """Evaluation with circuit breaker protection."""
    try:
        response = protected_api_call(prompt)
        score = evaluate_response(response, expected)

        return Result(score, prompt=prompt, response=response)

    except Exception as e:
        return Result(
            False,
            prompt=prompt,
            response=f"CIRCUIT_BREAKER: {str(e)}",
            scores={"error": True, "circuit_breaker_open": "OPEN" in str(e)}
        )
```

## Solution 5: Graceful Degradation

When APIs fail, fall back to alternative approaches:

```python
from typing import Union, List

class FallbackEvaluator:
    """Evaluator with multiple fallback strategies."""

    def __init__(self):
        self.primary_model = "gpt-4"
        self.fallback_models = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
        self.local_model = None  # Could be a local model instance

    def evaluate_with_fallback(self, prompt: str, expected: str) -> dict:
        """Try multiple approaches if primary fails."""

        # Try primary model
        try:
            response = self._call_api(prompt, self.primary_model)
            return {
                "success": True,
                "response": response,
                "model_used": self.primary_model,
                "fallback_used": False
            }
        except Exception as primary_error:
            print(f"Primary model failed: {primary_error}")

        # Try fallback models
        for fallback_model in self.fallback_models:
            try:
                response = self._call_api(prompt, fallback_model)
                return {
                    "success": True,
                    "response": response,
                    "model_used": fallback_model,
                    "fallback_used": True
                }
            except Exception as fallback_error:
                print(f"Fallback model {fallback_model} failed: {fallback_error}")
                continue

        # Try local model if available
        if self.local_model:
            try:
                response = self.local_model.generate(prompt)
                return {
                    "success": True,
                    "response": response,
                    "model_used": "local",
                    "fallback_used": True
                }
            except Exception as local_error:
                print(f"Local model failed: {local_error}")

        # All methods failed
        return {
            "success": False,
            "response": "All models failed",
            "model_used": None,
            "fallback_used": True
        }

    def _call_api(self, prompt: str, model: str) -> str:
        """Make API call to specific model."""
        return robust_api_call(prompt, model)

fallback_evaluator = FallbackEvaluator()

@foreach("prompt,expected", dataset)
def eval_with_fallback(prompt, expected):
    """Evaluation with fallback models."""
    result = fallback_evaluator.evaluate_with_fallback(prompt, expected)

    if result["success"]:
        score = evaluate_response(result["response"], expected)

        return Result(
            score,
            prompt=prompt,
            response=result["response"],
            scores={
                "accuracy": score,
                "model_used": result["model_used"],
                "fallback_used": result["fallback_used"]
            }
        )
    else:
        return Result(
            False,
            prompt=prompt,
            response="ALL_MODELS_FAILED",
            scores={"error": True, "all_models_failed": True}
        )
```

## Solution 6: Monitor API Usage and Costs

Track your API usage to avoid surprises:

```python
import json
from collections import defaultdict
from datetime import datetime

class APIUsageTracker:
    """Track API usage and costs."""

    def __init__(self):
        self.usage_log = []
        self.daily_usage = defaultdict(lambda: {"requests": 0, "tokens": 0, "cost": 0.0})

    def log_request(self, model: str, tokens_used: int, cost: float):
        """Log an API request."""
        timestamp = datetime.now()
        day_key = timestamp.strftime("%Y-%m-%d")

        self.usage_log.append({
            "timestamp": timestamp.isoformat(),
            "model": model,
            "tokens": tokens_used,
            "cost": cost
        })

        self.daily_usage[day_key]["requests"] += 1
        self.daily_usage[day_key]["tokens"] += tokens_used
        self.daily_usage[day_key]["cost"] += cost

    def get_daily_summary(self, date: str = None) -> dict:
        """Get usage summary for a specific day."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        return dict(self.daily_usage[date])

    def check_budget_limits(self, daily_budget: float = 50.0) -> bool:
        """Check if we're within budget limits."""
        today = datetime.now().strftime("%Y-%m-%d")
        today_cost = self.daily_usage[today]["cost"]

        if today_cost >= daily_budget:
            print(f"WARNING: Daily budget exceeded! Used ${today_cost:.2f} of ${daily_budget}")
            return False

        return True

    def save_usage_log(self, filename: str):
        """Save usage log to file."""
        with open(filename, 'w') as f:
            json.dump({
                "usage_log": self.usage_log,
                "daily_usage": dict(self.daily_usage)
            }, f, indent=2)

# Global usage tracker
usage_tracker = APIUsageTracker()

def tracked_api_call(prompt: str, model: str = "gpt-3.5-turbo") -> dict:
    """API call with usage tracking."""

    # Check budget before making call
    if not usage_tracker.check_budget_limits():
        raise Exception("Daily budget limit exceeded")

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )

    # Track usage
    tokens_used = response.usage.total_tokens
    cost = calculate_cost(model, tokens_used)  # You'd implement this

    usage_tracker.log_request(model, tokens_used, cost)

    return {
        "response": response.choices[0].message.content.strip(),
        "tokens_used": tokens_used,
        "cost": cost
    }

@foreach("prompt,expected", dataset)
def eval_with_usage_tracking(prompt, expected):
    """Evaluation with cost and usage tracking."""
    try:
        api_result = tracked_api_call(prompt)
        score = evaluate_response(api_result["response"], expected)

        return Result(
            score,
            prompt=prompt,
            response=api_result["response"],
            scores={
                "accuracy": score,
                "tokens_used": api_result["tokens_used"],
                "cost": api_result["cost"]
            }
        )

    except Exception as e:
        return Result(False, prompt=prompt, response=f"ERROR: {e}")
```

## Best Practices Summary

1. **Always use retry logic** with exponential backoff
2. **Handle specific error types** differently (rate limits vs server errors)
3. **Implement rate limiting** to stay within API quotas
4. **Use circuit breakers** to prevent cascading failures
5. **Have fallback strategies** when primary approaches fail
6. **Monitor usage and costs** to avoid budget surprises
7. **Set appropriate timeouts** to avoid hanging requests
8. **Log errors systematically** for debugging and monitoring

## Quick Error Handling Template

```python
@retry_with_backoff(max_retries=3)
def robust_model_call(prompt: str) -> str:
    try:
        # Your API call here
        response = api.generate(prompt)
        return response
    except RateLimitError:
        # This will be retried by the decorator
        raise
    except APIError as e:
        if "quota" in str(e).lower():
            # Quota errors shouldn't be retried
            raise Exception(f"Quota exceeded: {e}")
        raise  # Other API errors can be retried

@foreach("prompt,expected", dataset)
def eval_robust(prompt, expected):
    try:
        response = robust_model_call(prompt)
        return Result(True, prompt=prompt, response=response)
    except Exception as e:
        return Result(False, prompt=prompt, response=f"ERROR: {e}")
```

Robust error handling is essential for production evaluations. Start with basic retry logic and add more sophisticated patterns as needed.

## See Also

- **[Tutorial 8: Optimize Concurrency for Production](../tutorials/08-optimize-concurrency-for-production.md)** - Production-ready concurrency with error handling
- **[How to Debug Slow Evaluations](debug-slow-evaluations.md)** - Performance issues often relate to API problems
- **[How to Resume Failed Evaluations](resume-failed-evaluations.md)** - Recover from API failures and interruptions
- **[Tutorial 2: Using Real Models](../tutorials/02-using-real-models.md)** - Basic API integration patterns
- **[Reference: Async Evaluations](../reference/async.md)** - Async patterns for resilient API calls
