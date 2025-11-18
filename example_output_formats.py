"""
Example Script: Structured Output Formats Integration

This script demonstrates how to use the output_formats module with the
UMAP Analogy Engine to generate structured outputs in various formats.

It shows:
1. Formatting analogy results (JSON, CSV, Markdown, HTML)
2. Generating training reports
3. Exporting relation axes
4. Using data processing utilities (sorting, deduplication, filtering)
5. Schema validation

Author: Claude Code Framework
License: MIT
"""

import torch
import numpy as np
from pathlib import Path

# Import the UMAP analogy engine
from umap_analogy_engine import (
    train_relation_aware_umap,
    find_analogy,
    extract_relation_axes,
    compute_relation_statistics
)

# Import the output formatters
from output_formats import (
    AnalogiesFormatter,
    TrainingReportFormatter,
    AxisExportFormatter,
    DataProcessor,
    SchemaValidator,
    format_analogies,
    format_training_report,
    format_relation_axes
)


def create_synthetic_data(n_samples=1000, dim=300, n_relations=3):
    """Create synthetic embeddings and relation pairs for demonstration."""
    print(f"Creating synthetic data: {n_samples} samples, {dim} dimensions, {n_relations} relations")

    # Create random high-dimensional embeddings
    X_high = torch.randn(n_samples, dim)
    X_high = X_high / X_high.norm(dim=1, keepdim=True)  # Normalize

    # Create vocabulary
    vocab = [f"word_{i}" for i in range(n_samples)]

    # Create relation pairs
    relation_pairs = []
    relation_names = []

    for rel_idx in range(n_relations):
        pairs = []
        n_pairs = 50  # 50 pairs per relation

        for _ in range(n_pairs):
            # Randomly select indices
            idx1 = np.random.randint(0, n_samples)
            idx2 = np.random.randint(0, n_samples)

            if idx1 != idx2:
                pairs.append((idx1, idx2))

        relation_pairs.append(pairs)
        relation_names.append(f"relation_{rel_idx}")

    return X_high, vocab, relation_pairs, relation_names


