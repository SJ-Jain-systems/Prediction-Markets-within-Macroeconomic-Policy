# Deliverable manifest — Kalshi macro-policy repo completion

All files are at their repo-relative paths; unzip over the repo root to apply.
NOTHING was committed or pushed — review and push manually.

## Modified
- README.md                              (removed stray line-3 note; registered new files; added Network/data-access section)
- src/kalshi_utils.py                     (added candlesticks_to_daily_ladder helper; existing functions unchanged)

## New — code
- src/polymarket_api.py                   (read-only Polymarket client: Gamma + CLOB; mirrors kalshi_api.py)

## New — notebooks (run offline on synthetic data; USE_REAL_DATA flag for live pulls)
- notebooks/02_liquidity_comparison.ipynb (thin-market volume/OI by series — grounds section 3)
- notebooks/03_polymarket_comparison.ipynb (Kalshi vs Polymarket Figure-1-style — grounds section 5)

## Rewritten — paper sections (outlines -> full prose with [DATA PLACEHOLDER] callouts)
- paper/sections/1_background.md
- paper/sections/2_replication.md
- paper/sections/3_manipulation_risk.md
- paper/sections/4_institutional_pathway.md
- paper/sections/5_polymarket_comparison.md
- paper/sections/6_policy_recommendation.md

## Unchanged (present in working copy for verification only; not part of the diff)
- src/kalshi_api.py, notebooks/01_figure1_replication.ipynb, requirements.txt,
  references/diercks_katz_wright_2026.pdf, data/

## Verification run before delivery
- imports OK (kalshi_api, kalshi_utils, polymarket_api)
- candlesticks_to_daily_ladder unit check PASSED (error shrinks toward event)
- all 3 notebooks executed headless (MPLBACKEND=Agg) with NO errors, NO network
