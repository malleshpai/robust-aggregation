from __future__ import annotations

import re
from pathlib import Path
from typing import List


NFT_RE = re.compile(r"For NFT No\.\s*(\d+),")
PMBA_RE = re.compile(r"predicts Range\s*(\d+)\. The distance is\s*([0-9]+(?:\.[0-9]+)?)")
SP_RE = re.compile(r"SP \(average\) predicts Range\s*(1&2|3&4)")
MAJ_RE = re.compile(r"Majority \(average\) predicts Range\s*(\d+)")
TRUE_RE = re.compile(r"The true state is Range\s*(\d+)")


def parse_legacy_output(path: Path) -> List[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]

    out: List[dict] = []
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if len(lines) < 4:
            continue

        nft_m = NFT_RE.search(lines[0])
        pmba_m = PMBA_RE.search(lines[0])
        sp_m = SP_RE.search(lines[1])
        maj_m = MAJ_RE.search(lines[2])
        true_m = TRUE_RE.search(lines[3])

        if not (nft_m and sp_m and maj_m and true_m):
            continue

        pmba_pred = int(pmba_m.group(1)) if pmba_m else None
        pmba_dist = float(pmba_m.group(2)) if pmba_m else None

        out.append(
            {
                "nft_id": int(nft_m.group(1)),
                "pmba_pred_legacy": pmba_pred,
                "pmba_distance_legacy": pmba_dist,
                "sp_group_legacy": sp_m.group(1),
                "majority_pred_legacy": int(maj_m.group(1)),
                "true_state": int(true_m.group(1)),
            }
        )

    out.sort(key=lambda r: r["nft_id"])
    return out
