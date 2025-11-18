#!/usr/bin/env python3
"""
Code Execution Skill - Examples

This file demonstrates practical usage of the Code Execution Skill.
"""

import sys
import os
from pathlib import Path

# Add the skill to the path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    run_python,
    run_bash,
    write_file,
    read_file,
    analyze_data,
    create_visualization,
    install_package,
    list_files
)


def example_1_simple_python():
    """Example 1: Simple Python execution"""
    print("=" * 60)
    print("Example 1: Simple Python Execution")
    print("=" * 60)

    code = """
import numpy as np

# Create an array
arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Calculate statistics
print(f"Array: {arr}")
print(f"Mean: {arr.mean():.2f}")
print(f"Median: {np.median(arr):.2f}")
print(f"Std Dev: {arr.std():.2f}")
print(f"Sum: {arr.sum()}")
"""

    result = run_python(code)

    if result["success"]:
        print("✓ Execution successful!")
        print("\nOutput:")
        print(result["output"])
    else:
        print("✗ Execution failed!")
        print(f"Error: {result['error']}")

    print()


def example_2_bash_commands():
    """Example 2: Bash command execution"""
    print("=" * 60)
    print("Example 2: Bash Command Execution")
    print("=" * 60)

    # Create a temporary directory and list it
    commands = [
        "mkdir -p /tmp/code_exec_test",
        "touch /tmp/code_exec_test/file1.txt /tmp/code_exec_test/file2.txt",
        "ls -la /tmp/code_exec_test"
    ]

    for cmd in commands:
        print(f"\nExecuting: {cmd}")
        result = run_bash(cmd)

        if result["success"]:
            print("✓ Success!")
            if result["output"]:
                print(f"Output: {result['output']}")
        else:
            print("✗ Failed!")
            print(f"Error: {result['error']}")

    print()


def example_3_file_operations():
    """Example 3: File operations"""
    print("=" * 60)
    print("Example 3: File Operations")
    print("=" * 60)

    # Write a file
    print("\n1. Writing file...")
    content = """# Sample Data File

This is a sample data file created by the Code Execution Skill.

## Features
- File writing
- File reading
- Data analysis
- Visualizations
"""

    result = write_file("/tmp/code_exec_test/sample.md", content)

    if result["success"]:
        print(f"✓ File written successfully to: {result['path']}")
    else:
        print(f"✗ Failed to write file: {result['error']}")

    # Read the file back
    print("\n2. Reading file...")
    result = read_file("/tmp/code_exec_test/sample.md")

    if result["success"]:
        print("✓ File read successfully!")
        print("\nContent:")
        print(result["content"])
    else:
        print(f"✗ Failed to read file: {result['error']}")

    print()


def example_4_data_analysis():
    """Example 4: Data analysis"""
    print("=" * 60)
    print("Example 4: Data Analysis")
    print("=" * 60)

    # First, create a sample CSV file
    print("\n1. Creating sample data...")
    csv_content = """date,product,quantity,price,revenue
2024-01-01,Widget A,10,25.50,255.00
2024-01-02,Widget B,15,30.00,450.00
2024-01-03,Widget A,8,25.50,204.00
2024-01-04,Widget C,20,15.75,315.00
2024-01-05,Widget B,12,30.00,360.00
2024-01-06,Widget A,18,25.50,459.00
2024-01-07,Widget C,25,15.75,393.75
2024-01-08,Widget B,10,30.00,300.00
2024-01-09,Widget A,14,25.50,357.00
2024-01-10,Widget C,22,15.75,346.50
"""

    result = write_file("/tmp/code_exec_test/sales.csv", csv_content)
    if result["success"]:
        print(f"✓ Sample data created: {result['path']}")
    else:
        print(f"✗ Failed to create data: {result['error']}")
        return

    # Analyze the data
    print("\n2. Running summary analysis...")
    result = analyze_data("/tmp/code_exec_test/sales.csv", "summary")

    if result["success"]:
        print("✓ Analysis successful!")
        print("\nResults:")
        print(result["result"])
    else:
        print(f"✗ Analysis failed: {result['error']}")

    # Custom analysis
    print("\n3. Running custom analysis...")
    custom_code = """
import pandas as pd

df = pd.read_csv('/tmp/code_exec_test/sales.csv')

print("\\n=== Product Performance ===")
product_stats = df.groupby('product').agg({
    'quantity': 'sum',
    'revenue': 'sum'
}).round(2)

print(product_stats)

print("\\n=== Daily Statistics ===")
print(f"Average Daily Revenue: ${df['revenue'].mean():.2f}")
print(f"Total Revenue: ${df['revenue'].sum():.2f}")
print(f"Best Day: {df.loc[df['revenue'].idxmax(), 'date']} (${df['revenue'].max():.2f})")
"""

    result = analyze_data(
        "/tmp/code_exec_test/sales.csv",
        "custom",
        custom_code=custom_code
    )

    if result["success"]:
        print("✓ Custom analysis successful!")
        print("\nResults:")
        print(result["result"])
    else:
        print(f"✗ Custom analysis failed: {result['error']}")

    print()


