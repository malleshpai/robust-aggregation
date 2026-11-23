from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import THRESHOLD


@dataclass(frozen=True)
class PMBAPrediction:
    reasonable: int
    distance: float
    predicted_range: int


def pmba_predict(all_beta: np.ndarray, mu_hat: np.ndarray, threshold: float = THRESHOLD) -> PMBAPrediction:
    # compare_LR.m logic
    mu_bar = all_beta.T
    distances = np.sqrt(np.sum((mu_bar - mu_hat.reshape(1, -1)) ** 2, axis=1))

    min_index = int(np.argmin(distances)) + 1
    min_distance = float(np.min(distances))

    matching_indices = np.where(distances < threshold)[0]
    if matching_indices.size > 0:
        return PMBAPrediction(reasonable=1, distance=min_distance, predicted_range=min_index)
    return PMBAPrediction(reasonable=0, distance=min_distance, predicted_range=0)


def majority_prediction(mu_hat: np.ndarray) -> int:
    return int(np.argmax(mu_hat)) + 1


def sp_prediction(beliefs: np.ndarray, beliefs_pop: np.ndarray) -> dict:
    mu_hat = beliefs.mean(axis=0)
    alpha_hat = beliefs_pop.mean(axis=0)

    mu12 = float(mu_hat[0] + mu_hat[1])
    alpha12 = float(alpha_hat[0] + alpha_hat[1])

    # SP_Meta.m rule: if mu12 > alpha12 -> group 1 (ranges 1&2), else group 2 (3&4)
    sp_group = "1&2" if mu12 > alpha12 else "3&4"

    return {
        "mu12": mu12,
        "alpha12": alpha12,
        "sp_group": sp_group,
    }
