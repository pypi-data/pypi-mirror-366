from typing import Literal

import torch
import torch.nn.functional as F

__version__ = "v0.1.0"


def _compute_distance(
    x: torch.Tensor, y: torch.Tensor, distance_metric: Literal["l2", "cosine"] = "l2"
) -> torch.Tensor:
    if distance_metric == "l2":
        distances = torch.cdist(x, y, p=2)
    elif distance_metric == "cosine":
        x_norm = F.normalize(x, p=2, dim=1)
        y_norm = F.normalize(y, p=2, dim=1)
        similarities = torch.mm(x_norm, y_norm.t())
        distances = 1 - similarities
    else:
        raise ValueError(f"Unknown distance_metric: {distance_metric}")

    return distances


def _get_k_nearest_neighbors(distances: torch.Tensor, k: int, exclude_self: bool = True) -> torch.Tensor:
    topk_k = k + 1 if exclude_self is True else k
    (_, indices) = torch.topk(distances, k=topk_k, dim=1, largest=False)
    if exclude_self is True:
        indices = indices[:, 1:]

    return indices[:, :k]


def _compute_pdist(distances: torch.Tensor, neighbor_indices: torch.Tensor, lambda_: float) -> torch.Tensor:
    # Probabilistic Distance
    (N, k) = neighbor_indices.shape

    row_indices = torch.arange(N, device=distances.device).unsqueeze(1).expand(-1, k)
    neighbor_distances = distances[row_indices, neighbor_indices]

    std_distances = torch.sqrt(torch.mean(neighbor_distances.square(), dim=1))
    pdist = lambda_ * std_distances

    return pdist


def _compute_plof(pdist: torch.Tensor, neighbor_indices: torch.Tensor) -> torch.Tensor:
    # Probabilistic Local Outlier Factor
    neighbor_pdist = pdist[neighbor_indices]
    mean_neighbor_pdist = torch.mean(neighbor_pdist, dim=1)
    plof = (pdist / mean_neighbor_pdist) - 1

    return plof


def loop(
    data: torch.Tensor, lambda_: float = 3.0, k: int = 10, distance_metric: Literal["l2", "cosine"] = "l2"
) -> torch.Tensor:
    """
    Computes Local Outlier Probabilities (LoOP)

    LoOP is a density-based outlier detection method that assigns an outlier probability
    to each data point, indicating how likely it is to be an outlier relative to its
    local neighborhood.

    Parameters
    ----------
    data
        The input dataset, expected to be a 2D tensor of shape (N, D),
        where N is the number of samples and D is the number of features.
    lambda_
        Scaling factor for the probabilistic distance (pdist) and the
        normalization factor (n_plof). A common value suggested in the
        original paper is 3.0.
    k
        The number of nearest neighbors to consider for local density estimation.
    distance_metric
        The distance metric to use for computing neighbor distances.
        Can be "l2" for Euclidean distance or "cosine" for Cosine distance.

    Returns
    -------
    A 1D tensor of shape (N,) containing the LoOP score (outlier probability)
    for each data point, ranging from 0.0 to 1.0.

    Notes
    -----
    The paper available at https://www.dbs.ifi.lmu.de/Publikationen/Papers/LoOP1649.pdf

    References
    ----------
    [1] Hans-Peter Kriegel, Peer Kröger, Erich Schubert, and Arthur Zimek. 2009. LoOP: local outlier probabilities.
        In Proceedings of the 18th ACM conference on Information and knowledge management (CIKM '09).
        Association for Computing Machinery, New York, NY, USA, 1649-1652. https://doi.org/10.1145/1645953.1646195
    """

    distances = _compute_distance(data, data, distance_metric=distance_metric)
    neighbor_indices = _get_k_nearest_neighbors(distances, k, exclude_self=True)
    pdist = _compute_pdist(distances, neighbor_indices, lambda_)
    plof = _compute_plof(pdist, neighbor_indices)
    n_plof = lambda_ * torch.sqrt(torch.mean(plof.square()))

    erf_input = plof / (torch.sqrt(torch.tensor(2.0, dtype=plof.dtype, device=plof.device)) * n_plof)
    loop_values = torch.clamp(torch.erf(erf_input), min=0.0)

    return loop_values
