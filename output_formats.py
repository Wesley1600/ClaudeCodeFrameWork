"""
Structured Output Formats Module for UMAP Analogy Engine

This module provides comprehensive formatting capabilities for converting unstructured
outputs into structured formats such as JSON, tables, CSV, and Markdown. It includes:
- Sorting and deduplication utilities
- Schema validation for data conformance
- Multiple output format support (JSON, CSV, Markdown, HTML tables)
- Integration with analogy results, training metrics, and relation axes

Author: Claude Code Framework
License: MIT
"""

import json
import csv
import io
from typing import List, Tuple, Dict, Any, Optional, Union, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import OrderedDict
import warnings

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. Some features may be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    warnings.warn("NumPy not available. Some features may be limited.")


# ============================================================================
# DATA CLASSES FOR STRUCTURED OUTPUTS
# ============================================================================

@dataclass
class AnalogyResult:
    """Structured representation of a single analogy result."""
    rank: int
    word_index: int
    word: str
    similarity_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AnalogyResultSet:
    """Structured representation of a complete analogy query result."""
    query_word: str
    query_index: int
    relation_name: Optional[str]
    reference_pair: Optional[Tuple[str, str]]
    results: List[AnalogyResult]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['results'] = [r.to_dict() for r in self.results]
        return data


@dataclass
class TrainingMetrics:
    """Structured representation of training metrics."""
    epoch: int
    total_loss: float
    umap_loss: float
    alignment_loss: float
    orthogonality_loss: float
    learning_rate: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class RelationAxis:
    """Structured representation of a learned relation axis."""
    relation_name: str
    relation_index: int
    mean_direction: List[float]
    scale: float
    num_clusters: int
    centroids: Optional[List[List[float]]] = None
    statistics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# SCHEMA VALIDATION
# ============================================================================

class SchemaValidator:
    """Validates data against expected schemas."""

    @staticmethod
    def validate_analogy_result(data: Dict[str, Any], strict: bool = False) -> bool:
        """
        Validate analogy result dictionary against expected schema.

        Args:
            data: Dictionary to validate
            strict: If True, raise ValueError on validation failure

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If strict=True and validation fails
        """
        required_fields = {'rank', 'word_index', 'word', 'similarity_score'}
        optional_fields = {'metadata'}

        missing = required_fields - set(data.keys())
        if missing:
            if strict:
                raise ValueError(f"Missing required fields: {missing}")
            return False

        # Type validation
        try:
            assert isinstance(data['rank'], int)
            assert isinstance(data['word_index'], int)
            assert isinstance(data['word'], str)
            assert isinstance(data['similarity_score'], (int, float))
        except AssertionError:
            if strict:
                raise ValueError("Type validation failed for analogy result")
            return False

        return True

    @staticmethod
    def validate_training_metrics(data: Dict[str, Any], strict: bool = False) -> bool:
        """
        Validate training metrics dictionary against expected schema.

        Args:
            data: Dictionary to validate
            strict: If True, raise ValueError on validation failure

        Returns:
            True if valid, False otherwise
        """
        required_fields = {'epoch', 'total_loss'}

        missing = required_fields - set(data.keys())
        if missing:
            if strict:
                raise ValueError(f"Missing required fields: {missing}")
            return False

        # Type validation
        try:
            assert isinstance(data['epoch'], int)
            assert isinstance(data['total_loss'], (int, float))
        except AssertionError:
            if strict:
                raise ValueError("Type validation failed for training metrics")
            return False

        return True

    @staticmethod
    def validate_relation_axis(data: Dict[str, Any], strict: bool = False) -> bool:
        """
        Validate relation axis dictionary against expected schema.

        Args:
            data: Dictionary to validate
            strict: If True, raise ValueError on validation failure

        Returns:
            True if valid, False otherwise
        """
        required_fields = {'relation_name', 'mean_direction', 'scale'}

        missing = required_fields - set(data.keys())
        if missing:
            if strict:
                raise ValueError(f"Missing required fields: {missing}")
            return False

        # Type validation
        try:
            assert isinstance(data['relation_name'], str)
            assert isinstance(data['mean_direction'], (list, tuple))
            assert isinstance(data['scale'], (int, float))
        except AssertionError:
            if strict:
                raise ValueError("Type validation failed for relation axis")
            return False

        return True


