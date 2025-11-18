"""Comprehensive example demonstrating the agent template population system.

This example shows how to:
1. Create skill and agent configurations using the population helpers
2. Populate templates with metadata
3. Validate configurations
4. Register skills and agents
5. Execute skills through agents
"""

from templates import TemplatePopulator, populate_agent_config, populate_skill_config
from utils import MetadataManager, validate_agent_config, validate_skill_config
from skills import SkillRegistry
from agents import BaseAgent, AgentConfig, AgentRegistry
from pathlib import Path


def example_1_create_skill_config():
    """Example 1: Create a skill configuration using helper functions."""
    print("\n" + "="*70)
    print("Example 1: Creating Skill Configuration")
    print("="*70)

    # Create skill configuration using populate_skill_config helper
    skill_config = populate_skill_config(
        name="TextAnalyzer",
        description="Analyzes text content for sentiment, key themes, and linguistic patterns",
        category="nlp",
        inputs=[
            {
                "name": "text",
                "type": "string",
                "required": True,
                "description": "Text content to analyze"
            },
            {
                "name": "language",
                "type": "string",
                "required": False,
                "default": "en",
                "description": "Language code (ISO 639-1)"
            }
        ],
        outputs=[
            {
                "name": "sentiment",
                "type": "string",
                "description": "Detected sentiment (positive/negative/neutral)"
            },
            {
                "name": "themes",
                "type": "array",
                "description": "Identified key themes"
            }
        ],
        prompt_template="prompts/skill_prompts/text_analyzer.j2",
        metadata={
            "author": "NLP Team",
            "tags": ["nlp", "sentiment", "analysis"],
            "complexity": "medium"
        }
    )

    print(f"Created skill: {skill_config['skill_id']}")
    print(f"Name: {skill_config['name']}")
    print(f"Category: {skill_config['category']}")
    print(f"Inputs: {len(skill_config['inputs'])}")
    print(f"Outputs: {len(skill_config['outputs'])}")

    return skill_config


def example_2_populate_skill_template(skill_config):
    """Example 2: Populate a skill template with configuration."""
    print("\n" + "="*70)
    print("Example 2: Populating Skill Template")
    print("="*70)

    # Initialize template populator
    populator = TemplatePopulator()

    # Populate skill template
    populated_yaml = populator.populate_skill(skill_config)

    print("Populated YAML content:")
    print("-" * 70)
    print(populated_yaml[:500] + "..." if len(populated_yaml) > 500 else populated_yaml)
    print("-" * 70)

    # Save to file
    output_path = f"skills/examples/{skill_config['skill_id']}.yaml"
    populator.save_populated_template(output_path, populated_yaml)
    print(f"\nSaved to: {output_path}")

    return populated_yaml


def example_3_validate_skill(skill_config):
    """Example 3: Validate skill configuration."""
    print("\n" + "="*70)
    print("Example 3: Validating Skill Configuration")
    print("="*70)

    try:
        validate_skill_config(skill_config)
        print("✓ Skill configuration is valid!")
    except Exception as e:
        print(f"✗ Validation failed: {e}")


def example_4_create_agent_config(skill_ids):
    """Example 4: Create an agent configuration."""
    print("\n" + "="*70)
    print("Example 4: Creating Agent Configuration")
    print("="*70)

    # Create agent configuration
    agent_config = populate_agent_config(
        name="ResearchAgent",
        description="Conducts comprehensive research tasks using multiple search and analysis skills",
        skills=skill_ids,
        version="1.0.0",
        metadata={
            "author": "AI Research Team",
            "tags": ["research", "analysis", "nlp"],
            "complexity": "high",
            "license": "MIT"
        },
        prompt_template="prompts/agent_prompts/research_agent.j2",
        parameters={
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 0.9
        }
    )

    print(f"Created agent: {agent_config['id']}")
    print(f"Name: {agent_config['name']}")
    print(f"Version: {agent_config['version']}")
    print(f"Skills: {len(agent_config['skills'])}")

    return agent_config


