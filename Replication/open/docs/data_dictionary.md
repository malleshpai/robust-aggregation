# Data dictionary and sample construction

## Raw files (tracked)

- `Replication/data/raw/IG_Main_ordered_source.csv`
- `Replication/data/raw/true_state.csv`

## File: `IG_Main_ordered_source.csv`

Rows are respondent × NFT × range × belief-type observations in long format.

### Columns

| Column | Type | Description | Used in pipeline |
|---|---|---|---|
| `ID` | int | Respondent identifier | yes |
| `Pre_1`..`Pre_6` | int | Six pre-quiz responses | yes (IV recoding) |
| `Belief` | numeric/blank | Belief percentage (0–100); blank rows excluded | yes |
| `SC0` | int | Quiz score / control variable used in panel key | yes |
| `NFT` | int (1..20) | NFT identifier | yes |
| `Range` | int (1..4) | Price range state index | yes |
| `order` | string/blank | Survey order field | no |
| `Type` | int (`1`,`2`) | `1` first-order belief, `2` second-order belief | yes |
| `From` | int (`0`,`1`,`2`) | source/quality flag; only `From==1` kept | yes |

### Raw shape checks

- Total rows: `37,600`
- Unique NFTs: `20`
- Rows after filter (`From==1` and non-missing `Belief`): `15,920`

## File: `true_state.csv`

| Column | Type | Description |
|---|---|---|
| `NFT` | int (1..20) | NFT identifier |
| `TRUE` | int (1..4) | Ground-truth price range |

## Panel construction used for estimation

For each NFT:

1. Filter to `From==1` and non-empty `Belief`.
2. Build respondent key:
   `(ID, Pre_1, Pre_2, Pre_3, Pre_4, Pre_5, Pre_6, SC0)`.
3. For each key, collect complete 4-range vectors for:
   - first-order beliefs (`Type==1`), and
   - second-order beliefs (`Type==2`).
4. Drop keys with any missing range entry in either vector.
5. Rescale beliefs from percentages to proportions (`Belief/100`).

This yields one clean respondent row per NFT for the PMBA regressions.

## Final per-NFT sample sizes (`n_obs`)

| NFT | True state | n_obs |
|---:|---:|---:|
| 1 | 3 | 102 |
| 2 | 1 | 103 |
| 3 | 4 | 101 |
| 4 | 3 | 100 |
| 5 | 4 | 101 |
| 6 | 3 | 100 |
| 7 | 2 | 97 |
| 8 | 2 | 96 |
| 9 | 2 | 93 |
| 10 | 2 | 97 |
| 11 | 1 | 99 |
| 12 | 3 | 101 |
| 13 | 2 | 102 |
| 14 | 3 | 98 |
| 15 | 2 | 100 |
| 16 | 4 | 100 |
| 17 | 1 | 94 |
| 18 | 1 | 99 |
| 19 | 2 | 104 |
| 20 | 4 | 103 |
