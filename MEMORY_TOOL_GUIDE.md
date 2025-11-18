# Memory Tool Guide

## Overview

The Memory Tool provides persistent storage and retrieval of information across sessions for the UMAP Analogy Engine. It enables Claude to maintain continuity by remembering:

- **Facts**: Key information and preferences
- **Summaries**: Session notes and task summaries
- **Models**: Trained model weights and state dicts
- **Embeddings**: Vector representations and relation axes
- **Experiments**: Configuration and results tracking

## Key Features

✅ **File-based persistence** - All data stored in `.memory/` directory
✅ **CRUD operations** - Create, Read, Update, Delete with simple API
✅ **Vector-based search** - Semantic similarity search across memories
✅ **Type-safe storage** - Support for text, JSON, and PyTorch tensors
✅ **Automatic indexing** - Metadata tracking with timestamps
✅ **Session continuity** - Summaries for cross-session context

## Quick Start

### Basic Usage

```python
from memory_tool import MemoryTool

# Initialize
memory = MemoryTool()

# Create a fact
memory.create(
    "user_preference",
    "The user prefers concise technical explanations",
    memory_type="fact"
)

# Read it back
fact = memory.read("user_preference")
print(fact)  # "The user prefers concise technical explanations"

# Search semantically
results = memory.search("What does the user like?", k=3)
for key, score, metadata in results:
    print(f"{key}: {score:.2f}")
```

### Saving Models

```python
import torch
from memory_tool import MemoryTool

memory = MemoryTool()

# Save a trained model
model_state = model.state_dict()
memory.create(
    "analogy_model_v1",
    model_state,
    memory_type="model",
    metadata={"epochs": 300, "accuracy": 0.87}
)

# Load it later
loaded_state = memory.read("analogy_model_v1")
model.load_state_dict(loaded_state)
```

### Integration with UMAP Analogy Engine

```python
from memory_integration import AnalogyMemoryManager

manager = AnalogyMemoryManager()

# Save complete training run
manager.save_trained_model(
    model_state=model.state_dict(),
    embeddings=Z,
    relation_axes=axes,
    model_name="gender_analogy_v1",
    metadata={"epochs": 300, "accuracy": 0.87}
)

# Load everything back
bundle = manager.load_trained_model("gender_analogy_v1")
model.load_state_dict(bundle["model_state"])
Z = bundle["embeddings"]
axes = bundle["relation_axes"]
```

## Architecture

### Directory Structure

```
.memory/
├── facts/          # Text-based facts (JSON)
├── summaries/      # Session summaries (TXT)
├── models/         # Model state dicts (PT)
├── embeddings/     # Vectors and axes (PT)
│   └── *_embedding.pt  # Semantic search embeddings
└── index.json      # Master index with metadata
```

### Memory Types

| Type | Extension | Use Case | Example |
|------|-----------|----------|---------|
| `fact` | `.json` | Key-value information | User preferences, constants |
| `summary` | `.txt` | Session notes | Task summaries, findings |
| `model` | `.pt` | Model weights | Trained models, checkpoints |
| `embedding` | `.pt` | Vectors | Relation axes, embeddings |
| `vector` | `.pt` | Generic tensors | Any PyTorch data |

### Index Format

Each memory entry in `index.json` contains:

```json
{
  "user_preference": {
    "key": "user_preference",
    "memory_type": "fact",
    "file_path": ".memory/facts/user_preference.json",
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00",
    "metadata": {
      "category": "preferences",
      "importance": "high"
    },
    "has_embedding": true
  }
}
```

## API Reference

### MemoryTool Class

#### `__init__(memory_dir=None, verbose=True)`

Initialize the memory tool.

**Parameters:**
- `memory_dir` (Path, optional): Custom directory (default: `.memory/`)
- `verbose` (bool): Print status messages

#### `create(key, content, memory_type="fact", metadata=None, compute_embedding=True)`

Create a new memory entry.

