from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np

from .config import L_STATES
from .data_prep import NFTPanel


def _sigmoid(z: np.ndarray | float) -> np.ndarray | float:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _ols_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def _first_stage_predictions(beliefs: np.ndarray, iv_raw: np.ndarray) -> np.ndarray:
    # Stata reg `x' pre_* includes constant by default.
    Z = np.column_stack([np.ones(iv_raw.shape[0]), iv_raw])
    hats = np.zeros_like(beliefs)
    for j in range(L_STATES):
        b = _ols_fit(Z, beliefs[:, j])
        hats[:, j] = Z @ b
    return hats


def _drop_negative_rows(bhat: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, int]:
    keep = (bhat >= 0.0).all(axis=1)
    dropped = int((~keep).sum())
    return bhat[keep], y[keep], dropped


@dataclass
class EstimationResult:
    all_beta: np.ndarray  # shape (4,4) : row c == regression for state c
    dropped_rows: int


def estimate_ols(panel: NFTPanel, *, use_iv: bool, with_intercept: bool) -> EstimationResult:
    beliefs = panel.beliefs
    y_all = panel.beliefs_pop
    total_dropped = 0

    all_beta = np.zeros((L_STATES, L_STATES), dtype=float)

    for c in range(L_STATES):
        y = y_all[:, c]
        bhat = beliefs.copy()

        if use_iv:
            bhat = _first_stage_predictions(beliefs, panel.iv_raw)
            bhat, y, dropped = _drop_negative_rows(bhat, y)
            total_dropped += dropped

        if with_intercept:
            X = np.column_stack([np.ones(bhat.shape[0]), bhat[:, 0], bhat[:, 1], bhat[:, 2]])
            b = _ols_fit(X, y)
            all_beta[c, :] = [b[1] + b[0], b[2] + b[0], b[3] + b[0], b[0]]
        else:
            X = bhat
            b = _ols_fit(X, y)
            all_beta[c, :] = b

    return EstimationResult(all_beta=all_beta, dropped_rows=total_dropped)


def _adam_optimize(
    loss_grad_fn,
    n_params: int,
    *,
    max_iter: int = 5000,
    lr: float = 0.05,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    tol: float = 1e-10,
) -> np.ndarray:
    theta = np.zeros(n_params, dtype=float)
    m = np.zeros(n_params, dtype=float)
    v = np.zeros(n_params, dtype=float)

    prev_loss = np.inf
    patience = 0

    for t in range(1, max_iter + 1):
        loss, grad = loss_grad_fn(theta)

        m = beta1 * m + (1.0 - beta1) * grad
        v = beta2 * v + (1.0 - beta2) * (grad * grad)

        m_hat = m / (1.0 - beta1**t)
        v_hat = v / (1.0 - beta2**t)

        theta = theta - lr * m_hat / (np.sqrt(v_hat) + eps)

        if abs(prev_loss - loss) < tol:
            patience += 1
            if patience >= 10:
                break
        else:
            patience = 0

        prev_loss = loss

    return theta


def _fit_cls_with_intercept(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    # Stata CLSD4_C_* equivalent:
    # y = s(z1)x1 + s(z2)x2 + s(z3)x3 + s(c)
    # exported betas are [s(z1)+s(c), s(z2)+s(c), s(z3)+s(c), s(c)]
    x1, x2, x3 = x[:, 0], x[:, 1], x[:, 2]
    n = y.shape[0]

    def loss_grad(theta: np.ndarray):
        z1, z2, z3, c = theta
        s1, s2, s3, sc = _sigmoid(z1), _sigmoid(z2), _sigmoid(z3), _sigmoid(c)

        y_hat = s1 * x1 + s2 * x2 + s3 * x3 + sc
        err = y - y_hat

        loss = float(np.mean(err * err))

        g1 = (-2.0 / n) * np.sum(err * (s1 * (1.0 - s1) * x1))
        g2 = (-2.0 / n) * np.sum(err * (s2 * (1.0 - s2) * x2))
        g3 = (-2.0 / n) * np.sum(err * (s3 * (1.0 - s3) * x3))
        gc = (-2.0 / n) * np.sum(err * (sc * (1.0 - sc)))

        return loss, np.array([g1, g2, g3, gc], dtype=float)

    theta = _adam_optimize(loss_grad, 4)
    z1, z2, z3, c = theta
    s1, s2, s3, sc = _sigmoid(z1), _sigmoid(z2), _sigmoid(z3), _sigmoid(c)
    return np.array([s1 + sc, s2 + sc, s3 + sc, sc], dtype=float)


def _fit_cls_no_intercept(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    # Stata CLS_NC_* equivalent:
    # y = s(z1)x1 + s(z2)x2 + s(z3)x3 + s(z4)x4
    n = y.shape[0]

    def loss_grad(theta: np.ndarray):
        s = _sigmoid(theta)
        y_hat = x @ s
        err = y - y_hat
        loss = float(np.mean(err * err))

        scale = s * (1.0 - s)
        grads = np.zeros(4, dtype=float)
        for j in range(4):
            grads[j] = (-2.0 / n) * np.sum(err * (scale[j] * x[:, j]))

        return loss, grads

    theta = _adam_optimize(loss_grad, 4)
    return _sigmoid(theta)


def estimate_cls(panel: NFTPanel, *, use_iv: bool, with_intercept: bool) -> EstimationResult:
    beliefs = panel.beliefs
    y_all = panel.beliefs_pop
    total_dropped = 0

    all_beta = np.zeros((L_STATES, L_STATES), dtype=float)

    for c in range(L_STATES):
        y = y_all[:, c]
        bhat = beliefs.copy()

        if use_iv:
            bhat = _first_stage_predictions(beliefs, panel.iv_raw)
            bhat, y, dropped = _drop_negative_rows(bhat, y)
            total_dropped += dropped

        if with_intercept:
            all_beta[c, :] = _fit_cls_with_intercept(y, bhat)
        else:
            all_beta[c, :] = _fit_cls_no_intercept(y, bhat)

    return EstimationResult(all_beta=all_beta, dropped_rows=total_dropped)


def estimate_by_method(panel: NFTPanel, method: str) -> EstimationResult:
    mapping: Dict[str, Tuple[str, bool, bool]] = {
        "ols_iv_c": ("ols", True, True),
        "cls_iv_c": ("cls", True, True),
        "ols_iv_nc": ("ols", True, False),
        "cls_iv_nc": ("cls", True, False),
        "ols_noiv_c": ("ols", False, True),
        "cls_noiv_c": ("cls", False, True),
    }
    if method not in mapping:
        raise ValueError(f"Unknown method: {method}")

    family, use_iv, with_intercept = mapping[method]
    if family == "ols":
        return estimate_ols(panel, use_iv=use_iv, with_intercept=with_intercept)
    return estimate_cls(panel, use_iv=use_iv, with_intercept=with_intercept)
