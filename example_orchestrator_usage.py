"""
Example Usage of the Workflow Orchestrator

This script demonstrates various real-world scenarios using the orchestrator:
1. Data processing pipeline with dependencies
2. Machine learning training workflow
3. ETL (Extract, Transform, Load) workflow
4. Nested workflows with parent-child relationships
5. Error handling and recovery
6. Load-balanced concurrent processing

Author: Claude Code Framework
License: MIT
"""

import asyncio
import logging
import random
import time
from typing import List, Dict, Any
import json

from workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowTask,
    TaskPriority,
    TaskStatus,
    create_task_from_function,
)


# ============================================================================
# Setup Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Data Processing Pipeline
# ============================================================================

def fetch_data_from_api(api_url: str) -> Dict[str, Any]:
    """Simulate fetching data from an API"""
    logger.info(f"Fetching data from {api_url}")
    time.sleep(random.uniform(0.5, 1.5))

    # Simulate API response
    return {
        "url": api_url,
        "data": [random.randint(1, 100) for _ in range(100)],
        "timestamp": time.time()
    }


def validate_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate fetched data"""
    logger.info(f"Validating data from {data['url']}")
    time.sleep(0.3)

    # Simple validation
    if not data.get("data") or len(data["data"]) == 0:
        raise ValueError("Invalid data: empty dataset")

    data["validated"] = True
    return data


def transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data (e.g., normalization, aggregation)"""
    logger.info(f"Transforming data from {data['url']}")
    time.sleep(0.5)

    # Simple transformation
    transformed = {
        "url": data["url"],
        "mean": sum(data["data"]) / len(data["data"]),
        "max": max(data["data"]),
        "min": min(data["data"]),
        "count": len(data["data"])
    }

    return transformed


def save_results(results: List[Dict[str, Any]], output_file: str) -> str:
    """Save processed results"""
    logger.info(f"Saving {len(results)} results to {output_file}")
    time.sleep(0.3)

    # Simulate saving to file
    logger.info(f"Results saved to {output_file}")
    return output_file


async def example_data_processing_pipeline():
    """
    Example 1: Data Processing Pipeline

    Workflow:
    1. Fetch data from multiple APIs (parallel)
    2. Validate each dataset (parallel, depends on fetch)
    3. Transform each dataset (parallel, depends on validate)
    4. Aggregate and save results (depends on all transforms)
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 1: Data Processing Pipeline")
    logger.info("="*80 + "\n")

    orchestrator = WorkflowOrchestrator(
        max_workers=6,
        max_concurrent_tasks=2
    )

    # Add progress callback
    def progress_callback(event_type: str, *args):
        if event_type == "task_status_changed":
            task = args[0]
            logger.info(f"📊 Task {task.task_id}: {task.status.value}")

    orchestrator.add_progress_callback(progress_callback)

    # Define API sources
    api_urls = [
        "https://api.example.com/data/v1",
        "https://api.example.com/data/v2",
        "https://api.example.com/data/v3",
    ]

    # Stage 1: Fetch data (parallel, high priority)
    fetch_tasks = {}
    for i, url in enumerate(api_urls):
        task_id = orchestrator.add_task(
            fetch_data_from_api,
            url,
            task_id=f"fetch-{i}",
            priority=TaskPriority.HIGH
        )
        fetch_tasks[i] = task_id

    # Stage 2: Validate data (depends on fetch)
    validate_tasks = {}
    for i in range(len(api_urls)):
        # Note: In a real scenario, you'd pass the result from the previous task
        # For this example, we'll use a wrapper function
        task_id = orchestrator.add_task(
            lambda data=None: validate_data(data or {"url": f"source-{i}", "data": [1, 2, 3]}),
            task_id=f"validate-{i}",
            dependencies={fetch_tasks[i]},
            priority=TaskPriority.NORMAL
        )
        validate_tasks[i] = task_id

    # Stage 3: Transform data (depends on validate)
    transform_tasks = {}
    for i in range(len(api_urls)):
        task_id = orchestrator.add_task(
            lambda data=None: transform_data(data or {"url": f"source-{i}", "data": [1, 2, 3]}),
            task_id=f"transform-{i}",
            dependencies={validate_tasks[i]},
            priority=TaskPriority.NORMAL
        )
        transform_tasks[i] = task_id

    # Stage 4: Save results (depends on all transforms)
    save_task = orchestrator.add_task(
        save_results,
        [],
        "output/results.json",
        task_id="save-results",
        dependencies=set(transform_tasks.values()),
        priority=TaskPriority.NORMAL
    )

    # Execute workflow
    logger.info(f"Starting workflow with {len(orchestrator.tasks)} tasks")
    start_time = time.time()

    results = await orchestrator.execute_workflow()

    end_time = time.time()

    # Print statistics
    logger.info("\n" + "-"*80)
    logger.info("Workflow Statistics:")
    logger.info("-"*80)
    stats = orchestrator.get_statistics()
    logger.info(f"Total tasks: {stats['total_tasks']}")
    logger.info(f"Completed: {stats['completed']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Success rate: {stats['success_rate']:.1%}")
    logger.info(f"Average task time: {stats['average_execution_time']:.2f}s")
    logger.info(f"Total workflow time: {end_time - start_time:.2f}s")
    logger.info("-"*80 + "\n")

    await orchestrator.shutdown()


# ============================================================================
# Example 2: Machine Learning Training Workflow
# ============================================================================

def load_dataset(dataset_name: str) -> Dict[str, Any]:
    """Load a dataset"""
    logger.info(f"Loading dataset: {dataset_name}")
    time.sleep(1.0)

    return {
        "name": dataset_name,
        "samples": 10000,
        "features": 50
    }


def preprocess_data(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess dataset"""
    logger.info(f"Preprocessing dataset: {dataset['name']}")
    time.sleep(0.8)

    dataset["preprocessed"] = True
    dataset["train_samples"] = int(dataset["samples"] * 0.8)
    dataset["test_samples"] = int(dataset["samples"] * 0.2)

    return dataset