**Parameters:**
- `key` (str): Unique identifier
- `content` (Any): Content to store (text, dict, tensor, etc.)
- `memory_type` (str): Type (`"fact"`, `"summary"`, `"model"`, `"embedding"`, `"vector"`)
- `metadata` (dict, optional): Additional metadata
- `compute_embedding` (bool): Compute semantic embedding for search

**Returns:** `bool` - Success status

**Example:**
```python
memory.create(
    "project_goal",
    "Build a UMAP-based analogy engine",
    memory_type="fact",
    metadata={"category": "project", "priority": "high"}
)
```

#### `read(key)`

Read a memory entry.

**Parameters:**
- `key` (str): Memory identifier

**Returns:** Content or `None` if not found

**Example:**
```python
content = memory.read("project_goal")
```

#### `update(key, content, metadata=None, compute_embedding=True)`

Update an existing memory.

**Parameters:**
- `key` (str): Memory identifier
- `content` (Any): New content
- `metadata` (dict, optional): Metadata to merge
- `compute_embedding` (bool): Recompute embedding

**Returns:** `bool` - Success status

**Example:**
```python
memory.update(
    "project_goal",
    "Build a production-ready UMAP analogy engine",
    metadata={"status": "in_progress"}
)
```

#### `delete(key)`

Delete a memory entry.

**Parameters:**
- `key` (str): Memory identifier

**Returns:** `bool` - Success status

**Example:**
```python
memory.delete("old_experiment")
```

#### `list(memory_type=None)`

List all memories, optionally filtered by type.

**Parameters:**
- `memory_type` (str, optional): Filter by type

**Returns:** `List[Dict]` - List of memory entries (sorted by update time)

**Example:**
```python
# All memories
all_memories = memory.list()

# Only facts
facts = memory.list(memory_type="fact")

for entry in facts:
    print(f"{entry['key']}: {entry['updated_at']}")
```

#### `search(query, k=5, memory_type=None, threshold=0.0)`

Search memories using semantic similarity.

**Parameters:**
- `query` (str): Search query
- `k` (int): Number of results
- `memory_type` (str, optional): Filter by type
- `threshold` (float): Minimum similarity (0.0 to 1.0)

**Returns:** `List[Tuple[str, float, Dict]]` - (key, score, metadata) tuples

**Example:**
```python
results = memory.search("training hyperparameters", k=5)
for key, score, metadata in results:
    if score > 0.5:
        content = memory.read(key)
        print(f"{key} ({score:.2f}): {content}")
```

#### `get_stats()`

Get memory statistics.

**Returns:** `Dict` - Statistics including counts, sizes, etc.

**Example:**
```python
stats = memory.get_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"Storage: {stats['total_size_mb']} MB")
print(f"By type: {stats['by_type']}")
```

### AnalogyMemoryManager Class

Higher-level interface for UMAP analogy engine integration.

#### `save_trained_model(model_state, embeddings, relation_axes, model_name, metadata=None)`

Save complete training run (model + embeddings + axes).

**Parameters:**
- `model_state` (dict): Model state dictionary
- `embeddings` (Tensor): Low-dimensional embeddings
- `relation_axes` (list): Relation axis dictionaries
- `model_name` (str): Unique model name
- `metadata` (dict, optional): Additional metadata

**Example:**
```python
manager.save_trained_model(
    model_state=model.state_dict(),
    embeddings=Z,
    relation_axes=axes,
    model_name="gender_plural_v1",
    metadata={
        "epochs": 300,
        "accuracy": 0.87,
        "relations": ["gender", "plural"]
    }
)
```

#### `load_trained_model(model_name)`

Load a complete training bundle.

**Returns:** `Dict` with keys: `model_state`, `embeddings`, `relation_axes`, `metadata`

**Example:**
```python
bundle = manager.load_trained_model("gender_plural_v1")
model.load_state_dict(bundle["model_state"])
Z = bundle["embeddings"]
axes = bundle["relation_axes"]
```

#### `save_experiment(experiment_name, config, results, description="")`

