# Reproduction guide (external-reader workflow)

This guide assumes the reader only has this GitHub repository.

## 1) Environment

- Python `>=3.10`
- `numpy`, `scipy`, `matplotlib` (installed via package metadata)

From `Replication/open/`:

```bash
python3 -m pip install -e .
```

## 2) Run full replication

```bash
make all
```

`make all` executes:

1. `make baseline` — writes legacy-text freeze + side-by-side baseline files.
2. `make run` — runs full PMBA/SP pipeline into `outputs/run/`.
3. `make tables` — generates the original submission's table datasets and summaries in `outputs/tables/`.
4. `make check-paper` — checks those values against the original submission's tables.
5. `make final` — recomputes every empirical number in the final paper (`../../paper/main.tex`) and
   redraws its two appendix figures, writing to `outputs/final_paper/`.
6. `make check-final` — compares every recomputed number with the value printed in the final paper,
   writes `outputs/final_paper/final_paper_check.md`, and exits with status 1 on any mismatch.
7. `make test` — unit tests + smoke tests, including a test that the final-paper check has no mismatches.

## 3) Expected success signals

- `make check-paper` prints: `mismatches=0`
- `make check-final` prints: `mismatches=0`
- `make test` finishes with all tests passing

## 4) Build the paper PDF

From repository root:

```bash
cd paper
make
```

This compiles the paper source `paper/main.tex`.

## 5) Key artifacts for audit

- Core predictions: `outputs/run/predictions_by_method.csv`
- SP replication inputs/results: `outputs/run/sp_replication.csv`
- Table-level CSV outputs: `outputs/tables/table_*.csv`
- Summary statistics used in text/notes: `outputs/tables/*_summary.json`
- Final-paper tables, text numbers and figure data: `outputs/final_paper/`
- Final-paper check report: `outputs/final_paper/final_paper_check.md`
- Check against the original submission: `outputs/tables/paper_crosscheck_report.md`

## 6) Re-running a subset

If only the main PMBA baseline is needed:

```bash
python3 scripts/run_pipeline.py --methods ols_iv_c
```

If only the final-paper numbers are needed (from raw data):

```bash
PYTHONPATH=src python3 scripts/reproduce_final_paper.py
PYTHONPATH=src python3 scripts/check_final_paper.py
```
