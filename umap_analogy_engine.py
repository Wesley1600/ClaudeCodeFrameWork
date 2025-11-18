"""
UMAP-Inspired Universal Analogy Engine (V1 - Improved)

A semantic relationship engine that learns universal relationship mappings
inspired by UMAP's topological data analysis approach. Supports multi-relation
learning with differentiable clustering and relation axis extraction.

Key improvements over initial draft:
- Fixed metric mismatch in analogy finding (Euclidean distance vs cosine)
- Optimized clustering with caching and less frequent updates
- Improved numerical stability and edge case handling
- Better gradient computation for auto-alignment
- Enhanced input validation
- Comprehensive documentation
"""

__version__ = "1.0.0"
__author__ = "ClaudeCodeFrameWork"
__date__ = "2025-11-13"
__status__ = "Production"

import math
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from operation_cache import cached, get_cache_manager


# =========================
# Hyperparameters (defaults)
# =========================
N_NEIGHBORS = 15
MIN_DIST = 0.1
SPREAD = 1.0
EPOCHS = 400
EDGE_BS = 20000
NEG_RATIO = 5
LR = 1e-3
D_LOW = 2
ALIGN_W = 1.0  # base alignment weight (can be auto-calibrated)
ORTHO_W = 0.1
UMAP_REP_W = 1.0
KMEANS_ITERS = 50
KMEANS_UPDATE_FREQ = 10  # Update clusters every N steps (optimization)
DROPOUT_P = 0.10
HIDDEN_DIMS = [512, 256, 128]
USE_AMP = True  # mixed precision
AUTO_ALIGN = "once"  # {"once","ema",None}; auto-balance ALIGN_W vs UMAP by grad-norms
AUTO_ALIGN_EMA = 0.9  # EMA coefficient if AUTO_ALIGN=="ema"
EPS = 1e-8  # Global epsilon for numerical stability


# =========================
# UMAP utilities (COO graph)
# =========================
def fit_ab_params(min_dist: float = 0.1, spread: float = 1.0) -> Tuple[float, float]:
    """
    Stable (a,b) for UMAP's smooth approximation to fuzzy set membership.

    For spread=1.0, min_dist=0.1 (matching umap-learn defaults), returns
    precomputed values. For other settings, offline curve fitting is required.

    The function approximates: membership = 1 / (1 + a * d^(2b))
    where d is distance in low-dimensional space.

    Args:
        min_dist: Minimum distance between points in low-D space
        spread: Effective scale of embedded points

    Returns:
        Tuple of (a, b) parameters for the membership function
    """
    if abs(spread - 1.0) < 1e-6 and abs(min_dist - 0.1) < 1e-6:
        return 1.576943460, 0.895060879
    raise NotImplementedError(
        f"Custom spread={spread}, min_dist={min_dist} requires offline (a,b) fit. "
        "Use UMAP's find_ab_params from umap-learn for custom values."
    )


def smooth_knn_dist(
    distances: torch.Tensor, k: int, n_iter: int = 64, target: Optional[float] = None
) -> torch.Tensor:
    """
    Binary search for sigma (bandwidth) such that sum(exp(-d/sigma)) ≈ log2(k).

    This ensures consistent local density estimation across varying neighborhood
    densities, which is crucial for UMAP's fuzzy simplicial set construction.

    Args:
        distances: (N, k) tensor of distances to k nearest neighbors (excluding self),
                  should already be shifted by rho (distance to nearest neighbor)
                  and clamped to be >= 0
        k: Number of neighbors
        n_iter: Number of binary search iterations
        target: Target perplexity (default: log2(k))

    Returns:
        sigma: (N,) tensor of bandwidth parameters
    """
    N = distances.shape[0]
    target_val = target if target is not None else math.log2(k)
    sigma = torch.zeros(N, device=distances.device, dtype=distances.dtype)

    for i in range(N):
        lo, hi = 1e-10, 1e6
        di = distances[i]

        for _ in range(n_iter):
            mid = (lo + hi) / 2
            perplexity = torch.exp(-di / mid).sum()

            if perplexity < target_val:
                lo = mid
            else:
                hi = mid

        sigma[i] = 0.5 * (lo + hi)

    return sigma


