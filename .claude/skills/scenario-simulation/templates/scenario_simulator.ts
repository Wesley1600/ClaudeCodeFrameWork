/**
 * Scenario Simulation Template (TypeScript)
 * A flexible framework for running scenario-based simulations in TypeScript/JavaScript
 */

interface VariableConfig {
  name: string;
  bestCase: number | string;
  expectedCase: number | string;
  worstCase: number | string;
  description?: string;
  unit?: string;
}

interface ScenarioInputs {
  [key: string]: number | string;
}

interface ScenarioResults {
  [key: string]: number | string;
}

type ModelFunction = (inputs: ScenarioInputs) => ScenarioResults;
type ScenarioType = 'best_case' | 'expected_case' | 'worst_case';

class Variable {
  name: string;
  bestCase: number | string;
  expectedCase: number | string;
  worstCase: number | string;
  description: string;
  unit: string;

  constructor(config: VariableConfig) {
    this.name = config.name;
    this.bestCase = config.bestCase;
    this.expectedCase = config.expectedCase;
    this.worstCase = config.worstCase;
    this.description = config.description || '';
    this.unit = config.unit || '';
  }

  getValue(scenario: ScenarioType): number | string {
    const scenarios = {
      best_case: this.bestCase,
      expected_case: this.expectedCase,
      worst_case: this.worstCase,
    };
    return scenarios[scenario];
  }
}

class ScenarioSimulator {
  private variables: Map<string, Variable>;
  private results: Map<string, ScenarioResults>;

  constructor(variables: Variable[]) {
    this.variables = new Map(variables.map(v => [v.name, v]));
    this.results = new Map();
  }

  /**
   * Get all input values for a specific scenario
   */
  getInputs(scenario: ScenarioType): ScenarioInputs {
    const inputs: ScenarioInputs = {};
    this.variables.forEach((variable, name) => {
      inputs[name] = variable.getValue(scenario);
    });
    return inputs;
  }

  /**
   * Run a single scenario
   */
  runScenario(scenario: ScenarioType, modelFunc: ModelFunction): ScenarioResults {
    const inputs = this.getInputs(scenario);
    const result = modelFunc(inputs);
    this.results.set(scenario, result);
    return result;
  }

  /**
   * Run all standard scenarios
   */
  runAllScenarios(modelFunc: ModelFunction): Map<string, ScenarioResults> {
    const scenarios: ScenarioType[] = ['best_case', 'expected_case', 'worst_case'];
    scenarios.forEach(scenario => {
      this.runScenario(scenario, modelFunc);
    });
    return this.results;
  }

  /**
   * Run a custom scenario with specific input values
   */
  runCustomScenario(
    scenarioName: string,
    customInputs: ScenarioInputs,
    modelFunc: ModelFunction
  ): ScenarioResults {
    const result = modelFunc(customInputs);
    this.results.set(scenarioName, result);
    return result;
  }

  /**
   * Perform sensitivity analysis on a single variable
   */
  sensitivityAnalysis(
    variableName: string,
    modelFunc: ModelFunction,
    numSteps: number = 10
  ): Array<ScenarioResults & { [key: string]: number }> {
    const variable = this.variables.get(variableName);
    if (!variable) {
      throw new Error(`Variable ${variableName} not found`);
    }

    const baseInputs = this.getInputs('expected_case');
    const results: Array<ScenarioResults & { [key: string]: number }> = [];

    // Check if variable is numeric
    if (typeof variable.expectedCase === 'number') {
      const minVal = Math.min(
        variable.worstCase as number,
        variable.bestCase as number
      );
      const maxVal = Math.max(
        variable.worstCase as number,
        variable.bestCase as number
      );
      const step = (maxVal - minVal) / (numSteps - 1);

      for (let i = 0; i < numSteps; i++) {
        const value = minVal + step * i;
        const inputs = { ...baseInputs, [variableName]: value };
        const result = modelFunc(inputs);
        results.push({ [variableName]: value, ...result });
      }
    } else {
      // For non-numeric variables, test the three defined values
      [variable.worstCase, variable.expectedCase, variable.bestCase].forEach(value => {
        const inputs = { ...baseInputs, [variableName]: value };
        const result = modelFunc(inputs);
        results.push({ [variableName]: value as number, ...result });
      });
    }

    return results;
  }

  /**
   * Run Monte Carlo simulation with random sampling
   */
  monteCarloSimulation(
    modelFunc: ModelFunction,
    nIterations: number = 1000,
    randomSeed?: number
  ): ScenarioResults[] {
    // Simple seeded random number generator
    let seed = randomSeed || Date.now();
    const random = () => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };

    const results: ScenarioResults[] = [];

    for (let i = 0; i < nIterations; i++) {
      const inputs: ScenarioInputs = {};

      this.variables.forEach((variable, name) => {
        if (typeof variable.expectedCase === 'number') {
          // Triangular distribution
          const worst = variable.worstCase as number;
          const expected = variable.expectedCase as number;
          const best = variable.bestCase as number;

          const u = random();
          const fc = (expected - worst) / (best - worst);

          let value: number;
          if (u < fc) {
            value = worst + Math.sqrt(u * (best - worst) * (expected - worst));
          } else {
            value = best - Math.sqrt((1 - u) * (best - worst) * (best - expected));
          }
          inputs[name] = value;
        } else {
          inputs[name] = variable.expectedCase;
        }
      });

      results.push(modelFunc(inputs));
    }

