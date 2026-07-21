# Data-placeholder tracker

Every `[DATA PLACEHOLDER]` in the section drafts is a spot where a real number
or a source-verified citation must be swapped in. This table maps each one to
the notebook / data pull (or research task) that produces it, so the "what's
left to make this a real paper" state is legible at a glance.

Follow the "Suggested order of work" in the README; fill the rows in that order.

| # | Location (`file:line`) | What it needs | Filled by | Status |
|---|------------------------|---------------|-----------|--------|
| 1 | `paper/sections/1_background.md:40` | FEDS instrument-comparison table (OIS/TIPS/SME vs. Kalshi) | Literature/source verification against the FEDS paper | ☐ |
| 2 | `paper/sections/2_replication.md:43` | Re-plotted Figure 1 on an independent Kalshi pull | Notebook 01 on real fed funds rate series (`USE_REAL_DATA`) | ☐ |
| 3 | `paper/sections/2_replication.md:58` | Reproduced Table 3 accuracy numbers | Notebook 01 + NY Fed SME / fed funds futures baselines — **metric/test code ready: `src/forecast_eval.py` (`accuracy_metrics`, `metrics_by_horizon`, `diebold_mariano`); awaits real pull** | ☐ |
| 4 | `paper/sections/3_manipulation_risk.md:51` | Per-thin-series cost-to-move dollar estimates | Notebook 02 (trailing volume / OI vs. $7M cap) — **model ready: `src/manipulation.py` (`cost_to_move`, `exposure_vs_cap`); awaits calibrated `depth_dollars`** | ☐ |
| 5 | `paper/sections/3_manipulation_risk.md:63` | Trailing volume / open interest per series | Notebook 02 real pull (feeds `depth_dollars` in `src/manipulation.py`) | ☐ |
| 6 | `paper/sections/3_manipulation_risk.md:74` | CFTC enforcement precedent (needs source verification) | Research task | ☐ |
| 7 | `paper/sections/4_institutional_pathway.md:71` | Specific FOMC-minutes / speech citations (needs source verification) | Research task | ☐ |
| 8 | `paper/sections/4_institutional_pathway.md:85` | Any formal Fed use of market-implied measures (needs source verification) | Research task | ☐ |
| 9 | `paper/sections/4_institutional_pathway.md:102` | "Sourced to" column, verified citations | Research task | ☐ |
| 10 | `paper/sections/5_polymarket_comparison.md:29` | Inventory of overlapping Polymarket FOMC/macro markets | Notebook 03 via `polymarket_api.search_markets` | ☐ |
| 11 | `paper/sections/5_polymarket_comparison.md:44` | Side-by-side Figure 1 (Kalshi vs. Polymarket) | Notebook 03 real pull | ☐ |
| 12 | `paper/sections/5_polymarket_comparison.md:60` | Per-platform accuracy metric values + event windows | Notebook 03 real pull — **metric/test code ready: `src/forecast_eval.py`; awaits real pull** | ☐ |
| 13 | `paper/sections/6_policy_recommendation.md:40` | Numeric safeguard threshold from Section 3 evidence | Derived from rows 4–5 once filled (via `src/manipulation.exposure_vs_cap`) | ☐ |

Line numbers are current as of this tracker's creation; re-grep with
`grep -rn "DATA PLACEHOLDER" paper/sections/` if the drafts have since moved.

## Analysis modules added (code-complete, awaiting real data)

Three `src/` modules extend the pipeline beyond the original ladder→pdf core.
They are tested (`tests/test_forecast_eval.py`, `tests/test_manipulation.py`,
`tests/test_event_study.py`) and run offline; they turn qualitative claims in
the drafts into runnable analysis once real pulls land.

- **`src/forecast_eval.py`** — forecast-accuracy metrics (RMSE/MAE/bias/hit-rate)
  and the Diebold–Mariano equal-predictive-accuracy test. Backs the "Kalshi is
  statistically indistinguishable from / beats" claims (rows 3, 12).
- **`src/manipulation.py`** — cost-to-move estimator benchmarked against Kalshi's
  $7M per-market cap (`exposure_vs_cap`). Quantifies Section 3 (rows 4, 5, 13).
- **`src/event_study.py`** — pre→post shifts in the mean/variance/skewness of the
  implied distribution around scheduled events (extends toward FEDS Section 7).
