import numpy as np
from numpy.typing import ArrayLike, NDArray
from typing import Tuple


def infer_embedding_dim(myth_matrix: ArrayLike) -> int:
    """
    Infer embedding dimensionality D from a myth matrix of shape (N, 2D+1).

    Parameters
    ----------
    myth_matrix
        Array with shape (N, 2D+1): [embeddings | offsets | weights].

    Returns
    -------
    int
        Embedding dimension D.

    Raises
    ------
    ValueError
        If the shape is incompatible.
    """
    M = np.asarray(myth_matrix)
    if M.ndim != 2 or M.shape[1] < 3:
        raise ValueError("myth_matrix must be 2D with at least 3 columns")
    total = M.shape[1]
    if (total - 1) % 2 != 0:
        raise ValueError("myth_matrix width must be 2*D+1 for integer D")
    return (total - 1) // 2


def num_mythemes(myth_matrix: ArrayLike) -> int:
    """
    Number of mythemes (rows) in the myth matrix.

    Parameters
    ----------
    myth_matrix
        Array-like with shape (N, 2D+1).

    Returns
    -------
    int
        Number of mythemes N.
    """
    M = np.asarray(myth_matrix)
    if M.ndim != 2:
        raise ValueError("myth_matrix must be 2D")
    return M.shape[0]


def decompose_myth_matrix(
    myth_matrix: ArrayLike,
) -> Tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    """
    Split a myth matrix into embeddings, offsets, and weights.

    Parameters
    ----------
    myth_matrix
        Array of shape (N, 2D+1).

    Returns
    -------
    embeddings : (N, D)
    offsets : (N, D)
    weights : (N,)
    """
    M = np.asarray(myth_matrix)
    D = infer_embedding_dim(M)
    E = M[:, :D]
    O = M[:, D : 2 * D]
    W = M[:, -1]
    return E, O, W


def compose_myth_matrix(
    embeddings: ArrayLike,
    offsets: ArrayLike,
    weights: ArrayLike,
    *,
    enforce_checks: bool = True,
    dtype: np.dtype = None,
) -> NDArray[np.floating]:
    """
    Build a myth matrix from its components.

    Parameters
    ----------
    embeddings
        Shape (N, D)
    offsets
        Shape (N, D)
    weights
        Shape (N,) or (N, 1)
    enforce_checks
        If True, checks shape compatibility.
    dtype
        Optional dtype to cast result to.

    Returns
    -------
    myth_matrix : (N, 2D+1)
    """
    E = np.asarray(embeddings)
    O = np.asarray(offsets)
    W = np.asarray(weights)

    if enforce_checks:
        if E.ndim != 2 or O.ndim != 2:
            raise ValueError("embeddings and offsets must be 2D arrays")
        if E.shape != O.shape:
            raise ValueError("embeddings and offsets must have the same shape")
        if W.ndim not in (1, 2):
            raise ValueError("weights must be 1D or 2D column vector")
        if W.reshape(-1).shape[0] != E.shape[0]:
            raise ValueError("weights length must match number of themes")

    w_col = W.reshape(-1, 1)
    M = np.hstack([E, O, w_col])
    if dtype is not None:
        M = M.astype(dtype, copy=False)
    return M


def compute_myth_embedding(myth_matrix: ArrayLike) -> NDArray[np.floating]:
    """
    Compute the aggregated myth embedding: sum_i w_i * (e_i + o_i).

    Parameters
    ----------
    myth_matrix
        Array of shape (N, 2D+1).

    Returns
    -------
    embedding : (D,)
    """
    E, O, W = decompose_myth_matrix(myth_matrix)
    return ((E + O).T @ W).ravel()