    return results;
  }

  /**
   * Create comparison table of all scenarios
   */
  compareScenarios(): { metric: string; [scenario: string]: number | string }[] {
    if (this.results.size === 0) {
      throw new Error('No results to compare. Run scenarios first.');
    }

    // Get all metrics from first result
    const firstResult = Array.from(this.results.values())[0];
    const metrics = Object.keys(firstResult);

    return metrics.map(metric => {
      const row: { metric: string; [scenario: string]: number | string } = { metric };
      this.results.forEach((results, scenario) => {
        row[scenario] = results[metric] ?? 'N/A';
      });
      return row;
    });
  }

  /**
   * Export results to JSON
   */
  exportResults(): string {
    const resultsObj: { [key: string]: ScenarioResults } = {};
    this.results.forEach((value, key) => {
      resultsObj[key] = value;
    });
    return JSON.stringify(resultsObj, null, 2);
  }

  /**
   * Print formatted summary
   */
  printSummary(): void {
    console.log('\n' + '='.repeat(60));
    console.log('SCENARIO SIMULATION SUMMARY');
    console.log('='.repeat(60));

    console.log('\nInput Variables:');
    this.variables.forEach((variable, name) => {
      console.log(`\n  ${name}:`);
      console.log(`    Best Case: ${variable.bestCase} ${variable.unit}`);
      console.log(`    Expected:  ${variable.expectedCase} ${variable.unit}`);
      console.log(`    Worst Case: ${variable.worstCase} ${variable.unit}`);
    });

    if (this.results.size > 0) {
      console.log('\n' + '-'.repeat(60));
      console.log('Results Comparison:');
      console.log('-'.repeat(60));
      console.table(this.compareScenarios());
    }

    console.log('\n' + '='.repeat(60) + '\n');
  }

  /**
   * Calculate statistics from Monte Carlo results
   */
  static calculateStatistics(results: ScenarioResults[]): {
    [metric: string]: {
      mean: number;
      median: number;
      std: number;
      min: number;
      max: number;
      p5: number;
      p95: number;
    };
  } {
    if (results.length === 0) return {};

    const metrics = Object.keys(results[0]);
    const stats: any = {};

    metrics.forEach(metric => {
      const values = results
        .map(r => r[metric])
        .filter(v => typeof v === 'number')
        .sort((a, b) => (a as number) - (b as number)) as number[];

      if (values.length === 0) return;

      const sum = values.reduce((a, b) => a + b, 0);
      const mean = sum / values.length;
      const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
      const std = Math.sqrt(variance);

      stats[metric] = {
        mean: Math.round(mean * 100) / 100,
        median: values[Math.floor(values.length / 2)],
        std: Math.round(std * 100) / 100,
        min: values[0],
        max: values[values.length - 1],
        p5: values[Math.floor(values.length * 0.05)],
        p95: values[Math.floor(values.length * 0.95)],
      };
    });

    return stats;
  }
}

// Example usage
if (require.main === module) {
  // Define variables
  const variables = [
    new Variable({
      name: 'monthly_users',
      bestCase: 10000,
      expectedCase: 5000,
      worstCase: 1000,
      description: 'Number of monthly active users',
      unit: 'users',
    }),
    new Variable({
      name: 'conversion_rate',
      bestCase: 0.1,
      expectedCase: 0.05,
      worstCase: 0.02,
      description: 'Percentage of users who convert',
      unit: '%',
    }),
    new Variable({
      name: 'avg_revenue_per_user',
      bestCase: 100,
      expectedCase: 50,
      worstCase: 20,
      description: 'Average revenue per paying user',
      unit: '$',
    }),
    new Variable({
      name: 'monthly_costs',
      bestCase: 50000,
      expectedCase: 75000,
      worstCase: 100000,
      description: 'Monthly operating costs',
      unit: '$',
    }),
  ];

  // Define model function
  const revenueModel: ModelFunction = (inputs) => {
    const payingUsers = (inputs.monthly_users as number) * (inputs.conversion_rate as number);
    const revenue = payingUsers * (inputs.avg_revenue_per_user as number);
    const costs = inputs.monthly_costs as number;
    const profit = revenue - costs;
    const roi = costs > 0 ? (profit / costs) * 100 : 0;

    return {
      paying_users: Math.round(payingUsers),
      monthly_revenue: Math.round(revenue * 100) / 100,
      monthly_costs: Math.round(costs * 100) / 100,
      monthly_profit: Math.round(profit * 100) / 100,
      roi_percent: Math.round(roi * 100) / 100,
    };
  };

  // Run simulation
  const simulator = new ScenarioSimulator(variables);

  console.log('Running scenario analysis...');
  simulator.runAllScenarios(revenueModel);
  simulator.printSummary();

  // Sensitivity analysis
  console.log('\nRunning sensitivity analysis on conversion_rate...');
  const sensitivityResults = simulator.sensitivityAnalysis('conversion_rate', revenueModel);
  console.table(sensitivityResults);

  // Monte Carlo simulation
  console.log('\nRunning Monte Carlo simulation (1000 iterations)...');
  const mcResults = simulator.monteCarloSimulation(revenueModel, 1000, 42);

  console.log('\nMonte Carlo Results Summary:');
  const stats = ScenarioSimulator.calculateStatistics(mcResults);
  console.table(stats);

  // Export results
  console.log('\nResults JSON:');
  console.log(simulator.exportResults());
}

// Export for use as a module
export { ScenarioSimulator, Variable, ScenarioInputs, ScenarioResults, ModelFunction };
