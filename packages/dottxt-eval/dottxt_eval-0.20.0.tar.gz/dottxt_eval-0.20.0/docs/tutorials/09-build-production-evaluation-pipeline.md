# Tutorial 9: Build Production Evaluation Pipeline

In this tutorial, you'll create a complete evaluation pipeline that runs in CI/CD and tracks performance over time.

## What you'll learn

- How to build evaluations for complex multi-step workflows
- How to use SQLite storage for better performance and querying
- How to leverage automatic git tracking for reproducibility
- How to set up CI/CD automation for continuous evaluation
- How to track performance trends and detect regressions

## Step 1: Create Agent Workflow Evaluation

Start by building an evaluation for complex agent scenarios:

```python title="eval_agent_workflows.py"
import json
import asyncio
from doteval import foreach, Result
from doteval.evaluators import exact_match

def load_agent_scenarios():
    """Load multi-step agent evaluation scenarios."""
    return [
        {
            "scenario": "Book a restaurant reservation",
            "initial_state": {"user_location": "San Francisco", "date": "tomorrow"},
            "expected_actions": [
                {"type": "search", "query": "restaurants near me"},
                {"type": "call", "restaurant": "Best Italian"},
                {"type": "book", "time": "7pm", "party_size": 2}
            ],
            "success_criteria": ["reservation_confirmed", "correct_time", "correct_party_size"]
        },
        {
            "scenario": "Plan a weekend trip",
            "initial_state": {"budget": 500, "destination": "Portland", "dates": "next weekend"},
            "expected_actions": [
                {"type": "search", "query": "flights to Portland"},
                {"type": "book", "flight": "Delta 123"},
                {"type": "search", "query": "hotels in Portland"},
                {"type": "book", "hotel": "Hotel Deluxe"}
            ],
            "success_criteria": ["flight_booked", "hotel_booked", "within_budget"]
        },
        {
            "scenario": "Order groceries for dinner party",
            "initial_state": {"guest_count": 8, "dietary_restrictions": ["vegetarian", "gluten-free"]},
            "expected_actions": [
                {"type": "plan", "menu": "vegetarian_gluten_free"},
                {"type": "calculate", "quantities": "for_8_people"},
                {"type": "order", "items": "ingredient_list"}
            ],
            "success_criteria": ["menu_accommodates_restrictions", "correct_quantities", "order_placed"]
        }
    ]

class MockAgent:
    """Mock agent for demonstration - replace with your actual agent."""

    async def execute_scenario(self, scenario, initial_state):
        """Simulate agent executing a multi-step scenario."""
        await asyncio.sleep(0.1)  # Simulate processing time

        # Mock responses based on scenario
        if "restaurant" in scenario.lower():
            return AgentResult([
                {"type": "search", "query": "restaurants near me", "results": 5},
                {"type": "call", "restaurant": "Best Italian", "status": "answered"},
                {"type": "book", "time": "7pm", "party_size": 2, "status": "confirmed"}
            ])
        elif "trip" in scenario.lower():
            return AgentResult([
                {"type": "search", "query": "flights to Portland", "results": 3},
                {"type": "book", "flight": "Delta 123", "cost": 200},
                {"type": "search", "query": "hotels in Portland", "results": 8},
                {"type": "book", "hotel": "Hotel Deluxe", "cost": 250}
            ])
        else:  # groceries
            return AgentResult([
                {"type": "plan", "menu": "vegetarian_gluten_free", "dishes": 3},
                {"type": "calculate", "quantities": "for_8_people", "items": 15},
                {"type": "order", "items": "ingredient_list", "total": 89.50}
            ])

class AgentResult:
    """Container for agent execution results."""
    def __init__(self, actions):
        self.actions = actions

def evaluate_criterion(result, criterion, expected_actions):
    """Evaluate specific success criteria for agent workflows."""
    if criterion == "reservation_confirmed":
        return any(action.get("type") == "book" and action.get("status") == "confirmed"
                  for action in result.actions)
    elif criterion == "correct_time":
        booking_action = next((a for a in result.actions if a.get("type") == "book"), {})
        expected_time = next((a.get("time") for a in expected_actions if a.get("type") == "book"), None)
        return booking_action.get("time") == expected_time
    elif criterion == "correct_party_size":
        booking_action = next((a for a in result.actions if a.get("type") == "book"), {})
        expected_size = next((a.get("party_size") for a in expected_actions if a.get("type") == "book"), None)
        return booking_action.get("party_size") == expected_size
    elif criterion == "flight_booked":
        return any(action.get("type") == "book" and "flight" in action
                  for action in result.actions)
    elif criterion == "hotel_booked":
        return any(action.get("type") == "book" and "hotel" in action
                  for action in result.actions)
    elif criterion == "within_budget":
        total_cost = sum(action.get("cost", 0) for action in result.actions)
        return total_cost <= 500
    elif criterion == "menu_accommodates_restrictions":
        return any(action.get("menu") == "vegetarian_gluten_free"
                  for action in result.actions)
    elif criterion == "correct_quantities":
        return any(action.get("quantities") == "for_8_people"
                  for action in result.actions)
    elif criterion == "order_placed":
        return any(action.get("type") == "order"
                  for action in result.actions)
    return False

@foreach("scenario,initial_state,expected_actions,success_criteria", load_agent_scenarios())
async def eval_agent_workflow(scenario, initial_state, expected_actions, success_criteria):
    """Evaluate an agent's ability to complete multi-step workflows."""
    agent = MockAgent()

    # Execute agent workflow
    result = await agent.execute_scenario(scenario, initial_state)

    # Evaluate each success criterion
    scores = []
    for criterion in success_criteria:
        success = evaluate_criterion(result, criterion, expected_actions)
        scores.append(exact_match(success, True, name=criterion))

    return Result(
        *scores,
        prompt=f"Scenario: {scenario}",
        model_response=json.dumps(result.actions, indent=2)
    )
```