def train_model(dataset: Dict[str, Any], model_type: str) -> Dict[str, Any]:
    """Train a machine learning model"""
    logger.info(f"Training {model_type} on {dataset['name']}")
    time.sleep(2.0)

    # Simulate training
    accuracy = random.uniform(0.75, 0.95)

    return {
        "model_type": model_type,
        "dataset": dataset["name"],
        "accuracy": accuracy,
        "trained": True
    }


def evaluate_model(model_result: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate model performance"""
    logger.info(f"Evaluating {model_result['model_type']}")
    time.sleep(0.5)

    model_result["f1_score"] = model_result["accuracy"] * random.uniform(0.95, 1.05)
    model_result["evaluated"] = True

    return model_result


def select_best_model(model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Select the best performing model"""
    logger.info(f"Selecting best model from {len(model_results)} candidates")
    time.sleep(0.3)

    best_model = max(model_results, key=lambda x: x.get("accuracy", 0))
    logger.info(f"Best model: {best_model['model_type']} with accuracy {best_model['accuracy']:.2%}")

    return best_model


async def example_ml_training_workflow():
    """
    Example 2: Machine Learning Training Workflow

    Workflow:
    1. Load dataset
    2. Preprocess data
    3. Train multiple models in parallel
    4. Evaluate each model
    5. Select best model
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 2: Machine Learning Training Workflow")
    logger.info("="*80 + "\n")

    orchestrator = WorkflowOrchestrator(
        max_workers=4,
        max_concurrent_tasks=1
    )

    # Stage 1: Load dataset
    load_task = orchestrator.add_task(
        load_dataset,
        "customer_churn_dataset",
        task_id="load-dataset",
        priority=TaskPriority.CRITICAL
    )

    # Stage 2: Preprocess
    preprocess_task = orchestrator.add_task(
        lambda: preprocess_data({"name": "customer_churn_dataset", "samples": 10000, "features": 50}),
        task_id="preprocess",
        dependencies={load_task},
        priority=TaskPriority.HIGH
    )

    # Stage 3: Train multiple models (parallel)
    model_types = ["RandomForest", "GradientBoosting", "NeuralNetwork", "SVM"]
    train_tasks = {}
    evaluate_tasks = {}

    for model_type in model_types:
        # Training task
        train_task_id = orchestrator.add_task(
            lambda mt=model_type: train_model(
                {"name": "customer_churn_dataset", "samples": 10000, "features": 50, "preprocessed": True},
                mt
            ),
            task_id=f"train-{model_type}",
            dependencies={preprocess_task},
            priority=TaskPriority.NORMAL,
            timeout=10.0
        )
        train_tasks[model_type] = train_task_id

        # Evaluation task (depends on training)
        eval_task_id = orchestrator.add_task(
            lambda: evaluate_model({"model_type": model_type, "dataset": "customer_churn_dataset", "accuracy": 0.85, "trained": True}),
            task_id=f"evaluate-{model_type}",
            dependencies={train_task_id},
            priority=TaskPriority.NORMAL
        )
        evaluate_tasks[model_type] = eval_task_id

    # Stage 4: Select best model
    select_task = orchestrator.add_task(
        lambda: select_best_model([
            {"model_type": mt, "accuracy": random.uniform(0.75, 0.95), "evaluated": True}
            for mt in model_types
        ]),
        task_id="select-best",
        dependencies=set(evaluate_tasks.values()),
        priority=TaskPriority.HIGH
    )

    # Execute workflow
    logger.info(f"Starting ML workflow with {len(orchestrator.tasks)} tasks")
    start_time = time.time()

    results = await orchestrator.execute_workflow()

    end_time = time.time()

    # Print results
    logger.info("\n" + "-"*80)
    logger.info("Training Results:")
    logger.info("-"*80)
    for model_type in model_types:
        task_id = f"evaluate-{model_type}"
        if task_id in results and results[task_id].success:
            logger.info(f"{model_type}: Completed")

    if "select-best" in results and results["select-best"].success:
        best = results["select-best"].result
        logger.info(f"\nBest Model: {best}")

    logger.info(f"\nTotal workflow time: {end_time - start_time:.2f}s")
    logger.info("-"*80 + "\n")

    await orchestrator.shutdown()


# ============================================================================
# Example 3: ETL Workflow with Error Handling
# ============================================================================

def extract_from_source(source_id: int, fail_probability: float = 0.2) -> Dict[str, Any]:
    """Extract data from a source (with potential failures)"""
    logger.info(f"Extracting from source {source_id}")
    time.sleep(random.uniform(0.5, 1.5))

    # Simulate random failures
    if random.random() < fail_probability:
        raise ConnectionError(f"Failed to connect to source {source_id}")

    return {
        "source_id": source_id,
        "records": random.randint(100, 1000),
        "extracted_at": time.time()
    }


def transform_records(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform extracted records"""
    logger.info(f"Transforming {data['records']} records from source {data['source_id']}")
    time.sleep(0.5)

    data["transformed"] = True
    data["valid_records"] = int(data["records"] * 0.95)  # 95% valid

    return data


def load_to_warehouse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Load data to data warehouse"""
    logger.info(f"Loading {data['valid_records']} records from source {data['source_id']}")
    time.sleep(0.7)

    data["loaded"] = True
    data["load_time"] = time.time()

    return data


async def example_etl_workflow():
    """
    Example 3: ETL Workflow with Error Handling

    Demonstrates:
    - Parallel extraction from multiple sources
    - Automatic retries on failures
    - Data transformation pipeline
    - Load to warehouse
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 3: ETL Workflow with Error Handling")
    logger.info("="*80 + "\n")

    orchestrator = WorkflowOrchestrator(
        max_workers=5,
        max_concurrent_tasks=2
    )

    num_sources = 5
    extract_tasks = {}
    transform_tasks = {}
    load_tasks = {}

    # Create ETL pipeline for each source
    for source_id in range(num_sources):
        # Extract (with retries for failures)
        extract_task_id = orchestrator.add_task(
            extract_from_source,
            source_id,
            0.3,  # 30% failure probability
            task_id=f"extract-{source_id}",
            priority=TaskPriority.HIGH,
            max_retries=3,  # Retry up to 3 times
            timeout=5.0
        )
        extract_tasks[source_id] = extract_task_id

        # Transform (depends on extract)
        transform_task_id = orchestrator.add_task(
            lambda sid=source_id: transform_records({
                "source_id": sid,
                "records": random.randint(100, 1000),
                "extracted_at": time.time()
            }),
            task_id=f"transform-{source_id}",
            dependencies={extract_task_id},
            priority=TaskPriority.NORMAL
        )
        transform_tasks[source_id] = transform_task_id

        # Load (depends on transform)
        load_task_id = orchestrator.add_task(
            lambda sid=source_id: load_to_warehouse({
                "source_id": sid,
                "records": random.randint(100, 1000),
                "transformed": True,
                "valid_records": random.randint(90, 950)
            }),
            task_id=f"load-{source_id}",
            dependencies={transform_task_id},
            priority=TaskPriority.NORMAL
        )
        load_tasks[source_id] = load_task_id

    # Execute workflow
    logger.info(f"Starting ETL workflow for {num_sources} sources")
    start_time = time.time()

    results = await orchestrator.execute_workflow()

    end_time = time.time()

    # Print results
    logger.info("\n" + "-"*80)
    logger.info("ETL Results:")
    logger.info("-"*80)

    successful_loads = 0
    failed_sources = []

    for source_id in range(num_sources):
        load_task_id = f"load-{source_id}"
        if load_task_id in results:
            if results[load_task_id].success:
                successful_loads += 1
                logger.info(f"✓ Source {source_id}: Successfully loaded")
            else:
                failed_sources.append(source_id)
                logger.info(f"✗ Source {source_id}: Failed - {results[load_task_id].error}")

    logger.info(f"\nSuccessful: {successful_loads}/{num_sources}")
    logger.info(f"Failed sources: {failed_sources}")
    logger.info(f"Total workflow time: {end_time - start_time:.2f}s")

    # Show retry statistics
    stats = orchestrator.get_statistics()
    logger.info(f"\nOverall success rate: {stats['success_rate']:.1%}")
    logger.info("-"*80 + "\n")

    await orchestrator.shutdown()


# ============================================================================
# Example 4: Nested Workflows
# ============================================================================

async def example_nested_workflows():
    """
    Example 4: Nested Workflows

    Demonstrates:
    - Parent task spawning child workflows
    - Hierarchical task organization
    - Child task tracking
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 4: Nested Workflows")
    logger.info("="*80 + "\n")

    orchestrator = WorkflowOrchestrator(
        max_workers=4,
        enable_nested_workflows=True
    )

    def process_batch(batch_id: int) -> str:
        """Process a batch of data"""
        logger.info(f"Processing batch {batch_id}")
        time.sleep(0.5)
        return f"Batch {batch_id} processed"

    def spawn_batch_processing_workflow(orchestrator: WorkflowOrchestrator, parent_id: str, num_batches: int) -> List[str]:
        """Spawn child tasks for batch processing"""
        logger.info(f"Spawning {num_batches} batch processing tasks")

        child_tasks = [
            WorkflowTask(
                task_id=f"batch-{parent_id}-{i}",
                func=process_batch,
                args=(i,),
                priority=TaskPriority.NORMAL
            )
            for i in range(num_batches)
        ]

        child_ids = orchestrator.spawn_child_workflow(parent_id, child_tasks)
        logger.info(f"Spawned child tasks: {child_ids}")

        return child_ids

    # Create parent task that spawns children
    parent_task_id = orchestrator.add_task(
        spawn_batch_processing_workflow,
        orchestrator,
        "parent-1",
        5,  # 5 batches
        task_id="parent-1",
        priority=TaskPriority.HIGH
    )

    # Execute workflow
    logger.info("Starting nested workflow")
    start_time = time.time()

    results = await orchestrator.execute_workflow()

    end_time = time.time()

    # Print results
    logger.info("\n" + "-"*80)
    logger.info("Nested Workflow Results:")
    logger.info("-"*80)

    if parent_task_id in results:
        logger.info(f"Parent task completed: {results[parent_task_id].success}")
        child_ids = results[parent_task_id].result
        logger.info(f"Child tasks spawned: {len(child_ids)}")

    logger.info(f"\nTotal tasks executed: {len(results)}")
    logger.info(f"Total workflow time: {end_time - start_time:.2f}s")
    logger.info("-"*80 + "\n")

    await orchestrator.shutdown()


# ============================================================================
# Example 5: Load Balancing and Throttling
# ============================================================================

async def example_load_balancing():
    """
    Example 5: Load Balancing and Throttling

    Demonstrates:
    - Automatic load balancing across agents
    - System resource monitoring
    - Throttling during high load
    """
    logger.info("\n" + "="*80)
    logger.info("EXAMPLE 5: Load Balancing and Throttling")
    logger.info("="*80 + "\n")

    orchestrator = WorkflowOrchestrator(
        max_workers=3,
        max_concurrent_tasks=2,
        cpu_threshold=80.0,
        memory_threshold=85.0
    )

    def cpu_intensive_task(task_id: int, iterations: int = 1000000) -> int:
        """CPU-intensive task"""
        logger.info(f"Running CPU-intensive task {task_id}")
        result = 0
        for i in range(iterations):
            result += i ** 2
        return result

    # Add many CPU-intensive tasks
    num_tasks = 20
    for i in range(num_tasks):
        orchestrator.add_task(
            cpu_intensive_task,
            i,
            500000,  # Half million iterations
            task_id=f"cpu-task-{i}",
            priority=TaskPriority.NORMAL,
            timeout=30.0
        )

    # Execute workflow
    logger.info(f"Starting load-balanced workflow with {num_tasks} CPU-intensive tasks")
    start_time = time.time()

    # Monitor progress
    completed_count = 0

    def monitor_callback(event_type: str, *args):
        nonlocal completed_count
        if event_type == "task_status_changed":
            task = args[0]
            if task.status == TaskStatus.COMPLETED:
                completed_count += 1
                if completed_count % 5 == 0:
                    stats = orchestrator.get_statistics()
                    logger.info(
                        f"Progress: {completed_count}/{num_tasks} tasks, "
                        f"CPU: {stats['system_resources']['cpu_percent']:.1f}%, "
                        f"Memory: {stats['system_resources']['memory_percent']:.1f}%"
                    )

    orchestrator.add_progress_callback(monitor_callback)

    results = await orchestrator.execute_workflow()

    end_time = time.time()

    # Print results
    logger.info("\n" + "-"*80)
    logger.info("Load Balancing Results:")
    logger.info("-"*80)

    stats = orchestrator.get_statistics()
    logger.info(f"Total tasks: {stats['total_tasks']}")
    logger.info(f"Completed: {stats['completed']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Total time: {end_time - start_time:.2f}s")
    logger.info(f"Average task time: {stats['average_execution_time']:.2f}s")

    # Agent statistics
    logger.info("\nAgent Performance:")
    for agent_stat in stats['agents']:
        logger.info(
            f"  {agent_stat['agent_id']}: "
            f"completed={agent_stat['completed_tasks']}, "
            f"avg_time={agent_stat['average_task_time']:.2f}s"
        )

    logger.info("-"*80 + "\n")

    await orchestrator.shutdown()


# ============================================================================
# Main: Run All Examples
# ============================================================================

async def main():
    """Run all examples"""
    logger.info("\n")
    logger.info("="*80)
    logger.info(" WORKFLOW ORCHESTRATOR - COMPREHENSIVE EXAMPLES")
    logger.info("="*80)
    logger.info("\n")

    # Run examples sequentially
    examples = [
        ("Data Processing Pipeline", example_data_processing_pipeline),
        ("Machine Learning Training", example_ml_training_workflow),
        ("ETL with Error Handling", example_etl_workflow),
        ("Nested Workflows", example_nested_workflows),
        ("Load Balancing", example_load_balancing),
    ]

    for i, (name, example_func) in enumerate(examples, 1):
        logger.info(f"\nRunning Example {i}/{len(examples)}: {name}\n")
        try:
            await example_func()
        except Exception as e:
            logger.error(f"Error in {name}: {e}")

        # Small delay between examples
        await asyncio.sleep(1)

    logger.info("\n")
    logger.info("="*80)
    logger.info(" ALL EXAMPLES COMPLETED")
    logger.info("="*80)
    logger.info("\n")


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
