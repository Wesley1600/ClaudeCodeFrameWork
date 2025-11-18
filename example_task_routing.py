"""
Example usage of the Task Classification and Routing System.

This script demonstrates how to use the task classification and routing
components to automatically detect task types and route them to appropriate skills.
"""

from task_classification_routing import (
    TaskClassifier,
    SkillRegistry,
    TaskRouter,
    TaskCategory,
    SkillMetadata,
    classify_task,
    route_task,
)


def example_basic_classification():
    """Example 1: Basic task classification."""
    print("=" * 60)
    print("Example 1: Basic Task Classification")
    print("=" * 60)

    classifier = TaskClassifier()

    test_tasks = [
        "Please extract text from this PDF file: report.pdf",
        "Run this Python script and show me the output",
        "Create a pivot table from sales_data.xlsx",
        "Scrape product prices from this website: https://example.com",
        "Analyze sentiment in customer_reviews.csv",
        "Find analogies like king:queen :: man:?",
        "Resize this image to 800x600: photo.jpg",
    ]

    for task in test_tasks:
        result = classifier.classify(task)
        print(f"\nTask: {task}")
        print(f"  Category: {result.category.value}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Matched keywords: {', '.join(result.matched_keywords[:3])}")


def example_file_classification():
    """Example 2: File-based classification."""
    print("\n" + "=" * 60)
    print("Example 2: File-Based Classification")
    print("=" * 60)

    classifier = TaskClassifier()

    test_files = [
        "document.pdf",
        "data.xlsx",
        "script.py",
        "image.png",
        "database.sqlite",
        "styles.css",
        "report.csv",
    ]

    for file_path in test_files:
        result = classifier.classify_file(file_path)
        print(f"\nFile: {file_path}")
        print(f"  Category: {result.category.value}")
        print(f"  Confidence: {result.confidence:.2f}")


def example_skill_registry():
    """Example 3: Working with the skill registry."""
    print("\n" + "=" * 60)
    print("Example 3: Skill Registry")
    print("=" * 60)

    registry = SkillRegistry()

    # List all skills
    print("\nAll registered skills:")
    for skill in registry.list_all_skills()[:5]:  # Show top 5
        print(f"  [{skill.skill_id}] {skill.name} (priority: {skill.priority})")

    # Get skills by category
    print("\nSkills for PDF processing:")
    pdf_skills = registry.get_skills_by_category(TaskCategory.PDF)
    for skill in pdf_skills:
        print(f"  {skill.name}: {skill.description}")

    # Search for skills
    print("\nSearch for 'excel' skills:")
    excel_skills = registry.search_skills("excel")
    for skill in excel_skills:
        print(f"  {skill.name}: {skill.description}")

    # Register a custom skill
    print("\nRegistering a custom skill...")
    custom_skill = SkillMetadata(
        skill_id="custom_video_processor",
        name="Video Processor",
        category=TaskCategory.IMAGE_PROCESSING,  # Could create VIDEO category
        description="Process and analyze video files",
        file_patterns=["*.mp4", "*.avi", "*.mov"],
        keywords=["video", "movie", "clip", "encode"],
        capabilities=["transcode", "extract_frames", "add_subtitles"],
        priority=8
    )
    registry.register_skill(custom_skill)
    print(f"  Registered: {custom_skill.name}")

    # Verify registration
    retrieved = registry.get_skill("custom_video_processor")
    if retrieved:
        print(f"  Verified: {retrieved.name} is now available")


def example_task_routing():
    """Example 4: Complete task routing."""
    print("\n" + "=" * 60)
    print("Example 4: Task Routing")
    print("=" * 60)

    router = TaskRouter()

    test_tasks = [
        "Extract all tables from quarterly_report.pdf",
        "Execute this machine learning model training script",
        "Create a bar chart from the spreadsheet data in metrics.xlsx",
        "Find semantic analogies: happy:sad :: hot:?",
        "Scrape all product listings from the e-commerce site",
        "Compress and resize all images in the photos folder",
        "Query the user database for all active accounts",
    ]

    for task in test_tasks:
        result = router.route(task)
        print(f"\nTask: {task}")
        print(f"  Routed to: [{result.skill_id}] {result.skill_name}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning}")
        if result.alternative_skills:
            print(f"  Alternatives: {', '.join(result.alternative_skills)}")


def example_batch_routing():
    """Example 5: Batch routing with statistics."""
    print("\n" + "=" * 60)
    print("Example 5: Batch Routing & Statistics")
    print("=" * 60)

    router = TaskRouter()

    batch_tasks = [
        "Process report.pdf",
        "Analyze sales.xlsx",
        "Run analysis.py",
        "Extract data.csv",
        "Parse document.pdf",
        "Train model.py",
        "Visualize results from data.xlsx",
        "Find king:queen analogies",
        "Scrape website data",
        "Optimize image.png",
    ]

    print(f"\nRouting {len(batch_tasks)} tasks...")
    results = router.route_batch(batch_tasks)

    print("\nRouting Results:")
    for task, result in zip(batch_tasks, results):
        print(f"  {task[:30]:30s} -> {result.skill_id}")

    # Get statistics
    stats = router.get_routing_statistics(batch_tasks)
    print("\nRouting Statistics:")
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")
    print(f"  Unique categories: {stats['unique_categories']}")
    print(f"  Unique skills: {stats['unique_skills']}")

    print("\n  Category distribution:")
    for category, count in sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {category}: {count}")

    print("\n  Skill distribution:")
    for skill, count in sorted(stats['skill_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {skill}: {count}")


def example_quick_functions():
    """Example 6: Using convenience functions."""
    print("\n" + "=" * 60)
    print("Example 6: Quick Convenience Functions")
    print("=" * 60)

    # Quick classification
    result = classify_task("Parse this PDF document")
    print(f"\nQuick classify: '{result.category.value}' (confidence: {result.confidence:.2f})")

    # Quick routing
    routing = route_task("Execute machine learning training on data.csv")
    print(f"Quick route: {routing.skill_id} ({routing.skill_name})")


def example_integration_with_umap():
    """Example 7: Integration with UMAP Analogy Engine."""
    print("\n" + "=" * 60)
    print("Example 7: UMAP Analogy Engine Integration")
    print("=" * 60)

    router = TaskRouter()

    # Tasks that should route to the analogy finder
    analogy_tasks = [
        "Find word analogies: king is to queen as man is to what?",
        "Discover semantic relationships in word embeddings",
        "Train UMAP model to learn relation axes",
        "Extract relation patterns from word pairs",
    ]

    print("\nRouting analogy-related tasks:")
    for task in analogy_tasks:
        result = router.route(task)
        print(f"\n  Task: {task}")
        print(f"  Skill: {result.skill_name}")
        print(f"  Match: {'✓' if result.skill_id == 'analogy_finder' else '✗'}")

    # Demonstrate that the router correctly identifies analogy tasks
    print("\n" + "-" * 60)
    classification = classify_task("Find analogies using semantic embeddings")
    if classification.category == TaskCategory.ANALOGY_FINDING:
        print("✓ Successfully classified as ANALOGY_FINDING task")
        print(f"  Confidence: {classification.confidence:.2f}")
        print(f"  This would invoke the UMAP Analogy Engine")


def main():
    """Run all examples."""
    print("\n" + "🚀" * 30)
    print("Task Classification & Routing System - Examples")
    print("🚀" * 30)

    example_basic_classification()
    example_file_classification()
    example_skill_registry()
    example_task_routing()
    example_batch_routing()
    example_quick_functions()
    example_integration_with_umap()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
