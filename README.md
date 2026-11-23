# The Wisdom of the Crowd and Higher-Order Beliefs

Yi-Chun Chen, Manuel Mueller-Frank and Mallesh M. Pai

This repository contains the paper and the data and code for its experiment.

- `paper/`: LaTeX source (`main.tex`), bibliography, figures, and the compiled `main.pdf`.
- `Replication/data/raw/`: the experimental data. Participants are identified only by an anonymous numeric ID.
- `Replication/open/`: Python code that reproduces every empirical result in the paper (Section 4 and the experiment appendix), and checks each number against the value printed in the paper.

## Reproduce the results

Requires Python 3.10 or later with `numpy`, `scipy` and `matplotlib`.

```bash
cd Replication/open
make all
```

This runs the estimation, writes all tables, text numbers and figure data to `Replication/open/outputs/final_paper/`, and compares them with the paper (report: `outputs/final_paper/final_paper_check.md`). It takes a few minutes. See `Replication/open/docs/reproduction_guide.md` for the individual steps and `Replication/open/docs/table_mapping.md` for where each table and figure comes from.

## Build the paper

```bash
cd paper
make
```