Test your agent evaluation:

```bash
pytest eval_agent_workflows.py --experiment agent_test
```

## Step 2: Switch to SQLite Storage

For production pipelines, use SQLite instead of JSON for better querying:

```bash
# Create SQLite database for persistent storage
pytest eval_agent_workflows.py --experiment agent_baseline --storage sqlite://agent_results.db
```

View the results:

```bash
doteval show agent_baseline --storage sqlite://agent_results.db
```

SQLite storage provides:

- Better performance for large result sets
- SQL querying capabilities
- Atomic transactions
- Better CI/CD integration

## Step 3: Set Up Git Integration

doteval automatically captures git metadata (commit hash, branch, repo state) in every session. You can see this in your results:

```bash
doteval show agent_baseline --full --storage sqlite://agent_results.db
```

Look for the git information in the session metadata. This enables:

- Tracking which code version produced which results
- Correlating performance changes with specific commits
- Automatic reproducibility without manual tracking

## Step 4: Create CI/CD Integration

Set up automated evaluation in GitHub Actions:

```yaml title=".github/workflows/agent-evaluation.yml"
name: Agent Evaluation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  evaluate-agent:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install dottxt-eval
        # Add your other dependencies here

    - name: Run Agent Evaluation
      run: |
        pytest eval_agent_workflows.py \
          --experiment "agent_ci_${{ github.run_number }}" \
          --storage sqlite://agent_results.db

    - name: Upload Results Database
      uses: actions/upload-artifact@v3
      with:
        name: agent-evaluation-results
        path: agent_results.db

    - name: Show Evaluation Summary
      run: |
        doteval show "agent_ci_${{ github.run_number }}" \
          --storage sqlite://agent_results.db
```

For local development, create a simple script:

```bash title="run_evaluation.sh"
#!/bin/bash

# Generate unique experiment name with timestamp
EXPERIMENT_NAME="agent_dev_$(date +%Y%m%d_%H%M%S)"

echo "Running agent evaluation: $EXPERIMENT_NAME"

pytest eval_agent_workflows.py \
  --experiment "$EXPERIMENT_NAME" \
  --storage sqlite://agent_results.db

echo "Evaluation complete. View results with:"
echo "doteval show $EXPERIMENT_NAME --storage sqlite://agent_results.db"
```