# ============================================================================
# DATA PROCESSING UTILITIES
# ============================================================================

class DataProcessor:
    """Utilities for sorting, deduplication, and data cleaning."""

    @staticmethod
    def deduplicate_by_key(
        data: List[Dict[str, Any]],
        key: str,
        keep: str = 'first'
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicates from list of dictionaries based on a key.

        Args:
            data: List of dictionaries
            key: Key to use for deduplication
            keep: 'first' or 'last' - which duplicate to keep

        Returns:
            Deduplicated list
        """
        seen = set()
        result = []

        items = data if keep == 'first' else reversed(data)

        for item in items:
            value = item.get(key)
            if value not in seen:
                seen.add(value)
                result.append(item)

        return result if keep == 'first' else list(reversed(result))

    @staticmethod
    def sort_by_keys(
        data: List[Dict[str, Any]],
        keys: Union[str, List[str]],
        reverse: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Sort list of dictionaries by one or more keys.

        Args:
            data: List of dictionaries
            keys: Single key or list of keys to sort by
            reverse: If True, sort in descending order

        Returns:
            Sorted list
        """
        if isinstance(keys, str):
            keys = [keys]

        def get_sort_key(item):
            return tuple(item.get(k, None) for k in keys)

        return sorted(data, key=get_sort_key, reverse=reverse)

    @staticmethod
    def filter_by_threshold(
        data: List[Dict[str, Any]],
        key: str,
        threshold: float,
        comparison: str = 'ge'
    ) -> List[Dict[str, Any]]:
        """
        Filter list of dictionaries by threshold on a numeric key.

        Args:
            data: List of dictionaries
            key: Key to filter on
            threshold: Threshold value
            comparison: 'ge' (>=), 'gt' (>), 'le' (<=), 'lt' (<), 'eq' (==)

        Returns:
            Filtered list
        """
        comparisons = {
            'ge': lambda x, t: x >= t,
            'gt': lambda x, t: x > t,
            'le': lambda x, t: x <= t,
            'lt': lambda x, t: x < t,
            'eq': lambda x, t: x == t,
        }

        if comparison not in comparisons:
            raise ValueError(f"Invalid comparison: {comparison}")

        comp_func = comparisons[comparison]
        return [item for item in data if comp_func(item.get(key, 0), threshold)]

    @staticmethod
    def normalize_scores(
        data: List[Dict[str, Any]],
        score_key: str,
        method: str = 'minmax'
    ) -> List[Dict[str, Any]]:
        """
        Normalize score values in list of dictionaries.

        Args:
            data: List of dictionaries
            score_key: Key containing scores to normalize
            method: 'minmax' (0-1) or 'zscore' (standard score)

        Returns:
            Data with normalized scores
        """
        scores = [item[score_key] for item in data]

        if method == 'minmax':
            min_score = min(scores)
            max_score = max(scores)
            range_score = max_score - min_score

            if range_score == 0:
                return data  # All scores are the same

            result = []
            for item in data:
                new_item = item.copy()
                new_item[score_key] = (item[score_key] - min_score) / range_score
                result.append(new_item)

        elif method == 'zscore':
            mean = sum(scores) / len(scores)
            variance = sum((x - mean) ** 2 for x in scores) / len(scores)
            std = variance ** 0.5

            if std == 0:
                return data  # All scores are the same

            result = []
            for item in data:
                new_item = item.copy()
                new_item[score_key] = (item[score_key] - mean) / std
                result.append(new_item)
        else:
            raise ValueError(f"Invalid normalization method: {method}")

        return result


# ============================================================================
# ANALOGIES FORMATTER
# ============================================================================

class AnalogiesFormatter:
    """Format analogy results into various structured outputs."""

    @staticmethod
    def from_raw_results(
        results: List[Tuple[int, float]],
        vocab: Optional[List[str]] = None,
        query_word: Optional[str] = None,
        query_index: Optional[int] = None,
        relation_name: Optional[str] = None,
        reference_pair: Optional[Tuple[str, str]] = None,
        sort: bool = True,
        deduplicate: bool = True,
        top_k: Optional[int] = None
    ) -> AnalogyResultSet:
        """
        Convert raw analogy results to structured format.

        Args:
            results: List of (index, score) tuples
            vocab: Vocabulary list mapping indices to words
            query_word: Query word used
            query_index: Query word index
            relation_name: Name of the relation used
            reference_pair: Reference pair used (if applicable)
            sort: Sort by score descending
            deduplicate: Remove duplicate indices
            top_k: Keep only top K results

        Returns:
            Structured AnalogyResultSet
        """
        # Convert to structured format
        analogy_results = []
        for idx, score in results:
            word = vocab[idx] if vocab and idx < len(vocab) else f"<idx_{idx}>"
            analogy_results.append(AnalogyResult(
                rank=0,  # Will be set after sorting
                word_index=idx,
                word=word,
                similarity_score=float(score)
            ))

        # Deduplicate if requested
        if deduplicate:
            seen_indices = set()
            unique_results = []
            for result in analogy_results:
                if result.word_index not in seen_indices:
                    seen_indices.add(result.word_index)
                    unique_results.append(result)
            analogy_results = unique_results

        # Sort if requested
        if sort:
            analogy_results.sort(key=lambda x: x.similarity_score, reverse=True)

        # Limit to top K if requested
        if top_k is not None:
            analogy_results = analogy_results[:top_k]

        # Set ranks
        for rank, result in enumerate(analogy_results, start=1):
            result.rank = rank

        # Create result set
        return AnalogyResultSet(
            query_word=query_word or "<unknown>",
            query_index=query_index or -1,
            relation_name=relation_name,
            reference_pair=reference_pair,
            results=analogy_results
        )

    @staticmethod
    def to_json(
        result_set: AnalogyResultSet,
        pretty: bool = True,
        include_metadata: bool = True
    ) -> str:
        """
        Convert to JSON format.

        Args:
            result_set: Structured analogy result set
            pretty: Pretty-print with indentation
            include_metadata: Include metadata fields

        Returns:
            JSON string
        """
        data = result_set.to_dict()

        if not include_metadata:
            data.pop('metadata', None)
            data.pop('timestamp', None)

        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def to_csv(
        result_set: AnalogyResultSet,
        include_query_info: bool = True
    ) -> str:
        """
        Convert to CSV format.

        Args:
            result_set: Structured analogy result set
            include_query_info: Include query information in each row

        Returns:
            CSV string
        """
        output = io.StringIO()

        fieldnames = ['rank', 'word_index', 'word', 'similarity_score']
        if include_query_info:
            fieldnames = ['query_word', 'relation_name'] + fieldnames

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for result in result_set.results:
            row = {
                'rank': result.rank,
                'word_index': result.word_index,
                'word': result.word,
                'similarity_score': f"{result.similarity_score:.6f}"
            }

            if include_query_info:
                row['query_word'] = result_set.query_word
                row['relation_name'] = result_set.relation_name or 'N/A'

            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_markdown(
        result_set: AnalogyResultSet,
        include_header: bool = True,
        max_results: Optional[int] = None
    ) -> str:
        """
        Convert to Markdown table format.

        Args:
            result_set: Structured analogy result set
            include_header: Include header with query information
            max_results: Maximum number of results to include

        Returns:
            Markdown string
        """
        lines = []

        if include_header:
            lines.append(f"# Analogy Results")
            lines.append(f"")
            lines.append(f"**Query:** {result_set.query_word}")
            if result_set.relation_name:
                lines.append(f"**Relation:** {result_set.relation_name}")
            if result_set.reference_pair:
                lines.append(f"**Reference Pair:** {result_set.reference_pair[0]} → {result_set.reference_pair[1]}")
            lines.append(f"**Timestamp:** {result_set.timestamp}")
            lines.append(f"")

        # Table header
        lines.append("| Rank | Word | Similarity Score |")
        lines.append("|------|------|------------------|")

        # Table rows
        results = result_set.results[:max_results] if max_results else result_set.results
        for result in results:
            lines.append(f"| {result.rank} | {result.word} | {result.similarity_score:.6f} |")

        return "\n".join(lines)

    @staticmethod
    def to_html_table(
        result_set: AnalogyResultSet,
        table_class: str = "analogy-results",
        max_results: Optional[int] = None
    ) -> str:
        """
        Convert to HTML table format.

        Args:
            result_set: Structured analogy result set
            table_class: CSS class for the table
            max_results: Maximum number of results to include

        Returns:
            HTML string
        """
        lines = []
        lines.append(f'<table class="{table_class}">')
        lines.append('  <thead>')
        lines.append('    <tr>')
        lines.append('      <th>Rank</th>')
        lines.append('      <th>Word</th>')
        lines.append('      <th>Similarity Score</th>')
        lines.append('    </tr>')
        lines.append('  </thead>')
        lines.append('  <tbody>')

        results = result_set.results[:max_results] if max_results else result_set.results
        for result in results:
            lines.append('    <tr>')
            lines.append(f'      <td>{result.rank}</td>')
            lines.append(f'      <td>{result.word}</td>')
            lines.append(f'      <td>{result.similarity_score:.6f}</td>')
            lines.append('    </tr>')

        lines.append('  </tbody>')
        lines.append('</table>')

        return "\n".join(lines)


# ============================================================================
# TRAINING REPORT FORMATTER
# ============================================================================

class TrainingReportFormatter:
    """Format training metrics and statistics into structured outputs."""

    @staticmethod
    def from_training_history(
        loss_history: List[float],
        umap_loss_history: Optional[List[float]] = None,
        align_loss_history: Optional[List[float]] = None,
        ortho_loss_history: Optional[List[float]] = None,
        lr_history: Optional[List[float]] = None,
        relation_stats: Optional[Dict[str, Dict[str, float]]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create structured training report from training history.

        Args:
            loss_history: Total loss per epoch
            umap_loss_history: UMAP loss per epoch
            align_loss_history: Alignment loss per epoch
            ortho_loss_history: Orthogonality loss per epoch
            lr_history: Learning rate per epoch
            relation_stats: Relation statistics dictionary
            hyperparameters: Training hyperparameters

        Returns:
            Structured training report dictionary
        """
        num_epochs = len(loss_history)

        # Create metrics per epoch
        metrics_per_epoch = []
        for epoch in range(num_epochs):
            metric = TrainingMetrics(
                epoch=epoch + 1,
                total_loss=float(loss_history[epoch]),
                umap_loss=float(umap_loss_history[epoch]) if umap_loss_history else 0.0,
                alignment_loss=float(align_loss_history[epoch]) if align_loss_history else 0.0,
                orthogonality_loss=float(ortho_loss_history[epoch]) if ortho_loss_history else 0.0,
                learning_rate=float(lr_history[epoch]) if lr_history else 0.0
            )
            metrics_per_epoch.append(metric.to_dict())

        # Calculate summary statistics
        summary = {
            'total_epochs': num_epochs,
            'final_loss': float(loss_history[-1]),
            'best_loss': float(min(loss_history)),
            'best_epoch': int(loss_history.index(min(loss_history))) + 1,
            'average_loss': float(sum(loss_history) / len(loss_history)),
        }

        # Compile full report
        report = {
            'summary': summary,
            'metrics_per_epoch': metrics_per_epoch,
            'relation_statistics': relation_stats or {},
            'hyperparameters': hyperparameters or {},
            'timestamp': datetime.utcnow().isoformat()
        }

        return report

    @staticmethod
    def to_json(report: Dict[str, Any], pretty: bool = True) -> str:
        """
        Convert training report to JSON.

        Args:
            report: Training report dictionary
            pretty: Pretty-print with indentation

        Returns:
            JSON string
        """
        indent = 2 if pretty else None
        return json.dumps(report, indent=indent, ensure_ascii=False)

    @staticmethod
    def to_csv(report: Dict[str, Any], include_summary: bool = True) -> str:
        """
        Convert training metrics to CSV format.

        Args:
            report: Training report dictionary
            include_summary: Include summary row at the end

        Returns:
            CSV string
        """
        output = io.StringIO()

        metrics = report['metrics_per_epoch']
        if not metrics:
            return ""

        fieldnames = list(metrics[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for metric in metrics:
            writer.writerow(metric)

        if include_summary:
            output.write("\n# Summary\n")
            summary = report['summary']
            for key, value in summary.items():
                output.write(f"{key},{value}\n")

        return output.getvalue()

    @staticmethod
    def to_markdown(report: Dict[str, Any], include_plots: bool = False) -> str:
        """
        Convert training report to Markdown format.

        Args:
            report: Training report dictionary
            include_plots: Include ASCII plots (experimental)

        Returns:
            Markdown string
        """
        lines = []

        # Title and summary
        lines.append("# Training Report")
        lines.append("")
        lines.append("## Summary")
        lines.append("")

        summary = report['summary']
        for key, value in summary.items():
            formatted_key = key.replace('_', ' ').title()
            lines.append(f"- **{formatted_key}:** {value}")

        lines.append("")

        # Hyperparameters
        if report.get('hyperparameters'):
            lines.append("## Hyperparameters")
            lines.append("")
            for key, value in report['hyperparameters'].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Relation statistics
        if report.get('relation_statistics'):
            lines.append("## Relation Statistics")
            lines.append("")
            lines.append("| Relation | Mean Length | Std Length | Mean Direction Cos |")
            lines.append("|----------|-------------|------------|--------------------|")

            for rel_name, stats in report['relation_statistics'].items():
                mean_len = stats.get('mean_length', 0)
                std_len = stats.get('std_length', 0)
                mean_cos = stats.get('mean_direction_cos', 0)
                lines.append(f"| {rel_name} | {mean_len:.4f} | {std_len:.4f} | {mean_cos:.4f} |")

            lines.append("")

        # Training metrics table (first 10 and last 10 epochs)
        metrics = report['metrics_per_epoch']
        if metrics:
            lines.append("## Training Metrics")
            lines.append("")
            lines.append("### First 10 Epochs")
            lines.append("")
            lines.append("| Epoch | Total Loss | UMAP Loss | Align Loss | Ortho Loss | LR |")
            lines.append("|-------|------------|-----------|------------|------------|----|")

            for metric in metrics[:10]:
                lines.append(
                    f"| {metric['epoch']} | {metric['total_loss']:.6f} | "
                    f"{metric['umap_loss']:.6f} | {metric['alignment_loss']:.6f} | "
                    f"{metric['orthogonality_loss']:.6f} | {metric['learning_rate']:.6f} |"
                )

            if len(metrics) > 20:
                lines.append("")
                lines.append("### Last 10 Epochs")
                lines.append("")
                lines.append("| Epoch | Total Loss | UMAP Loss | Align Loss | Ortho Loss | LR |")
                lines.append("|-------|------------|-----------|------------|------------|----|")

                for metric in metrics[-10:]:
                    lines.append(
                        f"| {metric['epoch']} | {metric['total_loss']:.6f} | "
                        f"{metric['umap_loss']:.6f} | {metric['alignment_loss']:.6f} | "
                        f"{metric['orthogonality_loss']:.6f} | {metric['learning_rate']:.6f} |"
                    )

        lines.append("")
        lines.append(f"*Generated: {report['timestamp']}*")

        return "\n".join(lines)


# ============================================================================
# AXIS EXPORT FORMATTER
# ============================================================================

class AxisExportFormatter:
    """Format learned relation axes into structured outputs."""

    @staticmethod
    def from_raw_axes(
        axes: List[Optional[Dict[str, Any]]],
        relation_names: Optional[List[str]] = None,
        include_centroids: bool = False
    ) -> List[RelationAxis]:
        """
        Convert raw axis dictionaries to structured format.

        Args:
            axes: List of axis dictionaries from extract_relation_axes()
            relation_names: Names for each relation
            include_centroids: Include centroid data

        Returns:
            List of structured RelationAxis objects
        """
        structured_axes = []

        for idx, axis in enumerate(axes):
            if axis is None:
                continue

            # Extract mean direction
            mean_dir = axis.get('mean_direction')
            if TORCH_AVAILABLE and torch.is_tensor(mean_dir):
                mean_dir = mean_dir.cpu().numpy().tolist()
            elif NUMPY_AVAILABLE and isinstance(mean_dir, np.ndarray):
                mean_dir = mean_dir.tolist()
            elif not isinstance(mean_dir, list):
                mean_dir = list(mean_dir)

            # Extract centroids if requested
            centroids = None
            if include_centroids and 'centroids' in axis:
                cents = axis['centroids']
                if TORCH_AVAILABLE and torch.is_tensor(cents):
                    centroids = cents.cpu().numpy().tolist()
                elif NUMPY_AVAILABLE and isinstance(cents, np.ndarray):
                    centroids = cents.tolist()

            # Get relation name
            rel_name = relation_names[idx] if relation_names and idx < len(relation_names) else f"relation_{idx}"

            # Create structured axis
            structured_axis = RelationAxis(
                relation_name=rel_name,
                relation_index=idx,
                mean_direction=mean_dir,
                scale=float(axis.get('scale', 1.0)),
                num_clusters=len(centroids) if centroids else 0,
                centroids=centroids,
                statistics={}
            )

            structured_axes.append(structured_axis)

        return structured_axes

    @staticmethod
    def to_json(
        axes: List[RelationAxis],
        pretty: bool = True,
        include_centroids: bool = False
    ) -> str:
        """
        Convert relation axes to JSON.

        Args:
            axes: List of structured RelationAxis objects
            pretty: Pretty-print with indentation
            include_centroids: Include centroid data

        Returns:
            JSON string
        """
        data = []
        for axis in axes:
            axis_dict = axis.to_dict()
            if not include_centroids:
                axis_dict.pop('centroids', None)
            data.append(axis_dict)

        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def to_csv(axes: List[RelationAxis]) -> str:
        """
        Convert relation axes to CSV format (without full vectors).

        Args:
            axes: List of structured RelationAxis objects

        Returns:
            CSV string
        """
        output = io.StringIO()

        fieldnames = ['relation_name', 'relation_index', 'scale', 'num_clusters', 'direction_dim']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for axis in axes:
            row = {
                'relation_name': axis.relation_name,
                'relation_index': axis.relation_index,
                'scale': f"{axis.scale:.6f}",
                'num_clusters': axis.num_clusters,
                'direction_dim': len(axis.mean_direction)
            }
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_markdown(axes: List[RelationAxis]) -> str:
        """
        Convert relation axes to Markdown table.

        Args:
            axes: List of structured RelationAxis objects

        Returns:
            Markdown string
        """
        lines = []
        lines.append("# Learned Relation Axes")
        lines.append("")
        lines.append("| Relation | Index | Scale | Clusters | Dimension |")
        lines.append("|----------|-------|-------|----------|-----------|")

        for axis in axes:
            lines.append(
                f"| {axis.relation_name} | {axis.relation_index} | "
                f"{axis.scale:.4f} | {axis.num_clusters} | {len(axis.mean_direction)} |"
            )

        return "\n".join(lines)

    @staticmethod
    def to_numpy_archive(axes: List[RelationAxis], filepath: str):
        """
        Save relation axes to NumPy .npz archive.

        Args:
            axes: List of structured RelationAxis objects
            filepath: Path to save .npz file

        Requires:
            NumPy
        """
        if not NUMPY_AVAILABLE:
            raise ImportError("NumPy is required for .npz export")

        import numpy as np

        data = {}
        for axis in axes:
            prefix = f"{axis.relation_name}"
            data[f"{prefix}_direction"] = np.array(axis.mean_direction)
            data[f"{prefix}_scale"] = np.array(axis.scale)
            if axis.centroids:
                data[f"{prefix}_centroids"] = np.array(axis.centroids)

        np.savez(filepath, **data)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def format_analogies(
    results: List[Tuple[int, float]],
    vocab: Optional[List[str]] = None,
    output_format: str = 'json',
    **kwargs
) -> str:
    """
    One-line convenience function to format analogy results.

    Args:
        results: Raw analogy results as list of (index, score) tuples
        vocab: Vocabulary list
        output_format: 'json', 'csv', 'markdown', or 'html'
        **kwargs: Additional arguments passed to formatting functions

    Returns:
        Formatted string
    """
    result_set = AnalogiesFormatter.from_raw_results(results, vocab=vocab, **kwargs)

    if output_format == 'json':
        return AnalogiesFormatter.to_json(result_set)
    elif output_format == 'csv':
        return AnalogiesFormatter.to_csv(result_set)
    elif output_format == 'markdown':
        return AnalogiesFormatter.to_markdown(result_set)
    elif output_format == 'html':
        return AnalogiesFormatter.to_html_table(result_set)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def format_training_report(
    loss_history: List[float],
    output_format: str = 'json',
    **kwargs
) -> str:
    """
    One-line convenience function to format training report.

    Args:
        loss_history: Loss values per epoch
        output_format: 'json', 'csv', or 'markdown'
        **kwargs: Additional arguments passed to from_training_history

    Returns:
        Formatted string
    """
    report = TrainingReportFormatter.from_training_history(loss_history, **kwargs)

    if output_format == 'json':
        return TrainingReportFormatter.to_json(report)
    elif output_format == 'csv':
        return TrainingReportFormatter.to_csv(report)
    elif output_format == 'markdown':
        return TrainingReportFormatter.to_markdown(report)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def format_relation_axes(
    axes: List[Optional[Dict[str, Any]]],
    output_format: str = 'json',
    **kwargs
) -> str:
    """
    One-line convenience function to format relation axes.

    Args:
        axes: Raw axes from extract_relation_axes()
        output_format: 'json', 'csv', or 'markdown'
        **kwargs: Additional arguments passed to from_raw_axes

    Returns:
        Formatted string
    """
    structured_axes = AxisExportFormatter.from_raw_axes(axes, **kwargs)

    if output_format == 'json':
        return AxisExportFormatter.to_json(structured_axes)
    elif output_format == 'csv':
        return AxisExportFormatter.to_csv(structured_axes)
    elif output_format == 'markdown':
        return AxisExportFormatter.to_markdown(structured_axes)
    else:
        raise ValueError(f"Unknown format: {output_format}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Output Formats Module - Example Usage")
    print("=" * 80)
    print()

    # Example 1: Format analogy results
    print("Example 1: Analogy Results Formatting")
    print("-" * 40)

    raw_results = [(0, 0.95), (1, 0.87), (2, 0.82), (0, 0.75), (3, 0.70)]
    vocab = ["king", "queen", "man", "woman"]

    result_set = AnalogiesFormatter.from_raw_results(
        raw_results,
        vocab=vocab,
        query_word="king",
        relation_name="gender",
        deduplicate=True,
        top_k=3
    )

    print("JSON Output:")
    print(AnalogiesFormatter.to_json(result_set, pretty=True))
    print()

    print("Markdown Table:")
    print(AnalogiesFormatter.to_markdown(result_set, include_header=True))
    print()

    # Example 2: Format training report
    print("Example 2: Training Report Formatting")
    print("-" * 40)

    loss_history = [1.5, 1.2, 0.9, 0.7, 0.6, 0.55]
    report = TrainingReportFormatter.from_training_history(
        loss_history,
        hyperparameters={'lr': 0.001, 'epochs': 6}
    )

    print("Markdown Report:")
    print(TrainingReportFormatter.to_markdown(report))
    print()

    # Example 3: Data processing utilities
    print("Example 3: Data Processing Utilities")
    print("-" * 40)

    data = [
        {'id': 1, 'score': 0.9, 'name': 'A'},
        {'id': 2, 'score': 0.7, 'name': 'B'},
        {'id': 1, 'score': 0.8, 'name': 'A'},  # Duplicate
        {'id': 3, 'score': 0.5, 'name': 'C'},
    ]

    # Deduplicate
    dedup = DataProcessor.deduplicate_by_key(data, 'id', keep='first')
    print(f"Deduplicated (kept first): {len(dedup)} items")

    # Sort
    sorted_data = DataProcessor.sort_by_keys(dedup, 'score', reverse=True)
    print(f"Sorted by score: {[d['score'] for d in sorted_data]}")

    # Filter
    filtered = DataProcessor.filter_by_threshold(sorted_data, 'score', 0.75, 'ge')
    print(f"Filtered (score >= 0.75): {len(filtered)} items")
    print()

    print("=" * 80)
    print("Examples complete!")