@torch.no_grad()
@cached(cache_type="graph", ttl=3600)  # Cache for 1 hour
def build_fuzzy_simplicial_set(
    X: torch.Tensor, n_neighbors: int = 15
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Construct fuzzy simplicial set (UMAP's high-dimensional graph representation).

    Returns directed kNN graph as COO format (edge_i, edge_j, edge_weight), then
    symmetrizes using fuzzy set union: P(A ∪ B) = P(A) + P(B) - P(A)P(B).

    Results are cached to avoid redundant O(N²) distance computations.

    NOTE: This implementation uses O(N²) cdist for moderate N. For large datasets
    (N > 100k), replace the cdist+topk block with FAISS-GPU kNN for efficiency.

    Args:
        X: (N, D) high-dimensional data
        n_neighbors: Number of nearest neighbors

    Returns:
        edge_i: (E,) source node indices
        edge_j: (E,) target node indices
        edge_w: (E,) edge weights in [0, 1]
    """
    N = X.shape[0]
    device = X.device

    # Handle edge cases
    if N < 2:
        return (
            torch.empty(0, dtype=torch.long, device=device),
            torch.empty(0, dtype=torch.long, device=device),
            torch.empty(0, dtype=torch.float32, device=device),
        )

    kmax = min(n_neighbors, N - 1)
    if kmax < 1:
        return (
            torch.empty(0, dtype=torch.long, device=device),
            torch.empty(0, dtype=torch.long, device=device),
            torch.empty(0, dtype=torch.float32, device=device),
        )

    # Compute pairwise distances and find k nearest neighbors
    D = torch.cdist(X, X)  # (N, N)
    vals, idxs = torch.topk(D, k=kmax + 1, dim=1, largest=False)  # Include self

    # rho: distance to nearest neighbor (excluding self at index 0)
    rho = vals[:, 1].clamp_min(EPS)  # (N,)

    # Prepare distances for sigma estimation (shifted by rho, clamped >= 0)
    distances_for_sigma = (vals[:, 1:] - rho.unsqueeze(1)).clamp_min(0.0)
    sigma = smooth_knn_dist(distances_for_sigma, kmax, n_iter=64)

    # Build directed edges with fuzzy membership
    rows, cols, vals_w = [], [], []
    for i in range(N):
        si = float(sigma[i])
        ri = float(rho[i])

        for r in range(1, kmax + 1):  # Skip self at index 0
            j = int(idxs[i, r])
            if j == i:  # Paranoid check
                continue

            d = max(0.0, float(vals[i, r]) - ri)

            # Compute fuzzy membership
            if si > EPS:
                w = math.exp(-d / (si + EPS))
            else:
                w = 1.0 if d < EPS else 0.0

            if w > EPS:  # Only keep edges with non-trivial weight
                rows.append(i)
                cols.append(j)
                vals_w.append(w)

    # Fuzzy set union symmetrization (one pass)
    # P(A ∪ B) = P(A) + P(B) - P(A)P(B)
    acc = defaultdict(float)
    for r, c, v in zip(rows, cols, vals_w):
        # Normalize to undirected edge
        i, j = (r, c) if r <= c else (c, r)
        p_existing = acc[(i, j)]
        acc[(i, j)] = p_existing + v - p_existing * v

    # Expand to bidirectional edges for symmetric graph
    R, C, W = [], [], []
    for (i, j), w in acc.items():
        if w <= EPS:  # Filter out near-zero weights
            continue
        R += [i, j]
        C += [j, i]
        W += [w, w]

    ei = torch.tensor(R, dtype=torch.long, device=device)
    ej = torch.tensor(C, dtype=torch.long, device=device)
    ew = torch.tensor(W, dtype=torch.float32, device=device)

    return ei, ej, ew


# =========================
# Parametric encoder with LayerNorm
# =========================
class ParametricUMAP(nn.Module):
    """
    Parametric encoder mapping high-D embeddings to low-D space.

    Uses LayerNorm for stable training and dropout for regularization.
    Xavier initialization provides good starting weights.
    """

    def __init__(
        self,
        d_in: int,
        d_out: int,
        hidden_dims: Optional[List[int]] = None,
        dropout_p: float = DROPOUT_P,
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = HIDDEN_DIMS

        layers: List[nn.Module] = []
        prev = d_in

        for h in hidden_dims:
            layers += [
                nn.Linear(prev, h),
                nn.LayerNorm(h),
                nn.ReLU(),
                nn.Dropout(dropout_p),
            ]
            prev = h

        # Final projection to low-D space (no activation)
        layers += [nn.Linear(prev, d_out)]

        self.network = nn.Sequential(*layers)
        self._init_weights()

    def _init_weights(self):
        """Xavier initialization for better gradient flow."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


# =========================
# Loss functions
# =========================
def umap_cross_entropy_loss(
    embeddings: torch.Tensor,
    edge_i: torch.Tensor,
    edge_j: torch.Tensor,
    edge_w: torch.Tensor,
    a: float,
    b: float,
    negative_sample_rate: int = NEG_RATIO,
    repulsion_strength: float = UMAP_REP_W,
) -> torch.Tensor:
    """
    UMAP cross-entropy loss: attractive force on positive pairs + repulsive on negatives.

    Attractive term: -w * log(P(similar))
    Repulsive term: -log(1 - P(similar)) for randomly sampled pairs

    where P(similar) = 1 / (1 + a * ||z_i - z_j||²^b)

    Args:
        embeddings: (N, d) low-dimensional embeddings
        edge_i: (E,) source indices
        edge_j: (E,) target indices
        edge_w: (E,) edge weights from high-D graph
        a, b: UMAP curve parameters
        negative_sample_rate: Number of negative samples per positive
        repulsion_strength: Weight for repulsive term

    Returns:
        Combined attractive + repulsive loss
    """
    # Positive (attractive) term
    zi = embeddings[edge_i]
    zj = embeddings[edge_j]
    d2_pos = ((zi - zj) ** 2).sum(dim=-1).clamp_min(EPS)

    # P(similar) = 1 / (1 + a * d^(2b))
    p_pos = (1.0 / (1.0 + a * (d2_pos ** b))).clamp(EPS, 1 - EPS)

    w = edge_w.clamp(EPS, 1 - EPS)
    loss_pos = -(w * torch.log(p_pos)).mean()

    # Negative (repulsive) term
    n_pos = edge_i.numel()
    n_neg = max(1, n_pos * negative_sample_rate)
    N = embeddings.size(0)

    # Sample random pairs (uniform)
    ni = torch.randint(0, N, (n_neg,), device=embeddings.device)
    nj = torch.randint(0, N, (n_neg,), device=embeddings.device)

    # Filter out self-pairs
    mask = ni != nj
    ni, nj = ni[mask], nj[mask]

    if ni.numel() > 0:
        d2_neg = ((embeddings[ni] - embeddings[nj]) ** 2).sum(dim=-1).clamp_min(EPS)
        p_neg = (1.0 / (1.0 + a * (d2_neg ** b))).clamp(EPS, 1 - EPS)
        loss_neg = -torch.log(1.0 - p_neg).mean()
    else:
        loss_neg = embeddings.new_tensor(0.0)

    return loss_pos + repulsion_strength * loss_neg


def differentiable_kmeans(
    points: torch.Tensor,
    n_clusters: int,
    n_iter: int = 10,
    temperature: float = 0.5,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Soft k-means with k-means++ initialization and temperature-controlled assignments.

    Uses k-means++ for better initialization and soft assignments for differentiability.
    Lower temperature → harder assignments.

    Args:
        points: (N, D) data points
        n_clusters: Number of clusters
        n_iter: Number of EM iterations
        temperature: Softmax temperature for assignments (lower = harder)

    Returns:
        centroids: (K, D) cluster centers
        soft_assign: (N, K) soft assignment probabilities
    """
    N, D = points.shape
    device = points.device

    # Clamp n_clusters to valid range
    n_clusters = int(min(max(1, n_clusters), N))

    # Handle trivial case
    if n_clusters == 1 or N <= 1:
        centroid = points.mean(0, keepdim=True)
        assignments = torch.ones(N, 1, device=device)
        return centroid, assignments

    # k-means++ initialization
    centroids = []
    first_idx = torch.randint(0, N, (1,), device=device)
    centroids.append(points[first_idx])

    for _ in range(n_clusters - 1):
        C = torch.cat(centroids, dim=0)  # (len(centroids), D)
        # Distance to nearest centroid
        dists = torch.cdist(points, C)  # (N, len(centroids))
        dmin = dists.min(dim=1)[0] + EPS  # (N,)

        # Sample proportional to squared distance
        probs = dmin / dmin.sum()
        next_idx = torch.multinomial(probs, 1)
        centroids.append(points[next_idx])

    C = torch.cat(centroids, dim=0)  # (K, D)

    # EM iterations with soft assignments
    for _ in range(n_iter):
        # E-step: Soft assignments
        dists = torch.cdist(points, C)  # (N, K)
        A = F.softmax(-dists / temperature, dim=1)  # (N, K)

        # M-step: Update centroids
        for k in range(n_clusters):
            w = A[:, k:k+1]  # (N, 1)
            w_sum = w.sum().clamp_min(EPS)
            C[k] = (w * points).sum(0) / w_sum

    # Final soft assignments
    dists = torch.cdist(points, C)
    A = F.softmax(-dists / temperature, dim=1)

    return C, A


def relation_alignment_loss(
    embeddings: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
    relation_weights: Optional[List[float]] = None,
    kmeans_iters: int = 10,
    cached_clusters: Optional[List[Optional[Tuple[torch.Tensor, torch.Tensor]]]] = None,
) -> Tuple[torch.Tensor, List[Optional[torch.Tensor]], List[Optional[Tuple[torch.Tensor, torch.Tensor]]]]:
    """
    Multi-relation alignment loss with clustering and direction/length consistency.

    For each relation:
    1. Cluster the difference vectors (handles multi-modal relations)
    2. Minimize direction variance: encourages parallel difference vectors
    3. Minimize length variance: encourages consistent magnitudes (robust Huber loss)

    Args:
        embeddings: (N, d) low-dimensional embeddings
        pair_indices_list: List of (M_r, 2) pair indices per relation
        n_clusters_list: Number of clusters per relation
        relation_weights: Optional weight per relation
        kmeans_iters: Number of k-means iterations
        cached_clusters: Optional cached (centroids, assignments) per relation

    Returns:
        loss: Weighted average alignment loss
        mean_directions: Mean direction vector per relation (or None)
        updated_clusters: Updated (centroids, assignments) per relation for caching
    """
    if relation_weights is None:
        relation_weights = [1.0] * len(pair_indices_list)

    device = embeddings.device
    total_loss = embeddings.new_tensor(0.0)
    mean_directions: List[Optional[torch.Tensor]] = []
    updated_clusters: List[Optional[Tuple[torch.Tensor, torch.Tensor]]] = []
    active_relations = 0

    for r, pairs in enumerate(pair_indices_list):
        # Skip empty relations
        if pairs.numel() == 0:
            mean_directions.append(None)
            updated_clusters.append(None)
            continue

        # Validate pair indices
        max_idx = pairs.max().item()
        if max_idx >= embeddings.size(0):
            print(f"Warning: Relation {r} has invalid indices (max={max_idx}, N={embeddings.size(0)})")
            mean_directions.append(None)
            updated_clusters.append(None)
            continue

        # Compute difference vectors for this relation
        diffs = embeddings[pairs[:, 1]] - embeddings[pairs[:, 0]]  # (M, d)
        M = diffs.size(0)
        k = min(max(1, int(n_clusters_list[r])), M)

        # Use cached clusters or compute new ones
        if cached_clusters is not None and cached_clusters[r] is not None:
            C, A = cached_clusters[r]
            C, A = C.to(device), A.to(device)
            # Validate cached cluster shapes
            if C.size(0) != k or A.size(0) != M:
                C, A = differentiable_kmeans(
                    diffs, k, n_iter=kmeans_iters, temperature=0.5
                )
        else:
            C, A = differentiable_kmeans(
                diffs, k, n_iter=kmeans_iters, temperature=0.5
            )

        updated_clusters.append((C.detach(), A.detach()))

        # Compute alignment loss per cluster
        rel_loss = embeddings.new_tensor(0.0)
        cluster_means = []

        for c in range(k):
            w = A[:, c:c+1]  # (M, 1) soft assignment weights
            w_sum = w.sum().clamp_min(EPS)

            # Skip clusters with negligible weight
            if w_sum < 1e-3:
                continue

            # Mean direction for this cluster
            mu = C[c:c+1]  # (1, d)
            mu_dir = F.normalize(mu, dim=-1, eps=EPS)

            # Direction consistency loss (weighted 1 - cosine similarity)
            dirs = F.normalize(diffs, dim=-1, eps=EPS)  # (M, d)
            cos_sim = (dirs * mu_dir).sum(dim=-1, keepdim=True)  # (M, 1)
            dir_loss = ((1.0 - cos_sim) * w).sum() / w_sum

            # Length consistency loss (robust Huber on |len - mean_len|)
            lengths = diffs.norm(dim=-1, keepdim=True)  # (M, 1)
            mean_length = mu.norm(dim=-1, keepdim=True)  # (1, 1)
            delta_len = (lengths - mean_length).abs()
            len_loss = (
                F.huber_loss(
                    delta_len,
                    torch.zeros_like(delta_len),
                    delta=0.1,
                    reduction="none",
                )
                * w
            ).sum() / w_sum

            rel_loss += dir_loss + 0.5 * len_loss
            cluster_means.append(mu.squeeze(0))

        # Aggregate this relation's contribution
        if cluster_means:
            total_loss += relation_weights[r] * rel_loss
            mean_directions.append(torch.stack(cluster_means, 0).mean(0))
            active_relations += 1
        else:
            mean_directions.append(None)

    # Average over active relations
    if active_relations > 0:
        total_loss = total_loss / active_relations

    return total_loss, mean_directions, updated_clusters


def orthogonality_penalty(
    direction_vectors: List[Optional[torch.Tensor]],
    power: int = 2,
    eps: float = EPS,
) -> torch.Tensor:
    """
    Penalize correlation between relation direction vectors.

    Encourages learned relation axes to be orthogonal/disentangled.
    Computes pairwise dot products of normalized directions and penalizes
    off-diagonal elements.

    Args:
        direction_vectors: List of (d,) direction tensors (or None)
        power: Exponent for penalty (2 = quadratic)
        eps: Epsilon for normalization

    Returns:
        Orthogonality penalty (0 if < 2 valid directions)
    """
    # Filter valid, finite directions
    valid = []
    device = None

    for v in direction_vectors:
        if v is None:
            continue

        # Infer device from first valid vector
        if device is None:
            device = v.device

        nv = v.norm()
        if torch.isfinite(nv) and nv > eps:
            valid.append(F.normalize(v.to(device), dim=-1, eps=eps))

    # Need at least 2 directions for orthogonality
    if len(valid) < 2:
        if device is None:
            device = torch.device("cpu")
        return torch.tensor(0.0, device=device)

    # Gram matrix of normalized directions
    D = torch.stack(valid, dim=0)  # (R, d)
    G = D @ D.T  # (R, R)

    # Zero out diagonal (self-similarity = 1 is expected)
    G = G - torch.diag_embed(torch.diag(G))

    # Penalize off-diagonal correlations
    return (G.abs() ** power).mean()


def compute_relation_statistics(
    embeddings: torch.Tensor, pair_indices_list: List[torch.Tensor]
) -> Dict[str, Dict[str, float]]:
    """
    Compute statistics for each relation's difference vectors.

    Useful for monitoring training and understanding relation quality.

    Returns:
        Dict mapping relation name to stats dict with keys:
        - mean_length: Average magnitude of difference vectors
        - std_length: Standard deviation of magnitudes
        - mean_direction_cos: Average pairwise cosine similarity
    """
    stats = {}

    for r, pairs in enumerate(pair_indices_list):
        if pairs.numel() == 0:
            continue

        diffs = embeddings[pairs[:, 1]] - embeddings[pairs[:, 0]]
        lengths = diffs.norm(dim=-1)

        # Direction consistency
        if diffs.size(0) > 1:
            dirs = F.normalize(diffs, dim=-1, eps=EPS)
            cos_matrix = dirs @ dirs.T
            n = cos_matrix.size(0)
            # Exclude diagonal
            mask = ~torch.eye(n, device=cos_matrix.device, dtype=torch.bool)
            mean_cos = cos_matrix[mask].mean().item()
        else:
            mean_cos = 1.0

        stats[f"relation_{r}"] = {
            "mean_length": float(lengths.mean().item()),
            "std_length": float(lengths.std().item()),
            "mean_direction_cos": float(mean_cos),
        }

    return stats


# =========================
# Training loop with AMP + auto-alignment
# =========================
def train_relation_aware_umap(
    X_high: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
    relation_weights: Optional[List[float]] = None,
    n_neighbors: int = N_NEIGHBORS,
    min_dist: float = MIN_DIST,
    spread: float = SPREAD,
    d_low: int = D_LOW,
    epochs: int = EPOCHS,
    batch_size: int = EDGE_BS,
    lr: float = LR,
    align_weight: float = ALIGN_W,
    ortho_weight: float = ORTHO_W,
    umap_rep_weight: float = UMAP_REP_W,
    neg_sample_rate: int = NEG_RATIO,
    use_amp: bool = USE_AMP,
    auto_align: Optional[str] = AUTO_ALIGN,
    auto_align_ema: float = AUTO_ALIGN_EMA,
    kmeans_update_freq: int = KMEANS_UPDATE_FREQ,
    verbose: bool = True,
) -> Tuple[nn.Module, torch.Tensor]:
    """
    Train relation-aware parametric UMAP with multi-objective optimization.

    Jointly optimizes:
    1. UMAP topology preservation (attractive + repulsive)
    2. Relation alignment (direction + length consistency per relation)
    3. Orthogonality penalty (disentangle relation axes)

    Features:
    - Automatic mixed precision (AMP) for faster training
    - Auto-balancing of loss weights via gradient norm matching
    - Cluster caching to reduce computational overhead
    - Cosine annealing learning rate schedule

    Args:
        X_high: (N, D_high) high-dimensional embeddings
        pair_indices_list: List of (M_r, 2) pair indices per relation
        n_clusters_list: Number of clusters per relation
        relation_weights: Optional per-relation weights
        n_neighbors: UMAP k for kNN graph
        min_dist: UMAP minimum distance
        spread: UMAP spread
        d_low: Low-dimensional embedding size
        epochs: Training epochs
        batch_size: Edge batch size
        lr: Learning rate
        align_weight: Weight for alignment loss
        ortho_weight: Weight for orthogonality penalty
        umap_rep_weight: Weight for UMAP repulsive term
        neg_sample_rate: Negative samples per positive edge
        use_amp: Use automatic mixed precision
        auto_align: Auto-balance alignment weight ("once", "ema", or None)
        auto_align_ema: EMA coefficient for auto-alignment
        kmeans_update_freq: Update clusters every N steps
        verbose: Print progress

    Returns:
        model: Trained ParametricUMAP model
        Z_final: Final (N, d_low) embeddings
    """
    device = X_high.device
    N, d_high = X_high.shape

    # Validate inputs
    assert N > 1, "Need at least 2 samples"
    assert d_high > 0 and d_low > 0, "Invalid dimensions"
    for pairs in pair_indices_list:
        if pairs.numel() > 0:
            assert pairs.max() < N, f"Pair indices out of bounds (max={pairs.max()}, N={N})"
            assert pairs.min() >= 0, "Negative pair indices"

    # Get UMAP curve parameters
    a, b = fit_ab_params(min_dist, spread)
    if verbose:
        print(f"UMAP parameters: a={a:.6f}, b={b:.6f} | min_dist={min_dist}, spread={spread}")

    # Build fuzzy simplicial set (UMAP graph)
    if verbose:
        print("Building fuzzy simplicial set...")
    ei, ej, ew = build_fuzzy_simplicial_set(X_high, n_neighbors)
    n_edges = ei.numel()
    if verbose:
        print(f"Graph edges: {n_edges}")

    if n_edges == 0:
        print("Warning: No edges in graph. Check n_neighbors and data.")

    # Initialize model
    model = ParametricUMAP(d_high, d_low).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)

    # AMP scaler (only for CUDA)
    scaler = torch.cuda.amp.GradScaler(enabled=(use_amp and device.type == "cuda"))

    # Initialize alignment weight
    align_w_cur = align_weight

    # Cluster caching
    cached_clusters: Optional[List[Optional[Tuple[torch.Tensor, torch.Tensor]]]] = None

    # ---- One-time gradient norm calibration for auto-alignment ----
    if auto_align in ("once", "ema") and n_edges > 0:
        if verbose:
            print("Calibrating alignment weight via gradient norms...")

        model.eval()
        with torch.enable_grad():
            # Create a copy of model output that requires grad
            Z_cal = model(X_high).detach().requires_grad_(True)

            # Sample a subset of edges for quick calibration
            n_cal = min(4096, n_edges)
            idx_cal = torch.randperm(n_edges, device=device)[:n_cal]

            with torch.cuda.amp.autocast(enabled=(use_amp and device.type == "cuda")):
                # UMAP loss
                Lu = umap_cross_entropy_loss(
                    Z_cal,
                    ei[idx_cal],
                    ej[idx_cal],
                    ew[idx_cal],
                    a,
                    b,
                    negative_sample_rate=neg_sample_rate,
                    repulsion_strength=umap_rep_weight,
                )

                # Alignment loss
                La, _, _ = relation_alignment_loss(
                    Z_cal,
                    pair_indices_list,
                    n_clusters_list,
                    relation_weights,
                    kmeans_iters=KMEANS_ITERS,
                )

            # Compute gradient norms w.r.t. embeddings
            gu = torch.autograd.grad(Lu, Z_cal, retain_graph=True)[0].norm().item()
            ga = torch.autograd.grad(La, Z_cal, retain_graph=False)[0].norm().item()

            # Balance: ALIGN_W ≈ grad_norm(UMAP) / grad_norm(Align)
            if ga > EPS:
                ratio = float(max(0.1, min(10.0, gu / ga)))
                align_w_cur = ratio if auto_align == "once" else (
                    auto_align_ema * align_weight + (1 - auto_align_ema) * ratio
                )

            if verbose:
                print(f"[AutoAlign] ALIGN_W set to {align_w_cur:.4f} "
                      f"(grad_u={gu:.4f}, grad_a={ga:.4f})")

    # ---- Main training loop ----
    if verbose:
        print(f"\nTraining for {epochs} epochs...")

    for ep in range(epochs):
        model.train()

        # Shuffle edges
        if n_edges > 0:
            perm = torch.randperm(n_edges, device=device)
        else:
            perm = torch.empty(0, dtype=torch.long, device=device)

        epoch_tot = epoch_umap = epoch_align = epoch_ortho = 0.0
        steps = 0

        # Mini-batch loop
        for step_idx, s in enumerate(range(0, n_edges, batch_size)):
            idx = perm[s : s + batch_size]

            # Update clusters periodically
            update_clusters = (
                (step_idx % kmeans_update_freq == 0)
                or (cached_clusters is None)
            )

            with torch.cuda.amp.autocast(enabled=(use_amp and device.type == "cuda")):
                # Forward pass
                Z = model(X_high)

                # UMAP topology loss
                if idx.numel() > 0:
                    L_umap = umap_cross_entropy_loss(
                        Z,
                        ei[idx],
                        ej[idx],
                        ew[idx],
                        a,
                        b,
                        negative_sample_rate=neg_sample_rate,
                        repulsion_strength=umap_rep_weight,
                    )
                else:
                    L_umap = Z.new_tensor(0.0)

                # Relation alignment loss (with optional cluster caching)
                if update_clusters:
                    L_align, mean_dirs, cached_clusters = relation_alignment_loss(
                        Z,
                        pair_indices_list,
                        n_clusters_list,
                        relation_weights,
                        kmeans_iters=KMEANS_ITERS,
                        cached_clusters=None,
                    )
                else:
                    L_align, mean_dirs, _ = relation_alignment_loss(
                        Z,
                        pair_indices_list,
                        n_clusters_list,
                        relation_weights,
                        kmeans_iters=KMEANS_ITERS,
                        cached_clusters=cached_clusters,
                    )

                # Orthogonality penalty
                L_ortho = orthogonality_penalty(mean_dirs, power=2)

                # Combined loss
                L = L_umap + align_w_cur * L_align + ortho_weight * L_ortho

            # Backward pass
            opt.zero_grad(set_to_none=True)
            scaler.scale(L).backward()

            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(opt)
            scaler.update()

            # Track losses
            epoch_tot += float(L.item())
            epoch_umap += float(L_umap.item())
            epoch_align += float(L_align.item())
            epoch_ortho += float(L_ortho.item())
            steps += 1

        # Step scheduler
        sched.step()

        # Logging
        if verbose and ((ep + 1) % 50 == 0 or ep == 0):
            model.eval()
            with torch.no_grad():
                Z_current = model(X_high)
                rstats = compute_relation_statistics(Z_current, pair_indices_list)

            avg_tot = epoch_tot / max(steps, 1)
            avg_umap = epoch_umap / max(steps, 1)
            avg_align = epoch_align / max(steps, 1)
            avg_ortho = epoch_ortho / max(steps, 1)

            print(
                f"\nEpoch {ep+1}/{epochs} | "
                f"Total={avg_tot:.4f} | UMAP={avg_umap:.4f} | "
                f"Align={avg_align:.4f} | Ortho={avg_ortho:.4f} | "
                f"ALIGN_W={align_w_cur:.4f}"
            )

            for rel_name, st in rstats.items():
                print(
                    f"  {rel_name}: "
                    f"len={st['mean_length']:.4f}±{st['std_length']:.4f}, "
                    f"dir_cos={st['mean_direction_cos']:.4f}"
                )

    # Final evaluation
    model.eval()
    with torch.no_grad():
        Z_final = model(X_high)

    if verbose:
        print("\nTraining complete!")

    return model, Z_final


# =========================
# Relation axis extraction and analogy API
# =========================
def extract_relation_axes(
    model: nn.Module,
    X_high: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
    kmeans_iters: int = KMEANS_ITERS,
) -> List[Optional[Dict[str, Union[torch.Tensor, float]]]]:
    """
    Extract relation axes from trained model.

    For each relation, returns:
    - centroids: (K, d) cluster centroids of difference vectors
    - mean_direction: (d,) average direction (normalized)
    - scale: Robust scale (median length of differences)

    Args:
        model: Trained ParametricUMAP model
        X_high: (N, D_high) high-dimensional data
        pair_indices_list: List of pair indices per relation
        n_clusters_list: Number of clusters per relation
        kmeans_iters: K-means iterations

    Returns:
        List of axis dictionaries (or None for empty relations)
    """
    model.eval()
    with torch.no_grad():
        Z = model(X_high)

    axes: List[Optional[Dict[str, Union[torch.Tensor, float]]]] = []

    for r, pairs in enumerate(pair_indices_list):
        if pairs.numel() == 0:
            axes.append(None)
            continue

        # Difference vectors for this relation
        diffs = Z[pairs[:, 1]] - Z[pairs[:, 0]]  # (M, d)
        M = diffs.size(0)
        k = min(max(1, n_clusters_list[r]), M)

        # Cluster difference vectors
        if k == 1 or M <= 1:
            C = diffs.mean(0, keepdim=True)
        else:
            C, _ = differentiable_kmeans(
                diffs, k, n_iter=kmeans_iters, temperature=0.5
            )

        # Mean direction (normalized average of cluster centroids)
        mean_dir = F.normalize(C.mean(0), dim=-1, eps=EPS)

        # Robust scale estimate (median length)
        scale = diffs.norm(dim=-1).median().item()

        axes.append({
            "centroids": C.cpu(),
            "mean_direction": mean_dir.cpu(),
            "scale": scale,
        })

    return axes


@cached(cache_type="query", ttl=1800)  # Cache for 30 minutes
def find_analogy(
    embeddings: torch.Tensor,
    relation_axes: List[Optional[Dict[str, Union[torch.Tensor, float]]]],
    query_word_idx: int,
    relation_idx: int,
    k: int = 1,
    metric: str = "euclidean",
) -> List[Tuple[int, float]]:
    """
    Find analogies by applying a relation axis to a query embedding.

    Computes: target = query + relation_axis * scale
    Then finds k nearest neighbors to target.

    Results are cached to avoid redundant distance computations.

    **FIXED**: Now uses Euclidean distance by default (not cosine similarity),
    since we're computing an absolute target position.

    Args:
        embeddings: (N, d) low-dimensional embeddings
        relation_axes: Extracted relation axes
        query_word_idx: Index of query word
        relation_idx: Which relation to apply
        k: Number of results
        metric: Distance metric ("euclidean" or "cosine")

    Returns:
        List of (index, score) tuples, sorted by score (higher = more similar)
    """
    rel = relation_axes[relation_idx]
    if rel is None:
        return []

    axis = rel["mean_direction"].to(embeddings.device)
    scale = rel["scale"]

    # Compute target embedding
    target = embeddings[query_word_idx] + axis * scale  # (d,)

    # Compute similarity/distance
    if metric == "euclidean":
        # Euclidean distance (lower = more similar)
        dists = torch.norm(embeddings - target.unsqueeze(0), dim=-1)
        dists[query_word_idx] = float("inf")  # Exclude query itself

        # Get top-k (lowest distance)
        k_clamped = min(k, embeddings.size(0) - 1)
        topk = torch.topk(dists, k=k_clamped, largest=False)

        # Convert to similarity score (higher = better)
        scores = 1.0 / (1.0 + topk.values)
        return [(int(topk.indices[i]), float(scores[i])) for i in range(len(topk.indices))]

    elif metric == "cosine":
        # Cosine similarity (higher = more similar)
        sims = F.cosine_similarity(embeddings, target.unsqueeze(0), dim=-1)
        sims[query_word_idx] = -float("inf")  # Exclude query itself

        k_clamped = min(k, embeddings.size(0) - 1)
        topk = torch.topk(sims, k=k_clamped, largest=True)

        return [(int(topk.indices[i]), float(topk.values[i])) for i in range(len(topk.indices))]

    else:
        raise ValueError(f"Unknown metric: {metric}. Use 'euclidean' or 'cosine'.")


@cached(cache_type="query", ttl=1800)  # Cache for 30 minutes
def analogy_from_pair(
    model: nn.Module,
    X_high: torch.Tensor,
    pair_indices_list: List[torch.Tensor],
    n_clusters_list: List[int],
    word_a_idx: int,
    word_b_idx: int,
    query_word_idx: int,
    k: int = 1,
    metric: str = "euclidean",
) -> List[Tuple[int, float]]:
    """
    Perform analogy using a reference pair to determine the relation.

    Results are cached to avoid redundant computations.

    Example: Given "boy:girl" and query "king", find "queen" by:
    1. Identify which relation "boy:girl" belongs to
    2. Apply that relation to "king"
    3. Return nearest neighbors

    Args:
        model: Trained model
        X_high: High-dimensional data
        pair_indices_list: Relation pairs
        n_clusters_list: Clusters per relation
        word_a_idx: First word in reference pair
        word_b_idx: Second word in reference pair
        query_word_idx: Query word index
        k: Number of results
        metric: Distance metric

    Returns:
        List of (index, score) tuples
    """
    # Extract relation axes
    axes = extract_relation_axes(model, X_high, pair_indices_list, n_clusters_list)

    # Find which relation contains the reference pair
    rel_idx = 0  # Default to first relation
    for i, pairs in enumerate(pair_indices_list):
        for pr in pairs:
            if (int(pr[0]) == word_a_idx and int(pr[1]) == word_b_idx) or \
               (int(pr[0]) == word_b_idx and int(pr[1]) == word_a_idx):
                rel_idx = i
                break

    # Get embeddings
    model.eval()
    with torch.no_grad():
        Z = model(X_high)

    # Perform analogy
    return find_analogy(Z, axes, query_word_idx, rel_idx, k, metric)


# =========================
# Example usage (synthetic data)
# =========================
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"PyTorch version: {torch.__version__}")

    # Generate synthetic high-dimensional embeddings
    N, D_high = 2000, 300
    torch.manual_seed(42)
    X_high = F.normalize(torch.randn(N, D_high, device=device), dim=-1)

    print(f"\nDataset: {N} samples, {D_high} dimensions")

    # Define two synthetic relations
    # Relation 0: "gender-like" (10 pairs)
    pairs_gender = torch.tensor(
        [
            [0, 1], [2, 3], [4, 5], [6, 7], [8, 9],
            [10, 11], [12, 13], [14, 15], [16, 17], [18, 19],
        ],
        dtype=torch.long,
        device=device,
    )

    # Relation 1: "plural-like" (10 pairs)
    pairs_plural = torch.tensor(
        [
            [20, 21], [22, 23], [24, 25], [26, 27], [28, 29],
            [30, 31], [32, 33], [34, 35], [36, 37], [38, 39],
        ],
        dtype=torch.long,
        device=device,
    )

    pair_indices_list = [pairs_gender, pairs_plural]
    n_clusters_list = [1, 2]  # Single cluster for gender, 2 for plural
    relation_weights = [1.0, 0.8]  # Slightly higher weight on gender

    print(f"Relations: {len(pair_indices_list)}")
    print(f"  Relation 0 (gender): {len(pairs_gender)} pairs, {n_clusters_list[0]} cluster(s)")
    print(f"  Relation 1 (plural): {len(pairs_plural)} pairs, {n_clusters_list[1]} cluster(s)")

    # Train the model
    print("\n" + "=" * 60)
    print("Training relation-aware UMAP...")
    print("=" * 60)

    model, Z = train_relation_aware_umap(
        X_high,
        pair_indices_list,
        n_clusters_list,
        relation_weights=relation_weights,
        epochs=200,
        batch_size=EDGE_BS,
        use_amp=USE_AMP,
        auto_align="once",
        verbose=True,
    )

    # Extract relation axes
    print("\n" + "=" * 60)
    print("Extracting relation axes...")
    print("=" * 60)

    axes = extract_relation_axes(model, X_high, pair_indices_list, n_clusters_list)

    for i, axis in enumerate(axes):
        if axis is not None:
            print(f"\nRelation {i}:")
            print(f"  Centroids shape: {axis['centroids'].shape}")
            print(f"  Mean direction shape: {axis['mean_direction'].shape}")
            print(f"  Scale: {axis['scale']:.4f}")

    # Test analogy finding
    print("\n" + "=" * 60)
    print("Testing analogy finder...")
    print("=" * 60)

    query_idx = 6
    test_relation = 0

    print(f"\nApplying relation {test_relation} to item {query_idx}:")
    results = find_analogy(Z, axes, query_word_idx=query_idx, relation_idx=test_relation, k=5)

    print("Top 5 analogies:")
    for rank, (idx, score) in enumerate(results, 1):
        print(f"  {rank}. Index {idx} (score: {score:.4f})")

    # Test pair-based analogy
    print(f"\nPair-based analogy: if {pairs_gender[0][0]}:{pairs_gender[0][1]}, then {query_idx}:?")
    results_pair = analogy_from_pair(
        model,
        X_high,
        pair_indices_list,
        n_clusters_list,
        word_a_idx=int(pairs_gender[0][0]),
        word_b_idx=int(pairs_gender[0][1]),
        query_word_idx=query_idx,
        k=5,
    )

    print("Top 5 analogies:")
    for rank, (idx, score) in enumerate(results_pair, 1):
        print(f"  {rank}. Index {idx} (score: {score:.4f})")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
