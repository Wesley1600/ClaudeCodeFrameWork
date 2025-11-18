#!/usr/bin/env python3
"""
Scenario Simulation Template
A flexible framework for running scenario-based simulations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
import json


@dataclass
class Variable:
    """Represents a simulation variable with different scenario values"""
    name: str
    best_case: Any
    expected_case: Any
    worst_case: Any
    description: str = ""
    unit: str = ""

    def get_value(self, scenario: str) -> Any:
        """Get the value for a specific scenario"""
        scenarios = {
            'best_case': self.best_case,
            'expected_case': self.expected_case,
            'worst_case': self.worst_case
        }
        return scenarios.get(scenario, self.expected_case)


class ScenarioSimulator:
    """Base class for scenario simulations"""

    def __init__(self, variables: List[Variable]):
        self.variables = {var.name: var for var in variables}
        self.results = {}
        self.metrics = {}

    def get_inputs(self, scenario: str) -> Dict[str, Any]:
        """Get all input values for a specific scenario"""
        return {
            name: var.get_value(scenario)
            for name, var in self.variables.items()
        }

    def run_scenario(self, scenario: str, model_func: Callable) -> Dict[str, Any]:
        """
        Run a single scenario

        Args:
            scenario: 'best_case', 'expected_case', or 'worst_case'
            model_func: Function that takes inputs dict and returns results dict
        """
        inputs = self.get_inputs(scenario)
        result = model_func(inputs)
        self.results[scenario] = result
        return result

    def run_all_scenarios(self, model_func: Callable) -> Dict[str, Dict[str, Any]]:
        """Run all standard scenarios"""
        scenarios = ['best_case', 'expected_case', 'worst_case']
        for scenario in scenarios:
            self.run_scenario(scenario, model_func)
        return self.results

    def run_custom_scenario(self, scenario_name: str, custom_inputs: Dict[str, Any],
                           model_func: Callable) -> Dict[str, Any]:
        """Run a custom scenario with specific input values"""
        result = model_func(custom_inputs)
        self.results[scenario_name] = result
        return result

    def sensitivity_analysis(self, variable_name: str, model_func: Callable,
                           num_steps: int = 10) -> pd.DataFrame:
        """
        Perform sensitivity analysis on a single variable

        Args:
            variable_name: Name of variable to analyze
            model_func: Model function to run
            num_steps: Number of values to test
        """
        if variable_name not in self.variables:
            raise ValueError(f"Variable {variable_name} not found")

        var = self.variables[variable_name]
        base_inputs = self.get_inputs('expected_case')

        # Create range of values
        if isinstance(var.expected_case, (int, float)):
            min_val = min(var.worst_case, var.best_case)
            max_val = max(var.worst_case, var.best_case)
            values = np.linspace(min_val, max_val, num_steps)
        else:
            # For non-numeric variables, just test the three defined values
            values = [var.worst_case, var.expected_case, var.best_case]

        results = []
        for value in values:
            inputs = base_inputs.copy()
            inputs[variable_name] = value
            result = model_func(inputs)
            results.append({
                variable_name: value,
                **result
            })

        return pd.DataFrame(results)

    def monte_carlo_simulation(self, model_func: Callable,
                              n_iterations: int = 1000,
                              random_seed: int = 42) -> pd.DataFrame:
        """
        Run Monte Carlo simulation with random sampling

        Assumes triangular distribution between worst, expected, and best cases
        """
        np.random.seed(random_seed)
        results = []

        for _ in range(n_iterations):
            inputs = {}
            for name, var in self.variables.items():
                if isinstance(var.expected_case, (int, float)):
                    # Triangular distribution
                    value = np.random.triangular(
                        var.worst_case,
                        var.expected_case,
                        var.best_case
                    )
                    inputs[name] = value
                else:
                    # For non-numeric, use expected case
                    inputs[name] = var.expected_case

            result = model_func(inputs)
            results.append(result)

        return pd.DataFrame(results)

    def compare_scenarios(self, metrics: List[str] = None) -> pd.DataFrame:
        """Create comparison table of all scenarios"""
        if not self.results:
            raise ValueError("No results to compare. Run scenarios first.")

        if metrics is None:
            # Use all keys from first result
            metrics = list(next(iter(self.results.values())).keys())

        comparison = {}
        for metric in metrics:
            comparison[metric] = {
                scenario: results.get(metric, 'N/A')
                for scenario, results in self.results.items()
            }

        return pd.DataFrame(comparison).T

    def export_results(self, filepath: str, format: str = 'json'):
        """Export results to file"""
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
        elif format == 'csv':
            df = self.compare_scenarios()
            df.to_csv(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def print_summary(self):
        """Print a formatted summary of results"""
        print("\n" + "="*60)
        print("SCENARIO SIMULATION SUMMARY")
        print("="*60)

        print("\nInput Variables:")
        for name, var in self.variables.items():
            print(f"\n  {name}:")
            print(f"    Best Case: {var.best_case} {var.unit}")
            print(f"    Expected:  {var.expected_case} {var.unit}")
            print(f"    Worst Case: {var.worst_case} {var.unit}")

        if self.results:
            print("\n" + "-"*60)
            print("Results Comparison:")
            print("-"*60)
            df = self.compare_scenarios()
            print(f"\n{df.to_string()}")

        print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Define variables
    variables = [
        Variable(
            name="monthly_users",
            best_case=10000,
            expected_case=5000,
            worst_case=1000,
            description="Number of monthly active users",
            unit="users"
        ),
        Variable(
            name="conversion_rate",
            best_case=0.10,
            expected_case=0.05,
            worst_case=0.02,
            description="Percentage of users who convert",
            unit="%"
        ),
        Variable(
            name="avg_revenue_per_user",
            best_case=100,
            expected_case=50,
            worst_case=20,
            description="Average revenue per paying user",
            unit="$"
        ),
        Variable(
            name="monthly_costs",
            best_case=50000,
            expected_case=75000,
            worst_case=100000,
            description="Monthly operating costs",
            unit="$"
        )
    ]

    # Define model function
    def revenue_model(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Simple revenue model"""
        paying_users = inputs['monthly_users'] * inputs['conversion_rate']
        revenue = paying_users * inputs['avg_revenue_per_user']
        costs = inputs['monthly_costs']
        profit = revenue - costs
        roi = (profit / costs * 100) if costs > 0 else 0

        return {
            'paying_users': int(paying_users),
            'monthly_revenue': round(revenue, 2),
            'monthly_costs': round(costs, 2),
            'monthly_profit': round(profit, 2),
            'roi_percent': round(roi, 2)
        }

    # Run simulation
    simulator = ScenarioSimulator(variables)

    print("Running scenario analysis...")
    simulator.run_all_scenarios(revenue_model)
    simulator.print_summary()

    # Sensitivity analysis
    print("\nRunning sensitivity analysis on conversion_rate...")
    sensitivity_df = simulator.sensitivity_analysis('conversion_rate', revenue_model)
    print(sensitivity_df.to_string(index=False))

    # Monte Carlo simulation
    print("\nRunning Monte Carlo simulation (1000 iterations)...")
    mc_results = simulator.monte_carlo_simulation(revenue_model, n_iterations=1000)

    print("\nMonte Carlo Results Summary:")
    print(mc_results.describe())

    # Export results
    simulator.export_results('scenario_results.json', format='json')
    print("\nResults exported to scenario_results.json")