def example_5_populate_agent_template(agent_config):
    """Example 5: Populate an agent template."""
    print("\n" + "="*70)
    print("Example 5: Populating Agent Template")
    print("="*70)

    # Initialize template populator
    populator = TemplatePopulator()

    # Populate agent template
    populated_yaml = populator.populate_agent(agent_config)

    print("Populated YAML content:")
    print("-" * 70)
    print(populated_yaml[:500] + "..." if len(populated_yaml) > 500 else populated_yaml)
    print("-" * 70)

    # Save to file (create agents directory if it doesn't exist)
    Path("agents/examples").mkdir(parents=True, exist_ok=True)
    output_path = f"agents/examples/{agent_config['id']}.yaml"
    populator.save_populated_template(output_path, populated_yaml)
    print(f"\nSaved to: {output_path}")

    return populated_yaml


def example_6_validate_agent(agent_config):
    """Example 6: Validate agent configuration."""
    print("\n" + "="*70)
    print("Example 6: Validating Agent Configuration")
    print("="*70)

    try:
        validate_agent_config(agent_config)
        print("✓ Agent configuration is valid!")
    except Exception as e:
        print(f"✗ Validation failed: {e}")


def example_7_skill_registry():
    """Example 7: Using the skill registry."""
    print("\n" + "="*70)
    print("Example 7: Skill Registry")
    print("="*70)

    # Create registry
    registry = SkillRegistry()

    # Create and register multiple skills
    skills_data = [
        {
            "name": "WebSearch",
            "description": "Searches the web for information",
            "category": "search"
        },
        {
            "name": "DataAnalyzer",
            "description": "Analyzes structured data",
            "category": "data"
        },
        {
            "name": "TextSummarizer",
            "description": "Summarizes long text content",
            "category": "nlp"
        }
    ]

    for skill_data in skills_data:
        config = populate_skill_config(**skill_data)
        registry.register(config['skill_id'], config)
        print(f"Registered: {config['skill_id']}")

    print(f"\nTotal skills: {registry.get_skill_count()}")
    print(f"Categories: {', '.join(registry.list_categories())}")

    # Search for skills
    nlp_skills = registry.list_skills(category="nlp")
    print(f"NLP skills: {nlp_skills}")

    return registry


def example_8_agent_registry(agent_config, skill_registry):
    """Example 8: Using the agent registry."""
    print("\n" + "="*70)
    print("Example 8: Agent Registry")
    print("="*70)

    # Create agent registry
    agent_registry = AgentRegistry()

    # Create agent instance
    config_obj = AgentConfig.from_dict(agent_config)
    agent = BaseAgent(config_obj, skill_registry)

    # Initialize agent (validates skills)
    try:
        agent.initialize()
        print(f"✓ Agent initialized: {agent.config.name}")
    except ValueError as e:
        print(f"⚠ Agent initialization warning: {e}")
        print("  (This is expected if the agent references skills not in registry)")

    # Register agent
    agent_registry.register(agent)
    print(f"Registered agent: {agent.config.id}")

    # Query registry
    print(f"\nTotal agents: {agent_registry.get_agent_count()}")

    # Get agent info
    info = agent.get_info()
    print(f"Agent info: {info['name']} - {info['skill_count']} skills")

    return agent_registry


def example_9_metadata_manager():
    """Example 9: Using the metadata manager."""
    print("\n" + "="*70)
    print("Example 9: Metadata Manager")
    print("="*70)

    # Create metadata manager
    manager = MetadataManager("metadata")

    # Create skill config
    skill_config = populate_skill_config(
        name="ImageProcessor",
        description="Processes and analyzes images",
        category="visualization"
    )

    # Save metadata
    saved_path = manager.save_skill_metadata(
        skill_config['skill_id'],
        skill_config,
        format='yaml'
    )
    print(f"Saved skill metadata to: {saved_path}")

    # Load metadata
    loaded = manager.get_skill_metadata(skill_config['skill_id'])
    if loaded:
        print(f"Loaded skill: {loaded['name']}")

    # List all skills
    all_skills = manager.list_skills()
    print(f"Total skills in metadata: {len(all_skills)}")

    return manager


