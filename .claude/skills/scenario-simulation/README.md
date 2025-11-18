# Scenario Simulation Skill

A comprehensive skill for Claude Code that enables sophisticated scenario modeling, decision tree analysis, and impact assessment.

## Overview

The Scenario Simulation Skill helps you model different outcomes based on variable inputs, create decision trees, run simulations, and analyze impacts across best-case, worst-case, and expected scenarios.

## Features

### 1. **Multi-Scenario Analysis**
- Best-case scenarios (optimistic assumptions)
- Worst-case scenarios (pessimistic assumptions)
- Expected-case scenarios (realistic projections)
- Custom scenarios (user-defined combinations)

### 2. **Decision Tree Creation**
- Visual decision trees using Mermaid diagrams
- Path analysis and probability weighting
- Expected value calculations
- Recommended decision paths

### 3. **Simulation Methods**
- **Deterministic Simulations**: Fixed input values
- **Sensitivity Analysis**: Impact of individual variables
- **Monte Carlo Simulations**: Probabilistic modeling with random sampling
- **Time-Series Projections**: Multi-period forecasts

### 4. **Implementation Formats**
- Python scripts for data science and analytics
- TypeScript/JavaScript for web applications
- Spreadsheet-style calculations
- Markdown reports and visualizations

### 5. **Analysis Capabilities**
- Comparative scenario analysis
- Sensitivity rankings (which variables matter most)
- Break-even analysis
- Risk assessment and mitigation planning
- ROI calculations

## Installation

The skill is located in `.claude/skills/scenario-simulation.md` and is automatically available in Claude Code.

### Quick Start

1. **Invoke the skill** in Claude Code (method depends on your Claude Code version)
2. **Describe your scenario**: "I want to simulate launching a new product"
3. **Provide variables**: Share what can change (price, demand, costs, etc.)
4. **Review results**: Analyze outputs and iterate as needed

## File Structure

```
.claude/skills/
├── scenario-simulation.md           # Main skill definition
├── README.md                         # This file
├── examples/
│   └── scenario-simulation-example.md  # Example use cases
└── templates/
    ├── scenario_simulator.py         # Python implementation
    └── scenario_simulator.ts         # TypeScript implementation
```

## Usage Examples

### Example 1: Business Decision

```
User: "I'm deciding whether to launch a premium tier for my SaaS product.
       Help me simulate the revenue impact."

Claude: [Uses scenario simulation skill]
        - Identifies variables: pricing, adoption rate, churn, costs
        - Creates best/expected/worst scenarios
        - Runs 12-month projection
        - Provides decision recommendation
```

### Example 2: Technical Architecture

```
User: "Should we scale our infrastructure proactively or wait until we hit limits?"

Claude: [Uses scenario simulation skill]
        - Models traffic growth scenarios
        - Calculates infrastructure costs
        - Assesses outage risks
        - Creates decision tree with cost-benefit analysis
```

### Example 3: Risk Assessment

```
User: "What's the impact of different security breach scenarios?"

Claude: [Uses scenario simulation skill]
        - Defines breach severity levels
        - Models financial and reputational impacts
        - Simulates mitigation effectiveness
        - Recommends risk mitigation strategy
```

## Using the Python Template

```python
from scenario_simulator import ScenarioSimulator, Variable

# Define your variables
variables = [
    Variable(
        name="customer_growth",
        best_case=1000,
        expected_case=500,
        worst_case=100,
        description="New customers per month"
    ),
    # Add more variables...
]

# Define your model
def business_model(inputs):
    revenue = inputs['customer_growth'] * inputs['avg_revenue']
    profit = revenue - inputs['costs']
    return {'revenue': revenue, 'profit': profit}

# Run simulation
sim = ScenarioSimulator(variables)
sim.run_all_scenarios(business_model)
sim.print_summary()

# Sensitivity analysis
sim.sensitivity_analysis('customer_growth', business_model)

# Monte Carlo simulation
mc_results = sim.monte_carlo_simulation(business_model, n_iterations=1000)
```

## Using the TypeScript Template

```typescript
import { ScenarioSimulator, Variable } from './scenario_simulator';

// Define variables
const variables = [
  new Variable({
    name: 'traffic_growth',
    bestCase: 50000,
    expectedCase: 25000,
    worstCase: 5000,
    unit: 'requests/sec'
  })
];

// Define model
const performanceModel = (inputs) => {
  const servers = Math.ceil(inputs.traffic_growth / 1000);
  const cost = servers * 500;
  return { servers, monthly_cost: cost };
};

// Run simulation
const sim = new ScenarioSimulator(variables);
sim.runAllScenarios(performanceModel);
sim.printSummary();
```

## Common Use Cases

### Business & Finance
- Revenue forecasting
- Investment ROI analysis
- Pricing strategy optimization
- Market expansion decisions
- Fundraising scenarios

