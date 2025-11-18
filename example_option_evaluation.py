"""
Example Usage of Option Evaluation Skill

This script demonstrates various use cases for the Option Evaluation Skill,
including technology selection, hiring decisions, and investment analysis.

Run this script to see the skill in action:
    python example_option_evaluation.py
"""

from option_evaluator import (
    OptionEvaluator, Option, Criterion,
    OptimizationType, EvaluationMethod,
    quick_evaluate, compare_methods
)
import json


def example_1_cloud_provider_selection():
    """Example 1: Selecting a cloud provider for a new project."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Cloud Provider Selection")
    print("=" * 70)
    print("\nScenario: Choose the best cloud provider for a new web application")
    print("Criteria: Cost, Performance, Security, Support Quality, Ease of Use\n")

    # Define criteria
    criteria = [
        Criterion(
            name="monthly_cost",
            weight=0.25,
            optimization=OptimizationType.MINIMIZE,
            description="Monthly infrastructure cost in USD",
            threshold=5000  # Must be under $5000/month
        ),
        Criterion(
            name="performance_score",
            weight=0.25,
            optimization=OptimizationType.MAXIMIZE,
            description="Performance benchmark score (0-100)"
        ),
        Criterion(
            name="security_rating",
            weight=0.20,
            optimization=OptimizationType.MAXIMIZE,
            description="Security compliance rating (0-100)"
        ),
        Criterion(
            name="support_quality",
            weight=0.15,
            optimization=OptimizationType.MAXIMIZE,
            description="Support quality score (0-100)"
        ),
        Criterion(
            name="ease_of_use",
            weight=0.15,
            optimization=OptimizationType.MAXIMIZE,
            description="Developer ease-of-use rating (0-100)"
        )
    ]

    # Define options
    options = [
        Option(
            id="aws",
            name="Amazon Web Services",
            description="Industry leader with comprehensive services",
            attributes={
                "monthly_cost": 3500,
                "performance_score": 92,
                "security_rating": 95,
                "support_quality": 85,
                "ease_of_use": 75
            },
            metadata={"region": "us-east-1", "years_in_business": 17}
        ),
        Option(
            id="azure",
            name="Microsoft Azure",
            description="Strong enterprise integration",
            attributes={
                "monthly_cost": 3800,
                "performance_score": 90,
                "security_rating": 93,
                "support_quality": 88,
                "ease_of_use": 80
            },
            metadata={"region": "eastus", "years_in_business": 14}
        ),
        Option(
            id="gcp",
            name="Google Cloud Platform",
            description="Excellent for data analytics and ML",
            attributes={
                "monthly_cost": 3200,
                "performance_score": 89,
                "security_rating": 91,
                "support_quality": 80,
                "ease_of_use": 85
            },
            metadata={"region": "us-central1", "years_in_business": 12}
        ),
        Option(
            id="digitalocean",
            name="DigitalOcean",
            description="Simple and developer-friendly",
            attributes={
                "monthly_cost": 2500,
                "performance_score": 78,
                "security_rating": 82,
                "support_quality": 75,
                "ease_of_use": 95
            },
            metadata={"region": "nyc1", "years_in_business": 12}
        )
    ]

    # Evaluate using TOPSIS method
    evaluator = OptionEvaluator(
        criteria=criteria,
        method=EvaluationMethod.TOPSIS,
        enable_sensitivity_analysis=True
    )

    result = evaluator.evaluate(options)

    # Display results
    print(result.explanation)

    print("\n" + "-" * 70)
    print("Complete Rankings:")
    print("-" * 70)
    for rank, (opt_id, score) in enumerate(result.ranked_options, 1):
        opt = next(o for o in options if o.id == opt_id)
        print(f"{rank}. {opt.name:30s} - Score: {score:.4f}")

    # Show detailed breakdown for winner
    print("\n" + "-" * 70)
    print(f"Detailed Analysis for Winner: {result.best_option_id}")
    print("-" * 70)
    best_score = result.get_score(result.best_option_id)
    for crit_name, reasoning in best_score.reasoning.items():
        print(f"{crit_name:20s}: {reasoning}")

    # Sensitivity analysis
    if result.sensitivity_analysis:
        print("\n" + "-" * 70)
        print("Sensitivity Analysis (Decision Robustness)")
        print("-" * 70)
        print("How stable is the decision if we change criterion weights by ±20%?\n")
        for criterion, stability in result.sensitivity_analysis['rank_stability'].items():
            stability_pct = stability * 100
            status = "ROBUST" if stability == 1.0 else "SENSITIVE"
            print(f"  {criterion:20s}: {stability_pct:5.1f}% stable - {status}")


def example_2_hiring_decision():
    """Example 2: Hiring decision for a software engineering position."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Hiring Decision")
    print("=" * 70)
    print("\nScenario: Select the best candidate for Senior Software Engineer")
    print("Criteria: Technical Skills, Experience, Cultural Fit, Salary, Communication\n")

    # Quick evaluation using dictionary format
    options = [
        {
            "id": "candidate_alice",
            "name": "Alice Chen",
            "description": "10 years experience, Python/Go expert",
            "attributes": {
                "technical_skills": 95,
                "years_experience": 10,
                "cultural_fit": 85,
                "salary_expectation": 150000,
                "communication": 90
            },
            "metadata": {"previous_company": "Google", "education": "MS CS"}
        },
        {
            "id": "candidate_bob",
            "name": "Bob Martinez",
            "description": "7 years experience, full-stack generalist",
            "attributes": {
                "technical_skills": 82,
                "years_experience": 7,
                "cultural_fit": 92,
                "salary_expectation": 130000,
                "communication": 88
            },
            "metadata": {"previous_company": "Startup", "education": "BS CS"}
        },
        {
            "id": "candidate_carol",
            "name": "Carol Johnson",
            "description": "12 years experience, distributed systems specialist",
            "attributes": {
                "technical_skills": 98,
                "years_experience": 12,
                "cultural_fit": 78,
                "salary_expectation": 170000,
                "communication": 85
            },
            "metadata": {"previous_company": "Amazon", "education": "PhD CS"}
        }
    ]

    criteria = [
        {"name": "technical_skills", "weight": 0.30, "optimization": "maximize"},
        {"name": "years_experience", "weight": 0.20, "optimization": "maximize"},
        {"name": "cultural_fit", "weight": 0.25, "optimization": "maximize"},
        {"name": "salary_expectation", "weight": 0.15, "optimization": "minimize"},
        {"name": "communication", "weight": 0.10, "optimization": "maximize"}
    ]

    # Evaluate using quick_evaluate function
    result = quick_evaluate(options, criteria, method="weighted_sum")

    print(f"Best Candidate: {result['best_option']}")
    print(f"\n{result['explanation']}")

    print("\n" + "-" * 70)
    print("All Candidates Ranked:")
    print("-" * 70)
    for rank, (candidate_id, score) in enumerate(result['rankings'], 1):
        candidate = next(c for c in options if c['id'] == candidate_id)
        print(f"{rank}. {candidate['name']:20s} - Score: {score:.4f}")
        scores = result['scores'][candidate_id]
        print(f"   Technical: {scores['raw_values']['technical_skills']:.0f}, "
              f"Experience: {scores['raw_values']['years_experience']:.0f}yr, "
              f"Cultural Fit: {scores['raw_values']['cultural_fit']:.0f}, "
              f"Salary: ${scores['raw_values']['salary_expectation']:,.0f}")


