"""
Example script demonstrating the financial analyzer

This script shows how to use the financial_analyzer module to:
1. Load financial data from various sources
2. Compute comprehensive financial ratios
3. Generate insights and reports
"""

import sys
import os

# Add parent directory to path to import financial_analyzer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analyzer import (
    FinancialAnalyzer,
    FinancialStatement,
    analyze_file,
    analyze_dict
)


def example1_from_csv():
    """Example 1: Analyze financial data from CSV file"""
    print("=" * 80)
    print("EXAMPLE 1: Analyzing Financial Data from CSV")
    print("=" * 80)
    print()

    csv_path = os.path.join(
        os.path.dirname(__file__),
        'financial_data',
        'sample_financial_statement.csv'
    )

    try:
        statement, ratios, report = analyze_file(csv_path, file_type='csv')
        print(report)
    except Exception as e:
        print(f"Error: {e}")
        print("Note: Make sure pandas is installed: pip install pandas")


def example2_from_dict():
    """Example 2: Analyze financial data from dictionary"""
    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 2: Analyzing Financial Data from Dictionary")
    print("=" * 80)
    print()

    # Sample data for a tech company (in millions)
    financial_data = {
        'revenue': 2500.0,
        'cost_of_goods_sold': 875.0,
        'gross_profit': 1625.0,
        'operating_expenses': 950.0,
        'operating_income': 675.0,
        'interest_expense': 45.0,
        'net_income': 505.0,
        'cash': 450.0,
        'accounts_receivable': 380.0,
        'inventory': 125.0,
        'current_assets': 1100.0,
        'total_assets': 3850.0,
        'accounts_payable': 290.0,
        'short_term_debt': 150.0,
        'current_liabilities': 580.0,
        'long_term_debt': 800.0,
        'total_liabilities': 1620.0,
        'shareholders_equity': 2230.0,
        'operating_cash_flow': 625.0,
        'capital_expenditures': 225.0,
        'period': 'Q3 2024',
        'currency': 'USD',
        'scale': 'millions'
    }

    statement, ratios, report = analyze_dict(financial_data)
    print(report)


def example3_detailed_analysis():
    """Example 3: Step-by-step detailed analysis"""
    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 3: Detailed Step-by-Step Analysis")
    print("=" * 80)
    print()

    # Create analyzer
    analyzer = FinancialAnalyzer()

    # Load data
    financial_data = {
        'revenue': 5000.0,
        'cost_of_goods_sold': 3000.0,
        'operating_expenses': 1200.0,
        'operating_income': 800.0,
        'interest_expense': 100.0,
        'net_income': 560.0,
        'cash': 1200.0,
        'accounts_receivable': 800.0,
        'inventory': 600.0,
        'current_assets': 2800.0,
        'total_assets': 8000.0,
        'current_liabilities': 1400.0,
        'long_term_debt': 2000.0,
        'shareholders_equity': 4000.0,
        'period': 'FY 2024',
        'scale': 'millions'
    }

    statement = analyzer.load_from_dict(financial_data)

    print("Financial Statement Summary:")
    print(f"  Revenue: ${statement.revenue:,.2f}M")
    print(f"  Net Income: ${statement.net_income:,.2f}M")
    print(f"  Total Assets: ${statement.total_assets:,.2f}M")
    print(f"  Total Equity: ${statement.shareholders_equity:,.2f}M")
    print()

    # Compute ratios
    ratios = analyzer.compute_all_ratios(statement)

    print(f"Computed {len(ratios)} financial ratios:")
    print()

    # Group by category and display
    from collections import defaultdict
    by_category = defaultdict(list)
    for ratio in ratios:
        by_category[ratio.category.value].append(ratio)

    for category, category_ratios in by_category.items():
        print(f"{category.upper()} ({len(category_ratios)} ratios):")
        for ratio in category_ratios:
            health = "✓" if ratio.is_healthy() else ("⚠" if ratio.is_healthy() is False else "")
            print(f"  {ratio.name}: {ratio.format_value()} {health}")
        print()

    # Generate insights
    insights = analyzer.generate_insights(ratios)

    print("Key Insights:")
    print()

    if insights['strengths']:
        print(f"Strengths ({len(insights['strengths'])}):")
        for strength in insights['strengths'][:3]:  # Show top 3
            print(f"  ✓ {strength}")
        print()

    if insights['concerns']:
        print(f"Concerns ({len(insights['concerns'])}):")
        for concern in insights['concerns'][:3]:  # Show top 3
            print(f"  ⚠ {concern}")
        print()


def example4_manual_statement():
    """Example 4: Manually creating a financial statement"""
    print("\n\n")
    print("=" * 80)
    print("EXAMPLE 4: Manually Creating Financial Statement")
    print("=" * 80)
    print()

    # Create statement object
    stmt = FinancialStatement(
        # Income Statement
        revenue=10000,
        cost_of_goods_sold=6000,
        gross_profit=4000,
        operating_expenses=2000,
        operating_income=2000,
        interest_expense=200,
        net_income=1440,

        # Balance Sheet
        cash=3000,
        accounts_receivable=1500,
        inventory=1000,
        current_assets=6000,
        total_assets=20000,

        accounts_payable=800,
        short_term_debt=500,
        current_liabilities=2000,
        long_term_debt=5000,
        total_liabilities=8000,
        shareholders_equity=12000,

        # Cash Flow
        operating_cash_flow=2000,
        capital_expenditures=500,
        free_cash_flow=1500,

        # Metadata
        period="FY 2024",
        currency="USD",
        scale="thousands"
    )

    # Create analyzer and compute ratios
    analyzer = FinancialAnalyzer()
    ratios = analyzer.compute_all_ratios(stmt)

    # Print specific ratios of interest
    print("Selected Key Ratios:")
    print()

    for ratio in ratios:
        if ratio.name in [
            "Current Ratio",
            "Net Profit Margin",
            "Return on Equity (ROE)",
            "Debt-to-Equity Ratio",
            "Asset Turnover Ratio"
        ]:
            print(f"{ratio.name}: {ratio.format_value()}")
            print(f"  {ratio.interpretation}")
            if ratio.benchmark_range:
                min_val, max_val = ratio.benchmark_range
                status = "Within" if ratio.is_healthy() else "Outside"
                print(f"  {status} benchmark range: {min_val:.2f} - {max_val:.2f}")
            print()


if __name__ == "__main__":
    print("\n")
    print("Financial Analyzer - Example Demonstrations")
    print("=" * 80)
    print()

    # Run all examples
    example1_from_csv()
    example2_from_dict()
    example3_detailed_analysis()
    example4_manual_statement()

    print("\n")
    print("=" * 80)
    print("Examples completed!")
    print("=" * 80)
