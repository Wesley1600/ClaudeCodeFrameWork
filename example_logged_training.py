"""
Example: UMAP Analogy Engine with Activity Logging

This example demonstrates how to use the activity logging system with the
UMAP Analogy Engine for full transparency and auditability.

The example creates a synthetic dataset with multiple relations and trains
a model while logging all activities to the memory directory.
"""

import torch
import numpy as np
from logged_umap_wrapper import LoggedUMAPEngine
from activity_logger import ActivityLogger, ActivityType, LogLevel
from report_generator import ReportGenerator, generate_all_reports


def create_synthetic_dataset():
    """
    Create a synthetic dataset for demonstration.

    Returns:
        X: Input data (n_samples, n_features)
        relations: List of relation pairs
        relation_names: Names of relations
        vocab: List of sample names (for display)
    """
    print("Creating synthetic dataset...")

    # Set random seed for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)

    # Create 100 samples with 50 dimensions
    n_samples = 100
    n_features = 50

    X = torch.randn(n_samples, n_features)

    # Define 3 relations with example pairs
    # Relation 1: "shifts right" (+5 in feature 0)
    relation1_pairs = [
        (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
        (10, 15), (11, 16), (12, 17), (13, 18), (14, 19)
    ]
    for a, b in relation1_pairs:
        X[b] = X[a].clone()
        X[b, 0] += 5.0  # Shift in feature 0

    # Relation 2: "shifts up" (+3 in feature 1)
    relation2_pairs = [
        (20, 25), (21, 26), (22, 27), (23, 28), (24, 29),
        (30, 35), (31, 36), (32, 37), (33, 38), (34, 39)
    ]
    for a, b in relation2_pairs:
        X[b] = X[a].clone()
        X[b, 1] += 3.0  # Shift in feature 1

    # Relation 3: "diagonal" (+2 in both features 0 and 1)
    relation3_pairs = [
        (40, 45), (41, 46), (42, 47), (43, 48), (44, 49),
        (50, 55), (51, 56), (52, 57), (53, 58), (54, 59)
    ]
    for a, b in relation3_pairs:
        X[b] = X[a].clone()
        X[b, 0] += 2.0
        X[b, 1] += 2.0

    # Create vocabulary for demonstration
    vocab = [f"item_{i:03d}" for i in range(n_samples)]

    relation_names = ["shift_right", "shift_up", "diagonal"]
    relations = [relation1_pairs, relation2_pairs, relation3_pairs]

    print(f"  Created {n_samples} samples with {n_features} features")
    print(f"  Defined {len(relations)} relations:")
    for name, pairs in zip(relation_names, relations):
        print(f"    - {name}: {len(pairs)} pairs")

    return X, relations, relation_names, vocab


def example_basic_logging():
    """
    Example 1: Basic training with automatic logging.

    This shows the simplest usage: just wrap your training in LoggedUMAPEngine
    and all activities are automatically logged.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Training with Automatic Logging")
    print("=" * 80 + "\n")

    # Create dataset
    X, relations, relation_names, vocab = create_synthetic_dataset()

    # Create logged engine
    engine = LoggedUMAPEngine(
        task_name="basic_example",
        enable_logging=True,
        enable_console=True
    )

    print("\nTraining model with activity logging...")
    print(f"Log file: {engine.get_log_file()}\n")

    # Train (all activities are automatically logged)
    model, embeddings = engine.train(
        X=X,
        pair_indices_list=relations,
        relation_names=relation_names,
        epochs=50,  # Reduced for demo
        lr=1e-3,
        d_low=2,
        verbose=True
    )

    print("\nModel trained successfully!")
    print(f"Embedding shape: {embeddings.shape}")

    # Close session and generate report
    print("\nGenerating summary report...")
    report_path = engine.close_and_report(generate_report=True)
    print(f"Report saved to: {report_path}")

    return engine.get_session_id()


def example_inference_logging():
    """
    Example 2: Training + Inference with logging.

    This shows how inference queries are also logged for auditability.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Training + Inference Logging")
    print("=" * 80 + "\n")

    # Create dataset
    X, relations, relation_names, vocab = create_synthetic_dataset()

    # Create logged engine
    engine = LoggedUMAPEngine(
        task_name="inference_example",
        enable_logging=True,
        enable_console=True
    )

    # Train
    print("\nTraining model...")
    model, embeddings = engine.train(
        X=X,
        pair_indices_list=relations,
        relation_names=relation_names,
        epochs=50,
        verbose=False  # Suppress training output for clarity
    )

    # Perform several analogy queries (all logged)
    print("\nPerforming analogy queries (all logged)...")

    for i in range(3):
        query_idx = i * 10
        for rel_idx, rel_name in enumerate(relation_names):
            print(f"\n  Query: Apply '{rel_name}' to {vocab[query_idx]}")

            top_k_idx, top_k_dist = engine.find_analogy(
                model=model,
                X=X,
                query_idx=query_idx,
                relation_idx=rel_idx,
                pair_indices_list=relations,
                k=3
            )

            print(f"  Results: {[vocab[idx] for idx in top_k_idx]}")

    # Close and generate report
    print("\nGenerating summary report...")
    report_path = engine.close_and_report(generate_report=True)
    print(f"Report saved to: {report_path}")

    return engine.get_session_id()


def example_manual_logging():
    """
    Example 3: Manual logging for custom activities.

    This shows how to use the ActivityLogger directly for custom logging.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Manual Activity Logging")
    print("=" * 80 + "\n")

    # Create a logger for a custom task
    logger = ActivityLogger(
        task_name="custom_experiment",
        enable_console=True
    )

    # Log configuration
    logger.log_config(
        config_name="experiment_setup",
        config_values={
            "experiment_type": "hyperparameter_search",
            "search_space": {
                "learning_rate": [1e-4, 1e-3, 1e-2],
                "hidden_dims": [[256, 128], [512, 256, 128]],
                "dropout": [0.1, 0.2, 0.3]
            }
        }
    )

    # Log custom activities
    for lr in [1e-4, 1e-3, 1e-2]:
        logger.log_activity(
            activity_type=ActivityType.TRAINING,
            message=f"Testing learning rate: {lr}",
            level=LogLevel.INFO,
            metadata={"lr": lr, "status": "started"}
        )

        # Simulate training
        import time
        time.sleep(0.1)

        # Log results
        fake_loss = np.random.random()
        logger.log_activity(
            activity_type=ActivityType.TRAINING,
            message=f"Completed training with lr={lr}",
            level=LogLevel.INFO,
            metadata={"lr": lr, "final_loss": fake_loss, "status": "completed"}
        )

    # Log warnings
    logger.log_activity(
        activity_type=ActivityType.SYSTEM,
        message="High memory usage detected",
        level=LogLevel.WARNING,
        metadata={"memory_usage_gb": 7.8}
    )

    # Close session
    logger.close_session(summary={"trials_completed": 3, "best_lr": 1e-3})

    print(f"\nCustom logs saved to: {logger.get_log_file_path()}")

    return logger.get_session_id()


def example_generate_reports(session_ids):
    """
    Example 4: Generate comprehensive reports.

    This shows how to generate daily and per-session reports.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Generating Comprehensive Reports")
    print("=" * 80 + "\n")

    generator = ReportGenerator()

    # List all available sessions
    print("Available sessions:")
    all_sessions = generator.list_available_sessions()
    for session in all_sessions:
        print(f"  - {session}")

    # Generate reports for today
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")

    print(f"\nGenerating daily report for {today}...")
    daily_report = generator.generate_daily_report(today, output_format="markdown")
    print(f"  Saved to: {daily_report}")

    # Generate individual session reports
    print("\nGenerating individual session reports...")
    for session_id in session_ids[-3:]:  # Last 3 sessions
        if session_id:
            print(f"\n  Session: {session_id}")
            session_report = generator.generate_session_report(
                session_id,
                output_format="markdown"
            )
            print(f"    Report: {session_report}")

            training_summary = generator.generate_training_summary(
                session_id,
                output_format="markdown"
            )
            if training_summary:
                print(f"    Training: {training_summary}")

    # List all generated reports
    print("\nAll generated reports:")
    reports = generator.list_available_reports()
    for report in reports:
        print(f"  - {report}")

    print("\n✓ All reports generated successfully!")


def main():
    """
    Run all examples demonstrating the activity logging system.
    """
    print("\n" + "=" * 80)
    print("UMAP Analogy Engine - Activity Logging Examples")
    print("=" * 80)

    session_ids = []

    # Run examples
    session_ids.append(example_basic_logging())
    session_ids.append(example_inference_logging())
    session_ids.append(example_manual_logging())

    # Generate reports
    example_generate_reports(session_ids)

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)
    print(f"\nLogs saved to: memory/logs/")
    print(f"Reports saved to: memory/reports/")
    print("\nYou can:")
    print("  1. View individual log files (JSONL format)")
    print("  2. Read generated Markdown reports")
    print("  3. Use LogReader to programmatically analyze logs")
    print("  4. Generate custom reports using ReportGenerator")
    print()


if __name__ == "__main__":
    main()