def example_5_visualization():
    """Example 5: Data visualization"""
    print("=" * 60)
    print("Example 5: Data Visualization")
    print("=" * 60)

    # Create a more complex dataset
    print("\n1. Creating sample dataset...")
    data_code = """
import pandas as pd
import numpy as np

# Generate sample time series data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=30, freq='D')
data = {
    'date': dates,
    'sales': np.random.randint(100, 500, 30),
    'expenses': np.random.randint(50, 300, 30),
    'customers': np.random.randint(10, 50, 30)
}

df = pd.DataFrame(data)
df['profit'] = df['sales'] - df['expenses']
df.to_csv('/tmp/code_exec_test/timeseries.csv', index=False)
print(f"Created dataset with {len(df)} rows")
"""

    result = run_python(data_code)
    if result["success"]:
        print("✓ Dataset created successfully!")
    else:
        print(f"✗ Failed to create dataset: {result['error']}")
        return

    # Create a custom visualization
    print("\n2. Creating visualization...")
    viz_code = """
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('/tmp/code_exec_test/timeseries.csv')
df['date'] = pd.to_datetime(df['date'])

# Create a 2x2 subplot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Sales and Expenses over time
ax1.plot(df['date'], df['sales'], label='Sales', marker='o', linewidth=2)
ax1.plot(df['date'], df['expenses'], label='Expenses', marker='s', linewidth=2)
ax1.set_title('Sales vs Expenses Over Time', fontsize=12, fontweight='bold')
ax1.set_xlabel('Date')
ax1.set_ylabel('Amount ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Profit trend
ax2.fill_between(df['date'], df['profit'], alpha=0.3, color='green')
ax2.plot(df['date'], df['profit'], color='darkgreen', linewidth=2)
ax2.axhline(y=0, color='red', linestyle='--', alpha=0.5)
ax2.set_title('Daily Profit Trend', fontsize=12, fontweight='bold')
ax2.set_xlabel('Date')
ax2.set_ylabel('Profit ($)')
ax2.grid(True, alpha=0.3)

# Plot 3: Customer distribution
ax3.hist(df['customers'], bins=15, color='skyblue', edgecolor='black', alpha=0.7)
ax3.set_title('Customer Distribution', fontsize=12, fontweight='bold')
ax3.set_xlabel('Number of Customers')
ax3.set_ylabel('Frequency')
ax3.grid(True, alpha=0.3)

# Plot 4: Correlation heatmap
import seaborn as sns
corr_data = df[['sales', 'expenses', 'customers', 'profit']].corr()
sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax4,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
ax4.set_title('Correlation Matrix', fontsize=12, fontweight='bold')

plt.tight_layout()
"""

    result = create_visualization(
        data_source="/tmp/code_exec_test/timeseries.csv",
        plot_type="custom",
        output_path="/tmp/code_exec_test/dashboard.png",
        custom_code=viz_code
    )

    if result["success"]:
        print(f"✓ Visualization created successfully!")
        print(f"   Saved to: {result['path']}")
    else:
        print(f"✗ Visualization failed: {result['error']}")

    print()


def example_6_file_discovery():
    """Example 6: File discovery"""
    print("=" * 60)
    print("Example 6: File Discovery")
    print("=" * 60)

    # List all CSV files
    print("\n1. Finding all CSV files...")
    result = list_files("*.csv", path="/tmp/code_exec_test")

    if result["success"]:
        print(f"✓ Found {len(result['files'])} CSV file(s):")
        for file in result['files']:
            print(f"   - {file}")
    else:
        print(f"✗ Search failed: {result['error']}")

    # List all files
    print("\n2. Finding all files...")
    result = list_files("*", path="/tmp/code_exec_test")

    if result["success"]:
        print(f"✓ Found {len(result['files'])} file(s):")
        for file in result['files']:
            print(f"   - {file}")
    else:
        print(f"✗ Search failed: {result['error']}")

    print()


