from __future__ import annotations

from collections import Counter
from math import comb, exp, lgamma, sqrt
from typing import Iterable, Tuple

import numpy as np


def _betacf(a: float, b: float, x: float, max_iter: int = 200, eps: float = 3e-12) -> float:
    # Continued fraction for incomplete beta (Numerical Recipes style).
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0

    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d

    for m in range(1, max_iter + 1):
        m2 = 2 * m

        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta

        if abs(delta - 1.0) < eps:
            break

    return h


def regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    ln_beta = lgamma(a) + lgamma(b) - lgamma(a + b)
    bt = exp(a * np.log(x) + b * np.log(1.0 - x) - ln_beta)

    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def student_t_cdf(t: float, df: int) -> float:
    if df <= 0:
        raise ValueError("df must be positive")

    x = df / (df + t * t)
    ib = regularized_incomplete_beta(df / 2.0, 0.5, x)
    if t >= 0:
        return 1.0 - 0.5 * ib
    return 0.5 * ib


def paired_t_test_pvalue(x: Iterable[float], y: Iterable[float], alternative: str) -> float:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    if x.shape != y.shape:
        raise ValueError("x and y must have same shape")
    n = x.size
    if n < 2:
        return 1.0

    d = x - y
    mean_d = float(np.mean(d))
    sd = float(np.std(d, ddof=1))
    if sd == 0:
        return 1.0

    t_stat = mean_d / (sd / sqrt(n))
    cdf = student_t_cdf(t_stat, n - 1)

    if alternative == "less":
        return cdf
    if alternative == "greater":
        return 1.0 - cdf
    raise ValueError("alternative must be 'less' or 'greater'")


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.zeros_like(values, dtype=float)

    i = 0
    n = values.size
    while i < n:
        j = i + 1
        while j < n and values[order[j]] == values[order[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def wilcoxon_signed_rank_pvalue(x: Iterable[float], y: Iterable[float], alternative: str) -> float:
    x = np.asarray(list(x), dtype=float)
    y = np.asarray(list(y), dtype=float)
    d = x - y
    d = d[d != 0]
    m = d.size
    if m == 0:
        return 1.0

    ranks = _average_ranks(np.abs(d))
    w_plus = float(np.sum(ranks[d > 0]))

    # exact distribution by DP on scaled ranks (half-rank resolution)
    scale = 2
    weights = np.round(ranks * scale).astype(int)
    w_obs = int(round(w_plus * scale))

    dist = Counter({0: 1})
    for w in weights:
        nxt = Counter(dist)
        for s, c in dist.items():
            nxt[s + w] += c
        dist = nxt

    total = float(2**m)
    if alternative == "greater":
        p = sum(c for s, c in dist.items() if s >= w_obs) / total
    elif alternative == "less":
        p = sum(c for s, c in dist.items() if s <= w_obs) / total
    else:
        raise ValueError("alternative must be 'less' or 'greater'")

    return float(p)


def mcnemar_exact_pvalue(success_a: Iterable[int], success_b: Iterable[int]) -> float:
    a = np.asarray(list(success_a), dtype=int)
    b = np.asarray(list(success_b), dtype=int)
    if a.shape != b.shape:
        raise ValueError("inputs must have same shape")

    b_only = int(np.sum((a == 1) & (b == 0)))
    c_only = int(np.sum((a == 0) & (b == 1)))
    n = b_only + c_only
    if n == 0:
        return 1.0

    k = min(b_only, c_only)
    tail = sum(comb(n, i) for i in range(0, k + 1)) / (2**n)
    p = min(1.0, 2.0 * tail)
    return float(p)


def one_sample_t_pvalue(values: Iterable[float], mu0: float, alternative: str) -> float:
    v = np.asarray(list(values), dtype=float)
    y = np.full_like(v, mu0, dtype=float)
    return paired_t_test_pvalue(v, y, alternative=alternative)
