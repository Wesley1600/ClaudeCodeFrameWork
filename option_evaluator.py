"""
Option Evaluation Skill - Multi-Criteria Decision Analysis (MCDA)

This skill evaluates multiple options/recommendations and selects the best one based on
structured criteria such as cost, risk, user preferences, and custom metrics.

Features:
- Multiple evaluation methods (Weighted Sum, TOPSIS, Custom Scoring)
- Flexible criteria system with weights and optimization direction
- Structured reasoning with detailed explanations
- Risk assessment and sensitivity analysis
- Integration with other skills for data inputs
- Support for both quantitative and qualitative criteria

Author: Claude Code Framework
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import json


class OptimizationType(Enum):
    """Direction of optimization for a criterion."""
    MINIMIZE = "minimize"  # Lower is better (e.g., cost, risk)
    MAXIMIZE = "maximize"  # Higher is better (e.g., quality, user satisfaction)


class EvaluationMethod(Enum):
    """Available evaluation methods."""
    WEIGHTED_SUM = "weighted_sum"  # Simple weighted sum of normalized scores
    TOPSIS = "topsis"  # Technique for Order of Preference by Similarity to Ideal Solution
    CUSTOM_SCORING = "custom_scoring"  # User-defined scoring function
    MULTI_OBJECTIVE = "multi_objective"  # Pareto-optimal solution finding


@dataclass
class Criterion:
    """
    Represents an evaluation criterion.

    Attributes:
        name: Name of the criterion (e.g., "cost", "risk", "performance")
        weight: Importance weight (0-1, will be normalized if sum != 1)
        optimization: Whether to minimize or maximize this criterion
        description: Optional description of what this criterion measures
        threshold: Optional threshold value (options below/above this may be filtered)
        data_source: Optional function to fetch criterion value for an option
    """
    name: str
    weight: float = 1.0
    optimization: OptimizationType = OptimizationType.MAXIMIZE
    description: str = ""
    threshold: Optional[float] = None
    data_source: Optional[Callable[[str, Dict[str, Any]], float]] = None

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError(f"Weight must be non-negative, got {self.weight}")


@dataclass
class Option:
    """
    Represents an option/alternative to be evaluated.

    Attributes:
        id: Unique identifier for the option
        name: Human-readable name
        description: Detailed description of the option
        attributes: Dictionary of criterion values (criterion_name -> value)
        metadata: Additional metadata (tags, categories, etc.)
    """
    id: str
    name: str
    description: str = ""
    attributes: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_attribute(self, criterion_name: str, default: float = 0.0) -> float:
        """Get the value for a specific criterion."""
        return self.attributes.get(criterion_name, default)

    def set_attribute(self, criterion_name: str, value: float):
        """Set the value for a specific criterion."""
        self.attributes[criterion_name] = value


@dataclass
class EvaluationScore:
    """
    Detailed scoring information for an option.

    Attributes:
        option_id: ID of the evaluated option
        total_score: Final aggregated score
        criterion_scores: Individual scores per criterion (normalized)
        raw_values: Raw attribute values before normalization
        reasoning: Structured explanation of the score
    """
    option_id: str
    total_score: float
    criterion_scores: Dict[str, float]
    raw_values: Dict[str, float]
    reasoning: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """
    Complete evaluation result with rankings and explanations.

    Attributes:
        ranked_options: List of (option_id, score) tuples, sorted by score (best first)
        scores: Detailed scoring information for each option
        best_option_id: ID of the top-ranked option
        method: Evaluation method used
        criteria: Criteria used in evaluation
        sensitivity_analysis: Optional sensitivity analysis results
        explanation: Human-readable explanation of the decision
    """
    ranked_options: List[Tuple[str, float]]
    scores: Dict[str, EvaluationScore]
    best_option_id: str
    method: EvaluationMethod
    criteria: List[Criterion]
    sensitivity_analysis: Optional[Dict[str, Any]] = None
    explanation: str = ""

    def get_top_n(self, n: int = 3) -> List[Tuple[str, float]]:
        """Get the top N options."""
        return self.ranked_options[:n]

    def get_score(self, option_id: str) -> Optional[EvaluationScore]:
        """Get detailed score for a specific option."""
        return self.scores.get(option_id)


class OptionEvaluator:
    """
    Main class for evaluating options using multi-criteria decision analysis.

    This evaluator supports multiple MCDA methods and provides structured reasoning
    for decision-making. It can integrate with other skills to fetch data dynamically.
    """

    def __init__(
        self,
        criteria: List[Criterion],
        method: EvaluationMethod = EvaluationMethod.WEIGHTED_SUM,
        normalize_weights: bool = True,
        enable_sensitivity_analysis: bool = False
    ):
        """
        Initialize the option evaluator.

        Args:
            criteria: List of evaluation criteria
            method: Evaluation method to use
            normalize_weights: Whether to normalize criterion weights to sum to 1
            enable_sensitivity_analysis: Whether to perform sensitivity analysis
        """
        self.criteria = criteria
        self.method = method
        self.enable_sensitivity_analysis = enable_sensitivity_analysis

        # Normalize weights if requested
        if normalize_weights and criteria:
            total_weight = sum(c.weight for c in criteria)
            if total_weight > 0:
                for c in criteria:
                    c.weight = c.weight / total_weight

        # Create criterion lookup
        self.criterion_map = {c.name: c for c in criteria}

    def evaluate(
        self,
        options: List[Option],
        fetch_missing_data: bool = True
    ) -> EvaluationResult:
        """
        Evaluate all options and return ranked results.

        Args:
            options: List of options to evaluate
            fetch_missing_data: Whether to fetch missing criterion data using data_source

        Returns:
            EvaluationResult with ranked options and detailed scoring
        """
        if not options:
            raise ValueError("No options provided for evaluation")

        # Fetch missing data if needed
        if fetch_missing_data:
            self._fetch_missing_data(options)

        # Apply thresholds to filter options
        filtered_options = self._apply_thresholds(options)

        if not filtered_options:
            raise ValueError("No options passed threshold criteria")

        # Evaluate based on selected method
        if self.method == EvaluationMethod.WEIGHTED_SUM:
            scores = self._evaluate_weighted_sum(filtered_options)
        elif self.method == EvaluationMethod.TOPSIS:
            scores = self._evaluate_topsis(filtered_options)
        elif self.method == EvaluationMethod.MULTI_OBJECTIVE:
            scores = self._evaluate_multi_objective(filtered_options)
        else:
            scores = self._evaluate_weighted_sum(filtered_options)

        # Rank options by score
        ranked = sorted(
            [(opt_id, score.total_score) for opt_id, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        best_option_id = ranked[0][0] if ranked else None

        # Generate explanation
        explanation = self._generate_explanation(ranked, scores, options)

        # Sensitivity analysis
        sensitivity = None
        if self.enable_sensitivity_analysis:
            sensitivity = self._sensitivity_analysis(filtered_options, scores)

        return EvaluationResult(
            ranked_options=ranked,
            scores=scores,
            best_option_id=best_option_id,
            method=self.method,
            criteria=self.criteria,
            sensitivity_analysis=sensitivity,
            explanation=explanation
        )

    def _fetch_missing_data(self, options: List[Option]):
        """Fetch missing criterion data using data_source functions."""
        for criterion in self.criteria:
            if criterion.data_source is None:
                continue

            for option in options:
                if criterion.name not in option.attributes:
                    try:
                        value = criterion.data_source(option.id, option.metadata)
                        option.set_attribute(criterion.name, value)
                    except Exception as e:
                        # Log error but continue with default value
                        print(f"Warning: Failed to fetch {criterion.name} for {option.id}: {e}")

    def _apply_thresholds(self, options: List[Option]) -> List[Option]:
        """Filter options based on criterion thresholds."""
        filtered = []

        for option in options:
            passes_thresholds = True

            for criterion in self.criteria:
                if criterion.threshold is None:
                    continue

                value = option.get_attribute(criterion.name, float('-inf'))

                if criterion.optimization == OptimizationType.MINIMIZE:
                    if value > criterion.threshold:
                        passes_thresholds = False
                        break
                else:  # MAXIMIZE
                    if value < criterion.threshold:
                        passes_thresholds = False
                        break

            if passes_thresholds:
                filtered.append(option)

        return filtered

    def _normalize_matrix(
        self,
        options: List[Option]
    ) -> Tuple[np.ndarray, Dict[str, Tuple[float, float]]]:
        """
        Create and normalize the decision matrix.

        Returns:
            Normalized matrix (options x criteria) and normalization bounds
        """
        n_options = len(options)
        n_criteria = len(self.criteria)

        # Build raw matrix
        matrix = np.zeros((n_options, n_criteria))
        bounds = {}

        for j, criterion in enumerate(self.criteria):
            values = [opt.get_attribute(criterion.name, 0.0) for opt in options]
            matrix[:, j] = values

            min_val, max_val = min(values), max(values)
            bounds[criterion.name] = (min_val, max_val)

            # Normalize to [0, 1]
            if max_val > min_val:
                if criterion.optimization == OptimizationType.MINIMIZE:
                    # Invert for minimization criteria
                    matrix[:, j] = (max_val - matrix[:, j]) / (max_val - min_val)
                else:
                    matrix[:, j] = (matrix[:, j] - min_val) / (max_val - min_val)
            else:
                # All values are the same
                matrix[:, j] = 1.0

        return matrix, bounds

    def _evaluate_weighted_sum(self, options: List[Option]) -> Dict[str, EvaluationScore]:
        """Evaluate using weighted sum method."""
        matrix, bounds = self._normalize_matrix(options)
        weights = np.array([c.weight for c in self.criteria])

        # Calculate weighted scores
        weighted_matrix = matrix * weights
        total_scores = np.sum(weighted_matrix, axis=1)

        # Build detailed scores
        scores = {}
        for i, option in enumerate(options):
            criterion_scores = {}
            raw_values = {}
            reasoning = {}

            for j, criterion in enumerate(self.criteria):
                raw_val = option.get_attribute(criterion.name, 0.0)
                norm_val = matrix[i, j]
                weighted_val = weighted_matrix[i, j]

                criterion_scores[criterion.name] = norm_val
                raw_values[criterion.name] = raw_val

                # Generate reasoning
                min_val, max_val = bounds[criterion.name]
                if criterion.optimization == OptimizationType.MINIMIZE:
                    reasoning[criterion.name] = (
                        f"Raw: {raw_val:.2f} (range: [{min_val:.2f}, {max_val:.2f}]), "
                        f"Normalized: {norm_val:.2f}, Weighted: {weighted_val:.2f} "
                        f"(lower is better)"
                    )
                else:
                    reasoning[criterion.name] = (
                        f"Raw: {raw_val:.2f} (range: [{min_val:.2f}, {max_val:.2f}]), "
                        f"Normalized: {norm_val:.2f}, Weighted: {weighted_val:.2f} "
                        f"(higher is better)"
                    )

            scores[option.id] = EvaluationScore(
                option_id=option.id,
                total_score=float(total_scores[i]),
                criterion_scores=criterion_scores,
                raw_values=raw_values,
                reasoning=reasoning
            )

        return scores

    def _evaluate_topsis(self, options: List[Option]) -> Dict[str, EvaluationScore]:
        """
        Evaluate using TOPSIS method.

        TOPSIS finds the option closest to the ideal solution and farthest from
        the negative-ideal solution.
        """
        matrix, bounds = self._normalize_matrix(options)
        weights = np.array([c.weight for c in self.criteria])

        # Weight the normalized matrix
        weighted_matrix = matrix * weights

        # Determine ideal and negative-ideal solutions
        ideal_solution = np.max(weighted_matrix, axis=0)
        negative_ideal = np.min(weighted_matrix, axis=0)

        # Calculate distances
        dist_to_ideal = np.sqrt(np.sum((weighted_matrix - ideal_solution) ** 2, axis=1))
        dist_to_negative = np.sqrt(np.sum((weighted_matrix - negative_ideal) ** 2, axis=1))

        # Calculate relative closeness to ideal solution
        total_dist = dist_to_ideal + dist_to_negative
        closeness = np.where(total_dist > 0, dist_to_negative / total_dist, 0.5)

        # Build detailed scores
        scores = {}
        for i, option in enumerate(options):
            criterion_scores = {}
            raw_values = {}
            reasoning = {}

            for j, criterion in enumerate(self.criteria):
                raw_val = option.get_attribute(criterion.name, 0.0)
                norm_val = matrix[i, j]

                criterion_scores[criterion.name] = norm_val
                raw_values[criterion.name] = raw_val

                min_val, max_val = bounds[criterion.name]
                deviation_from_ideal = abs(weighted_matrix[i, j] - ideal_solution[j])
                reasoning[criterion.name] = (
                    f"Raw: {raw_val:.2f}, Normalized: {norm_val:.2f}, "
                    f"Deviation from ideal: {deviation_from_ideal:.3f}"
                )

            reasoning["topsis"] = (
                f"Distance to ideal: {dist_to_ideal[i]:.3f}, "
                f"Distance to negative-ideal: {dist_to_negative[i]:.3f}, "
                f"Closeness coefficient: {closeness[i]:.3f}"
            )

            scores[option.id] = EvaluationScore(
                option_id=option.id,
                total_score=float(closeness[i]),
                criterion_scores=criterion_scores,
                raw_values=raw_values,
                reasoning=reasoning
            )

        return scores

    def _evaluate_multi_objective(self, options: List[Option]) -> Dict[str, EvaluationScore]:
        """
        Evaluate using multi-objective approach (Pareto optimality).

        Assigns higher scores to Pareto-optimal solutions.
        """
        matrix, bounds = self._normalize_matrix(options)
        n_options = len(options)

        # Find Pareto-optimal solutions
        is_pareto = np.ones(n_options, dtype=bool)
        for i in range(n_options):
            for j in range(n_options):
                if i != j:
                    # Check if j dominates i (j is better in all criteria)
                    if np.all(matrix[j] >= matrix[i]) and np.any(matrix[j] > matrix[i]):
                        is_pareto[i] = False
                        break

        # Score based on Pareto rank and dominance count
        scores = {}
        for i, option in enumerate(options):
            # Count how many solutions this option dominates
            dominates = 0
            dominated_by = 0

            for j in range(n_options):
                if i != j:
                    if np.all(matrix[i] >= matrix[j]) and np.any(matrix[i] > matrix[j]):
                        dominates += 1
                    if np.all(matrix[j] >= matrix[i]) and np.any(matrix[j] > matrix[i]):
                        dominated_by += 1

            # Calculate score: higher if Pareto-optimal and dominates more solutions
            pareto_bonus = 1.0 if is_pareto[i] else 0.0
            dominance_score = dominates / max(n_options - 1, 1)
            penalty = dominated_by / max(n_options - 1, 1)

            total_score = pareto_bonus + dominance_score - penalty

            criterion_scores = {}
            raw_values = {}
            reasoning = {}

            for j, criterion in enumerate(self.criteria):
                raw_val = option.get_attribute(criterion.name, 0.0)
                norm_val = matrix[i, j]

                criterion_scores[criterion.name] = norm_val
                raw_values[criterion.name] = raw_val
                reasoning[criterion.name] = f"Raw: {raw_val:.2f}, Normalized: {norm_val:.2f}"

            reasoning["pareto"] = (
                f"Pareto-optimal: {is_pareto[i]}, "
                f"Dominates: {dominates} options, "
                f"Dominated by: {dominated_by} options"
            )

            scores[option.id] = EvaluationScore(
                option_id=option.id,
                total_score=float(total_score),
                criterion_scores=criterion_scores,
                raw_values=raw_values,
                reasoning=reasoning
            )

        return scores

    def _generate_explanation(
        self,
        ranked: List[Tuple[str, float]],
        scores: Dict[str, EvaluationScore],
        options: List[Option]
    ) -> str:
        """Generate human-readable explanation of the evaluation."""
        if not ranked:
            return "No options to evaluate."

        # Get best option
        best_id, best_score = ranked[0]
        best_option = next((opt for opt in options if opt.id == best_id), None)
        best_eval = scores[best_id]

        explanation = [
            f"=== Option Evaluation Results ({self.method.value}) ===\n",
            f"Best Option: {best_option.name if best_option else best_id}",
            f"Overall Score: {best_score:.3f}\n",
            "\nKey Strengths:"
        ]

        # Find strongest criteria
        sorted_criteria = sorted(
            best_eval.criterion_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for crit_name, crit_score in sorted_criteria[:3]:
            criterion = self.criterion_map.get(crit_name)
            raw_val = best_eval.raw_values.get(crit_name, 0)
            if criterion:
                explanation.append(
                    f"  - {crit_name}: {raw_val:.2f} "
                    f"(normalized: {crit_score:.2f}, weight: {criterion.weight:.2f})"
                )

        # Show comparison with runner-up if exists
        if len(ranked) > 1:
            second_id, second_score = ranked[1]
            second_option = next((opt for opt in options if opt.id == second_id), None)
            explanation.append(
                f"\nRunner-up: {second_option.name if second_option else second_id} "
                f"(score: {second_score:.3f}, difference: {best_score - second_score:.3f})"
            )

        explanation.append(f"\nTotal options evaluated: {len(ranked)}")

        return "\n".join(explanation)

    def _sensitivity_analysis(
        self,
        options: List[Option],
        base_scores: Dict[str, EvaluationScore]
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis by varying criterion weights.

        Returns how robust the top choice is to weight changes.
        """
        analysis = {
            "weight_variations": {},
            "rank_stability": {}
        }

        base_best = max(base_scores.items(), key=lambda x: x[1].total_score)[0]

        # Test each criterion weight variation
        for criterion in self.criteria:
            original_weight = criterion.weight
            variations = []

            # Try increasing and decreasing weight by 20%
            for factor in [0.8, 1.2]:
                criterion.weight = original_weight * factor

                # Re-normalize weights
                total_weight = sum(c.weight for c in self.criteria)
                for c in self.criteria:
                    c.weight = c.weight / total_weight

                # Re-evaluate
                if self.method == EvaluationMethod.WEIGHTED_SUM:
                    new_scores = self._evaluate_weighted_sum(options)
                elif self.method == EvaluationMethod.TOPSIS:
                    new_scores = self._evaluate_topsis(options)
                else:
                    new_scores = self._evaluate_weighted_sum(options)

                new_best = max(new_scores.items(), key=lambda x: x[1].total_score)[0]

                variations.append({
                    "factor": factor,
                    "new_weight": criterion.weight,
                    "best_option": new_best,
                    "changed": new_best != base_best
                })

            # Restore original weight
            criterion.weight = original_weight

            analysis["weight_variations"][criterion.name] = variations

            # Calculate stability (how often the best option changed)
            changes = sum(1 for v in variations if v["changed"])
            analysis["rank_stability"][criterion.name] = 1.0 - (changes / len(variations))

        # Re-normalize weights to original state
        total_weight = sum(c.weight for c in self.criteria)
        for c in self.criteria:
            c.weight = c.weight / total_weight

        return analysis


