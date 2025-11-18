# Scenario Simulation - Quick Start Guide

## 30-Second Start

1. **Invoke the skill** in Claude Code
2. **Describe what you want to simulate**
3. **Provide 3-5 key variables** that can change
4. **Get results** with best/worst/expected scenarios

## Common Requests

### Business Decision
```
"I'm deciding whether to hire 2 more engineers or outsource development.
Help me simulate the cost and timeline impacts over 6 months."
```

### Technical Decision
```
"Should we migrate to microservices or stick with our monolith?
Model the scenarios for development time, performance, and operational costs."
```

### Risk Assessment
```
"What's the financial impact if our main supplier fails?
Simulate best/worst/expected scenarios for finding alternatives."
```

## What You'll Get

✅ **Scenario Comparison Table** - Side-by-side results
✅ **Decision Tree** - Visual decision paths (when applicable)
✅ **Executable Code** - Python or TypeScript simulation
✅ **Sensitivity Analysis** - Which variables matter most
✅ **Recommendations** - What to do based on the analysis

## Variable Types

Most simulations need:
- **Inputs**: Things you control (price, team size, budget)
- **Assumptions**: External factors (market size, competition, growth rate)
- **Outcomes**: What you're measuring (revenue, time, quality, risk)

## Scenarios Explained

| Scenario | When to Use | Example |
|----------|-------------|---------|
| **Best Case** | Optimistic assumptions, everything goes right | 20% market share, low costs |
| **Expected Case** | Realistic middle ground, most likely outcome | 5% market share, normal costs |
| **Worst Case** | Pessimistic assumptions, things go wrong | 1% market share, high costs |
| **Custom** | Specific "what-if" you want to test | What if we get 50% of our target? |

## Decision Trees vs. Simulations

### Use Decision Trees When:
- Clear decision points (yes/no, A/B/C choices)
- Sequential decisions matter
- Want to visualize paths
- Calculating expected values

**Example**: Should we build in-house or buy a solution, then customize or use as-is?

### Use Code Simulations When:
- Complex calculations needed
- Many variables interact
- Need statistical analysis
- Want Monte Carlo simulation

**Example**: Revenue projection with 10 interacting variables over 24 months

### Use Both When:
- Major strategic decisions
- High uncertainty
- Multiple stakeholders need different views

## Quick Examples

### Example 1: Pricing Decision (2 minutes)

**Request:**
```
"Help me decide between $49, $79, or $99/month pricing.
We have 1000 trial users, expecting 5-10% conversion,
and $20K monthly costs."
```

**You'll Get:**
- Revenue projections for each price point
- Break-even analysis
- Sensitivity to conversion rate
- Recommended pricing with reasoning

---

### Example 2: Hiring Decision (3 minutes)

**Request:**
```
"Should we hire 3 junior devs or 1 senior dev?
Project is 6 months, budget is $300K,
complexity is high but timeline is flexible."
```

**You'll Get:**
- Cost comparison
- Timeline projections
- Quality/risk trade-offs
- Decision tree with recommendations

---

### Example 3: Infrastructure Scaling (5 minutes)

**Request:**
```
"Our traffic is growing 10-30% monthly.
Current capacity: 10K req/sec, costs $5K/month.
Outages cost $25K/hour.
Should we scale proactively or reactively?"
```

**You'll Get:**
- 6-month capacity projections
- Cost models for both strategies
- Risk-adjusted total costs
- Recommendation with monitoring thresholds

## Tips for Better Results

### ✅ DO:
- Provide realistic ranges for variables
- Mention constraints or requirements
- Share what you're optimizing for (cost, time, quality, risk)
- Include your domain context

### ❌ DON'T:
- Provide single point estimates for everything (makes simulation pointless)
- Include 20+ variables upfront (start with 3-5 most important)
- Forget about probabilities (what's likely vs. possible)
- Skip validation (garbage in, garbage out)

## Interpreting Results

### When Results Show:
- **Wide gap between scenarios**: High uncertainty, gather more data
- **Expected case is unprofitable**: Reconsider the decision or change assumptions
- **One variable dominates**: Focus on validating/controlling that variable
- **All scenarios similar**: Decision is robust, proceed with confidence

## Next Steps After Simulation

1. **Validate Assumptions**: Are the input ranges realistic?
2. **Test Sensitivities**: Run "what-if" on uncertain variables
3. **Set Milestones**: Define checkpoints to reassess
4. **Plan for Worst Case**: Have contingencies ready
5. **Monitor Actuals**: Track real results vs. projections

## Advanced Usage

Once comfortable with basics:

- **Monte Carlo**: Run 1000s of iterations for probability distributions
- **Time Series**: Model month-by-month changes over time
- **Multi-Objective**: Optimize for multiple goals simultaneously
- **Bayesian Updates**: Refine scenarios as new data arrives

## Common Pitfalls

1. **Overfitting**: Making model too complex for available data
2. **Overconfidence**: Treating expected case as certain
3. **Ignoring Correlations**: Variables often move together
4. **Static Models**: Forgetting that conditions change over time
5. **Analysis Paralysis**: Simulating instead of deciding

## When to Skip Simulation

Simulations aren't needed for:
- Trivial decisions with obvious outcomes
- Decisions already made (unless validating)
- Situations with only one viable option
- When you need to act immediately

## Getting Help

If simulation results are unclear:
- Ask for sensitivity analysis
- Request simpler model with fewer variables
- Ask for visual decision tree
- Request explanation of key assumptions
- Ask for comparison with industry benchmarks

## Template Files

After first use, you'll have:
- `scenario_simulator.py` - Python implementation
- `scenario_simulator.ts` - TypeScript implementation
- Example notebooks or scripts for your specific case

You can modify and reuse these for similar scenarios!

---

## Remember:

> **The goal isn't perfect predictions—it's better decisions.**

Simulations help you:
- Understand trade-offs
- Quantify risks
- Challenge assumptions
- Make informed choices

---

**Ready to start? Just describe what you want to simulate!**
