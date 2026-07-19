# Kalshi and the Institutionalization of Macro Prediction Markets

[![CI](https://github.com/sj-jain-systems/prediction-markets-within-macroeconomic-policy/actions/workflows/ci.yml/badge.svg)](https://github.com/sj-jain-systems/prediction-markets-within-macroeconomic-policy/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

This project extends **Diercks, Katz, and Wright (2026), "Kalshi and the Rise of
Macro Markets,"** Finance and Economics Discussion Series 2026-010, Federal
Reserve Board (the "FEDS paper"). A copy is included at
`references/diercks_katz_wright_2026.pdf`.

## What the FEDS paper already establishes (not duplicated here)

- Kalshi is the largest CFTC-approved prediction market (a "Designated
  Contract Market," the same regulatory category as the CME), trading
  contracts on CPI, core CPI, PCE, unemployment, payrolls, GDP growth,
  recession probability, and FOMC rate decisions (Table 1).
- A model-free method for converting a ladder of binary "exceeds strike X"
  contract prices into a full risk-neutral probability density function
  (Section 3).
- Kalshi's fed funds rate forecasts are statistically indistinguishable from
  (and on some metrics better than) the NY Fed's Survey of Market
  Expectations and fed funds futures (Figure 1, Table 3); headline CPI
  forecasts significantly beat the Bloomberg consensus.
- Event-study evidence that macro news and FOMC communications move not just
  the mean but the variance and skewness of the implied fed funds rate
  distribution (Sections 7).

## The gap this project addresses

The FEDS paper validates Kalshi as an accurate forecasting instrument. It
does **not** ask whether, or how, that instrument should be built into the
policy process. Five questions follow from that gap:

1. **Institutional adoption pathway** — What would it actually mean for the
   Fed or Treasury to use Kalshi data formally (dashboard, Beige Book
   citation, standing data feed), and how does that compare to how OIS and
   TIPS breakevens are already used?
2. **Manipulation and market integrity risk** — The FEDS paper cites Hanson
   and Oprea (2009) in one sentence. Given Kalshi's $7M per-market exposure
   cap and the much thinner liquidity in series like GDP growth and
   recession probability (vs. the multi-million-to-hundred-million-dollar
   volumes seen in the fed funds rate series, Figures 2–3 of the FEDS
   paper), how exposed is a pre-FOMC market to a motivated actor?
3. **Political economy and optics** — Should a central bank reference a
   market where the public is betting on its own decisions? This is a
   legitimacy question distinct from forecast accuracy, and the FEDS paper
   does not raise it.
4. **Regulated vs. unregulated signal quality** — The FEDS paper mentions
   Polymarket only to dismiss it as operating "in a legal gray area" with
   lower liquidity and looser position limits. It does not run a
   side-by-side comparison. Eichengreen, Viswanath-Natraj, Wang and Wang
   (2025), cited in passing by the FEDS paper, use Polymarket data on Fed
   independence questions — a natural bridge for that comparison.
5. **A concrete policy recommendation** — The FEDS paper stops at
   validation. This project ends with an actual proposal and named
   safeguards.

## Repo structure

```
kalshi-macro-policy/
├── data/                          # raw + processed Kalshi/Polymarket pulls (gitignored by default)
├── notebooks/
│   ├── 01_figure1_replication.ipynb    # baseline: replicates FEDS Figure 1 methodology
│   ├── 02_liquidity_comparison.ipynb   # new: thin-market volume/OI by series (grounds section 3)
│   └── 03_polymarket_comparison.ipynb  # new: Kalshi vs. Polymarket Figure-1-style (grounds section 5)
├── paper/
│   └── sections/
│       ├── 1_background.md            # framing vs. the FEDS paper
│       ├── 2_replication.md           # your validation of their findings
│       ├── 3_manipulation_risk.md     # new: exposure limits, thin markets, manipulation
│       ├── 4_institutional_pathway.md # new: how the Fed could formally use this
│       ├── 5_polymarket_comparison.md # new: regulated vs. unregulated signal quality
│       └── 6_policy_recommendation.md # new: the actual proposal
├── src/
│   ├── kalshi_utils.py            # ladder-of-strikes -> pdf -> mean/median/mode (paper's Section 3 method);
│   │                              #   candlesticks_to_daily_ladder bridges the API to the pdf pipeline
│   ├── kalshi_api.py              # thin client for Kalshi's public market-data API
│   └── polymarket_api.py          # new: thin read-only client for Polymarket (Gamma + CLOB), for section 5
│                                  #   (src/ is installed as importable modules via pyproject.toml)
├── tests/                        # new: pytest suite for the src/ pipeline
│   ├── test_kalshi_utils.py      #   ladder->pdf, daily ladder, forecast-error helper
│   └── test_api_clients.py       #   URL building, pagination, retry wiring (HTTP mocked)
├── docs/
│   └── data_schema.md            # new: shapes a real Kalshi/Polymarket pull must have
├── references/
│   └── diercks_katz_wright_2026.pdf
├── .github/workflows/ci.yml      # new: lint + tests + offline notebook execution
├── .pre-commit-config.yaml       # new: ruff, ruff-format, nbstripout
├── pyproject.toml                # new: packaging + ruff/pytest config
├── TODO.md                       # new: [DATA PLACEHOLDER] tracker
├── LICENSE                       # new: MIT
├── requirements.txt
└── README.md
```

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .              # installs the src/ modules as importable packages
jupyter notebook notebooks/01_figure1_replication.ipynb
```

Installing with `-e .` puts `kalshi_utils`, `kalshi_api`, and `polymarket_api`
on the path directly, so imports work from anywhere (the `sys.path.append("../src")`
line in each notebook is then just a no-network fallback). `pip install -r
requirements.txt` still works if you only want the runtime dependencies.

## Development

```bash
pip install -e ".[dev]"      # runtime deps + pytest, ruff, nbconvert, pre-commit
pytest                       # unit tests for the src/ pipeline (tests/)
ruff check .                 # lint
pre-commit install           # optional: run ruff + nbstripout on every commit
```

`.github/workflows/ci.yml` runs the linter, the tests, and executes all three
notebooks offline (synthetic data, no network) on Python 3.11 and 3.12, so a
broken pipeline or notebook is caught in CI.

See [`TODO.md`](TODO.md) for the tracker of every `[DATA PLACEHOLDER]` in the
paper drafts (which notebook / pull fills each), and
[`docs/data_schema.md`](docs/data_schema.md) for the exact shape a real Kalshi /
Polymarket pull must have to drop into the `src/` helpers.

All three notebooks ship with a **synthetic data generator** so they run end
to end with no credentials and no network. Swap in real pulls via
`src/kalshi_api.py` / `src/polymarket_api.py` (both platforms' market-data
endpoints are public and unauthenticated) once you're ready to reproduce
Figure 1, the liquidity comparison, and the Polymarket comparison on real
trade-level data. See `paper/sections/2_replication.md` for what a faithful
replication additionally needs (NY Fed SME PDFs, Bloomberg consensus — the
latter is proprietary and will need a substitute or a data-sharing
arrangement).

## Network / data access

The Kalshi and Polymarket market-data endpoints are public and unauthenticated,
but they are **external services**. Restricted or sandboxed environments (CI,
locked-down egress policies) may block `api.kalshi.com` and
`gamma-api.polymarket.com` — the notebooks are written to fall back to synthetic
data so they still run there. To pull *real* data, run them in an environment
with outbound HTTPS access to those hosts, and flip the `USE_REAL_DATA` flag in
notebooks 02/03 (and swap the synthetic generator in notebook 01). The Kalshi
client also carries a caveat about the live/historical endpoint split (Feb 2026)
and token-bucket rate limiting (Apr 2026) — verify current paths against
https://docs.kalshi.com before a large pull.

## Suggested order of work

1. Run the notebooks as-is (synthetic data) to confirm the pipelines work.
2. Point `kalshi_api.py` at real Kalshi fed funds rate series and re-run
   notebook 01 — this gives you an actual replication of Figure 1, which
   anchors `2_replication.md`. Use `kalshi_utils.candlesticks_to_daily_ladder`
   to turn per-strike candlesticks into the daily ladder the figure needs.
3. Pull volume/open-interest data for the *thin* series (GDP, recession
   probability, core CPI annual) via notebook 02, to ground
   `3_manipulation_risk.md` in real numbers instead of the FEDS paper's
   qualitative treatment.
4. Pull overlapping Polymarket FOMC markets via `polymarket_api.py` and run
   notebook 03 for the regulated-vs-unregulated comparison in
   `5_polymarket_comparison.md`.
5. Research and firm up `4_institutional_pathway.md` (FOMC minutes, speeches,
   MPR — the source-verification `[DATA PLACEHOLDER]` items) — a literature/
   policy section, not a data section.
6. Finalize `6_policy_recommendation.md` last, once 3–5 give you concrete
   evidence to set the safeguard thresholds.

The section drafts are complete prose with `[DATA PLACEHOLDER]` callouts
marking every spot where a real number or a source-verified citation must be
swapped in once the corresponding data pull is done.

## License

Code, notebooks, and prose in this repository are released under the MIT License
(see [`LICENSE`](LICENSE)), © 2026 SJ-Jain-Systems. The bundled FEDS working
paper (`references/diercks_katz_wright_2026.pdf`) is a U.S. Federal Reserve Board
work reproduced for reference under its own terms — cite it via the DOI below.

## Citation

Diercks, Anthony M., Jared Dean Katz, and Jonathan H. Wright (2026). "Kalshi
and the Rise of Macro Markets," Finance and Economics Discussion Series
2026-010. Washington: Board of Governors of the Federal Reserve System,
https://doi.org/10.17016/FEDS.2026.010.
