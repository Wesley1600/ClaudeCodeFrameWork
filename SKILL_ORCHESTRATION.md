# Skill Orchestration Framework

A flexible, extensible system for chaining AI/ML skills together into complex workflows.

## Overview

The Skill Orchestration Framework enables you to:

- **Chain multiple skills** into complex workflows
- **Pass data between skills** through a shared context
- **Execute sequentially or in parallel** (parallel support planned)
- **Configure chains** via code or YAML/JSON files
- **Handle errors gracefully** with recovery options
- **Extend easily** with custom skills

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                  Skill Orchestrator                      │
│  • Chain execution                                       │
│  • Data flow management                                  │
│  • Error handling                                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ├─→ SkillRegistry
                  │   • Skill discovery
                  │   • Registration
                  │   • Instantiation
                  │
                  ├─→ ChainConfig
                  │   • YAML/JSON loading
                  │   • Step definitions
                  │   • Builder pattern
                  │
                  └─→ SkillContext
                      • Result storage
                      • Shared state
                      • Error tracking
```

### Skill Hierarchy

```
BaseSkill (Abstract)
├── PassthroughSkill
├── TransformSkill (Abstract)
└── Custom Skills
    ├── RAGPipelineSkill
    ├── SummarizationSkill
    ├── ReportingSkill
    └── Your Custom Skills
```

## Quick Start

### 1. Register Skills

```python
from skills import get_global_registry

registry = get_global_registry()

# Auto-discover skills in a package
registry.discover_skills("skills.implementations")

# Or register manually
from skills.implementations import RAGPipelineSkill
registry.register(RAGPipelineSkill)
```

### 2. Create a Chain (Programmatically)

```python
from skills import SkillOrchestrator

orchestrator = SkillOrchestrator()

# Build a chain using the builder pattern
chain = (
    orchestrator
    .create_chain(
        name="my_pipeline",
        description="RAG + Summarization + Reporting"
    )
    .add_step("rag_pipeline", config={
        "rag_pipeline": {"top_k": 5}
    })
    .add_step("summarization", config={
        "summarization": {"strategy": "extractive"}
    })
    .add_step("reporting", config={
        "reporting": {"format": "markdown"}
    })
)

# Set initial data
chain.initial_data = {
    "query": "What are the key features?",
    "documents": ["Document 1...", "Document 2..."]
}
```

### 3. Execute the Chain

```python
# Execute and get results
context = orchestrator.execute_chain(chain)

# Access results
report = context.get_result("reporting")
print(report["report"])
```

### 4. Or Load from YAML

```yaml
# my_chain.yaml
name: my_pipeline
description: RAG + Summarization + Reporting

initial_data:
  query: "What are the key features?"
  documents:
    - "Document 1..."
    - "Document 2..."

steps:
  - name: "Retrieve Context"
    skills: rag_pipeline
    config:
      rag_pipeline:
        top_k: 5

  - name: "Summarize"
    skills: summarization
    config:
      summarization:
        strategy: extractive

  - name: "Generate Report"
    skills: reporting
    config:
      reporting:
        format: markdown
```

```python
# Execute from file
context = orchestrator.execute_from_file("my_chain.yaml")
```

## Built-in Skills

### RAGPipelineSkill

Retrieval-Augmented Generation pipeline.

**Configuration:**
- `embedding_dim`: Embedding dimension (default: 384)
- `chunk_size`: Max tokens per chunk (default: 512)
- `top_k`: Number of documents to retrieve (default: 5)
- `similarity_threshold`: Minimum similarity (default: 0.5)

**Input:**
- `query`: Search query
- `documents`: Optional list of documents

**Output:**
```python
{
    "documents": [...],  # Retrieved documents
    "context": "...",    # Assembled context text
    "scores": [...],     # Relevance scores
    "metadata": {...}    # Retrieval info
}
```

### SummarizationSkill

Text summarization with multiple strategies.

**Configuration:**
- `strategy`: `extractive` | `abstractive` | `bullet_points`
- `max_length`: Max summary length in words (default: 200)
- `num_sentences`: Number of sentences for extractive (default: 3)

**Input:**
- `text`: Text to summarize (or uses RAG context)

**Output:**
```python
{
    "summary": "...",        # Generated summary
    "key_points": [...],     # Extracted key points
    "metadata": {...}        # Statistics
}
```

### ReportingSkill

Formatted report generation.

**Configuration:**
- `format`: `text` | `markdown` | `json` | `html`
- `include_metadata`: Include execution metadata (default: true)
- `include_sources`: Include source documents (default: true)
- `title`: Report title

**Input:**
- Uses entire SkillContext (all previous results)

**Output:**
```python
{
    "report": "...",     # Formatted report
    "format": "...",     # Format used
    "metadata": {...}    # Report metadata
}
```

## Creating Custom Skills

### Basic Skill

```python
from skills import BaseSkill, SkillContext, SkillMetadata

class MyCustomSkill(BaseSkill):
    """My custom skill"""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            description="Does something cool",
            tags=["custom"]
        )

    def execute(self, context: SkillContext, **kwargs) -> dict:
        # Get data from previous skills
        previous_result = context.get_result("previous_skill")

        # Or from kwargs
        input_data = kwargs.get("data")

        # Do your processing
        result = {"output": "processed data"}

        return result

    def validate_inputs(self, context: SkillContext, **kwargs) -> bool:
        # Optional: validate inputs
        return kwargs.get("data") is not None
```

### Transform Skill

```python
from skills import TransformSkill