Save experiment configuration and results.

**Example:**
```python
manager.save_experiment(
    experiment_name="exp_001_baseline",
    config={"epochs": 300, "lr": 1e-3, "d_low": 50},
    results={"accuracy": 0.87, "loss": 0.123},
    description="Baseline gender+plural analogy experiment"
)
```

#### `save_session_summary(session_id, summary, tasks_completed, key_findings, metadata=None)`

Save session summary for continuity.

**Example:**
```python
manager.save_session_summary(
    session_id="2025_01_15_debugging",
    summary="Fixed metric mismatch bug and optimized performance",
    tasks_completed=[
        "Changed analogy metric from cosine to Euclidean",
        "Added cluster caching for 10x speedup"
    ],
    key_findings=[
        "Cosine similarity doesn't work for absolute positions",
        "Cluster caching dramatically improves speed"
    ]
)
```

#### `save_analogy_pattern(pattern_name, description, examples, metadata=None)`

Save discovered analogy patterns.

**Example:**
```python
manager.save_analogy_pattern(
    pattern_name="gender_relations",
    description="Gender transformation in English",
    examples=[
        ("king", "queen", "man", "woman"),
        ("boy", "girl", "father", "mother")
    ],
    metadata={"language": "english"}
)
```

#### `search_experiments(query, k=5)`

Search experiments by semantic similarity.

**Example:**
```python
results = manager.search_experiments("high accuracy gender", k=3)
for key, score, metadata in results:
    print(f"{key}: {score:.2f} - {metadata}")
```

#### `get_continuity_summary()`

Get a formatted summary for session continuity.

**Returns:** `str` - Formatted summary text

**Example:**
```python
print(manager.get_continuity_summary())
```

## Semantic Search

The memory tool uses vector embeddings for semantic similarity search.

### How It Works

1. **Text embedding**: When you create a text-based memory with `compute_embedding=True`, the system:
   - Computes a vector embedding of the text
   - Stores it in `.memory/embeddings/{key}_embedding.pt`
   - Marks the entry as searchable in the index

2. **Query processing**: When you search:
   - Query text is embedded into the same vector space
   - Cosine similarity computed between query and all memory embeddings
   - Results ranked by similarity score

3. **Current implementation**: Uses a simple hash-based embedding (placeholder)
   - **For production**: Replace `_compute_embedding()` with:
     - Sentence transformers (e.g., `sentence-transformers` library)
     - OpenAI embeddings API
     - Your own UMAP embeddings from the analogy engine

### Improving Search Quality

To use better embeddings:

```python
from sentence_transformers import SentenceTransformer

class ImprovedMemoryTool(MemoryTool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def _compute_embedding(self, text: str) -> torch.Tensor:
        # Use sentence transformer instead of hash
        embedding = self.encoder.encode(text, convert_to_tensor=True)
        return F.normalize(embedding, dim=-1)
```

## Use Cases

### 1. Session Continuity

Remember context across conversations:

```python
# At end of session
manager.save_session_summary(
    session_id="2025_01_15",
    summary="Implemented and tested memory tool",
    tasks_completed=["CRUD ops", "Semantic search", "Integration"],
    key_findings=["Memory tool works well", "Tests pass"]
)

# In next session
recent = manager.get_recent_sessions(n=3)
print("Last session:", recent[0])
```

### 2. Experiment Tracking

Track all your training runs:

```python
# After each experiment
manager.save_experiment(
    experiment_name=f"exp_{run_id}",
    config=hyperparameters,
    results=metrics,
    description=f"Testing {strategy}"
)

# Find best experiments
results = manager.search_experiments("high accuracy low loss", k=5)
best_config = memory.read(results[0][0])
```

### 3. Model Versioning

Save model checkpoints:

```python
# Save regularly during training
if epoch % 100 == 0:
    manager.save_trained_model(
        model_state=model.state_dict(),
        embeddings=Z,
        relation_axes=axes,
        model_name=f"checkpoint_epoch_{epoch}",
        metadata={"epoch": epoch, "loss": current_loss}
    )

# Load best checkpoint
best = manager.load_trained_model("checkpoint_epoch_300")
```

