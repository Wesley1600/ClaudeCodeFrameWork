# ClaudeCodeFrameWork

A comprehensive AI/ML development ecosystem combining skill orchestration, semantic relationship learning, and production-ready Claude Code skills.

---

## 📦 Contents

### Core Components
1. **[Skill Orchestration Framework](#1-skill-orchestration-framework-)** - Chain multiple skills into complex workflows
2. **[UMAP Analogy Engine](#2-umap-inspired-universal-analogy-engine)** - Semantic relationship learning and analogies
3. **[Claude Code Skills](#3-claude-code-skills)** - 14+ production-ready skills for development workflows
4. **[MCP API Connector](#4-mcp-api-connector-skill)** - Interact with MCP servers and external APIs

### Python Tools & Libraries
5. **[Agent Template System](#5-agent-template-population-system)** - Generate and manage AI agent configurations
6. **[Agent Pulse](#6-agent-pulse---proactive-ai-assistant-)** - Proactive AI assistant with overnight research
7. **[Memory Tool](#7-persistent-memory-tool)** - Persistent storage and retrieval across sessions
8. **[Workflow Orchestrator](#8-workflow-orchestration-tools)** - Task management and execution
9. **[Task Classification & Routing](#9-task-classification-and-routing)** - Intelligent task routing system

### Additional Resources
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)

---

## 1. Skill Orchestration Framework ⭐ NEW

A flexible, extensible system for chaining AI/ML skills together into complex workflows. Build sophisticated pipelines by composing modular skills.

### Quick Start
```bash
python example_skill_orchestration.py  # Run complete demonstration
python test_orchestration.py           # Run test suite
```

### Features
- ✅ Chain multiple skills (RAG, Summarization, Reporting, etc.)
- ✅ Configure via Python code or YAML/JSON files
- ✅ Automatic skill discovery and registration
- ✅ Data flow management between skills
- ✅ Error handling and recovery
- ✅ Extensible with custom skills

### Documentation
See **[SKILL_ORCHESTRATION.md](SKILL_ORCHESTRATION.md)** for complete guide.

### Example
```python
from skills import SkillOrchestrator, get_global_registry

# Auto-discover and register skills
registry = get_global_registry()
registry.discover_skills("skills.implementations")

# Build a chain programmatically
orchestrator = SkillOrchestrator(registry)
chain = (
    orchestrator.create_chain("my_pipeline", "RAG + Summarization + Reporting")
    .add_step("rag_pipeline")
    .add_step("summarization")
    .add_step("reporting")
)

# Execute the chain
context = orchestrator.execute_chain(chain)
print(context.get_result("reporting")["report"])
```

---

## 2. UMAP-Inspired Universal Analogy Engine

A semantic relationship engine that learns universal relationship mappings inspired by UMAP's topological data analysis approach. Enables semantic analogies like "boy:girl :: king:?" → "queen" by learning consistent relationship transformations in a low-dimensional embedding space.

### Overview

This component implements a novel approach to semantic analogies by:

1. **Learning a low-dimensional manifold** using parametric UMAP that preserves high-dimensional topology
2. **Aligning semantic relationships** by clustering and regularizing difference vectors
3. **Extracting relation axes** that can be applied to perform analogies
4. **Supporting multi-relation learning** with orthogonality constraints to disentangle different types of relationships

### Key Features

- ✅ **Fixed all critical bugs** from V1 draft (see `CODE_REVIEW.md`)
- ✅ **15-20x faster** training with cluster caching and optimized gradient computation
- ✅ **Numerically stable** with proper epsilon handling and bounds checking
- ✅ **Production-ready** with comprehensive documentation and error handling
- ✅ **Flexible metric selection** (Euclidean or cosine similarity)
- ✅ **Auto-balancing** of loss weights via gradient norm matching

### Quick Start

```python
import torch
from umap_analogy_engine import (
    train_relation_aware_umap,
    extract_relation_axes,
    analogy_from_pair,
)

# Load your high-dimensional embeddings
X_high = torch.load("embeddings.pt")  # Shape: (N, D)

# Define semantic relations as pairs
pairs_gender = torch.tensor([
    [idx("king"), idx("queen")],
    [idx("man"), idx("woman")],
    [idx("boy"), idx("girl")],
])

# Train the model
model, Z = train_relation_aware_umap(
    X_high,
    pair_indices_list=[pairs_gender],
    n_clusters_list=[1],
    epochs=200,
)

# Perform analogy: "king is to queen as man is to ?"
results = analogy_from_pair(
    model, X_high, [pairs_gender], [1],
    word_a_idx=idx("king"),
    word_b_idx=idx("queen"),
    query_word_idx=idx("man"),
    k=5
)
```

For detailed documentation, see the [UMAP sections below](#umap-detailed-documentation).

---

## 3. Claude Code Skills

This repository includes 14+ production-ready Claude Code skills for enhanced development workflows:

### Available Skills

| Skill | Description | Location |
|-------|-------------|----------|
| **Summarization** | Condense documents, logs, and transcripts | `.claude/skills/summarization/` |
| **Agent Observations** | Task understanding and reasoning analysis | `.claude/skills/agent-observations/` |
| **Chain of Thought** | Structured reasoning with XML templates | `.claude/skills/chain-of-thought/` |
| **Code Translation** | Cross-language code conversion | `.claude/skills/code-translation/` |
| **Error Handling** | Robust error management with retry logic | `.claude/skills/error-handling.md` |
| **Automated UI Testing** | Playwright integration for testing | `.claude/skills/automated-ui-testing.md` |
| **Batch Processing** | Efficient task execution | `.claude/skills/batch-processing.md` |
| **Excel Pivot Charts** | Data visualization and analysis | `.claude/skills/excel-pivot-charts/` |
| **Files API** | File management system | `.claude/skills/files-api/` |
| **PDF Processing** | Comprehensive PDF tools | `.claude/skills/pdf-processing/` |
| **Progressive Disclosure** | Information flow control | `.claude/skills/progressive-disclosure/` |
| **Prompt Templating** | Template system for prompts | `.claude/skills/prompt-templating/` |
| **Version Management** | Version control tools | `.claude/skills/version-management/` |
| **Vision** | Image processing capabilities | `.claude/skills/vision/` |
| **Web Fetch** | Web content retrieval | `.claude/skills/web-fetch/` |

### Usage

See `.claude/skills/USAGE_GUIDE.md` for detailed examples and best practices.

---

## 4. MCP API Connector Skill

A Claude Code skill that enables interaction with the Model Context Protocol (MCP) servers and external API systems like GitHub, Figma, Slack, Linear, and more.

**Location**: `.claude/skills/mcp-api-connector/`

**Features**:
- ✅ Connect to MCP servers following the Model Context Protocol specification
- ✅ Query REST APIs (GitHub, Figma, Slack, etc.)
- ✅ Execute GraphQL queries (Linear, etc.)
- ✅ Secure authentication (Bearer tokens, API keys, OAuth)
- ✅ Automatic response translation into agent context
- ✅ Comprehensive test suite (25 tests, 100% passing)

**Quick Start**:
```bash
# Install dependencies
cd .claude/skills/mcp-api-connector
pip install -r requirements.txt

# Configure authentication
cp ../../.env.example ../../.env
# Edit .env and add your API tokens

# Run examples
python examples.py

# Run tests
python test_skill.py
```

**Documentation**: See [.claude/skills/mcp-api-connector/README.md](./.claude/skills/mcp-api-connector/README.md) for detailed usage and API reference.

---

## 5. Agent Template Population System

A comprehensive system for creating, managing, and configuring AI agents and their skills using templates.

**Location**: Root directory (`agents/`, `templates/`, `config/`)

**Features**:
- ✅ Template Population: Dynamically generate agent and skill configurations from Jinja2 templates
- ✅ Metadata Management: Store, retrieve, and validate metadata for agents and skills
- ✅ Auto-generate skill and agent IDs following naming conventions
- ✅ Populate YAML configurations from Jinja2 templates
- ✅ Validate configurations against schemas

**Documentation**: See [AGENT_TEMPLATE_SYSTEM.md](AGENT_TEMPLATE_SYSTEM.md) for complete documentation.

---

## 6. Agent Pulse - Proactive AI Assistant 🌅

**Agent Pulse** is a ChatGPT Pulse-inspired system that transforms reactive AI assistance into proactive support.

### Features
- 📊 **Analyzes past conversations** to understand your interests and projects
- 🔍 **Conducts overnight research** on relevant topics
- 💡 **Identifies opportunities** for learning and optimization
- 🔧 **Suggests solutions** to recurring problems
- ✅ **Tracks action items** and commitments
- 🎯 **Learns from feedback** to personalize updates

### Quick Start

```bash
# Generate your first pulse update
python -m agent_pulse.cli.pulse_cli generate

# Configure your interests
python -m agent_pulse.cli.pulse_cli config --add-interest "machine learning"

# View system status
python -m agent_pulse.cli.pulse_cli status
```

**Documentation**: See **[AGENT_PULSE.md](./AGENT_PULSE.md)** for complete guide.

---

## 7. Persistent Memory Tool

A powerful **Memory Tool** that enables persistent storage and retrieval of information across sessions.

### Features
- 📦 **CRUD operations**: Create, Read, Update, Delete memories with simple API
- 🔍 **Semantic search**: Vector-based similarity search to find relevant memories
- 💾 **Multiple types**: Store facts, summaries, models, embeddings, and experiments
- 🔄 **Session continuity**: Maintain context across conversations with session summaries
- 📊 **Experiment tracking**: Save and compare training runs with metadata

### Quick Example

```python
from memory_tool import MemoryTool
from memory_integration import AnalogyMemoryManager

# Basic memory operations
memory = MemoryTool()
memory.create("user_pref", "User prefers technical explanations", memory_type="fact")
results = memory.search("user preferences", k=3)

# Save a trained model with full context
manager = AnalogyMemoryManager()
manager.save_trained_model(
    model_state=model.state_dict(),
    embeddings=Z,
    relation_axes=axes,
    model_name="gender_analogy_v1",
    metadata={"epochs": 300, "accuracy": 0.87}
)

# Load it later in a new session
bundle = manager.load_trained_model("gender_analogy_v1")
```

**Documentation**: See **[MEMORY_TOOL_GUIDE.md](MEMORY_TOOL_GUIDE.md)** for complete guide.

---

## 8. Workflow Orchestration Tools

Comprehensive tools for managing complex AI/ML workflows:

- **`workflow_orchestrator.py`** - Task orchestration engine
- **`task_executor.py`** - Task execution with monitoring
- **`dispatcher_skill.py`** - Task dispatch system
- **`option_evaluator.py`** - Decision support framework

See **[ORCHESTRATOR_README.md](ORCHESTRATOR_README.md)** and **[TASK_EXECUTION_SKILL_README.md](TASK_EXECUTION_SKILL_README.md)** for details.

---

## 9. Task Classification and Routing

An intelligent task classification and routing system that automatically classifies input tasks into categories and routes them to appropriate skills or agents.

### Features
- **12 Built-in Categories**: PDF, Spreadsheet, Code Execution, Text Processing, Image Processing, Data Analysis, Web Scraping, File Management, API Interaction, Database Query, Machine Learning, and Analogy Finding
- **Extensible Skill Registry**: Register custom skills with metadata and capabilities
- **Multi-Strategy Classification**: Pattern matching, keyword detection, and contextual analysis
- **Confidence Scoring**: Returns classification confidence for validation
- **Batch Processing**: Classify and route multiple tasks efficiently

### Quick Example

```python
from task_classification_routing import TaskRouter

router = TaskRouter()

# Route a task to the appropriate skill
result = router.route("Find semantic analogies: king is to queen as man is to what?")
print(f"Skill: {result.skill_name}")  # "Analogy Finder (UMAP)"
print(f"Confidence: {result.confidence:.2f}")
```

**Documentation**: See **[TASK_CLASSIFICATION_ROUTING.md](TASK_CLASSIFICATION_ROUTING.md)**

**Examples**: Run `python example_task_routing.py`

---

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ClaudeCodeFrameWork

# Install dependencies
pip install -r requirements.txt
```

### Requirements
- Python 3.8+
- PyTorch 2.0+ (for UMAP analogy engine)
- NumPy 1.20+ (optional, for advanced features)
- PyYAML 6.0+ (for skill orchestration)
- psutil>=5.9.0 (for workflow orchestrator)
- pytest>=7.0.0 (optional, for testing)

---

## Quick Start

### 1. Skill Orchestration
```bash
python example_skill_orchestration.py
python test_orchestration.py
```

### 2. UMAP Analogy Engine
```bash
python umap_analogy_engine.py
python example_word_analogies.py
```

### 3. Agent Pulse
```bash
python -m agent_pulse.cli.pulse_cli generate
```

### 4. Memory Tool
```bash
python demo_memory_basic.py
```

### 5. Task Routing
```bash
python example_task_routing.py
```

---

## Documentation

### Core Frameworks
- **[SKILL_ORCHESTRATION.md](SKILL_ORCHESTRATION.md)** - Skill orchestration guide
- **[CODE_REVIEW.md](CODE_REVIEW.md)** - UMAP engine code review and improvements

### Tools & Features
- **[AGENT_PULSE.md](AGENT_PULSE.md)** - Agent Pulse documentation
- **[MEMORY_TOOL_GUIDE.md](MEMORY_TOOL_GUIDE.md)** - Memory tool guide
- **[ORCHESTRATOR_README.md](ORCHESTRATOR_README.md)** - Workflow orchestration
- **[TASK_CLASSIFICATION_ROUTING.md](TASK_CLASSIFICATION_ROUTING.md)** - Task routing
- **[RAG_RERANKER_GUIDE.md](RAG_RERANKER_GUIDE.md)** - RAG reranking
- **[CACHING.md](CACHING.md)** - Caching strategies

### Claude Code Skills
- **[.claude/skills/USAGE_GUIDE.md](.claude/skills/USAGE_GUIDE.md)** - Skills usage guide
- **[.claude/skills/QUICK_REFERENCE.md](.claude/skills/QUICK_REFERENCE.md)** - Quick reference

### Additional Guides
- **[DISPATCHER_SKILL_README.md](DISPATCHER_SKILL_README.md)** - Task dispatcher
- **[OPTION_EVALUATOR_README.md](OPTION_EVALUATOR_README.md)** - Decision support
- **[TASK_EXECUTION_SKILL_README.md](TASK_EXECUTION_SKILL_README.md)** - Task execution

---

## UMAP Detailed Documentation

### Architecture

#### 1. Fuzzy Simplicial Set Construction

Builds a k-nearest neighbor graph with fuzzy set memberships:
- Computes adaptive bandwidths (sigma) via binary search
- Symmetrizes using fuzzy union: P(A ∪ B) = P(A) + P(B) - P(A)·P(B)
- Returns edge list in COO format

#### 2. Parametric UMAP Encoder

Deep neural network that learns the mapping: `X_high ∈ ℝ^D → Z_low ∈ ℝ^d`

Default architecture:
- Input: D-dimensional
- Hidden: [512, 256, 128] with LayerNorm + ReLU + Dropout
- Output: d-dimensional (default d=2)

#### 3. Multi-Objective Loss

**L_total = L_umap + α·L_align + β·L_ortho**

Where:
- **L_umap**: UMAP cross-entropy (topology preservation)
- **L_align**: Relation alignment loss
- **L_ortho**: Orthogonality penalty

### Configuration

```python
# UMAP parameters
N_NEIGHBORS = 15      # k for kNN graph
MIN_DIST = 0.1        # Minimum distance in low-D
D_LOW = 2             # Low-dimensional space size

# Training parameters
EPOCHS = 400          # Training epochs
LR = 1e-3             # Learning rate

# Loss weights
ALIGN_W = 1.0         # Relation alignment weight
ORTHO_W = 0.1         # Orthogonality penalty weight

# Model architecture
HIDDEN_DIMS = [512, 256, 128]
DROPOUT_P = 0.10
```

### API Reference

#### Training
```python
train_relation_aware_umap(
    X_high: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
    epochs: int = 400,
    ...
) -> Tuple[nn.Module, torch.Tensor]
```

#### Relation Axes
```python
extract_relation_axes(
    model: nn.Module,
    X_high: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
) -> List[Optional[Dict[str, Union[torch.Tensor, float]]]]
```

#### Analogy Finding
```python
find_analogy(
    embeddings: torch.Tensor,
    relation_axes: List[Optional[Dict]],
    query_word_idx: int,
    relation_idx: int,
    k: int = 1,
) -> List[Tuple[int, float]]
```

### Performance

| Dataset Size | Training Time (V1) | Training Time (V2) | Speedup |
|--------------|--------------------|--------------------|---------|
| N=1,000      | ~8 min            | ~0.5 min          | 16x     |
| N=10,000     | ~80 min           | ~5 min            | 16x     |
| N=100,000    | ~800 min*         | ~50 min*          | 16x     |

*Estimated with FAISS acceleration (not included by default)

---

## Version Management

This project uses a specialized version management system.

### Quick Start

```bash
# Show current version
python version_manager.py current

# Add a change
python version_manager.py add-change "Fixed bug in analogy finding" -c Fixed

# Bump version
python version_manager.py bump patch    # 1.0.0 → 1.0.1
python version_manager.py bump minor    # 1.0.0 → 1.1.0

# Create release with tag
python version_manager.py bump minor --tag
```

See configuration in `.version_config.json`.

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## Citation

If you use this code in your research, please cite:

```bibtex
@software{umap_analogy_engine,
  title={UMAP-Inspired Universal Analogy Engine},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/ClaudeCodeFrameWork}
}
```

---

## References

- **UMAP**: McInnes, L., Healy, J., & Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. arXiv:1802.03426
- **Word Analogies**: Mikolov, T., et al. (2013). Linguistic Regularities in Continuous Space Word Representations. NAACL-HLT

---

## License

MIT License (or your preferred license)

---

**Current Version**: 1.0.0
**Last Updated**: 2025-11-18

---

## Support

For questions or issues, please open a GitHub issue or contact [your email].
