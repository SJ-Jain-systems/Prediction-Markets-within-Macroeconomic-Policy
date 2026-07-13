# 5. Regulated vs. Unregulated Signal Quality: Kalshi vs. Polymarket

The FEDS paper compares Kalshi to itself and to traditional instruments —
surveys, futures, options — but never to another prediction market. Polymarket
appears exactly once, to be dismissed: "Polymarket operates in a legal gray
area and, along with PredictIt and Interactive Brokers, supports fewer
contracts, lower liquidity, and smaller individual position limits" (p.8). The
paper leans on Kalshi's regulated status as a reason to prefer it, but never
tests whether that status buys measurably better *signal*, as opposed to a
cleaner legal and legitimacy story. This section runs the comparison the FEDS
paper skips — and is careful about what it can and cannot conclude.

## The opening the FEDS paper leaves

The FEDS paper cites, without engaging, **Eichengreen, Viswanath-Natraj, Wang
and Wang (2025)** (p.8), who use *Polymarket* data to study questions around
Fed independence. That is a natural bridge: Polymarket demonstrably carries
Fed-adjacent contracts that researchers already treat as informative, so a
head-to-head on the overlapping contracts is feasible rather than hypothetical.

## What this section does that the FEDS paper doesn't

1. **Identify the overlapping contracts.** Find Polymarket's Fed/macro markets
   contemporaneous with the Kalshi series the FEDS paper studies — FOMC rate
   decisions at minimum. Polymarket may have no direct analog for
   CPI/GDP/unemployment; verify what actually exists rather than assuming
   symmetry.

   > **[DATA PLACEHOLDER]** Inventory of Polymarket FOMC/macro markets with
   > liquidity and date coverage, pulled via `src/polymarket_api.py`
   > (`search_markets`, `list_event_markets`). Note which Kalshi series have no
   > Polymarket counterpart.

2. **Run the same pipeline on both.** Polymarket lists a Fed decision as a set
   of *sibling* YES/NO markets rather than a single strike ladder, so the
   ladder must be assembled from the siblings before conversion.
   `polymarket_api.fed_ladder_from_markets` does that assembly, and the result
   feeds the *same* `kalshi_utils.candlesticks_to_daily_ladder` →
   `ladder_to_pdf` path used for Kalshi. `notebooks/03_polymarket_comparison.ipynb`
   reproduces the Figure-1-style forecast-error-by-days-before-FOMC chart with
   both platforms overlaid (synthetic fallback so it runs offline; real-pull
   seam flagged).

   > **[DATA PLACEHOLDER]** The side-by-side Figure 1 (Kalshi solid vs.
   > Polymarket dashed) on real pulls, plus a Table-3-style MAE/RMSE row for
   > each platform.

3. **Test "regulation improves signal quality" directly**, rather than
   asserting it. Candidate metrics:
   - **Forecast error (MAE/RMSE)** — does Kalshi actually forecast the FOMC
     outcome better, or does it merely have more contracts and cleaner data?
   - **Bid-ask spread / price staleness** — does CFTC market-maker
     infrastructure (Susquehanna) produce tighter, fresher markets than
     Polymarket's automated-market-maker / peer-to-peer liquidity?
   - **Divergence around controversial events** — around a Fed-independence
     episode of the kind Eichengreen et al. study, does Polymarket's
     pseudonymous, crypto-native base price the tails systematically
     differently than Kalshi's KYC'd, partly-institutional base?

   > **[DATA PLACEHOLDER]** Metric values per platform, with the event windows
   > used spelled out.

4. **State the confound honestly.** Kalshi and Polymarket differ in far more
   than regulatory status: user-base composition (KYC'd/partly-institutional
   vs. pseudonymous/crypto-native), contract design (strike ladder vs. sibling
   binaries), settlement currency (USD vs. USDC), position limits, and listing
   history. A clean *causal* "CFTC regulation → better signal" claim is not
   identified from observational data across two platforms that differ on all
   of these axes at once. Frame any observed gap as **suggestive, not causal**,
   unless the evidence is unusually strong. `notebooks/03` states these
   confounds inline (cell 5) so the caveat travels with the chart.

## Deliverable for this section

A side-by-side version of the FEDS paper's Figure 1 (or a Table 3 row) with a
Polymarket series added, plus two to three paragraphs on what the comparison
does and does not tell us about whether CFTC regulation is doing real work for
signal quality — as opposed to functioning purely as a legal and legitimacy
label. The honest expected finding: regulation plausibly buys tighter, less
stale markets and a cleaner manipulation backstop (Section 3), but a decisive
*forecast-accuracy* edge is hard to establish across platforms this
different — which is itself a useful, publishable result, and one the FEDS
paper's one-sentence dismissal never earns.