def example_3_investment_portfolio():
    """Example 3: Investment portfolio allocation decision."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Investment Portfolio Allocation")
    print("=" * 70)
    print("\nScenario: Allocate $100K across investment opportunities")
    print("Criteria: Expected Return, Risk, Liquidity, Time Horizon\n")

    criteria = [
        Criterion(
            name="expected_return",
            weight=0.35,
            optimization=OptimizationType.MAXIMIZE,
            description="Expected annual return (%)"
        ),
        Criterion(
            name="risk_score",
            weight=0.30,
            optimization=OptimizationType.MINIMIZE,
            description="Risk score (0-100, lower is safer)",
            threshold=70  # Maximum acceptable risk
        ),
        Criterion(
            name="liquidity",
            weight=0.20,
            optimization=OptimizationType.MAXIMIZE,
            description="Liquidity score (0-100, higher is more liquid)"
        ),
        Criterion(
            name="time_horizon",
            weight=0.15,
            optimization=OptimizationType.MINIMIZE,
            description="Time to maturity (years)"
        )
    ]

    options = [
        Option(
            id="tech_stocks",
            name="Technology Stocks ETF",
            description="Diversified tech stock portfolio",
            attributes={
                "expected_return": 12.5,
                "risk_score": 65,
                "liquidity": 95,
                "time_horizon": 1
            }
        ),
        Option(
            id="bonds",
            name="Corporate Bonds",
            description="Investment-grade corporate bonds",
            attributes={
                "expected_return": 5.5,
                "risk_score": 25,
                "liquidity": 75,
                "time_horizon": 5
            }
        ),
        Option(
            id="real_estate",
            name="REIT Fund",
            description="Real estate investment trust",
            attributes={
                "expected_return": 8.0,
                "risk_score": 45,
                "liquidity": 80,
                "time_horizon": 3
            }
        ),
        Option(
            id="crypto",
            name="Cryptocurrency Index",
            description="Diversified crypto holdings",
            attributes={
                "expected_return": 25.0,
                "risk_score": 85,  # Exceeds risk threshold!
                "liquidity": 90,
                "time_horizon": 1
            }
        ),
        Option(
            id="dividend_stocks",
            name="Dividend Aristocrats",
            description="High-quality dividend-paying stocks",
            attributes={
                "expected_return": 7.5,
                "risk_score": 40,
                "liquidity": 92,
                "time_horizon": 2
            }
        )
    ]

    # Evaluate
    evaluator = OptionEvaluator(
        criteria=criteria,
        method=EvaluationMethod.WEIGHTED_SUM
    )

    result = evaluator.evaluate(options)

    print(result.explanation)

    print("\n" + "-" * 70)
    print("Investment Options Ranked:")
    print("-" * 70)
    for rank, (opt_id, score) in enumerate(result.ranked_options, 1):
        opt = next(o for o in options if o.id == opt_id)
        details = result.get_score(opt_id)
        print(f"{rank}. {opt.name:30s} - Score: {score:.4f}")
        print(f"   Return: {details.raw_values['expected_return']:5.1f}%, "
              f"Risk: {details.raw_values['risk_score']:5.1f}, "
              f"Liquidity: {details.raw_values['liquidity']:5.1f}, "
              f"Time: {details.raw_values['time_horizon']:3.0f}yr")

    # Note about filtered options
    print("\n" + "-" * 70)
    print(f"Note: Crypto option was filtered out due to risk > threshold ({criteria[1].threshold})")


def example_4_method_comparison():
    """Example 4: Compare different evaluation methods."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Comparing Evaluation Methods")
    print("=" * 70)
    print("\nScenario: Product feature prioritization using different methods\n")

    criteria = [
        Criterion(name="user_value", weight=0.4, optimization=OptimizationType.MAXIMIZE),
        Criterion(name="dev_cost", weight=0.3, optimization=OptimizationType.MINIMIZE),
        Criterion(name="time_to_market", weight=0.3, optimization=OptimizationType.MINIMIZE)
    ]

    options = [
        Option(
            id="feature_search",
            name="Advanced Search",
            attributes={"user_value": 85, "dev_cost": 40, "time_to_market": 8}
        ),
        Option(
            id="feature_mobile",
            name="Mobile App",
            attributes={"user_value": 95, "dev_cost": 80, "time_to_market": 16}
        ),
        Option(
            id="feature_analytics",
            name="Analytics Dashboard",
            attributes={"user_value": 70, "dev_cost": 30, "time_to_market": 6}
        ),
        Option(
            id="feature_social",
            name="Social Integration",
            attributes={"user_value": 60, "dev_cost": 25, "time_to_market": 4}
        )
    ]

    # Compare methods
    results = compare_methods(options, criteria)

    print("Method Comparison Results:")
    print("-" * 70)
    for method, best_option in results.items():
        opt = next(o for o in options if o.id == best_option)
        print(f"{method.value:25s} → {opt.name}")

    # Show detailed results for each method
    for method in [EvaluationMethod.WEIGHTED_SUM, EvaluationMethod.TOPSIS, EvaluationMethod.MULTI_OBJECTIVE]:
        print(f"\n{method.value.upper()} Method Rankings:")
        evaluator = OptionEvaluator(criteria, method=method)
        result = evaluator.evaluate(options)
        for rank, (opt_id, score) in enumerate(result.ranked_options, 1):
            opt = next(o for o in options if o.id == opt_id)
            print(f"  {rank}. {opt.name:25s} - {score:.4f}")


