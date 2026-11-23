"""Compare computed final-paper values with the numbers printed in the paper."""
from __future__ import annotations

import json
from pathlib import Path

from .final_paper import compute_all, flat_values
from .final_paper_expectations import expected_values, nft_list_internal_checks


def values_match(got, expected, decimals) -> bool:
    """Exact match when decimals is None; otherwise `got` must round to the printed value."""
    if decimals is None:
        if isinstance(expected, bool) or isinstance(got, bool):
            return bool(got) == bool(expected) and type(got) is type(expected)
        return got == expected
    if got is None:
        return False
    return abs(float(got) - float(expected)) <= 0.5 * 10 ** (-decimals) + 1e-9


def section_of(key: str) -> str:
    return key.split("/")[0]


def run_final_check(out_dir: Path, res: dict | None = None) -> dict:
    if res is None:
        res = compute_all()
    got = flat_values(res)
    expected = expected_values()

    results = []
    for key, (exp, decimals) in expected.items():
        if key not in got:
            results.append({"key": key, "expected": exp, "got": "not computed", "ok": False})
            continue
        results.append({"key": key, "expected": exp, "got": got[key], "decimals": decimals,
                        "ok": values_match(got[key], exp, decimals)})

    # Histogram bins that the code finds but the figure does not show count as mismatches.
    for key, val in got.items():
        if key.startswith("fig:state_mean_distribution/bin_") and key not in expected:
            results.append({"key": key, "expected": 0, "got": val, "ok": False})

    for key, ok in nft_list_internal_checks():
        results.append({"key": key, "expected": True, "got": ok, "ok": ok, "internal": True})

    unchecked = sorted(k for k in got if k not in expected and "bin_" not in k)
    notes = [
        "fig:state_mean_distribution panel (b) prints 'Maximum absolute error: 2.00e-15'. Floating-point "
        "rounding noise is platform dependent, so the check only requires the maximum to be below 1e-12; "
        f"this run gives {res['validity']['max_abs_sum_error']:.2e}.",
        "tab:nft_list collection names, token numbers and prices are not in the raw data; the check confirms "
        "the Range column equals true_state.csv and that the printed prices are internally consistent.",
    ]

    mismatches = [r for r in results if not r["ok"]]
    report = {
        "n_checked": len(results),
        "n_matches": len(results) - len(mismatches),
        "n_mismatches": len(mismatches),
        "mismatches": mismatches,
        "results": results,
        "computed_but_not_printed": unchecked,
        "notes": notes,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "final_paper_check.json").write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    write_markdown(out_dir / "final_paper_check.md", report)
    return report


def write_markdown(path: Path, report: dict) -> None:
    by_section = {}
    for r in report["results"]:
        sec = section_of(r["key"])
        ok, total = by_section.get(sec, (0, 0))
        by_section[sec] = (ok + int(r["ok"]), total + 1)

    lines = [
        "# Check of computed values against the final paper",
        "",
        "Expected values are the numbers printed in `paper/main.tex`, transcribed in",
        "`src/replication_open/final_paper_expectations.py`. A rounded number matches when the",
        "computed value rounds to it at the printed precision.",
        "",
        f"- Quantities checked: **{report['n_checked']}**",
        f"- Matches: **{report['n_matches']}**",
        f"- Mismatches: **{report['n_mismatches']}**",
        "",
        "## By table, figure or paragraph",
        "",
        "| Source | Matches | Checked |",
        "|---|---:|---:|",
    ]
    for sec, (ok, total) in by_section.items():
        lines.append(f"| `{sec}` | {ok} | {total} |")
    lines += ["", "## Mismatches", ""]
    if report["mismatches"]:
        lines += ["| Key | Paper | Computed |", "|---|---:|---:|"]
        for m in report["mismatches"]:
            lines.append(f"| `{m['key']}` | {m['expected']} | {m['got']} |")
    else:
        lines.append("None.")
    lines += ["", "## Notes", ""]
    lines += [f"- {n}" for n in report["notes"]]
    lines += ["", "## All checked quantities", "", "| Key | Paper | Computed | OK |", "|---|---:|---:|:---:|"]
    for r in report["results"]:
        got = r["got"]
        if isinstance(got, float):
            got = f"{got:.6g}"
        lines.append(f"| `{r['key']}` | {r['expected']} | {got} | {'yes' if r['ok'] else 'NO'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
