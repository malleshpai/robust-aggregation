from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

from .config import KEY_COLUMNS, L_STATES


@dataclass(frozen=True)
class NFTPanel:
    nft_id: int
    true_state: int
    n_obs: int
    beliefs: np.ndarray       # shape (n, 4)
    beliefs_pop: np.ndarray   # shape (n, 4)
    iv_raw: np.ndarray        # shape (n, 6)


def load_raw_rows(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def load_true_states(path: Path) -> Dict[int, int]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return {int(r["NFT"]): int(r["TRUE"]) for r in reader}


def filter_verified(rows: Iterable[dict]) -> List[dict]:
    return [r for r in rows if r["From"] == "1" and r["Belief"] != ""]


def _recode_pre_iv(pre_vals: Tuple[int, int, int, int, int, int]) -> np.ndarray:
    # Mirrors PMBA_IV.m exactly.
    p1, p2, p3, p4, p5, p6 = pre_vals
    return np.array(
        [
            1.0 if p1 == 2 else 0.0,
            1.0 if p2 == 3 else 0.0,
            1.0 if p3 == 2 else 0.0,
            1.0 if p4 == 3 else 0.0,
            1.0 if p5 == 1 else 0.0,
            1.0 if p6 == 3 else 0.0,
        ],
        dtype=float,
    )


def build_nft_panel(rows: Iterable[dict], nft_id: int, true_state: int) -> NFTPanel:
    sub = [r for r in rows if int(r["NFT"]) == nft_id]
    if not sub:
        raise ValueError(f"No rows for NFT {nft_id}")

    type1 = defaultdict(lambda: np.full(L_STATES, np.nan, dtype=float))
    type2 = defaultdict(lambda: np.full(L_STATES, np.nan, dtype=float))

    for r in sub:
        key = tuple(r[c] for c in KEY_COLUMNS)
        range_idx = int(r["Range"]) - 1
        belief = float(r["Belief"]) / 100.0
        if r["Type"] == "1":
            type1[key][range_idx] = belief
        elif r["Type"] == "2":
            type2[key][range_idx] = belief

    common_keys = sorted(set(type1).intersection(set(type2)))
    beliefs = []
    beliefs_pop = []
    iv_raw = []

    for key in common_keys:
        b = type1[key]
        a = type2[key]
        if np.isnan(b).any() or np.isnan(a).any():
            continue

        beliefs.append(b)
        beliefs_pop.append(a)
        pre_tuple = tuple(int(key[i]) for i in range(1, 7))
        iv_raw.append(_recode_pre_iv(pre_tuple))

    if not beliefs:
        raise ValueError(f"No complete panel rows for NFT {nft_id}")

    beliefs_arr = np.vstack(beliefs)
    beliefs_pop_arr = np.vstack(beliefs_pop)
    iv_arr = np.vstack(iv_raw)

    return NFTPanel(
        nft_id=nft_id,
        true_state=true_state,
        n_obs=beliefs_arr.shape[0],
        beliefs=beliefs_arr,
        beliefs_pop=beliefs_pop_arr,
        iv_raw=iv_arr,
    )


def build_all_panels(raw_data_path: Path, true_state_path: Path) -> Dict[int, NFTPanel]:
    rows = filter_verified(load_raw_rows(raw_data_path))
    true_states = load_true_states(true_state_path)

    panels: Dict[int, NFTPanel] = {}
    for nft_id in sorted(true_states):
        panels[nft_id] = build_nft_panel(rows, nft_id, true_states[nft_id])
    return panels
