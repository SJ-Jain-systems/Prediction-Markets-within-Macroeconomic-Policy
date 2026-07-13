# 2. Replication

The purpose of this section is validation, not improvement: confirm the FEDS
paper's core accuracy result on independently pulled data, so that the novel
sections (3–6) rest on a result we have reproduced ourselves rather than one
we have only cited. The bar is a qualitative match to the FEDS paper's shape
and ordering, not an exact numeric reproduction — the sample window, the
Bloomberg vendor cut, and the precise SME PDF vintage we can access will
differ from theirs.

## What we replicate

### Figure 1 — FOMC fed funds rate forecast error by days-before-meeting

The FEDS paper's headline preview (Figure 1, p.4) plots the mean absolute
forecast error of the effective federal funds rate, averaged across all FOMC
meetings since 2022, against the number of days before each meeting, comparing
Kalshi's implied mean/median/mode to fed funds futures, with the SME shown as
a one-half-standard-deviation band at the dates its surveys were completed.
The paper's stated result: **the Kalshi median and mode have a perfect
forecast record on the day before the FOMC meeting**, a statistically
significant improvement over the fed funds futures forecast, and for the fed
funds rate 150 days (three meetings) ahead Kalshi's mean absolute error is
very similar to that of professional forecasters.

The baseline pipeline is in `notebooks/01_figure1_replication.ipynb`. It
currently runs on a **synthetic strike-ladder generator** that noisily
converges to each meeting's realized rate, which demonstrates the machinery
end to end with no credentials: each day's ladder of "exceeds strike X" Yes
prices is converted to a mean/median/mode via
`src/kalshi_utils.ladder_to_pdf`, and errors are aggregated by
days-before-meeting exactly as Figure 1 does. The synthetic run reproduces the
*shape* the FEDS paper describes — errors shrinking as the meeting approaches,
the mode reaching near-zero error at the end — which confirms the pipeline is
correct before any real data is attached.

To turn this into an actual replication, swap the synthetic generator for a
real pull. `src/kalshi_api.py` provides the market-data client, and
`src/kalshi_utils.candlesticks_to_daily_ladder` bridges the last gap the
notebook flags: it takes one daily candlestick series per strike and assembles
the per-day ladder that `ladder_to_pdf` consumes.

> **[DATA PLACEHOLDER]** Insert the re-plotted Figure 1 on independently
> pulled Kalshi fed funds rate data (FEDS window: 2022–2025), with real fed
> funds futures settlement and the SME band overlaid. Report whether the
> Kalshi median/mode reach ~zero error by the meeting date on our pull, and
> whether the ordering (Kalshi ≥ futures near the meeting) holds.

### Table 3 — forecast accuracy vs. benchmarks

The FEDS paper reports MAE/RMSE for headline CPI, core CPI, and unemployment
(Kalshi mean/median/mode vs. Bloomberg consensus), and for the fed funds rate
(Kalshi vs. fed funds futures), with Diebold–Mariano significance tests. Its
qualitative findings (pp.3–4): Kalshi is **statistically similar** to the
Bloomberg consensus for core CPI and unemployment, and provides a
**statistically significant improvement** over Bloomberg for headline CPI.

> **[DATA PLACEHOLDER]** Reproduce the Table 3 numbers on our own pull. The
> specific headline-CPI comparison the project outline targets — Kalshi
> median/mode MAE ≈ 0.063 vs. Bloomberg ≈ 0.081 — should be quoted from the
> FEDS paper's Table 3 as the target to reproduce, and our reproduced values
> reported alongside with Diebold–Mariano p-values. Confirm the exact FEDS
> figures against the PDF's Table 3 before asserting them.

## Data gaps to solve (and how we handle each)

- **Kalshi trade-level data** — public and unauthenticated via
  `src/kalshi_api.py` (`list_markets`, `get_market_candlesticks`,
  `get_market_trades`). No special access. Note the module's own caveat: the
  live/historical endpoint split (Feb 2026) and token-bucket rate limiting
  (Apr 2026) mean paths and params should be verified against
  https://docs.kalshi.com before a large pull.
- **NY Fed Survey of Market Expectations** — published as per-FOMC-cycle PDFs
  (modal path + distribution), not a point-in-time downloadable series. Needs
  manual or scripted ingestion of the SME summary PDFs.
- **Bloomberg consensus** — proprietary (Bloomberg terminal). If unavailable,
  substitute a comparably timed public consensus aggregator and **flag the
  substitution explicitly** — a silent data-source swap would make this a
  "reproduction" in name only.
- **Fed funds futures settlement** — CME data; historical intraday may need a
  paid feed, but end-of-day settlement prices are sufficient here because the
  FEDS comparison is itself low-frequency (daily).

## What "success" looks like

A re-plotted Figure 1 on our own pull that qualitatively matches the FEDS
paper's shape: errors shrinking as the FOMC meeting approaches, Kalshi
median/mode reaching ~zero error near the meeting date, and broad overlap with
the SME's one-half-standard-deviation band. Exact numeric agreement is not the
bar — window, vendor cut, and SME vintage differences are expected and should
be disclosed rather than tuned away.
