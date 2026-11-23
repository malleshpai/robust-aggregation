# Open-source replication package

This folder contains the open-source replication pipeline for the paper's empirical results.
The paper source is `../../paper/main.tex` (path relative to this folder).

## What this package does

- Loads raw survey data from `../data/raw/`.
- Reconstructs respondent-level NFT panels exactly as used in estimation.
- Runs all six PMBA regression variants plus the mean-belief, plurality-voting and SP benchmarks.
- Recomputes every empirical number in the final paper (Section 4 and the experiment appendix),
  including the alternative-matching table and both appendix figures.
- Checks each recomputed number against the value printed in the final paper (`make check-final`).
- Keeps the older check against the tables of the original submission (`make check-paper`).

## Data sources (tracked in GitHub)

- `../data/raw/IG_Main_ordered_source.csv`
- `../data/raw/true_state.csv`
- `data/reference/Pilot_New_OLSD4_C_NoIV.txt` (frozen legacy text output used by `make baseline`)

## Methods implemented

- `ols_iv_c` (baseline PMBA, "OLS--IV" in the paper)
- `cls_iv_c`
- `ols_iv_nc`
- `cls_iv_nc`
- `ols_noiv_c`
- `cls_noiv_c`

## Requirements

Python 3.10 or later with `numpy`, `scipy` and `matplotlib`. Run with plain `python3`.

## Quick start

From `Replication/open/`:

```bash
make all
```

Equivalent step-by-step:

```bash
make baseline      # freeze legacy text output, baseline comparison
make run           # PMBA/SP pipeline -> outputs/run/
make tables        # tables in the layout of the original submission -> outputs/tables/
make check-paper   # check against the original submission's tables
make final         # every final-paper number and both figures -> outputs/final_paper/
make check-final   # check against the numbers printed in the final paper (exit 1 on mismatch)
make test          # unit tests, including zero mismatches against the final paper
```

## Output files

Final paper (`make final`, `make check-final`):

- `outputs/final_paper/table_*.csv` — one file per table in the final paper
- `outputs/final_paper/item_level.csv` — every per-NFT quantity in one file
- `outputs/final_paper/summary.json` — numbers quoted in the text
- `outputs/final_paper/values.json` — every checked quantity, keyed as in the check report
- `outputs/final_paper/figure_data/*.csv` — data behind the two appendix figures
- `outputs/final_paper/figures/state_contingent_vec_dist.png`, `outputs/final_paper/figures/valid_grid.png`
- `outputs/final_paper/final_paper_check.md` (and `.json`) — match report

Original submission (`make run`, `make tables`, `make check-paper`):

- `outputs/run/predictions_by_method.csv`
- `outputs/run/sp_replication.csv`
- `outputs/tables/table_*.csv`
- `outputs/tables/paper_crosscheck_report.md`

## Documentation

- `docs/README.md` — documentation index
- `docs/reproduction_guide.md` — exact commands to reproduce all outputs
- `docs/regression_specifications.md` — full regression equations and prediction rules
- `docs/data_dictionary.md` — raw variables, filtering, panel construction, sample sizes
- `docs/table_mapping.md` — mapping from every final-paper table, figure and text number to its output file
