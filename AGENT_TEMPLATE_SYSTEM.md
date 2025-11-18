# Agent Template Population System

A comprehensive framework for creating, managing, and populating agent and skill configurations with proper metadata, validation, and template rendering.

## Overview

This system provides infrastructure for:

- **Template Population**: Dynamically generate agent and skill configurations from Jinja2 templates
- **Metadata Management**: Store, retrieve, and validate metadata for agents and skills
- **Skill Registry**: Centralized management of available skills
- **Agent Registry**: Management of agent instances and capabilities
- **Validation**: Ensure configurations conform to defined schemas

## Architecture

```
ClaudeCodeFrameWork/
├── agents/                          # Agent management
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class
│   ├── registry.py                 # Agent registry
│   └── examples/                   # Generated agent configs
│
├── skills/                          # Skill management
│   ├── __init__.py
│   ├── registry.py                 # Skill registry
│   ├── skill_loader.py             # Load skills from files
│   └── examples/                   # Generated skill configs
│
├── templates/                       # Template system
│   ├── __init__.py
│   ├── template_engine.py          # Core template renderer
│   ├── population.py               # Helper functions
│   └── prompts/                    # Jinja2 templates
│       ├── agent_template.yaml.j2  # Agent config template
│       ├── skill_template.yaml.j2  # Skill config template
│       ├── agent_prompts/          # Agent prompt templates
│       └── skill_prompts/          # Skill prompt templates
│
├── config/                          # Configuration schemas
│   ├── agent_schema.yaml           # Agent schema definition
│   └── skill_schema.yaml           # Skill schema definition
│
├── utils/                           # Utilities
│   ├── __init__.py
│   ├── metadata.py                 # Metadata management
│   └── validators.py               # Configuration validation
│
└── metadata/                        # Metadata storage
    ├── agents/                     # Agent metadata files
    └── skills/                     # Skill metadata files
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `jinja2>=3.1.0` - Template rendering
- `pyyaml>=6.0` - YAML configuration parsing

### 2. Run Examples

```bash
python example_usage.py
```

This will demonstrate:
- Creating skill configurations
- Populating templates
- Validating configurations
- Using registries
- Complete end-to-end workflow

## Core Components

### 1. Template Population

The template system uses Jinja2 to populate configuration templates with metadata.

#### Creating a Skill Configuration

```python
from templates import populate_skill_config

skill_config = populate_skill_config(
    name="TextAnalyzer",
    description="Analyzes text for sentiment and themes",
    category="nlp",
    inputs=[
        {
            "name": "text",
            "type": "string",
            "required": True,
            "description": "Text to analyze"
        }
    ],
    outputs=[
        {
            "name": "sentiment",
            "type": "string",
            "description": "Detected sentiment"
        }
    ]
)

# Automatically generates:
# - skill_id: "skill_nlp_textanalyzer_001"
# - created_at: Current timestamp
# - metadata with defaults
```

#### Creating an Agent Configuration

```python
from templates import populate_agent_config

agent_config = populate_agent_config(
    name="ResearchAgent",
    description="Conducts research tasks",
    skills=["skill_search_001", "skill_analyze_001"],
    version="1.0.0",
    parameters={
        "temperature": 0.7,
        "max_tokens": 4000
    }
)

# Automatically generates:
# - id: "agent_researchagent_v1"
# - created_at: Current timestamp
# - Default parameters
```

#### Populating Templates

```python
from templates import TemplatePopulator

populator = TemplatePopulator()

# Populate skill template
skill_yaml = populator.populate_skill(skill_config)

# Populate agent template
agent_yaml = populator.populate_agent(agent_config)

# Save to file
populator.save_populated_template("output.yaml", skill_yaml)
```

### 2. Metadata Management

Store and retrieve metadata for agents and skills.

```python
from utils import MetadataManager

manager = MetadataManager("metadata")

# Save metadata
manager.save_skill_metadata(
    skill_id="skill_nlp_001",
    metadata=skill_config,
    format='yaml'
)

# Load metadata
skill_meta = manager.get_skill_metadata("skill_nlp_001")

# List all skills
all_skills = manager.list_skills()

# Filter by category
nlp_skills = manager.list_skills(category="nlp")

# Search skills
results = manager.search_skills("sentiment analysis")
```

### 3. Validation

Validate configurations against schemas.

```python
from utils import validate_skill_config, validate_agent_config, ValidationError

try:
    validate_skill_config(skill_config)
    validate_agent_config(agent_config)
    print("✓ All configurations valid!")
except ValidationError as e:
    print(f"Validation failed: {e}")
    for error in e.errors:
        print(f"  - {error}")
```

### 4. Skill Registry

Centralized management of available skills.

```python
from skills import SkillRegistry

registry = SkillRegistry()

# Register a skill
registry.register(
    skill_id="skill_nlp_001",
    skill_config=skill_config,
    executor=my_skill_function  # Optional executor
)

# Retrieve skill
skill = registry.get("skill_nlp_001")

# List skills
all_skills = registry.list_skills()
nlp_skills = registry.list_skills(category="nlp")

