"""
Skill Orchestration Framework - Complete Example

This script demonstrates the full capabilities of the skill orchestration system:
1. Skill registration and discovery
2. Creating custom skills
3. Building chains programmatically
4. Loading chains from configuration files
5. Executing complete workflows

Run with:
    python example_skill_orchestration.py
"""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run orchestration examples"""

    print("=" * 80)
    print("SKILL ORCHESTRATION FRAMEWORK - EXAMPLES")
    print("=" * 80)
    print()

    # Import framework components
    from skills import (
        SkillRegistry,
        SkillOrchestrator,
        ChainConfig,
        SkillContext,
        get_global_registry
    )

    # Example 1: Register built-in skills
    print("=" * 80)
    print("EXAMPLE 1: Skill Registration & Discovery")
    print("=" * 80)
    print()

    registry = get_global_registry()

    # Discover skills in the implementations package
    print("Discovering skills...")
    num_discovered = registry.discover_skills("skills.implementations")
    print(f"✓ Discovered and registered {num_discovered} skills\n")

    # List all available skills
    print("Available skills:")
    for skill_name in registry.list_skills():
        metadata = registry.get_metadata(skill_name)
        print(f"  • {skill_name}: {metadata.description}")
    print()

    # Example 2: Build a chain programmatically
    print("=" * 80)
    print("EXAMPLE 2: Programmatic Chain Building")
    print("=" * 80)
    print()

    orchestrator = SkillOrchestrator(registry)

    # Create a chain using the builder pattern
    chain = (
        orchestrator
        .create_chain(
            name="programmatic_example",
            description="Programmatically built chain"
        )
        .add_step(
            "summarization",
            config={
                "summarization": {
                    "strategy": "bullet_points",
                    "num_sentences": 3
                }
            }
        )
        .add_step(
            "reporting",
            config={
                "reporting": {
                    "format": "text",
                    "title": "Programmatic Chain Report"
                }
            }
        )
    )

    # Add initial data
    chain.initial_data = {
        "text": "Skill orchestration enables chaining multiple AI tasks together. "
                "Each skill performs a specific function like RAG retrieval, summarization, or reporting. "
                "Results flow between skills through a shared context. "
                "This creates powerful, composable workflows for complex tasks. "
                "The orchestration engine manages execution, data flow, and error handling. "
                "Skills can run sequentially or in parallel with conditional logic. "
                "The framework supports configuration via code or YAML files."
    }

    print("Chain created with 2 steps:")
    print(f"  1. Summarization (extract key points)")
    print(f"  2. Reporting (format output)")
    print()

    print("Executing chain...")
    print("-" * 80)

    context = orchestrator.execute_chain(chain)

    print("-" * 80)
    print("\n✓ Chain execution complete!\n")

    # Display the report
    report_result = context.get_result("reporting")
    if report_result:
        print("GENERATED REPORT:")
        print("=" * 80)
        print(report_result["report"])
        print("=" * 80)
    print()

    # Example 3: Load and execute from YAML file
    print("=" * 80)
    print("EXAMPLE 3: Execute Chain from Configuration File")
    print("=" * 80)
    print()

    config_path = Path("chains/quick_summary.yaml")

    if config_path.exists():
        print(f"Loading chain from: {config_path}")

        # Load chain config
        chain_from_file = ChainConfig.from_yaml(config_path)

        print(f"Loaded chain: '{chain_from_file.name}'")
        print(f"Description: {chain_from_file.description.strip()}")
        print(f"Steps: {len(chain_from_file.steps)}")
        print()

        print("Executing chain from file...")
        print("-" * 80)

        context2 = orchestrator.execute_chain(chain_from_file)

        print("-" * 80)
        print("\n✓ File-based chain execution complete!\n")

        # Get the markdown report
        report_result2 = context2.get_result("reporting")
        if report_result2:
            print("GENERATED MARKDOWN REPORT:")
            print("=" * 80)
            print(report_result2["report"])
            print("=" * 80)
    else:
        print(f"⚠ Configuration file not found: {config_path}")
        print("  Skipping this example.")

    print()

    # Example 4: Custom skill creation
    print("=" * 80)
    print("EXAMPLE 4: Creating a Custom Skill")
    print("=" * 80)
    print()

    from skills import BaseSkill, SkillMetadata

    class WordCountSkill(BaseSkill):
        """Custom skill that counts words in text"""

        def _create_metadata(self) -> SkillMetadata:
            return SkillMetadata(
                name="word_count",
                description="Count words and characters in text",
                tags=["utility", "text-processing"]
            )

        def execute(self, context: SkillContext, **kwargs) -> dict:
            # Get text from previous skills or kwargs
            text = kwargs.get("text")

            if not text:
                # Try to get summary from previous skill
                summary_result = context.get_result("summarization")
                if summary_result:
                    text = summary_result.get("summary", "")

            if not text:
                raise ValueError("No text provided")

            # Count statistics
            words = text.split()
            word_count = len(words)
            char_count = len(text)
            sentence_count = text.count('.') + text.count('!') + text.count('?')

            result = {
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "avg_word_length": char_count / word_count if word_count > 0 else 0
            }

            print(f"  📊 Text Statistics:")
            print(f"     Words: {word_count}")
            print(f"     Characters: {char_count}")
            print(f"     Sentences: {sentence_count}")
            print(f"     Avg word length: {result['avg_word_length']:.2f}")

            return result

    # Register the custom skill
    registry.register(WordCountSkill)
    print("✓ Registered custom skill: word_count\n")

    # Create a chain that uses it
    custom_chain = (
        orchestrator
        .create_chain(name="custom_skill_demo", description="Using custom skill")
        .add_step("summarization")
        .add_step("word_count")
    )

    custom_chain.initial_data = {
        "text": "The quick brown fox jumps over the lazy dog. "
                "This sentence contains every letter of the alphabet. "
                "It's commonly used for testing fonts and keyboards."
    }

    print("Executing chain with custom skill...")
    print("-" * 80)

    context3 = orchestrator.execute_chain(custom_chain)

    print("-" * 80)
    print("\n✓ Custom skill execution complete!\n")

    # Example 5: Error handling
    print("=" * 80)
    print("EXAMPLE 5: Error Handling & Recovery")
    print("=" * 80)
    print()

    # Create a chain with continue_on_error
    error_chain = orchestrator.create_chain(
        name="error_handling_demo",
        description="Demonstrates error handling"
    )

    error_chain.fail_fast = False  # Don't stop on errors

    error_chain.add_step(
        "rag_pipeline",
        config={"rag_pipeline": {"top_k": 1}},
        continue_on_error=True  # Continue even if this fails
    )

    error_chain.add_step(
        "summarization",
        config={"summarization": {"strategy": "extractive"}}
    )

    error_chain.initial_data = {
        "text": "This text will be summarized even if RAG fails."
    }

    print("Executing chain with error recovery...")
    print("-" * 80)

    try:
        context4 = orchestrator.execute_chain(error_chain)
        print("-" * 80)
        print(f"\n✓ Chain completed with {len(context4.errors)} error(s)\n")

        if context4.errors:
            print("Errors encountered:")
            for error in context4.errors:
                print(f"  • {error['skill']}: {error['error']}")
    except Exception as e:
        print(f"✗ Chain failed: {e}")

    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("The skill orchestration framework provides:")
    print("  ✓ Modular, reusable skill components")
    print("  ✓ Flexible chain configuration (code or YAML/JSON)")
    print("  ✓ Automatic skill discovery and registration")
    print("  ✓ Data flow management between skills")
    print("  ✓ Error handling and recovery")
    print("  ✓ Multiple execution modes (sequential/parallel)")
    print("  ✓ Extensible architecture for custom skills")
    print()
    print("Next steps:")
    print("  • Create custom skills for your domain")
    print("  • Build complex chains with conditional logic")
    print("  • Integrate with real ML models (embeddings, LLMs, etc.)")
    print("  • Add async/parallel execution support")
    print("  • Deploy chains as microservices")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