Make it executable and run:

```bash
chmod +x run_evaluation.sh
./run_evaluation.sh
```

## Step 5: Track Performance Over Time

Query results across multiple runs:

```bash
# List all evaluations
doteval list --storage sqlite://agent_results.db

# Compare specific experiments
doteval show agent_ci_123 --storage sqlite://agent_results.db
doteval show agent_ci_124 --storage sqlite://agent_results.db

# Show only success rates
doteval show agent_ci_123 --storage sqlite://agent_results.db | grep "Success Rate"
```

Create a performance tracking script:

```python title="track_performance.py"
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def analyze_performance():
    """Analyze agent performance trends over time."""
    conn = sqlite3.connect('agent_results.db')

    # Query session performance data
    query = """
    SELECT
        name,
        created_at,
        success_rate,
        total_samples,
        git_commit
    FROM sessions
    WHERE name LIKE 'agent_ci_%'
    ORDER BY created_at
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Plot performance trends
    plt.figure(figsize=(12, 6))
    plt.plot(df['created_at'], df['success_rate'], marker='o')
    plt.title('Agent Performance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Success Rate')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('agent_performance_trend.png')
    plt.show()

    # Print summary statistics
    print(f"Latest success rate: {df['success_rate'].iloc[-1]:.2%}")
    print(f"Average success rate: {df['success_rate'].mean():.2%}")
    print(f"Best performance: {df['success_rate'].max():.2%}")
    print(f"Worst performance: {df['success_rate'].min():.2%}")

if __name__ == "__main__":
    analyze_performance()
```

Run the analysis:

```bash
python track_performance.py
```

## Step 6: Add Performance Alerts

Create a simple alerting script for CI/CD:

```python title="check_performance_regression.py"
import sqlite3
import sys

def check_for_regression(experiment_name, threshold=0.1):
    """Check if latest run shows significant performance regression."""
    conn = sqlite3.connect('agent_results.db')

    # Get latest and previous results
    query = """
    SELECT success_rate
    FROM sessions
    WHERE name LIKE 'agent_ci_%'
    ORDER BY created_at DESC
    LIMIT 2
    """

    results = conn.execute(query).fetchall()
    conn.close()

    if len(results) < 2:
        print("Not enough data for regression analysis")
        return True

    latest_rate = results[0][0]
    previous_rate = results[1][0]

    regression = previous_rate - latest_rate

    if regression > threshold:
        print(f"⚠️  Performance regression detected!")
        print(f"Previous: {previous_rate:.2%}")
        print(f"Latest: {latest_rate:.2%}")
        print(f"Regression: {regression:.2%}")
        return False
    else:
        print(f"✅ Performance stable: {latest_rate:.2%}")
        return True

if __name__ == "__main__":
    experiment_name = sys.argv[1] if len(sys.argv) > 1 else None
    success = check_for_regression(experiment_name)
    sys.exit(0 if success else 1)
```

Add to your CI/CD workflow:

```yaml
- name: Check for Performance Regression
  run: |
    python check_performance_regression.py "agent_ci_${{ github.run_number }}"
```

## What you've learned

You now understand:

1. **Complex evaluations** - Building multi-step agent workflow evaluations
2. **SQLite integration** - Using database storage for better querying and CI/CD
3. **Git tracking** - Leveraging automatic git metadata for reproducibility
4. **CI/CD automation** - Setting up pipelines for continuous evaluation
5. **Performance monitoring** - Tracking trends and detecting regressions over time
6. **Production deployment** - Best practices for evaluation pipelines at scale

## Production Best Practices

For production evaluation pipelines:

- ✅ Use SQLite storage for better performance and querying
- ✅ Leverage doteval's automatic git metadata capture
- ✅ Set up CI/CD automation for every code change
- ✅ Track performance trends over time
- ✅ Alert on significant regressions
- ✅ Archive evaluation databases for historical analysis

## Conclusion

Congratulations! You now have a complete, production-ready evaluation pipeline that scales with your development workflow. You've learned to build complex evaluations, optimize performance, manage resources efficiently, and integrate with CI/CD systems for continuous monitoring.