# Search
results = registry.search("text analysis")

# Execute skill (if executor provided)
result = registry.execute("skill_nlp_001", text="Hello world")
```

### 5. Agent Registry

Manage agent instances.

```python
from agents import BaseAgent, AgentConfig, AgentRegistry

# Create agent
config_obj = AgentConfig.from_dict(agent_config)
agent = BaseAgent(config_obj, skill_registry)

# Initialize (validates skills)
agent.initialize()

# Register agent
agent_registry = AgentRegistry()
agent_registry.register(agent)

# Retrieve agent
agent = agent_registry.get("agent_research_v1")

# Find agents with specific skill
agents = agent_registry.search_by_skill("skill_nlp_001")
```

## Configuration Schemas

### Agent Schema

```yaml
# Required fields
id: "agent_research_v1"              # Pattern: agent_[name]_v[version]
name: "ResearchAgent"                # Human-readable name
version: "1.0.0"                     # Semantic version
description: "Detailed description"  # Min 10, max 1000 chars
skills:                              # List of skill_ids (min 1)
  - "skill_search_001"
  - "skill_analyze_001"

# Optional fields
metadata:
  author: "AI Team"
  tags: ["research", "analysis"]
  complexity: "medium"               # low, medium, high
  license: "MIT"

prompt_template: "prompts/research_agent.j2"

parameters:
  temperature: 0.7                   # 0.0-2.0
  max_tokens: 4000                   # >= 1
  top_p: 0.9                        # 0.0-1.0
```

### Skill Schema

```yaml
# Required fields
skill_id: "skill_nlp_textanalyzer_001"  # Pattern: skill_[category]_[name]_[id]
name: "TextAnalyzer"                     # Human-readable name
description: "Detailed description"       # Min 10, max 1000 chars
category: "nlp"                          # nlp, data, search, etc.

# Optional fields
inputs:
  - name: "text"
    type: "string"                       # string, integer, float, etc.
    required: true
    description: "Text to analyze"

outputs:
  - name: "sentiment"
    type: "string"
    description: "Detected sentiment"

metadata:
  complexity: "medium"
  tags: ["nlp", "sentiment"]
  dependencies: ["skill_preprocessing_001"]
  version: "1.0.0"
  author: "NLP Team"
```

## Template System

### Jinja2 Templates

Templates are located in `templates/prompts/` and use Jinja2 syntax.

#### Agent Template (`agent_template.yaml.j2`)

```jinja2
id: "{{ id }}"
name: "{{ name }}"
version: "{{ version }}"
description: |
  {{ description }}

skills:
{%- for skill_id in skills %}
  - "{{ skill_id }}"
{%- endfor %}

metadata:
  author: "{{ metadata.get('author', 'Unknown') }}"
  created_at: "{{ created_at | timestamp }}"
{%- if metadata.get('tags') %}
  tags:
  {%- for tag in metadata.tags %}
    - "{{ tag }}"
  {%- endfor %}
{%- endif %}
```

#### Custom Filters

- `timestamp`: Format datetime as ISO 8601 string
- `capitalize_first`: Capitalize first letter

### Creating Custom Templates

1. Create a new `.j2` file in `templates/prompts/`
2. Use Jinja2 syntax with metadata variables
3. Populate using `TemplatePopulator.populate()`

```python
populator = TemplatePopulator()
content = populator.populate(
    template_name="my_custom_template.j2",
    metadata={"key": "value"}
)
```

## Advanced Features

### ID Generation

Automatic ID generation follows conventions:

```python
from templates import generate_skill_id, generate_agent_id

# Skill IDs: skill_[category]_[name]_[suffix]
skill_id = generate_skill_id("TextAnalyzer", "nlp")
# Result: "skill_nlp_textanalyzer_001"

# With UUID for uniqueness
skill_id = generate_skill_id("TextAnalyzer", use_uuid=True)
# Result: "skill_textanalyzer_f47ac10b"

# Agent IDs: agent_[name]_v[major_version]
agent_id = generate_agent_id("ResearchAgent", "1.0.0")
# Result: "agent_researchagent_v1"
```

### Metadata Merging

Combine base and override metadata:

```python
from templates import merge_metadata

base = {"author": "Team A", "tags": ["ml"]}
override = {"tags": ["ml", "nlp"], "version": "2.0"}

merged = merge_metadata(base, override)
# Result: {"author": "Team A", "tags": ["ml", "nlp"], "version": "2.0"}
```

### Dependency Validation

Validate skill dependencies:

```python
from skills import SkillRegistry

registry = SkillRegistry()

# Check if dependencies are satisfied
is_valid, missing = registry.validate_dependencies("skill_advanced_001")

if not is_valid:
    print(f"Missing dependencies: {missing}")
```

### Skill Loading

Load skills from files:

```python
from skills import SkillLoader, load_skill, load_all_skills

# Load single skill
config = load_skill("text_analyzer.yaml", "skills/examples/")

# Load all skills
all_skills = load_all_skills("skills/examples/")