def demonstrate_analogy_formatting(model, Z_low, vocab, relation_axes):
    """Demonstrate analogy result formatting in multiple formats."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION 1: Analogy Results Formatting")
    print("=" * 80)

    # Perform an analogy query
    query_idx = 10
    query_word = vocab[query_idx]
    print(f"\nQuery word: {query_word}")
    print(f"Using relation: relation_0")

    # Get raw results
    raw_results = find_analogy(
        model=model,
        Z_low=Z_low,
        query_idx=query_idx,
        relation_axes=relation_axes,
        relation_idx=0,
        top_k=10
    )

    print(f"Found {len(raw_results)} raw results")

    # Format 1: JSON
    print("\n" + "-" * 40)
    print("Format 1: JSON (structured)")
    print("-" * 40)

    json_output = format_analogies(
        raw_results,
        vocab=vocab,
        output_format='json',
        query_word=query_word,
        query_index=query_idx,
        relation_name='relation_0',
        deduplicate=True,
        sort=True,
        top_k=5
    )

    print(json_output)

    # Save to file
    output_dir = Path("output_examples")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "analogies.json", "w") as f:
        f.write(json_output)
    print(f"\n✓ Saved to: {output_dir / 'analogies.json'}")

    # Format 2: CSV
    print("\n" + "-" * 40)
    print("Format 2: CSV (tabular)")
    print("-" * 40)

    result_set = AnalogiesFormatter.from_raw_results(
        raw_results,
        vocab=vocab,
        query_word=query_word,
        query_index=query_idx,
        relation_name='relation_0',
        top_k=5
    )

    csv_output = AnalogiesFormatter.to_csv(result_set, include_query_info=True)
    print(csv_output)

    with open(output_dir / "analogies.csv", "w") as f:
        f.write(csv_output)
    print(f"✓ Saved to: {output_dir / 'analogies.csv'}")

    # Format 3: Markdown
    print("\n" + "-" * 40)
    print("Format 3: Markdown (human-readable)")
    print("-" * 40)

    markdown_output = AnalogiesFormatter.to_markdown(result_set, include_header=True)
    print(markdown_output)

    with open(output_dir / "analogies.md", "w") as f:
        f.write(markdown_output)
    print(f"\n✓ Saved to: {output_dir / 'analogies.md'}")

    # Format 4: HTML Table
    print("\n" + "-" * 40)
    print("Format 4: HTML Table")
    print("-" * 40)

    html_output = AnalogiesFormatter.to_html_table(result_set, table_class="results-table")
    print(html_output[:300] + "...")  # Show first 300 chars

    with open(output_dir / "analogies.html", "w") as f:
        # Add basic HTML wrapper
        f.write("<!DOCTYPE html>\n<html>\n<head>\n")
        f.write("<style>table { border-collapse: collapse; } th, td { border: 1px solid black; padding: 8px; }</style>\n")
        f.write("</head>\n<body>\n")
        f.write(f"<h1>Analogy Results for: {query_word}</h1>\n")
        f.write(html_output)
        f.write("\n</body>\n</html>")
    print(f"\n✓ Saved to: {output_dir / 'analogies.html'}")


def demonstrate_training_report(loss_history, relation_pairs, relation_names):
    """Demonstrate training report formatting."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION 2: Training Report Formatting")
    print("=" * 80)

    # Simulate component losses (in real usage, these would be tracked during training)
    n_epochs = len(loss_history)
    umap_losses = [loss_history[i] * 0.6 for i in range(n_epochs)]
    align_losses = [loss_history[i] * 0.3 for i in range(n_epochs)]
    ortho_losses = [loss_history[i] * 0.1 for i in range(n_epochs)]
    lrs = [0.001 * (0.95 ** i) for i in range(n_epochs)]

    # Create mock relation statistics
    relation_stats = {}
    for rel_name in relation_names:
        relation_stats[rel_name] = {
            'mean_length': np.random.uniform(0.5, 2.0),
            'std_length': np.random.uniform(0.1, 0.5),
            'mean_direction_cos': np.random.uniform(0.7, 0.95)
        }

    # Hyperparameters
    hyperparams = {
        'n_neighbors': 15,
        'min_dist': 0.1,
        'epochs': n_epochs,
        'learning_rate': 0.001,
        'batch_size': 20000,
        'align_weight': 1.0,
        'ortho_weight': 0.1,
    }

    # Format 1: JSON Report
    print("\n" + "-" * 40)
    print("Format 1: JSON Training Report")
    print("-" * 40)

    report = TrainingReportFormatter.from_training_history(
        loss_history=loss_history,
        umap_loss_history=umap_losses,
        align_loss_history=align_losses,
        ortho_loss_history=ortho_losses,
        lr_history=lrs,
        relation_stats=relation_stats,
        hyperparameters=hyperparams
    )

    json_report = TrainingReportFormatter.to_json(report, pretty=True)
    print(json_report[:500] + "\n... (truncated)")

    output_dir = Path("output_examples")
    with open(output_dir / "training_report.json", "w") as f:
        f.write(json_report)
    print(f"\n✓ Saved to: {output_dir / 'training_report.json'}")

    # Format 2: Markdown Report
    print("\n" + "-" * 40)
    print("Format 2: Markdown Training Report")
    print("-" * 40)

    markdown_report = TrainingReportFormatter.to_markdown(report)
    print(markdown_report)

    with open(output_dir / "training_report.md", "w") as f:
        f.write(markdown_report)
    print(f"\n✓ Saved to: {output_dir / 'training_report.md'}")

    # Format 3: CSV Metrics
    print("\n" + "-" * 40)
    print("Format 3: CSV Training Metrics")
    print("-" * 40)

    csv_report = TrainingReportFormatter.to_csv(report, include_summary=True)
    print(csv_report[:400] + "\n... (truncated)")

    with open(output_dir / "training_metrics.csv", "w") as f:
        f.write(csv_report)
    print(f"\n✓ Saved to: {output_dir / 'training_metrics.csv'}")


