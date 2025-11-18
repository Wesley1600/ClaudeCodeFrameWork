# Option Evaluation Skill

A comprehensive Multi-Criteria Decision Analysis (MCDA) skill that evaluates multiple options or recommendations and selects the best one based on structured criteria.

## Overview

The Option Evaluation Skill provides a robust framework for making data-driven decisions when faced with multiple alternatives. It supports various evaluation methods, weighted criteria, and structured reasoning to help you choose the best option based on quantitative and qualitative factors.

## Features

- **Multiple Evaluation Methods**
  - Weighted Sum Model (WSM) - Simple and intuitive
  - TOPSIS - Technique for Order of Preference by Similarity to Ideal Solution
  - Multi-Objective - Pareto-optimal solution finding

- **Flexible Criteria System**
  - Support for both minimization (cost, risk) and maximization (quality, performance)
  - Weighted criteria with automatic normalization
  - Threshold filtering to eliminate unacceptable options
  - Dynamic data fetching through custom data sources

- **Structured Reasoning**
  - Detailed explanations for each score
  - Comparative analysis between options
  - Sensitivity analysis to test decision robustness

- **Integration Capabilities**
  - Call other skills or functions for data inputs
  - Support for external data sources
  - Extensible architecture for custom scoring functions

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Example

```python
from option_evaluator import quick_evaluate

# Define options
options = [
    {
        "id": "option_a",
        "name": "Cloud Solution A",
        "attributes": {
            "cost": 1000,
            "performance": 85,
            "risk": 3
        }
    },
    {
        "id": "option_b",
        "name": "Cloud Solution B",
        "attributes": {
            "cost": 1500,
            "performance": 95,
            "risk": 2
        }
    }
]

# Define criteria
criteria = [
    {"name": "cost", "weight": 0.4, "optimization": "minimize"},
    {"name": "performance", "weight": 0.4, "optimization": "maximize"},
    {"name": "risk", "weight": 0.2, "optimization": "minimize"}
]

# Evaluate
result = quick_evaluate(options, criteria, method="weighted_sum")

print(f"Best option: {result['best_option']}")
print(f"Explanation:\n{result['explanation']}")
```

### Advanced Example with Classes

```python
from option_evaluator import (
    OptionEvaluator, Option, Criterion,
    OptimizationType, EvaluationMethod
)

# Create criteria
criteria = [
    Criterion(
        name="cost",
        weight=0.3,
        optimization=OptimizationType.MINIMIZE,
        description="Total cost of ownership",
        threshold=2000  # Maximum acceptable cost
    ),
    Criterion(
        name="user_satisfaction",
        weight=0.4,
        optimization=OptimizationType.MAXIMIZE,
        description="User satisfaction score (0-100)"
    ),
    Criterion(
        name="implementation_time",
        weight=0.3,
        optimization=OptimizationType.MINIMIZE,
        description="Time to implement (days)"
    )
]

# Create options
options = [
    Option(
        id="solution_1",
        name="In-house Development",
        description="Build custom solution internally",
        attributes={
            "cost": 1500,
            "user_satisfaction": 90,
            "implementation_time": 120
        },
        metadata={"team": "engineering", "priority": "high"}
    ),
    Option(
        id="solution_2",
        name="Commercial Software",
        description="Purchase off-the-shelf solution",
        attributes={
            "cost": 1200,
            "user_satisfaction": 75,
            "implementation_time": 30
        },
        metadata={"team": "procurement", "priority": "medium"}
    ),
    Option(
        id="solution_3",
        name="Hybrid Approach",
        description="Combine custom + commercial components",
        attributes={
            "cost": 1800,
            "user_satisfaction": 85,
            "implementation_time": 60
        },
        metadata={"team": "engineering", "priority": "high"}
    )
]

# Create evaluator
evaluator = OptionEvaluator(
    criteria=criteria,
    method=EvaluationMethod.TOPSIS,
    enable_sensitivity_analysis=True
)

# Evaluate
result = evaluator.evaluate(options)

# Display results
print(result.explanation)
print(f"\nTop 3 options:")
for rank, (opt_id, score) in enumerate(result.get_top_n(3), 1):
    opt = next(o for o in options if o.id == opt_id)
    print(f"{rank}. {opt.name}: {score:.3f}")

# Show detailed reasoning
best_score = result.get_score(result.best_option_id)
print(f"\nDetailed reasoning for {result.best_option_id}:")
for criterion_name, reasoning in best_score.reasoning.items():
    print(f"  {criterion_name}: {reasoning}")
```

## Evaluation Methods

### 1. Weighted Sum Model (WSM)

The simplest and most intuitive method. Normalizes all criteria to [0,1], applies weights, and sums them up.

**Best for:**
- Straightforward decision-making
- When all criteria are measurable and comparable
- Quick evaluations

**Formula:**
```
Score = Σ(weight_i × normalized_value_i)
```

### 2. TOPSIS

Finds the option closest to the ideal solution and farthest from the negative-ideal solution.

**Best for:**
- Complex multi-criteria decisions
- When you want to consider both best and worst scenarios
- More nuanced comparisons

**Process:**
1. Normalize decision matrix
2. Apply weights
3. Determine ideal and negative-ideal solutions
4. Calculate Euclidean distances
5. Compute closeness coefficient

### 3. Multi-Objective (Pareto)

Identifies Pareto-optimal solutions (not dominated by any other option).

**Best for:**
- Trade-off analysis
- When no single "best" solution exists
- Understanding the solution space

## Dynamic Data Integration

You can fetch criterion values dynamically using custom data sources:

```python
def fetch_cost_from_api(option_id: str, metadata: dict) -> float:
    """Fetch cost data from external API."""
    # Call pricing API
    response = api_client.get_price(option_id)
    return response['total_cost']

def calculate_risk_score(option_id: str, metadata: dict) -> float:
    """Calculate risk using another skill/model."""
    # Could call another Claude Code skill here
    risk_factors = analyze_risk_factors(option_id)
    return risk_factors['composite_score']

# Use in criteria
criteria = [
    Criterion(
        name="cost",
        weight=0.5,
        optimization=OptimizationType.MINIMIZE,
        data_source=fetch_cost_from_api  # Dynamic data fetching
    ),
    Criterion(
        name="risk",
        weight=0.5,
        optimization=OptimizationType.MINIMIZE,
        data_source=calculate_risk_score  # Integration with other skills
    )
]
```

## Sensitivity Analysis

Enable sensitivity analysis to understand how robust your decision is:

```python
evaluator = OptionEvaluator(
    criteria=criteria,
    method=EvaluationMethod.WEIGHTED_SUM,
    enable_sensitivity_analysis=True
)

result = evaluator.evaluate(options)

# Check sensitivity
if result.sensitivity_analysis:
    print("\nSensitivity Analysis:")
    for criterion, stability in result.sensitivity_analysis['rank_stability'].items():
        print(f"  {criterion}: {stability:.1%} stable")
```

This shows how changing each criterion's weight by ±20% affects the final ranking.

## Use Cases

### 1. Technology Selection

```python
# Evaluate cloud providers
options = [aws_option, azure_option, gcp_option]
criteria = [cost, performance, security, support, integration_ease]
```

### 2. Hiring Decisions

```python
# Evaluate job candidates
options = [candidate_a, candidate_b, candidate_c]
criteria = [experience, cultural_fit, technical_skills, salary_expectations]
```

### 3. Investment Analysis

```python
# Evaluate investment opportunities
options = [stock_a, stock_b, bond_c, real_estate_d]
criteria = [expected_return, risk, liquidity, time_horizon]
```

### 4. Product Features

```python
# Prioritize feature development
options = [feature_1, feature_2, feature_3]
criteria = [user_value, implementation_cost, technical_risk, time_to_market]
```

### 5. Vendor Selection

```python
# Choose suppliers
options = [vendor_a, vendor_b, vendor_c]
criteria = [price, quality, delivery_time, reliability, sustainability]
```

## API Reference

### Classes

#### `Option`
Represents an alternative to evaluate.

**Attributes:**
- `id: str` - Unique identifier
- `name: str` - Human-readable name
- `description: str` - Detailed description
- `attributes: Dict[str, float]` - Criterion values
- `metadata: Dict[str, Any]` - Additional data

#### `Criterion`
Represents an evaluation criterion.

**Attributes:**
- `name: str` - Criterion name
- `weight: float` - Importance weight (0-1)
- `optimization: OptimizationType` - MINIMIZE or MAXIMIZE
- `description: str` - What this measures
- `threshold: Optional[float]` - Filter threshold
- `data_source: Optional[Callable]` - Dynamic data fetcher

#### `OptionEvaluator`
Main evaluation engine.

**Methods:**
- `evaluate(options, fetch_missing_data=True)` - Evaluate all options
- Returns `EvaluationResult` with rankings and detailed scores

#### `EvaluationResult`
Complete evaluation results.

**Attributes:**
- `ranked_options: List[Tuple[str, float]]` - Sorted rankings
- `scores: Dict[str, EvaluationScore]` - Detailed scores
- `best_option_id: str` - Top choice
- `explanation: str` - Human-readable summary
- `sensitivity_analysis: Optional[Dict]` - Robustness analysis

**Methods:**
- `get_top_n(n)` - Get top N options
- `get_score(option_id)` - Get detailed score for option

### Functions

#### `quick_evaluate(options, criteria, method)`
Convenience function for dictionary-based evaluation.

#### `compare_methods(options, criteria)`
Compare results across different evaluation methods.

## Best Practices

1. **Choose Appropriate Weights**
   - Weights should reflect true importance
   - Consider using sensitivity analysis to validate
   - Involve stakeholders in weight assignment

2. **Normalize Criteria**
   - The skill handles normalization automatically
   - Ensure raw values are on comparable scales when possible

3. **Use Thresholds Wisely**
   - Set thresholds for must-have requirements
   - Filters out unacceptable options early

4. **Validate Results**
   - Compare multiple methods
   - Run sensitivity analysis
   - Check if results align with intuition

5. **Document Assumptions**
   - Record why certain weights were chosen
   - Document data sources
   - Keep track of evaluation context

## Limitations

- Assumes criteria independence (no interactions between criteria)
- Linear weighting may not capture complex preferences
- Requires quantifiable criteria (qualitative factors need conversion)
- Garbage in, garbage out (quality depends on input data)

## Future Enhancements

- [ ] Support for fuzzy logic criteria
- [ ] Group decision-making (aggregating multiple evaluators)
- [ ] Machine learning-based weight optimization
- [ ] Interactive web UI for evaluation
- [ ] Export to decision documentation formats

## Contributing

This skill is part of the Claude Code Framework. To extend or modify:

1. Add new evaluation methods by implementing scoring logic
2. Create custom data source integrations
3. Add new sensitivity analysis techniques
4. Improve explanation generation

## License

Part of Claude Code Framework - Internal Use

## Version History

- **1.0.0** (2025-11-18): Initial release
  - Weighted Sum, TOPSIS, and Multi-Objective methods
  - Sensitivity analysis
  - Dynamic data fetching
  - Comprehensive documentation

## Support

For issues or questions about this skill:
- See `example_option_evaluation.py` for more examples
- Check the main documentation in this README
- Review inline code documentation in `option_evaluator.py`