### Technology & Engineering
- Infrastructure capacity planning
- Performance optimization trade-offs
- Migration risk assessment
- Technology stack decisions
- API rate limit planning

### Project Management
- Timeline estimation (optimistic/pessimistic/realistic)
- Resource allocation
- Budget planning
- Risk mitigation planning
- Team scaling decisions

### Product & Strategy
- Feature prioritization
- A/B test planning
- Market entry strategies
- Competitive response scenarios
- Product roadmap planning

## Best Practices

1. **Start with Clear Objectives**: Define what you're trying to decide or understand
2. **Validate Assumptions**: Ensure input ranges are realistic and grounded in data
3. **Focus on Key Variables**: Start with 3-5 most impactful variables, add complexity as needed
4. **Document Everything**: Record assumptions, sources, and reasoning
5. **Iterate**: Refine models based on feedback and new information
6. **Use Sensitivity Analysis**: Identify which variables matter most
7. **Consider Probabilities**: Weight scenarios by likelihood when possible
8. **Plan for Extremes**: Don't just model the expected case
9. **Make It Actionable**: Connect results to specific decisions or actions
10. **Update Regularly**: Revisit scenarios as conditions change

## Output Deliverables

When using this skill, you typically receive:

1. **Simulation Code**: Python or TypeScript files ready to run
2. **Results Summary**: Markdown report with findings
3. **Data Files**: CSV or JSON with input/output data
4. **Visualizations**: Decision trees, comparison tables, charts
5. **Recommendations**: Actionable insights and next steps

## Advanced Features

### Monte Carlo Simulation

Run thousands of iterations with probabilistic inputs:

```python
results = simulator.monte_carlo_simulation(model_func, n_iterations=10000)
print(results.describe())  # Statistical summary
```

### Sensitivity Analysis

Identify which variables have the most impact:

```python
sensitivity = simulator.sensitivity_analysis('variable_name', model_func)
# Shows how output changes as variable changes
```

### Custom Scenarios

Test specific "what-if" situations:

```python
custom_inputs = {'var1': 100, 'var2': 0.5, 'var3': 'high'}
simulator.run_custom_scenario('optimistic_growth', custom_inputs, model_func)
```

### Time-Series Projections

Model outcomes over multiple time periods:

```python
def time_series_model(inputs, periods=12):
    results = []
    state = initial_state
    for month in range(periods):
        result = calculate_month(state, inputs)
        results.append(result)
        state = update_state(state, result)
    return results
```

## Tips for Effective Simulations

### For Business Decisions
- Include both revenue and cost variables
- Model customer lifetime value, not just initial revenue
- Account for time-to-market and competitive responses
- Consider market saturation and growth limits

### For Technical Decisions
- Model both average and peak loads
- Include failure scenarios and degradation
- Account for scaling delays and costs
- Consider operational complexity

### For Risk Assessment
- Use probability distributions, not just point estimates
- Model cascading failures and dependencies
- Include both likelihood and impact
- Quantify mitigation costs vs. risk reduction

## Troubleshooting

**Problem**: Results seem unrealistic
- **Solution**: Validate input ranges with data or experts

**Problem**: Too many variables to consider
- **Solution**: Start with 3-5 most impactful, use sensitivity analysis to prioritize

**Problem**: Unclear which scenario to believe
- **Solution**: Use Monte Carlo simulation to get probability distributions

**Problem**: Model is too simple / too complex
- **Solution**: Iterate - start simple, add complexity only when needed

## Contributing

To improve this skill:

1. Add new example scenarios to `examples/`
2. Enhance templates with new features
3. Share your custom model functions
4. Document edge cases and solutions

## Resources

- [Decision Analysis Overview](https://en.wikipedia.org/wiki/Decision_analysis)
- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Sensitivity Analysis](https://en.wikipedia.org/wiki/Sensitivity_analysis)
- [Decision Trees](https://en.wikipedia.org/wiki/Decision_tree)

## License

This skill is part of the Claude Code framework and follows the same license terms.

---

## Quick Reference

### Invoking the Skill

The method to invoke depends on your Claude Code setup. Typically:
- Direct invocation in Claude Code interface
- Reference in conversation: "Use the scenario simulation skill to..."

### Key Commands

When using the skill, you can request:
- "Run a scenario simulation for [situation]"
- "Create a decision tree for [choice]"
- "Perform sensitivity analysis on [variable]"
- "Run Monte Carlo simulation with [parameters]"
- "Compare best/worst/expected cases for [decision]"

### Expected Flow

1. **Define** the decision or situation
2. **Identify** variables and ranges
3. **Choose** simulation method
4. **Run** scenarios
5. **Analyze** results
6. **Decide** on action

---

*For questions or issues, consult the main Claude Code documentation or create an issue in your repository.*
