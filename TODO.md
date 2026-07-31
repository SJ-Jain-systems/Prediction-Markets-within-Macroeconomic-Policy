# What is left to do

This is the honest running list. The code and the section drafts are done; what
is missing is real data and a handful of citations I refuse to fabricate. Every
item below corresponds to a `[DATA PLACEHOLDER]` somewhere in `paper/sections/`,
and the whole project is designed so that filling these in is a swap, not a
rewrite.

The rough order of attack: get one real Kalshi pull working, let it flow through
the notebooks, then chase down the source-verification items in parallel.

## First, and it unblocks almost everything: a real Kalshi pull

- [ ] Point `src/kalshi_api.py` at the real fed funds rate series and re-run
      notebook 01. Use `kalshi_utils.candlesticks_to_daily_ladder` to turn the
      per-strike candlesticks into the daily ladder Figure 1 needs. This is the
      thing that turns "reproduces the shape" into an actual replication.
- [ ] Before any large pull, check current endpoint paths against
      <https://docs.kalshi.com>. Kalshi split live vs. historical (Feb 2026) and
      added rate limiting (Apr 2026), so the client's assumptions may have drifted.

## Replication (section 2)

- [ ] Re-plot Figure 1 on the real pull: mean absolute error by
      days-before-meeting, with real fed funds futures settlement and the NY Fed
      survey band overlaid. Report whether the Kalshi median/mode reach roughly
      zero error by the meeting date, and whether the ordering holds.
- [ ] Reproduce the Table 3 numbers (MAE/RMSE for headline CPI, core CPI,
      unemployment, fed funds) with Diebold–Mariano p-values. Confirm the exact
      FEDS figures against the PDF before quoting them as targets.
- [ ] Get the NY Fed Survey of Market Expectations PDFs and script their
      ingestion (they publish as per-cycle PDFs, not a clean series).
- [ ] Sort out the Bloomberg consensus. It is proprietary. If it is not
      available, substitute a comparable public aggregator and flag the
      substitution loudly. A silent swap makes this a "reproduction" in name only.

## Manipulation risk (section 3)

- [ ] Pull daily volume and open interest for every Table 1 series in
      notebook 02, and produce the liquidity chart with the $7M cap overlaid.
      This is probably the single most persuasive original piece of evidence the
      project has, and it currently runs on synthetic volumes.
- [ ] Compute cost-to-move: from real order-book depth in the pre-release
      window, how many dollars would move a thin series by ~10 points? Compare
      to the $7M cap and to a position a bank or PAC could plausibly take.
- [ ] Express $7M as a share of trailing volume / open interest per series, so
      the "binding here, trivial there" claim has numbers behind it.
- [ ] (Verify) Has the CFTC ever taken a manipulation action against a DCM
      prediction market? Cite the specific action or state plainly that none was
      found. Do not imply a deterrent record that has not been checked.
- [ ] Optional but nice: run the weak-form-efficiency (ADF / KPSS) screen on the
      deep fed funds series vs. the thin ones, to turn the liquidity floor into a
      data-driven threshold rather than a round number.

## Institutional pathway (section 4)

- [ ] (Verify) Find real FOMC-minutes, MPR, or speech citations of OIS paths,
      futures-implied probabilities, and TIPS breakevens, with dates, to fill the
      "Sourced to" column of the comparison table. Mark anything unverified as an
      inference rather than inventing a citation.
- [ ] (Verify) Does Treasury, BLS, or CBO cite any prediction-market data in a
      formal capacity? Reasonable prior is no; either way, say so explicitly.

## Polymarket comparison (section 5)

- [ ] Inventory Polymarket's Fed/macro markets contemporaneous with the Kalshi
      series, via `src/polymarket_api.py`. Note which Kalshi series have no
      Polymarket counterpart rather than assuming symmetry.
- [ ] Run notebook 03 on real pulls: the side-by-side Figure 1 (Kalshi solid,
      Polymarket dashed) plus a Table-3-style MAE/RMSE row per platform.
- [ ] Fill in the per-platform metric values (forecast error, bid-ask spread /
      staleness, divergence around a Fed-independence episode), with the event
      windows spelled out. Keep the "suggestive, not causal" framing.

## Policy implementation (section 6)

- [ ] (Verify) Do TBAC materials or Treasury's Office of Debt Management already
      reference market-implied rate *distributions*, as opposed to the
      futures-implied path? Cite the document or note that none was found.
- [ ] (Verify) Any reference to prediction-market data by a non-US central bank
      (BoE, ECB, BoJ) or an international body (BIS, IMF)? Prior is none in a
      formal capacity, which would reinforce the "US-specific, novel territory"
      framing.

## Policy recommendation (section 7)

- [ ] Set the numeric liquidity-floor threshold from the section 3 cost-to-move
      results, so it is calibrated to "deep enough that a $7M position cannot
      move the implied probability by more than a few points," not picked out of
      the air.

## Housekeeping

- [ ] `tests/test_callibration.py` is an empty file with a typo in the name.
      Either write the calibration tests there or rename it to
      `test_calibration.py`.
- [ ] Once real data lands, revisit each section and delete the
      `[DATA PLACEHOLDER]` callouts as they get filled, so the drafts stop
      advertising gaps that no longer exist.