def example_5_dynamic_data():
    """Example 5: Using dynamic data sources (simulation)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Dynamic Data Fetching")
    print("=" * 70)
    print("\nScenario: Vendor selection with live pricing data\n")

    # Simulate external data sources
    pricing_database = {
        "vendor_a": 12500,
        "vendor_b": 15000,
        "vendor_c": 11800
    }

    quality_scores = {
        "vendor_a": 85,
        "vendor_b": 92,
        "vendor_c": 88
    }

    def fetch_price(vendor_id: str, metadata: dict) -> float:
        """Simulate fetching price from external API."""
        print(f"  [Fetching price for {vendor_id}...]")
        return pricing_database.get(vendor_id, 0)

    def fetch_quality(vendor_id: str, metadata: dict) -> float:
        """Simulate fetching quality score from database."""
        print(f"  [Fetching quality score for {vendor_id}...]")
        return quality_scores.get(vendor_id, 0)

    # Define criteria with data sources
    criteria = [
        Criterion(
            name="price",
            weight=0.5,
            optimization=OptimizationType.MINIMIZE,
            data_source=fetch_price  # Dynamic pricing
        ),
        Criterion(
            name="quality",
            weight=0.3,
            optimization=OptimizationType.MAXIMIZE,
            data_source=fetch_quality  # Dynamic quality scores
        ),
        Criterion(
            name="delivery_time",
            weight=0.2,
            optimization=OptimizationType.MINIMIZE
        )
    ]

    # Options without price/quality (will be fetched)
    options = [
        Option(
            id="vendor_a",
            name="Vendor Alpha",
            attributes={"delivery_time": 14},  # Only delivery time provided
            metadata={"location": "USA", "certified": True}
        ),
        Option(
            id="vendor_b",
            name="Vendor Beta",
            attributes={"delivery_time": 10},
            metadata={"location": "EU", "certified": True}
        ),
        Option(
            id="vendor_c",
            name="Vendor Gamma",
            attributes={"delivery_time": 21},
            metadata={"location": "Asia", "certified": False}
        )
    ]

    print("Fetching missing data from external sources...")
    evaluator = OptionEvaluator(criteria, method=EvaluationMethod.WEIGHTED_SUM)
    result = evaluator.evaluate(options, fetch_missing_data=True)

    print("\n" + result.explanation)

    print("\n" + "-" * 70)
    print("Vendor Rankings with Fetched Data:")
    print("-" * 70)
    for rank, (opt_id, score) in enumerate(result.ranked_options, 1):
        opt = next(o for o in options if o.id == opt_id)
        details = result.get_score(opt_id)
        print(f"{rank}. {opt.name:20s} - Score: {score:.4f}")
        print(f"   Price: ${details.raw_values['price']:,.0f}, "
              f"Quality: {details.raw_values['quality']:.0f}, "
              f"Delivery: {details.raw_values['delivery_time']:.0f} days")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print(" OPTION EVALUATION SKILL - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    example_1_cloud_provider_selection()
    example_2_hiring_decision()
    example_3_investment_portfolio()
    example_4_method_comparison()
    example_5_dynamic_data()

    print("\n" + "=" * 70)
    print(" All examples completed!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  1. Different methods can yield different results")
    print("  2. Weights significantly impact the final decision")
    print("  3. Thresholds help filter out unacceptable options")
    print("  4. Sensitivity analysis shows decision robustness")
    print("  5. Dynamic data fetching enables real-time evaluation")
    print("\nFor more details, see OPTION_EVALUATOR_README.md")


if __name__ == "__main__":
    main()
