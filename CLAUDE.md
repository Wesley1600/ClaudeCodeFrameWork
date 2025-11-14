# CLAUDE.md - AI Assistant Guide for UMAP Analogy Engine

**Last Updated**: 2025-11-14
**Status**: Production-ready V1.0

## Table of Contents

1. [Project Overview](#project-overview)
2. [Repository Structure](#repository-structure)
3. [Architecture & Core Concepts](#architecture--core-concepts)
4. [Development Workflow](#development-workflow)
5. [Key Conventions](#key-conventions)
6. [Testing & Validation](#testing--validation)
7. [Common Tasks for AI Assistants](#common-tasks-for-ai-assistants)
8. [Critical Considerations](#critical-considerations)
9. [Git Workflow](#git-workflow)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is This Project?

The **UMAP-Inspired Universal Analogy Engine** is a semantic relationship learning system that performs analogies like "king:queen :: man:?" → "woman" by:

1. Learning a low-dimensional manifold using parametric UMAP
2. Aligning semantic relationships through difference vector clustering
3. Extracting relation axes that can be applied to perform analogies
4. Supporting multi-relation learning with orthogonality constraints

### Technology Stack

- **Language**: Python 3.8+
- **Framework**: PyTorch 2.0+
- **Core Dependencies**: NumPy 1.20+
- **Optional**: gensim (for Word2Vec embeddings)

### Project Status

- ✅ V1.0 Production-ready
- ✅ All critical bugs fixed (see CODE_REVIEW.md)
- ✅ 15-20x faster than initial draft
- ✅ Numerically stable with comprehensive documentation

---

## Repository Structure

```
ClaudeCodeFrameWork/
├── umap_analogy_engine.py      # Main implementation (1000+ lines)
│   ├── UMAP utilities          # Graph construction, fuzzy sets
│   ├── Model architecture      # Parametric encoder
│   ├── Loss functions          # UMAP, alignment, orthogonality
│   ├── Training loop           # Main training function
│   └── Analogy API             # Public interface for analogies
│
├── example_word_analogies.py   # Example usage with real embeddings
│   ├── Embedding loaders       # GloVe, Word2Vec
│   ├── Relation definitions    # Gender, plural, etc.
│   └── Evaluation metrics      # Analogy accuracy tests
│
├── README.md                   # User-facing documentation
├── CODE_REVIEW.md              # Detailed code review & fixes
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git ignore rules
```

### File Purposes

| File | Purpose | When to Modify |
|------|---------|----------------|
| `umap_analogy_engine.py` | Core implementation | Algorithm improvements, bug fixes |
| `example_word_analogies.py` | Usage examples | Adding new examples, testing |
| `README.md` | User documentation | Feature updates, API changes |
| `CODE_REVIEW.md` | Technical review | Document major changes |
| `requirements.txt` | Dependencies | New package dependencies |

---

## Architecture & Core Concepts

### High-Level Architecture

```
Input: High-D Embeddings (N, D)
    ↓
[1] Build k-NN Graph → Fuzzy Simplicial Set (COO format)
    ↓
[2] Parametric UMAP Encoder → Low-D Embeddings (N, d)
    ↓
[3] Multi-Objective Training:
    - L_umap: Preserve topology
    - L_align: Align relation difference vectors
    - L_ortho: Disentangle relation axes
    ↓
[4] Extract Relation Axes → Direction + Scale
    ↓
Output: Analogy Function (query + relation → target)
```

### Core Components

#### 1. Fuzzy Simplicial Set Construction
**Location**: Lines 53-180 in `umap_analogy_engine.py`

- Builds k-NN graph with adaptive bandwidths (sigma)
- Uses binary search for perplexity-based calibration
- Symmetrizes using fuzzy union: P(A∪B) = P(A) + P(B) - P(A)·P(B)
- Returns COO format (edges_i, edges_j, weights)

**Key Functions**:
- `smooth_knn_dist()`: Binary search for sigma
- `build_fuzzy_simplicial_set()`: Main graph construction

#### 2. Parametric UMAP Encoder
**Location**: Lines 183-210 in `umap_analogy_engine.py`

Deep neural network mapping X_high → Z_low:
- Input: D-dimensional embeddings
- Hidden: [512, 256, 128] with LayerNorm + ReLU + Dropout
- Output: d-dimensional (default d=2)

**Architecture**:
```python
ParametricUMAPEncoder(
    d_in=D,              # Input dimension
    d_out=d_low,         # Output dimension (default 2)
    hidden_dims=[512, 256, 128],
    dropout_p=0.10
)
```

#### 3. Loss Functions

**a) UMAP Cross-Entropy Loss** (Lines 213-263)
- Attractive term: -log(sigmoid(1 - ||z_i - z_j||²))
- Repulsive term: -log(1 - sigmoid(1 - ||z_i - z_neg||²))
- Preserves topological structure

**b) Relation Alignment Loss** (Lines 266-380)
- Clusters difference vectors per relation
- Direction loss: 1 - cosine_similarity(v_i, centroid)
- Length loss: Huber(||v_i||, median_length)
- Uses differentiable k-means with temperature

**c) Orthogonality Penalty** (Lines 383-426)
- Penalizes correlation between relation axes
- Gram matrix approach: ||V^T V - I||²
- Keeps different relations disentangled

#### 4. Training Loop
**Location**: Lines 474-716 in `umap_analogy_engine.py`

Key features:
- **Cluster caching**: Updates every N steps (10x speedup)
- **Auto-alignment**: Balances loss weights via gradient matching
- **Mixed precision**: Automatic mixed precision training (AMP)
- **Edge batching**: Processes graph in batches for memory efficiency

#### 5. Analogy API
**Location**: Lines 719-878 in `umap_analogy_engine.py`

Public functions:
- `extract_relation_axes()`: Extract relation directions from trained model
- `find_analogy()`: Apply relation to query word
- `analogy_from_pair()`: Infer relation from example pair

---

## Development Workflow

### Setting Up the Environment

```bash
# Clone repository
git clone <repo-url>
cd ClaudeCodeFrameWork

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Demo

```bash
# Run synthetic example
python umap_analogy_engine.py

# Expected output:
# - Graph construction (5-10 seconds)
# - Training progress (200-400 epochs)
# - Relation statistics
# - Analogy test results
```

### Testing with Real Embeddings

```bash
# Download GloVe embeddings first
# wget http://nlp.stanford.edu/data/glove.6B.zip
# unzip glove.6B.zip

python example_word_analogies.py
```

### Development Cycle

1. **Make Changes**: Edit `umap_analogy_engine.py`
2. **Test Locally**: Run demo script
3. **Validate**: Check loss convergence and analogy results
4. **Document**: Update docstrings and comments
5. **Commit**: Use descriptive commit messages

---

## Key Conventions

### Code Style

1. **Naming Conventions**:
   - Functions: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private variables: `_leading_underscore`

2. **Documentation**:
   - All public functions have comprehensive docstrings
   - Docstring format: Google style (Args, Returns, Raises)
   - Inline comments for complex logic

3. **Type Hints**:
   - Use type hints for all function signatures
   - Import types from `typing` module
   - Example: `def foo(x: torch.Tensor, k: int = 5) -> List[Tuple[int, float]]`

### Mathematical Conventions

- **Tensors**:
  - `X_high`: High-dimensional embeddings (N, D)
  - `Z` or `Z_low`: Low-dimensional embeddings (N, d)
  - `pairs`: Relation pairs (M, 2) with indices

- **Indices**:
  - `i, j`: Sample indices
  - `r`: Relation index
  - `k`: Number of neighbors or top-k results

- **Dimensions**:
  - `N`: Number of samples
  - `D`: High-dimensional space dimension
  - `d` or `d_low`: Low-dimensional space dimension
  - `M`: Number of pairs

### Hyperparameter Defaults

**UMAP Parameters**:
```python
N_NEIGHBORS = 15      # k-NN graph connectivity
MIN_DIST = 0.1        # Minimum distance in low-D
SPREAD = 1.0          # Spread of points in low-D
D_LOW = 2             # Low-dimensional space size
```

**Training Parameters**:
```python
EPOCHS = 400          # Training epochs
EDGE_BS = 20000       # Edge batch size
LR = 1e-3             # Learning rate
NEG_RATIO = 5         # Negative samples per positive
```

**Loss Weights**:
```python
ALIGN_W = 1.0         # Relation alignment weight (auto-calibrated)
ORTHO_W = 0.1         # Orthogonality penalty weight
UMAP_REP_W = 1.0      # UMAP repulsion strength
```

**When to Change Defaults**:
- `N_NEIGHBORS`: Increase for denser graphs, decrease for sparser
- `EPOCHS`: Increase for better convergence, decrease for faster testing
- `D_LOW`: Typically 2-10; higher for complex relationships
- `ALIGN_W`: Use `AUTO_ALIGN="once"` to calibrate automatically

---

## Testing & Validation

### What to Check After Changes

1. **Loss Convergence**:
   - All losses should decrease smoothly
   - No NaN or Inf values
   - L_umap should converge to ~0.1-0.5
   - L_align should converge to ~0.01-0.1

2. **Relation Statistics**:
   - `mean_direction_cos > 0.7` indicates well-aligned relations
   - `std_length < 0.5 * mean_length` indicates consistent relations

3. **Analogy Results**:
   - Top-k results should be semantically meaningful
   - Scores should be positive and ordered correctly

4. **Performance**:
   - Training should complete in reasonable time (~5-10 min for N=10k)
   - Memory usage should be stable

### Synthetic Test (Built-in)

Run the demo at the end of `umap_analogy_engine.py`:
```python
if __name__ == "__main__":
    # Tests with 2000 synthetic embeddings
    # 2 relations with 30 pairs each
```

### Real-World Test

Use `example_word_analogies.py` with actual embeddings:
- Tests standard analogies: king:queen, man:woman, etc.
- Measures accuracy on held-out test sets

### Numerical Stability Checks

```python
# Check for NaN/Inf in tensors
assert torch.isfinite(loss).all(), "Loss contains NaN/Inf"

# Check gradient norms
grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
assert grad_norm < 100.0, f"Gradient explosion: {grad_norm}"
```

---

## Common Tasks for AI Assistants

### Task 1: Add a New Hyperparameter

**Example**: Add temperature control for k-means clustering

1. Add constant at top of file:
```python
KMEANS_TEMPERATURE = 0.5  # Softmax temperature
```

2. Update function signature:
```python
def differentiable_kmeans(
    X: torch.Tensor,
    k: int,
    n_iter: int = 50,
    temperature: float = 0.5,  # NEW PARAMETER
) -> Tuple[torch.Tensor, torch.Tensor]:
```

3. Update docstring with parameter description
4. Update all call sites
5. Document in README.md Configuration section

### Task 2: Fix a Bug

**Follow this process**:

1. **Reproduce**: Ensure you can reproduce the bug
2. **Locate**: Use grep/search to find relevant code
3. **Understand**: Read surrounding context (50-100 lines)
4. **Fix**: Make minimal changes to fix the issue
5. **Test**: Run demo and validate fix
6. **Document**: Add comment explaining the fix
7. **Update**: If critical, mention in CODE_REVIEW.md

**Example Locations**:
- Numerical issues → Check epsilon values and clamping
- Graph construction → Check `build_fuzzy_simplicial_set()`
- Training divergence → Check loss computation and gradient flow
- Analogy errors → Check `find_analogy()` metric selection

### Task 3: Optimize Performance

**Key Optimization Areas**:

1. **Cluster Caching**: Already implemented
   - Controlled by `KMEANS_UPDATE_FREQ` (default: 10)
   - Trade-off: accuracy vs speed

2. **FAISS for Large N**: For N > 100k
   ```python
   import faiss
   # Replace torch.cdist with FAISS IndexFlatL2
   ```

3. **Gradient Checkpointing**: For memory constraints
   ```python
   from torch.utils.checkpoint import checkpoint
   ```

4. **Data Parallel**: For multi-GPU
   ```python
   model = nn.DataParallel(model)
   ```

### Task 4: Add a New Feature

**Example**: Add cosine metric support for graph construction

1. **Plan**: Decide where feature fits (which function/class)
2. **Implement**: Add code with proper type hints
3. **Document**: Add comprehensive docstring
4. **Test**: Create test case in demo
5. **Integrate**: Update training loop and API functions
6. **Update Docs**: Add to README.md and this file

### Task 5: Debug Training Issues

**Common Issues & Solutions**:

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Loss = NaN | Numerical instability | Check epsilon values, clamping |
| Loss not decreasing | Learning rate too low | Increase LR or epochs |
| Loss exploding | Learning rate too high | Decrease LR, use gradient clipping |
| Poor analogies | Metric mismatch | Use Euclidean distance for absolute positions |
| Out of memory | Batch size too large | Reduce EDGE_BS |
| Slow training | Cluster recomputation | Increase KMEANS_UPDATE_FREQ |

---

## Critical Considerations

### 🚨 Critical Bugs That Were Fixed (DO NOT Reintroduce!)

1. **Metric Mismatch** (Lines 719-878):
   - MUST use Euclidean distance for analogy finding
   - Cosine similarity ignores magnitude → incorrect results
   - See CODE_REVIEW.md Section 1 for details

2. **Gradient Computation** (Lines 600-650):
   - Auto-alignment must use separate forward pass
   - Don't compute gradients inside training loop
   - Use calibration pass before training

3. **Epsilon Values** (Line 47):
   - Use `EPS = 1e-8` (not 1e-12)
   - Prevents underflow on GPU
   - Critical for numerical stability

4. **Device Handling** (Lines 383-426):
   - Always use `torch.device` objects (not strings)
   - Check device before creating tensors

### 🔒 Code Sections to Be Careful With

1. **Fuzzy Set Construction** (Lines 53-180):
   - Mathematical formula is correct, don't change without deep understanding
   - Fuzzy union: `w_sym = w_ij + w_ji - w_ij * w_ji`

2. **Loss Functions** (Lines 213-426):
   - Loss weights are carefully balanced
   - Use `AUTO_ALIGN` to calibrate automatically
   - Don't change formulas without mathematical justification

3. **Cluster Caching** (Lines 474-716):
   - Complex logic for performance optimization
   - Modify with care, test thoroughly

4. **Analogy Finding** (Lines 719-878):
   - Metric selection is critical (Euclidean vs cosine)
   - Default to Euclidean for correct results

### ⚡ Performance-Critical Sections

1. **Graph Construction**: O(N²) without FAISS
2. **K-means Clustering**: O(k × M × n_iter) per update
3. **Edge Batching**: Process in chunks to avoid OOM

### 🔐 Security Considerations

This is a research/ML codebase with no external input handling:
- No user input validation needed
- No network operations
- File I/O limited to loading embeddings

**When adding features**:
- Be cautious with `pickle` (use `torch.load` with `weights_only=True` for PyTorch 2.0+)
- Validate embedding file formats before loading
- Check tensor shapes before operations

---

## Git Workflow

### Branch Naming Convention

- Feature branches: `feature/<description>`
- Bug fixes: `fix/<issue-description>`
- AI assistant branches: `claude/<session-id>`

### Commit Message Format

```
<type>: <short summary> (50 chars max)

<optional detailed description>

<optional footer: issue references, breaking changes>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `perf`: Performance improvement
- `docs`: Documentation updates
- `refactor`: Code refactoring (no behavior change)
- `test`: Test additions or updates
- `chore`: Maintenance tasks

**Examples**:
```
feat: Add FAISS support for large-scale k-NN search

Integrates FAISS IndexFlatL2 for datasets with N > 100k samples.
Provides 10-100x speedup for graph construction.

fix: Correct metric in find_analogy() from cosine to Euclidean

Critical bug fix. Cosine similarity ignores magnitude, causing
incorrect analogy results. See CODE_REVIEW.md Section 1.

perf: Implement cluster caching with configurable update frequency

Reduces training time by 10x by reusing k-means clusters across
steps. Controlled by KMEANS_UPDATE_FREQ parameter.
```

### Before Committing

1. **Test**: Run demo script successfully
2. **Format**: Ensure code follows conventions
3. **Document**: Update docstrings and comments
4. **Review**: Check diff for unintended changes

### Pushing Changes

```bash
# Check current branch
git status

# Stage changes
git add <files>

# Commit with descriptive message
git commit -m "feat: Add new feature description"

# Push to feature branch
git push -u origin <branch-name>
```

---

## Troubleshooting

### Installation Issues

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
1. Check Python version: `python --version` (need 3.8+)
2. Update pip: `pip install --upgrade pip`
3. Install PyTorch separately: Visit pytorch.org for platform-specific command
4. Check CUDA version if using GPU: `nvidia-smi`

### Runtime Errors

**Problem**: "RuntimeError: CUDA out of memory"

**Solutions**:
1. Reduce `EDGE_BS` (default 20000 → try 10000 or 5000)
2. Reduce `N_NEIGHBORS` (default 15 → try 10)
3. Use CPU instead: Set `device = torch.device("cpu")`
4. Enable gradient checkpointing (advanced)

**Problem**: "AssertionError: Pair indices out of bounds"

**Solutions**:
1. Check that pair indices are in range [0, N)
2. Validate embeddings are not empty: `X_high.size(0) > 0`
3. Check pair tensor dimensions: `pairs.size(1) == 2`

**Problem**: Loss is NaN or Inf

**Solutions**:
1. Check `EPS` value (should be 1e-8)
2. Reduce learning rate: `LR = 1e-4`
3. Enable gradient clipping in training loop
4. Check for extreme values in embeddings: `X_high.abs().max()`

### Performance Issues

**Problem**: Training is very slow

**Solutions**:
1. Enable AMP: `USE_AMP = True`
2. Increase cluster update frequency: `KMEANS_UPDATE_FREQ = 20`
3. Reduce epochs for testing: `EPOCHS = 100`
4. Use GPU if available
5. For large N (>100k), implement FAISS (see CODE_REVIEW.md)

**Problem**: Poor analogy results

**Solutions**:
1. Check metric: Must use `metric="euclidean"` in `find_analogy()`
2. Increase training epochs: `EPOCHS = 500`
3. Increase alignment weight: `ALIGN_W = 2.0` or enable `AUTO_ALIGN`
4. Add more training pairs per relation
5. Check relation statistics: `mean_direction_cos` should be > 0.7

### Getting Help

1. **Read CODE_REVIEW.md**: Detailed explanation of fixes and issues
2. **Check README.md**: User-facing documentation and API reference
3. **Search code**: Use grep to find relevant functions
4. **Print debug info**: Add logging to training loop
5. **Visualize embeddings**: Plot low-D embeddings to inspect structure

---

## Quick Reference

### Essential File Locations

| Task | File | Lines |
|------|------|-------|
| Modify graph construction | `umap_analogy_engine.py` | 53-180 |
| Change model architecture | `umap_analogy_engine.py` | 183-210 |
| Adjust loss functions | `umap_analogy_engine.py` | 213-426 |
| Modify training loop | `umap_analogy_engine.py` | 474-716 |
| Update analogy API | `umap_analogy_engine.py` | 719-878 |
| Add example usage | `example_word_analogies.py` | Entire file |

### Essential Functions

| Function | Purpose | Location |
|----------|---------|----------|
| `build_fuzzy_simplicial_set()` | Construct k-NN graph | Line 113 |
| `ParametricUMAPEncoder` | Define model architecture | Line 183 |
| `umap_cross_entropy_loss()` | Compute UMAP loss | Line 213 |
| `relation_alignment_loss()` | Compute alignment loss | Line 266 |
| `train_relation_aware_umap()` | Main training function | Line 474 |
| `extract_relation_axes()` | Extract relation directions | Line 719 |
| `find_analogy()` | Perform analogy query | Line 788 |
| `analogy_from_pair()` | Infer relation from pair | Line 838 |

### Essential Commands

```bash
# Run demo
python umap_analogy_engine.py

# Run with real embeddings
python example_word_analogies.py

# Check code structure
head -n 50 umap_analogy_engine.py

# Search for function
grep -n "def find_analogy" umap_analogy_engine.py

# View recent changes
git log --oneline -10

# Check current branch
git status
```

---

## Roadmap

### Phase 1: Foundation (✅ Completed)
- Parametric UMAP implementation
- Multi-relation alignment
- Analogy finding API
- Performance optimizations

### Phase 2: Inverse Projection (Planned)
- Inverse parametric model (Z_low → X_high)
- Riemannian manifold reconstruction
- Relation simplex aggregation
- High-dimensional analogy prediction

### Phase 3: Advanced Features (Future)
- Automatic relation discovery
- Hierarchical relations
- Compositional analogies (multi-hop)
- Interactive visualization
- FAISS integration for scaling

---

## Contact & Resources

- **Repository**: `ClaudeCodeFrameWork`
- **Documentation**: `README.md` (user guide), `CODE_REVIEW.md` (technical review)
- **References**:
  - UMAP paper: McInnes et al. (2018) arXiv:1802.03426
  - Word analogies: Mikolov et al. (2013) NAACL-HLT

---

**Remember**: This codebase is production-ready but actively evolving. When making changes:
1. ✅ Read relevant documentation first
2. ✅ Test thoroughly with demo scripts
3. ✅ Document changes in code and commit messages
4. ✅ Preserve numerical stability and performance optimizations
5. ✅ Don't reintroduce fixed bugs (especially metric mismatch!)

Good luck developing the UMAP Analogy Engine! 🚀