### 4. Knowledge Base

Build searchable knowledge:

```python
# Store facts as you discover them
memory.create("fact_learning_rate", "Learning rate 1e-3 works best", "fact")
memory.create("fact_align_weight", "align_weight=1.0 gives good balance", "fact")

# Search when needed
tips = memory.search("best hyperparameters for training", k=5)
```

## Best Practices

### 1. Use Descriptive Keys

```python
# Good
memory.create("user_prefers_concise_output", ...)
memory.create("model_gender_plural_v1", ...)

# Bad
memory.create("pref1", ...)
memory.create("model", ...)
```

### 2. Add Rich Metadata

```python
memory.create(
    "experiment_baseline",
    content,
    metadata={
        "date": "2025-01-15",
        "author": "claude",
        "category": "baseline",
        "status": "completed",
        "priority": "high"
    }
)
```

### 3. Regular Cleanup

```python
# Delete obsolete memories
old_experiments = memory.list(memory_type="fact")
for entry in old_experiments:
    if entry["metadata"].get("status") == "obsolete":
        memory.delete(entry["key"])
```

### 4. Namespace Your Keys

```python
# Use prefixes for organization
memory.create("user:preference:output_style", ...)
memory.create("model:gender:v1", ...)
memory.create("experiment:baseline:001", ...)
```

### 5. Leverage Search

Don't rely on exact key recall - use search:

```python
# Instead of trying to remember the exact key
# results = memory.read("what_was_that_experiment_name")

# Use search
results = memory.search("that experiment about gender", k=1)
if results:
    key = results[0][0]
    content = memory.read(key)
```

## Testing

Run the comprehensive test suite:

```bash
python test_memory_tool.py
```

Tests cover:
- ✅ Basic CRUD operations
- ✅ Semantic search
- ✅ Model persistence
- ✅ Analogy engine integration
- ✅ Statistics and metadata

## Limitations

1. **Embedding quality**: Current implementation uses simple hash-based embeddings
   - For production, integrate proper sentence embeddings

2. **Scale**: File-based storage works well up to ~10K memories
   - For larger scale, consider SQLite or vector database

3. **Concurrency**: No locking mechanism for concurrent access
   - Single-process use only

4. **Versioning**: No built-in version control for memories
   - Use metadata and timestamps to track changes

## Future Enhancements

- [ ] Integration with sentence-transformers for better embeddings
- [ ] SQLite backend for better scalability
- [ ] Vector database support (FAISS, Pinecone)
- [ ] Memory expiration and auto-cleanup
- [ ] Compression for large tensors
- [ ] Multi-modal memories (images, audio)
- [ ] Memory graphs and relationships
- [ ] Automatic summarization of long sessions

## Troubleshooting

### Memory not found after creation

Check if creation succeeded:
```python
success = memory.create(key, content, ...)
if not success:
    print("Creation failed - key might already exist")
```

### Search returns no results

1. Ensure memories have embeddings:
   ```python
   stats = memory.get_stats()
   print(f"With embeddings: {stats['with_embeddings']}")
   ```

2. Lower the threshold:
   ```python
   results = memory.search(query, threshold=0.0)
   ```

3. Check memory type filter:
   ```python
   # Don't filter if unsure
   results = memory.search(query, memory_type=None)
   ```

### Index corruption

Rebuild index from files:
```python
memory.index = {}
for memory_type in ["fact", "summary", "model", "embedding"]:
    directory = memory._get_directory(memory_type)
    for file_path in directory.glob("*"):
        # Rebuild index entry
        # (Manual recovery - implement as needed)
```

## Support

For questions or issues:
1. Check this guide
2. Review `test_memory_tool.py` for examples
3. Open an issue on GitHub

---

**Version**: 1.0
**Last updated**: 2025-01-15
**Status**: Production-ready