# Convenience functions for common use cases

def quick_evaluate(
    options: List[Dict[str, Any]],
    criteria: List[Dict[str, Any]],
    method: str = "weighted_sum"
) -> Dict[str, Any]:
    """
    Quick evaluation function with dictionary inputs.

    Args:
        options: List of option dicts with keys: id, name, description, attributes
        criteria: List of criterion dicts with keys: name, weight, optimization
        method: Evaluation method name

    Returns:
        Dictionary with evaluation results
    """
    # Convert dicts to objects
    option_objects = []
    for opt in options:
        option_objects.append(Option(
            id=opt["id"],
            name=opt.get("name", opt["id"]),
            description=opt.get("description", ""),
            attributes=opt.get("attributes", {}),
            metadata=opt.get("metadata", {})
        ))

    criterion_objects = []
    for crit in criteria:
        opt_type = OptimizationType.MINIMIZE if crit.get("optimization") == "minimize" else OptimizationType.MAXIMIZE
        criterion_objects.append(Criterion(
            name=crit["name"],
            weight=crit.get("weight", 1.0),
            optimization=opt_type,
            description=crit.get("description", "")
        ))

    # Create evaluator and evaluate
    method_enum = EvaluationMethod(method)
    evaluator = OptionEvaluator(criterion_objects, method=method_enum)
    result = evaluator.evaluate(option_objects)

    # Convert result to dict
    return {
        "best_option": result.best_option_id,
        "rankings": result.ranked_options,
        "explanation": result.explanation,
        "scores": {
            opt_id: {
                "total": score.total_score,
                "criteria": score.criterion_scores,
                "raw_values": score.raw_values
            }
            for opt_id, score in result.scores.items()
        }
    }


def compare_methods(
    options: List[Option],
    criteria: List[Criterion]
) -> Dict[EvaluationMethod, str]:
    """
    Compare results across different evaluation methods.

    Returns:
        Dictionary mapping methods to their best option IDs
    """
    results = {}

    for method in [EvaluationMethod.WEIGHTED_SUM, EvaluationMethod.TOPSIS, EvaluationMethod.MULTI_OBJECTIVE]:
        evaluator = OptionEvaluator(criteria, method=method)
        result = evaluator.evaluate(options)
        results[method] = result.best_option_id

    return results


if __name__ == "__main__":
    # Example usage
    print("Option Evaluator Skill - Multi-Criteria Decision Analysis")
    print("=" * 60)
    print("\nThis skill helps evaluate multiple options based on weighted criteria.")
    print("See example_option_evaluation.py for detailed usage examples.")