def demonstrate_axis_export(relation_axes, relation_names):
    """Demonstrate relation axis export formatting."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION 3: Relation Axes Export")
    print("=" * 80)

    # Format 1: JSON Export
    print("\n" + "-" * 40)
    print("Format 1: JSON Axes (with centroids)")
    print("-" * 40)

    json_axes = format_relation_axes(
        relation_axes,
        output_format='json',
        relation_names=relation_names,
        include_centroids=True
    )

    print(json_axes[:500] + "\n... (truncated)")

    output_dir = Path("output_examples")
    with open(output_dir / "relation_axes.json", "w") as f:
        f.write(json_axes)
    print(f"\n✓ Saved to: {output_dir / 'relation_axes.json'}")

    # Format 2: CSV Summary
    print("\n" + "-" * 40)
    print("Format 2: CSV Axes Summary")
    print("-" * 40)

    structured_axes = AxisExportFormatter.from_raw_axes(
        relation_axes,
        relation_names=relation_names,
        include_centroids=False
    )

    csv_axes = AxisExportFormatter.to_csv(structured_axes)
    print(csv_axes)

    with open(output_dir / "relation_axes.csv", "w") as f:
        f.write(csv_axes)
    print(f"✓ Saved to: {output_dir / 'relation_axes.csv'}")

    # Format 3: Markdown Table
    print("\n" + "-" * 40)
    print("Format 3: Markdown Axes Table")
    print("-" * 40)

    markdown_axes = AxisExportFormatter.to_markdown(structured_axes)
    print(markdown_axes)

    with open(output_dir / "relation_axes.md", "w") as f:
        f.write(markdown_axes)
    print(f"\n✓ Saved to: {output_dir / 'relation_axes.md'}")

    # Format 4: NumPy Archive
    print("\n" + "-" * 40)
    print("Format 4: NumPy .npz Archive")
    print("-" * 40)

    npz_path = output_dir / "relation_axes.npz"
    AxisExportFormatter.to_numpy_archive(structured_axes, str(npz_path))
    print(f"✓ Saved to: {npz_path}")

    # Load and verify
    loaded = np.load(npz_path)
    print(f"Archive contains {len(loaded.files)} arrays:")
    for key in loaded.files[:6]:  # Show first 6
        print(f"  - {key}: shape {loaded[key].shape}")


def demonstrate_data_processing():
    """Demonstrate data processing utilities."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION 4: Data Processing Utilities")
    print("=" * 80)

    # Sample data with duplicates and varying scores
    sample_data = [
        {'word_index': 5, 'word': 'apple', 'score': 0.95},
        {'word_index': 12, 'word': 'banana', 'score': 0.87},
        {'word_index': 5, 'word': 'apple', 'score': 0.90},  # Duplicate
        {'word_index': 8, 'word': 'orange', 'score': 0.82},
        {'word_index': 15, 'word': 'grape', 'score': 0.78},
        {'word_index': 12, 'word': 'banana', 'score': 0.85},  # Duplicate
        {'word_index': 3, 'word': 'cherry', 'score': 0.65},
        {'word_index': 20, 'word': 'melon', 'score': 0.55},
    ]

    print(f"\nOriginal data: {len(sample_data)} items")
    for item in sample_data:
        print(f"  {item}")

    # 1. Deduplication
    print("\n" + "-" * 40)
    print("1. Deduplication (by word_index, keep first)")
    print("-" * 40)

    dedup_data = DataProcessor.deduplicate_by_key(sample_data, 'word_index', keep='first')
    print(f"After deduplication: {len(dedup_data)} items")
    for item in dedup_data:
        print(f"  {item}")

    # 2. Sorting
    print("\n" + "-" * 40)
    print("2. Sorting (by score, descending)")
    print("-" * 40)

    sorted_data = DataProcessor.sort_by_keys(dedup_data, 'score', reverse=True)
    print(f"After sorting:")
    for item in sorted_data:
        print(f"  {item}")

    # 3. Filtering
    print("\n" + "-" * 40)
    print("3. Filtering (score >= 0.80)")
    print("-" * 40)

    filtered_data = DataProcessor.filter_by_threshold(sorted_data, 'score', 0.80, comparison='ge')
    print(f"After filtering: {len(filtered_data)} items")
    for item in filtered_data:
        print(f"  {item}")

    # 4. Score normalization
    print("\n" + "-" * 40)
    print("4. Score Normalization (min-max to 0-1)")
    print("-" * 40)

    normalized_data = DataProcessor.normalize_scores(filtered_data, 'score', method='minmax')
    print(f"After normalization:")
    for item in normalized_data:
        print(f"  {item['word']}: {item['score']:.4f}")


