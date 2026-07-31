# Kalshi and the Institutionalization of Macro Prediction Markets

[![CI](https://github.com/sj-jain-systems/prediction-markets-within-macroeconomic-policy/actions/workflows/ci.yml/badge.svg)](https://github.com/sj-jain-systems/prediction-markets-within-macroeconomic-policy/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Diercks, Katz and Wright (2026), "Kalshi and the Rise of Macro Markets" (FEDS
2026-010), showed that Kalshi's macro prediction markets forecast about as well
as the professionals. This project starts where that paper ends. It takes the
accuracy result as settled and asks the question the paper deliberately leaves
alone: now that we know the instrument is accurate, should a public institution
actually use it, how far, and with what protections?

A copy of the paper is in `references/diercks_katz_wright_2026.pdf`, and the
argument built on top of it lives in `paper/sections/`.

## The one thing to know before you read anything else

The code runs, the tests pass, and the notebooks produce the figures. But the
empirical sections currently run on **synthetic data**. Every notebook ships a
generator so it works offline with no credentials, and every place a real
Kalshi number belongs is marked `[DATA PLACEHOLDER]`. So when a section says it
"replicates Figure 1," it means the pipeline reproduces the *shape* of the
result on simulated ladders. It has not been re-plotted on a real pull yet.
That pull is the next job, and `TODO.md` is the honest list of what is still
missing.

I would rather you know that up front than discover it three sections in.

## What the paper already settled, and what I am adding

The FEDS paper does the hard empirical work, and none of this project is
possible without it. In short, it establishes:

- Kalshi is the largest CFTC-approved prediction market, a Designated Contract
  Market in the same regulatory category as the CME, trading contracts on CPI,
  core CPI, PCE, unemployment, payrolls, GDP, recession probability, and FOMC
  rate decisions.
- A model-free way to turn a ladder of "exceeds strike X" contracts into a full
  risk-neutral probability distribution.
- Forecasts that are statistically indistinguishable from the NY Fed survey and
  fed funds futures on the policy rate, and that beat the Bloomberg consensus on
  headline CPI.
- Event-study evidence that news moves the variance and skew of the implied
  distribution, not just its mean.

What the paper does not ask is whether or how that instrument should enter the
policy process. This project picks up six threads from that gap:

1. **Replication.** Reproduce the density method and the accuracy result on
   independently pulled data, so the rest rests on something checked here rather
   than only cited.
2. **Manipulation risk.** The deep fed funds market is very hard to move. The
   thin series (GDP, recession probability) are a different animal, and it is
   the thin ones a motivated actor would target.
3. **Institutional pathway.** What formal Fed or Treasury use would actually
   look like, measured against how OIS paths and TIPS breakevens are already
   cited.
4. **Regulated vs. unregulated signal.** A head-to-head against Polymarket to
   test whether CFTC regulation buys a better signal or just a cleaner story.
5. **Policy implementation.** Which concrete channels a distributional signal
   could serve, what the distribution adds over the point estimates officials
   already have, and where the reflexivity of acting on a market that bets on
   the Fed's own decisions makes use unsafe. One channel, statutory fiscal
   triggers, gets explicitly ruled out.
6. **A concrete recommendation.** A specific, falsifiable proposal with named
   safeguards, instead of "more research is needed."

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .              # puts the src/ modules on your path
jupyter notebook notebooks/01_figure1_replication.ipynb
```

Installing with `-e .` makes `kalshi_utils`, `policy_signals`, and the rest
importable from anywhere, so the `sys.path.append("../src")` line in each
notebook is just a fallback. If you only want the runtime dependencies,
`pip install -r requirements.txt` still works.

To hack on it:

```bash
pip install -e ".[dev]"       # adds pytest, ruff, nbconvert, pre-commit
pytest                        # the src/ pipeline is covered
ruff check .                  # lint
pre-commit install            # optional: ruff + nbstripout on every commit
```

CI runs the linter, the tests, and all three notebooks offline on Python 3.11
and 3.12, so a broken pipeline gets caught before it lands.

## What is where

```
├── paper/sections/       the actual argument, one file per section (1–7)
├── notebooks/
│   ├── 01_figure1_replication.ipynb   the density method + Figure 1 shape
│   ├── 02_liquidity_comparison.ipynb  how thin the thin series really are
│   └── 03_polymarket_comparison.ipynb Kalshi vs. Polymarket, same pipeline
├── src/
│   ├── kalshi_utils.py       ladder -> risk-neutral pdf -> mean/median/mode/…
│   ├── ladder_validation.py  no-arbitrage screen; run it before ladder_to_pdf
│   ├── policy_signals.py     fed funds ladder -> cut/hold/hike + opposite_tail_prob
│   ├── forecast_eval.py      RMSE/MAE/bias + Diebold–Mariano (Table 3 machinery)
│   ├── calibration.py        Brier + reliability: tests the probabilities as probabilities
│   ├── event_study.py        how variance/skew jump around FOMC events
│   ├── manipulation.py       prototype cost-to-move for a thin market
│   ├── kalshi_api.py         thin read-only Kalshi market-data client
│   └── polymarket_api.py     thin read-only Polymarket client (Gamma + CLOB)
├── tests/                pytest suite for the pipeline above
├── docs/                 data_schema.md + paper_integration_ideas.md
├── references/           the FEDS paper + Sumner (2018) + Snowberg–Wolfers–Zitzewitz (2012)
├── data/                 raw + processed pulls (gitignored)
├── TODO.md               the honest what-is-left list
└── pyproject.toml        packaging + ruff/pytest config
```

## A note on data and network access

Both the Kalshi and Polymarket market-data endpoints are public and
unauthenticated, but they are still external services. Sandboxed environments
(CI, locked-down egress) may block `api.kalshi.com` and
`gamma-api.polymarket.com`, which is exactly why the notebooks fall back to
synthetic data. To pull the real thing, run them somewhere with outbound HTTPS
to those hosts and flip the `USE_REAL_DATA` flag in notebooks 02 and 03 (and
swap the generator in notebook 01). One caveat worth heeding: Kalshi split its
live and historical endpoints (Feb 2026) and added token-bucket rate limiting
(Apr 2026), so verify current paths against <https://docs.kalshi.com> before a
large pull.

A faithful replication also needs a couple of things the code cannot conjure:
the NY Fed Survey of Market Expectations PDFs, and the Bloomberg consensus. The
latter is proprietary, so it will need a substitute or a data-sharing
arrangement, and any substitution should be called out loudly rather than
slipped in quietly.

## License and citation

Code, notebooks, and prose here are MIT-licensed (see `LICENSE`), © 2026
SJ-Jain-Systems. The bundled FEDS working paper is a U.S. Federal Reserve Board
work included for reference under its own terms; cite it via the DOI below.

> Diercks, Anthony M., Jared Dean Katz, and Jonathan H. Wright (2026). "Kalshi
> and the Rise of Macro Markets," Finance and Economics Discussion Series
> 2026-010. Washington: Board of Governors of the Federal Reserve System.
> <https://doi.org/10.17016/FEDS.2026.010>