# Load by category
loader = SkillLoader("skills/examples/")
nlp_skills = loader.load_by_category("nlp")
```

## Best Practices

### 1. Naming Conventions

**Agent IDs:**
- Pattern: `agent_[descriptive_name]_v[major_version]`
- Examples: `agent_research_v1`, `agent_dataprocessor_v2`

**Skill IDs:**
- Pattern: `skill_[category]_[name]_[number]`
- Examples: `skill_nlp_textanalyzer_001`, `skill_search_websearch_001`

### 2. Version Management

Use semantic versioning for agents:
- Major: Breaking changes to skills or interface
- Minor: New features, backward compatible
- Patch: Bug fixes

### 3. Metadata Organization

Always include:
- `author`: Creator/team name
- `tags`: Categorization tags
- `complexity`: low, medium, or high
- `created_at`: Timestamp (auto-generated)

### 4. Skill Dependencies

Document skill dependencies in metadata:

```python
metadata={
    "dependencies": ["skill_preprocessing_001", "skill_tokenizer_001"]
}
```

### 5. Template Organization

Organize templates by type:
- `templates/prompts/agent_prompts/` - Agent-specific prompts
- `templates/prompts/skill_prompts/` - Skill-specific prompts
- `templates/prompts/` - Configuration templates

## Common Use Cases

### 1. Creating a New Skill

```python
from templates import populate_skill_config, TemplatePopulator
from utils import validate_skill_config

# 1. Define skill configuration
config = populate_skill_config(
    name="ImageClassifier",
    description="Classifies images into categories",
    category="visualization",
    inputs=[{"name": "image", "type": "string", "required": True}],
    outputs=[{"name": "category", "type": "string"}]
)

# 2. Validate
validate_skill_config(config)

# 3. Populate template
populator = TemplatePopulator()
yaml_content = populator.populate_skill(config)

# 4. Save
populator.save_populated_template(
    f"skills/examples/{config['skill_id']}.yaml",
    yaml_content
)
```

### 2. Creating a Multi-Skill Agent

```python
from templates import populate_agent_config
from agents import BaseAgent, AgentConfig
from skills import SkillRegistry

# 1. Register skills
skill_registry = SkillRegistry()
skill_registry.register("skill_search_001", search_config)
skill_registry.register("skill_analyze_001", analyze_config)

# 2. Create agent
agent_config = populate_agent_config(
    name="ResearchAssistant",
    description="Helps with research tasks",
    skills=["skill_search_001", "skill_analyze_001"]
)

# 3. Instantiate and initialize
config_obj = AgentConfig.from_dict(agent_config)
agent = BaseAgent(config_obj, skill_registry)
agent.initialize()

# 4. Use agent
if agent.has_skill("skill_search_001"):
    result = agent.execute_skill("skill_search_001", query="AI research")
```

### 3. Batch Loading Skills

```python
from skills import SkillLoader, SkillRegistry

# Load all skills from directory
loader = SkillLoader("skills/examples/")
all_skills = loader.load_all()

# Register all
registry = SkillRegistry()
for skill in all_skills:
    registry.register(skill['skill_id'], skill)

print(f"Loaded {registry.get_skill_count()} skills")
print(f"Categories: {', '.join(registry.list_categories())}")
```

## Troubleshooting

### Common Issues

**1. Template Not Found**

```
TemplateNotFound: Template 'skill_template.yaml.j2' not found
```

**Solution:** Ensure templates are in `templates/prompts/` directory.

**2. Validation Errors**

```
ValidationError: Missing required field: 'skill_id'
```

**Solution:** Use helper functions like `populate_skill_config()` to ensure all required fields are present.

**3. Skill Dependency Errors**

```
ValueError: Agent requires skills that are not registered
```

**Solution:** Register all required skills before initializing the agent.

**4. YAML Syntax Errors**

**Solution:** Use `TemplatePopulator` to generate valid YAML instead of manual editing.

## Extension Points

### Custom Validators

Add custom validation logic:

```python
from utils.validators import ConfigValidator

class MyValidator(ConfigValidator):
    def validate_custom_field(self, config):
        # Add custom validation
        pass
```

### Custom Executors

Implement skill execution logic:

```python
def my_skill_executor(text: str) -> dict:
    # Process input
    result = process_text(text)
    return {"output": result}

# Register with executor
registry.register(
    skill_id="skill_custom_001",
    skill_config=config,
    executor=my_skill_executor
)
```

### Custom Template Filters

Add Jinja2 filters:

```python
populator = TemplatePopulator()
populator.env.filters['my_filter'] = lambda x: x.upper()

# Use in template: {{ name | my_filter }}
```

## API Reference

See individual module documentation:
- `templates/` - Template population
- `utils/` - Validation and metadata
- `skills/` - Skill management
- `agents/` - Agent management

## Contributing

When adding new features:

1. Update schemas in `config/`
2. Add templates in `templates/prompts/`
3. Update validation in `utils/validators.py`
4. Add examples to `example_usage.py`
5. Update this documentation

## License

This system is part of the ClaudeCodeFrameWork project.
