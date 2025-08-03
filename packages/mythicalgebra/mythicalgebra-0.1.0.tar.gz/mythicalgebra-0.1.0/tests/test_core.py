# test_myth_functions.py
import pytest
import numpy as np
from numpy.testing import assert_allclose

from mythicalgebra import (  # replace with the actual import path
    infer_embedding_dim,
    num_mythemes,
    compose_myth_matrix,
    decompose_myth_matrix,
    compute_myth_embedding,
)


@pytest.fixture(autouse=True)
def rng_seed():
    np.random.seed(1234)  # deterministic for tests


def manual_embedding(embeddings: np.ndarray, offsets: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Direct formula: sum_i w_i * (e_i + o_i)
    """
    w = weights.reshape(-1)
    return ((embeddings + offsets).T @ w).ravel()


def test_infer_embedding_dim_valid():
    D = 5
    N = 3
    embeddings = np.random.randn(N, D)
    offsets = np.random.randn(N, D)
    weights = np.random.randn(N)
    M = compose_myth_matrix(embeddings, offsets, weights)
    inferred = infer_embedding_dim(M)
    assert inferred == D


def test_infer_embedding_diminvalid_width():
    bad = np.zeros((3, 8))
    with pytest.raises(ValueError):
        infer_embedding_dim(bad)


def test_num_mythemes_valid_and_invalid():
    M = np.zeros((4, 9))
    assert num_mythemes(M) == 4
    with pytest.raises(ValueError):
        num_mythemes(np.zeros(1))  # not 2D


def test_compose_and_decompose_roundtrip():
    D = 8
    N = 6
    embeddings = np.random.randn(N, D)
    offsets = np.random.randn(N, D)
    weights = np.random.rand(N)  # non-negative weights

    M = compose_myth_matrix(embeddings, offsets, weights)
    E, O, W = decompose_myth_matrix(M)

    # validate shapes
    assert E.shape == (N, D)
    assert O.shape == (N, D)
    assert W.shape == (N,)

    # components should match originals
    assert_allclose(E, embeddings)
    assert_allclose(O, offsets)
    assert_allclose(W, weights)

    # embedding should equal manual computation
    emb_calc = compute_myth_embedding(M)
    emb_manual = manual_embedding(embeddings, offsets, weights)
    assert emb_calc.shape == (D,)
    assert_allclose(emb_calc, emb_manual, rtol=1e-6, atol=1e-8)


def test_compose_with_dtype_and_no_checks():
    D = 4
    N = 5
    embeddings = np.random.randn(N, D).astype(np.float64)
    offsets = np.random.randn(N, D).astype(np.float64)
    weights = np.random.randn(N).astype(np.float64)

    # force float32 and skip checks
    M = compose_myth_matrix(embeddings, offsets, weights, enforce_checks=False, dtype=np.float32)
    assert M.dtype == np.float32

    # still valid embedding
    emb_calc = compute_myth_embedding(M.astype(np.float64))  # upcast for comparison
    emb_manual = manual_embedding(embeddings, offsets, weights)
    assert_allclose(emb_calc, emb_manual, rtol=1e-5, atol=1e-5)


def test_error_on_mismatched_shapes_in_compose():
    D = 3
    embeddings = np.random.randn(4, D)
    offsets = np.random.randn(5, D)  # mismatched N
    weights = np.random.randn(4)

    with pytest.raises(ValueError):
        compose_myth_matrix(embeddings, offsets, weights)


def test_error_on_bad_weight_shape():
    D = 2
    N = 3
    embeddings = np.random.randn(N, D)
    offsets = np.random.randn(N, D)
    weights = np.random.randn(N, 2)  # 2 columns, ambiguous

    # This should still work if reshape succeeds; but if shape is incompatible, error
    with pytest.raises(ValueError):
        compose_myth_matrix(embeddings, offsets, weights.reshape(N, 2), enforce_checks=True)