class UppercaseSkill(TransformSkill):
    """Convert text to uppercase"""

    def _create_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="uppercase",
            description="Convert text to uppercase",
            tags=["transform", "text"]
        )

    def transform(self, data: str) -> str:
        return data.upper()
```

## Chain Configuration

### YAML Format

```yaml
name: chain_name
description: Chain description

# Initial data
initial_data:
  key: value

# Global config for all skills
global_config:
  verbose: true

# Steps
steps:
  - name: "Step 1"
    skills: skill_name
    config:
      skill_name:
        param: value
    mode: sequential  # or parallel
    continue_on_error: false

# Execution settings
fail_fast: true
timeout: 60.0
```

### Execution Modes

- **sequential**: Execute skills one after another (default)
- **parallel**: Execute skills concurrently (planned feature)

### Error Handling

```python
# Stop on first error
chain.fail_fast = True

# Continue despite errors
step.continue_on_error = True
```

## Data Flow

Data flows between skills through `SkillContext`:

```python
# In Skill 1
def execute(self, context, **kwargs):
    result = {"data": "processed"}
    return result  # Automatically added to context

# In Skill 2
def execute(self, context, **kwargs):
    # Get result from Skill 1
    previous = context.get_result("skill_1")
    data = previous["data"]

    # Or use shared state
    context.shared_state["key"] = "value"
```

## Advanced Features

### Conditional Execution

```python
from skills import SkillStep

def condition(context: SkillContext) -> bool:
    # Only execute if previous step succeeded
    return context.get_result("previous_skill") is not None

step = SkillStep(
    skills="conditional_skill",
    condition=condition
)
```

### Lifecycle Hooks

```python
class MySkill(BaseSkill):
    def on_before_execute(self, context: SkillContext):
        print("Starting execution...")

    def on_after_execute(self, context: SkillContext, result):
        print(f"Completed with: {result}")

    def on_error(self, context: SkillContext, error: Exception):
        print(f"Error occurred: {error}")
```

### Dependency Resolution

```python
metadata = SkillMetadata(
    name="my_skill",
    dependencies=["required_skill_1", "required_skill_2"]
)

# Registry will automatically order skills
ordered = registry.get_dependency_order(["skill_a", "skill_b", "skill_c"])
```

## Examples

### Example 1: RAG → Summary → Report

```python
orchestrator = SkillOrchestrator()

chain = orchestrator.create_chain("rag_pipeline", "Full RAG workflow")

chain.add_step("rag_pipeline", config={
    "rag_pipeline": {"top_k": 5}
})

chain.add_step("summarization", config={
    "summarization": {"strategy": "extractive", "num_sentences": 4}
})

chain.add_step("reporting", config={
    "reporting": {"format": "markdown", "title": "Analysis Report"}
})

chain.initial_data = {
    "query": "What are the main features?",
    "documents": [...]
}

context = orchestrator.execute_chain(chain)
print(context.get_result("reporting")["report"])
```

### Example 2: Custom Processing Chain

```python
# Register custom skills
registry.register(DataLoaderSkill)
registry.register(PreprocessingSkill)
registry.register(AnalysisSkill)
registry.register(VisualizationSkill)

# Build chain
chain = (
    orchestrator.create_chain("data_analysis", "Complete data analysis")
    .add_step("data_loader")
    .add_step("preprocessing")
    .add_step("analysis")
    .add_step("visualization")
)

context = orchestrator.execute_chain(chain)
```

## Best Practices

1. **Keep skills focused**: Each skill should do one thing well
2. **Use descriptive names**: Make chains easy to understand
3. **Validate inputs**: Implement `validate_inputs()` for robust skills
4. **Handle errors gracefully**: Use `continue_on_error` appropriately
5. **Document configuration**: Clearly document all config parameters
6. **Test skills independently**: Before chaining, test each skill alone
7. **Use shared state wisely**: Prefer explicit result passing over shared state

## Future Enhancements

- [ ] **Async execution**: True parallel execution with asyncio
- [ ] **Distributed execution**: Run skills across multiple machines
- [ ] **Caching layer**: Cache expensive skill results
- [ ] **Monitoring/Observability**: Built-in metrics and tracing
- [ ] **Version control**: Track chain versions and skill versions
- [ ] **A/B testing**: Compare different skill configurations
- [ ] **Auto-optimization**: Automatically tune parameters

## Architecture Decisions

### Why This Design?

1. **Composability**: Skills are self-contained, reusable units
2. **Flexibility**: Support both code and config-based chains
3. **Extensibility**: Easy to add new skills without modifying core
4. **Observability**: SkillContext tracks everything
5. **Error Recovery**: Granular control over error handling

### Design Patterns Used

- **Strategy Pattern**: Different execution modes
- **Builder Pattern**: Fluent chain construction
- **Registry Pattern**: Skill discovery and instantiation
- **Template Method**: BaseSkill lifecycle hooks
- **Chain of Responsibility**: Skill execution pipeline

## Contributing

To add a new skill:

1. Inherit from `BaseSkill` or `TransformSkill`
2. Implement `_create_metadata()` and `execute()`
3. Add to `skills/implementations/`
4. Register in `__init__.py`
5. Add tests and documentation

## License

MIT License - see LICENSE file

## See Also

- [UMAP Analogy Engine](README.md) - The original analogy engine
- [Example Script](example_skill_orchestration.py) - Complete working examples
- [Chain Configurations](chains/) - Example chain YAML files