def example_10_complete_workflow():
    """Example 10: Complete end-to-end workflow."""
    print("\n" + "="*70)
    print("Example 10: Complete End-to-End Workflow")
    print("="*70)

    # 1. Create skill configurations
    print("\n1. Creating skill configurations...")
    skill1 = populate_skill_config(
        name="SentimentAnalyzer",
        description="Analyzes sentiment in text",
        category="nlp"
    )

    skill2 = populate_skill_config(
        name="EntityExtractor",
        description="Extracts named entities from text",
        category="nlp"
    )

    # 2. Populate and save skill templates
    print("\n2. Populating skill templates...")
    populator = TemplatePopulator()

    for skill in [skill1, skill2]:
        yaml_content = populator.populate_skill(skill)
        output_path = f"skills/examples/{skill['skill_id']}.yaml"
        populator.save_populated_template(output_path, yaml_content)
        print(f"   Saved: {output_path}")

    # 3. Create and validate agent configuration
    print("\n3. Creating agent configuration...")
    agent_config = populate_agent_config(
        name="NLPAgent",
        description="Natural language processing agent",
        skills=[skill1['skill_id'], skill2['skill_id']]
    )

    # 4. Validate configurations
    print("\n4. Validating configurations...")
    try:
        validate_skill_config(skill1)
        validate_skill_config(skill2)
        validate_agent_config(agent_config)
        print("   ✓ All configurations valid!")
    except Exception as e:
        print(f"   ✗ Validation error: {e}")

    # 5. Register skills
    print("\n5. Registering skills...")
    skill_registry = SkillRegistry()
    skill_registry.register(skill1['skill_id'], skill1)
    skill_registry.register(skill2['skill_id'], skill2)
    print(f"   Registered {skill_registry.get_skill_count()} skills")

    # 6. Create and register agent
    print("\n6. Creating and registering agent...")
    agent_registry = AgentRegistry()
    config_obj = AgentConfig.from_dict(agent_config)
    agent = BaseAgent(config_obj, skill_registry)
    agent.initialize()
    agent_registry.register(agent)
    print(f"   Agent registered: {agent.config.name}")

    # 7. Save metadata
    print("\n7. Saving metadata...")
    metadata_manager = MetadataManager("metadata")
    metadata_manager.save_skill_metadata(skill1['skill_id'], skill1)
    metadata_manager.save_skill_metadata(skill2['skill_id'], skill2)
    metadata_manager.save_agent_metadata(agent_config['id'], agent_config)
    print(f"   Metadata saved for {len([skill1, skill2])} skills and 1 agent")

    print("\n✓ Complete workflow finished successfully!")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("AGENT TEMPLATE POPULATION SYSTEM - EXAMPLES")
    print("="*70)

    # Example 1-3: Skill creation and validation
    skill_config = example_1_create_skill_config()
    example_2_populate_skill_template(skill_config)
    example_3_validate_skill(skill_config)

    # Example 4-6: Agent creation and validation
    agent_config = example_4_create_agent_config([skill_config['skill_id']])
    example_5_populate_agent_template(agent_config)
    example_6_validate_agent(agent_config)

    # Example 7-9: Registry and metadata management
    skill_registry = example_7_skill_registry()
    example_8_agent_registry(agent_config, skill_registry)
    example_9_metadata_manager()

    # Example 10: Complete workflow
    example_10_complete_workflow()

    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nGenerated files:")
    print("  - skills/examples/*.yaml (skill configurations)")
    print("  - agents/examples/*.yaml (agent configurations)")
    print("  - metadata/skills/*.yaml (skill metadata)")
    print("  - metadata/agents/*.yaml (agent metadata)")
    print("\nNext steps:")
    print("  1. Review the generated configurations")
    print("  2. Customize templates in templates/prompts/")
    print("  3. Create your own skills and agents")
    print("  4. Implement skill executors for actual functionality")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
