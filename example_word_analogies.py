"""
Example: Word Analogies with Pre-trained Embeddings

This script demonstrates how to use the UMAP Analogy Engine with real word embeddings
(e.g., Word2Vec, GloVe) to solve analogy tasks like:
    "king is to queen as man is to ?"  → "woman"

Prerequisites:
    pip install torch gensim

You'll need to download pre-trained embeddings:
    - Word2Vec: https://code.google.com/archive/p/word2vec/
    - GloVe: https://nlp.stanford.edu/projects/glove/
"""

import torch
import numpy as np
from typing import Dict, List, Tuple

from umap_analogy_engine import (
    train_relation_aware_umap,
    extract_relation_axes,
    find_analogy,
    analogy_from_pair,
)
from operation_cache import cached, print_cache_stats


# =========================
# Load Pre-trained Embeddings
# =========================

@cached(cache_type="embeddings", ttl=86400)  # Cache for 24 hours
def load_glove_embeddings(path: str, vocab_size: int = 50000) -> Tuple[torch.Tensor, Dict[str, int], List[str]]:
    """
    Load GloVe embeddings from text file.

    Results are cached to disk for faster subsequent loads.

    Args:
        path: Path to GloVe file (e.g., glove.6B.300d.txt)
        vocab_size: Maximum vocabulary size to load

    Returns:
        embeddings: (N, D) tensor
        word_to_idx: Dict mapping words to indices
        idx_to_word: List mapping indices to words
    """
    print(f"Loading GloVe embeddings from {path}... (not cached)")

    embeddings = []
    idx_to_word = []
    word_to_idx = {}

    with open(path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx >= vocab_size:
                break

            parts = line.strip().split()
            word = parts[0]
            vector = np.array([float(x) for x in parts[1:]], dtype=np.float32)

            embeddings.append(vector)
            idx_to_word.append(word)
            word_to_idx[word] = idx

            if (idx + 1) % 10000 == 0:
                print(f"  Loaded {idx + 1} words...")

    embeddings = torch.tensor(np.array(embeddings))
    print(f"✓ Loaded {len(idx_to_word)} word embeddings ({embeddings.size(1)}-dim)\n")

    return embeddings, word_to_idx, idx_to_word


@cached(cache_type="embeddings", ttl=86400)  # Cache for 24 hours
def load_word2vec_embeddings(path: str, vocab_size: int = 50000) -> Tuple[torch.Tensor, Dict[str, int], List[str]]:
    """
    Load Word2Vec embeddings using gensim.

    Results are cached to disk for faster subsequent loads.

    Args:
        path: Path to Word2Vec .bin file
        vocab_size: Maximum vocabulary size

    Returns:
        embeddings: (N, D) tensor
        word_to_idx: Dict mapping words to indices
        idx_to_word: List mapping indices to words
    """
    try:
        from gensim.models import KeyedVectors
    except ImportError:
        raise ImportError("Install gensim: pip install gensim")

    print(f"Loading Word2Vec embeddings from {path}... (not cached)")
    wv = KeyedVectors.load_word2vec_format(path, binary=True, limit=vocab_size)

    embeddings = torch.tensor(wv.vectors, dtype=torch.float32)
    idx_to_word = wv.index_to_key
    word_to_idx = {word: idx for idx, word in enumerate(idx_to_word)}

    print(f"✓ Loaded {len(idx_to_word)} word embeddings ({embeddings.size(1)}-dim)\n")
    return embeddings, word_to_idx, idx_to_word


# =========================
# Define Semantic Relations
# =========================

def build_relation_pairs(
    word_to_idx: Dict[str, int],
    relation_definitions: Dict[str, List[Tuple[str, str]]]
) -> Tuple[List[torch.Tensor], List[str]]:
    """
    Convert word pairs to index tensors.

    Args:
        word_to_idx: Vocabulary mapping
        relation_definitions: Dict of {relation_name: [(word_a, word_b), ...]}

    Returns:
        pair_indices_list: List of (M_r, 2) tensors
        relation_names: List of relation names
    """
    pair_indices_list = []
    relation_names = []

    for rel_name, pairs in relation_definitions.items():
        valid_pairs = []

        for word_a, word_b in pairs:
            if word_a in word_to_idx and word_b in word_to_idx:
                idx_a = word_to_idx[word_a]
                idx_b = word_to_idx[word_b]
                valid_pairs.append([idx_a, idx_b])
            else:
                missing = []
                if word_a not in word_to_idx:
                    missing.append(word_a)
                if word_b not in word_to_idx:
                    missing.append(word_b)
                print(f"  Warning: Skipping pair ({word_a}, {word_b}) - missing: {missing}")

        if valid_pairs:
            pair_indices_list.append(torch.tensor(valid_pairs, dtype=torch.long))
            relation_names.append(rel_name)
            print(f"✓ Relation '{rel_name}': {len(valid_pairs)} pairs")
        else:
            print(f"✗ Relation '{rel_name}': No valid pairs found")

    return pair_indices_list, relation_names


# =========================
# Main Example
# =========================

def main():
    # Configuration
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    EMBEDDING_PATH = "glove.6B.300d.txt"  # Update this path
    # Or for Word2Vec:
    # EMBEDDING_PATH = "GoogleNews-vectors-negative300.bin"

    print("=" * 60)
    print("UMAP Analogy Engine - Word Embedding Demo")
    print("=" * 60)
    print(f"Device: {DEVICE}\n")

    # Load embeddings
    try:
        # For GloVe:
        X_high, word_to_idx, idx_to_word = load_glove_embeddings(
            EMBEDDING_PATH, vocab_size=50000
        )
        # For Word2Vec:
        # X_high, word_to_idx, idx_to_word = load_word2vec_embeddings(
        #     EMBEDDING_PATH, vocab_size=50000
        # )
    except FileNotFoundError:
        print(f"Error: Could not find embeddings at {EMBEDDING_PATH}")
        print("Please download GloVe or Word2Vec embeddings:")
        print("  GloVe: https://nlp.stanford.edu/projects/glove/")
        print("  Word2Vec: https://code.google.com/archive/p/word2vec/")
        return

    X_high = X_high.to(DEVICE)

    # Define semantic relations
    print("\n" + "=" * 60)
    print("Defining semantic relations...")
    print("=" * 60)

    relation_definitions = {
        "gender": [
            ("king", "queen"),
            ("man", "woman"),
            ("boy", "girl"),
            ("father", "mother"),
            ("son", "daughter"),
            ("uncle", "aunt"),
            ("husband", "wife"),
            ("prince", "princess"),
            ("brother", "sister"),
            ("grandfather", "grandmother"),
        ],
        "plural": [
            ("cat", "cats"),
            ("dog", "dogs"),
            ("car", "cars"),
            ("house", "houses"),
            ("book", "books"),
            ("tree", "trees"),
            ("child", "children"),
            ("person", "people"),
            ("mouse", "mice"),
            ("foot", "feet"),
        ],
        "comparative": [
            ("good", "better"),
            ("bad", "worse"),
            ("big", "bigger"),
            ("small", "smaller"),
            ("fast", "faster"),
            ("slow", "slower"),
            ("high", "higher"),
            ("low", "lower"),
        ],
        "capital": [
            ("france", "paris"),
            ("germany", "berlin"),
            ("spain", "madrid"),
            ("italy", "rome"),
            ("japan", "tokyo"),
            ("china", "beijing"),
            ("russia", "moscow"),
            ("england", "london"),
        ],
    }

    pair_indices_list, relation_names = build_relation_pairs(
        word_to_idx, relation_definitions
    )

    if not pair_indices_list:
        print("Error: No valid relations found!")
        return

    # Configure relation clustering (1 cluster per relation is usually good)
    n_clusters_list = [1] * len(pair_indices_list)

    # Train the model
    print("\n" + "=" * 60)
    print("Training relation-aware UMAP...")
    print("=" * 60)

    model, Z = train_relation_aware_umap(
        X_high,
        pair_indices_list,
        n_clusters_list,
        relation_weights=None,  # Equal weight for all relations
        n_neighbors=15,
        min_dist=0.1,
        spread=1.0,
        d_low=50,  # Higher dimensionality for better semantic preservation
        epochs=300,
        batch_size=20000,
        lr=1e-3,
        align_weight=1.0,
        ortho_weight=0.1,
        use_amp=True,
        auto_align="once",
        verbose=True,
    )

    # Extract relation axes
    print("\n" + "=" * 60)
    print("Extracting relation axes...")
    print("=" * 60)

    axes = extract_relation_axes(model, X_high, pair_indices_list, n_clusters_list)

    for i, (rel_name, axis) in enumerate(zip(relation_names, axes)):
        if axis is not None:
            print(f"✓ {rel_name}: scale={axis['scale']:.4f}")

    # Test analogies
    print("\n" + "=" * 60)
    print("Testing analogies...")
    print("=" * 60)

    test_cases = [
        # (relation, word_a, word_b, query, expected)
        ("gender", "king", "queen", "man", "woman"),
        ("gender", "king", "queen", "boy", "girl"),
        ("plural", "cat", "cats", "dog", "dogs"),
        ("plural", "mouse", "mice", "child", "children"),
        ("comparative", "good", "better", "bad", "worse"),
        ("capital", "france", "paris", "germany", "berlin"),
    ]

    for rel_name, word_a, word_b, query, expected in test_cases:
        # Check all words exist
        missing = []
        for w in [word_a, word_b, query, expected]:
            if w not in word_to_idx:
                missing.append(w)
        if missing:
            print(f"\n⊗ Skipping: {word_a}:{word_b} :: {query}:? (missing: {missing})")
            continue

        print(f"\n📝 Test: {word_a}:{word_b} :: {query}:?")
        print(f"   Expected: {expected}")

        # Get indices
        idx_a = word_to_idx[word_a]
        idx_b = word_to_idx[word_b]
        idx_query = word_to_idx[query]
        idx_expected = word_to_idx[expected]

        # Perform analogy
        results = analogy_from_pair(
            model,
            X_high,
            pair_indices_list,
            n_clusters_list,
            word_a_idx=idx_a,
            word_b_idx=idx_b,
            query_word_idx=idx_query,
            k=5,
            metric="euclidean",
        )

        print("   Top 5 predictions:")
        for rank, (idx, score) in enumerate(results, 1):
            word = idx_to_word[idx]
            marker = "✓" if idx == idx_expected else " "
            print(f"   {marker} {rank}. {word} (score: {score:.4f})")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)

    # Print cache statistics
    print_cache_stats()


if __name__ == "__main__":
    main()