def demonstrate_schema_validation():
    """Demonstrate schema validation."""
    print("\n" + "=" * 80)
    print("DEMONSTRATION 5: Schema Validation")
    print("=" * 80)

    # Valid analogy result
    valid_result = {
        'rank': 1,
        'word_index': 42,
        'word': 'example',
        'similarity_score': 0.95,
        'metadata': {}
    }

    # Invalid results (missing fields, wrong types)
    invalid_result_1 = {
        'rank': 1,
        'word': 'example',
        # Missing word_index and similarity_score
    }

    invalid_result_2 = {
        'rank': "one",  # Wrong type (should be int)
        'word_index': 42,
        'word': 'example',
        'similarity_score': 0.95,
    }

    print("\n" + "-" * 40)
    print("Validating Analogy Results")
    print("-" * 40)

    # Test valid result
    print(f"\nValid result: {valid_result}")
    is_valid = SchemaValidator.validate_analogy_result(valid_result, strict=False)
    print(f"  Validation: {'✓ PASS' if is_valid else '✗ FAIL'}")

    # Test invalid result 1
    print(f"\nInvalid result 1 (missing fields): {invalid_result_1}")
    is_valid = SchemaValidator.validate_analogy_result(invalid_result_1, strict=False)
    print(f"  Validation: {'✓ PASS' if is_valid else '✗ FAIL'}")

    # Test invalid result 2
    print(f"\nInvalid result 2 (wrong types): {invalid_result_2}")
    is_valid = SchemaValidator.validate_analogy_result(invalid_result_2, strict=False)
    print(f"  Validation: {'✓ PASS' if is_valid else '✗ FAIL'}")

    # Test strict mode (raises exception)
    print("\n" + "-" * 40)
    print("Strict Mode Validation (raises exceptions)")
    print("-" * 40)

    try:
        SchemaValidator.validate_analogy_result(invalid_result_1, strict=True)
        print("  No exception raised (unexpected)")
    except ValueError as e:
        print(f"  ✓ Exception raised: {e}")


def main():
    """Main demonstration script."""
    print("=" * 80)
    print("UMAP ANALOGY ENGINE - STRUCTURED OUTPUT FORMATS DEMONSTRATION")
    print("=" * 80)

    # Create synthetic data
    print("\nSetting up demonstration data...")
    X_high, vocab, relation_pairs, relation_names = create_synthetic_data(
        n_samples=500,
        dim=300,
        n_relations=3
    )

    # Train the model (quick version for demonstration)
    print("\nTraining UMAP analogy engine (this may take a minute)...")
    print("Note: Using reduced parameters for faster demonstration")

    model, Z_low, loss_history = train_relation_aware_umap(
        X_high=X_high,
        relation_pairs=relation_pairs,
        n_components=16,
        n_neighbors=10,
        epochs=20,  # Reduced for demo
        edge_bs=5000,
        lr=1e-3,
        verbose=True
    )

    print(f"\n✓ Training complete! Final loss: {loss_history[-1]:.4f}")

    # Extract relation axes
    print("\nExtracting relation axes...")
    relation_axes = extract_relation_axes(
        model=model,
        X_high=X_high,
        Z_low=Z_low,
        relation_pairs=relation_pairs,
        num_clusters=3
    )
    print(f"✓ Extracted {len(relation_axes)} relation axes")

    # Run demonstrations
    demonstrate_analogy_formatting(model, Z_low, vocab, relation_axes)
    demonstrate_training_report(loss_history, relation_pairs, relation_names)
    demonstrate_axis_export(relation_axes, relation_names)
    demonstrate_data_processing()
    demonstrate_schema_validation()

    # Final summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 80)
    print("\nAll output files saved to: output_examples/")
    print("\nGenerated files:")
    output_dir = Path("output_examples")
    if output_dir.exists():
        for file in sorted(output_dir.iterdir()):
            print(f"  - {file.name}")

    print("\n" + "=" * 80)
    print("Key Features Demonstrated:")
    print("-" * 40)
    print("✓ Analogy results formatting (JSON, CSV, Markdown, HTML)")
    print("✓ Training report generation (JSON, CSV, Markdown)")
    print("✓ Relation axes export (JSON, CSV, Markdown, NumPy)")
    print("✓ Data processing (deduplication, sorting, filtering)")
    print("✓ Schema validation")
    print("=" * 80)


if __name__ == "__main__":
    main()