def example_7_complete_workflow():
    """Example 7: Complete data workflow"""
    print("=" * 60)
    print("Example 7: Complete Data Workflow")
    print("=" * 60)

    workflow_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Step 1: Data Collection")
print("-" * 40)

# Simulate data collection
np.random.seed(42)
data = {
    'customer_id': range(1, 101),
    'age': np.random.randint(18, 70, 100),
    'purchases': np.random.randint(1, 50, 100),
    'total_spent': np.random.uniform(10, 1000, 100).round(2),
    'satisfaction': np.random.randint(1, 6, 100)
}
df = pd.DataFrame(data)
print(f"Collected data for {len(df)} customers")

print("\\nStep 2: Data Cleaning")
print("-" * 40)

# Clean data
initial_count = len(df)
df = df[df['total_spent'] > 0]  # Remove invalid entries
df = df[df['purchases'] > 0]
print(f"Removed {initial_count - len(df)} invalid records")

print("\\nStep 3: Data Analysis")
print("-" * 40)

# Analyze
print(f"Average Age: {df['age'].mean():.1f} years")
print(f"Average Purchases: {df['purchases'].mean():.1f}")
print(f"Average Spent: ${df['total_spent'].mean():.2f}")
print(f"Average Satisfaction: {df['satisfaction'].mean():.2f}/5")

# Segment customers
df['segment'] = pd.cut(df['total_spent'],
                       bins=[0, 200, 500, 1000],
                       labels=['Low', 'Medium', 'High'])

print("\\nCustomer Segments:")
print(df['segment'].value_counts())

print("\\nStep 4: Insights")
print("-" * 40)

# Correlation analysis
print("\\nSpending vs Satisfaction:")
correlation = df['total_spent'].corr(df['satisfaction'])
print(f"Correlation: {correlation:.3f}")

# Top customers
print("\\nTop 5 Customers by Spending:")
top_customers = df.nlargest(5, 'total_spent')[['customer_id', 'total_spent', 'satisfaction']]
print(top_customers.to_string(index=False))

print("\\nStep 5: Export Results")
print("-" * 40)

# Save processed data
df.to_csv('/tmp/code_exec_test/processed_customers.csv', index=False)
print("✓ Saved processed data to processed_customers.csv")

# Save summary report
summary = f'''
# Customer Analysis Report

## Overview
- Total Customers: {len(df)}
- Date: 2024-11-18

## Key Metrics
- Average Age: {df['age'].mean():.1f} years
- Average Purchases: {df['purchases'].mean():.1f}
- Average Spent: ${df['total_spent'].mean():.2f}
- Average Satisfaction: {df['satisfaction'].mean():.2f}/5

## Segments
{df['segment'].value_counts().to_string()}

## Insights
- Spending-Satisfaction Correlation: {correlation:.3f}
- High value customers show {'positive' if correlation > 0 else 'negative'} correlation with satisfaction
'''

with open('/tmp/code_exec_test/analysis_report.md', 'w') as f:
    f.write(summary)
print("✓ Saved analysis report to analysis_report.md")

print("\\n" + "=" * 40)
print("Workflow completed successfully!")
"""

    print("\nRunning complete workflow...")
    result = run_python(workflow_code, timeout=180000)  # 3 minutes

    if result["success"]:
        print("\n" + "=" * 60)
        print("WORKFLOW OUTPUT")
        print("=" * 60)
        print(result["output"])
        print("=" * 60)
        print("\n✓ Complete workflow executed successfully!")
    else:
        print(f"\n✗ Workflow failed: {result['error']}")

    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CODE EXECUTION SKILL - EXAMPLES" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    examples = [
        example_1_simple_python,
        example_2_bash_commands,
        example_3_file_operations,
        example_4_data_analysis,
        example_5_visualization,
        example_6_file_discovery,
        example_7_complete_workflow
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
            input(f"Press Enter to continue to Example {i + 1}..." if i < len(examples) else "Press Enter to finish...")
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\n✗ Example {i} failed with error: {e}")
            input("Press Enter to continue...")

    print("\n")
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
