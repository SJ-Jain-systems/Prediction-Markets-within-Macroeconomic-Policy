# 1. Background

Managing expectations is central to modern macroeconomic policy, and the
instruments used to measure those expectations are imperfect. Surveys —
the New York Fed's Survey of Market Expectations (SME), the Bloomberg
consensus, Blue Chip, and the Survey of Professional Forecasters — deliver
point forecasts at fixed intervals and go stale between rounds. Market-based
measures — fed funds futures, SOFR options, overnight index swaps (OIS), CPI
fixings, and TIPS breakevens — update continuously but exist only for the
contracts the market happens to trade, and can be thin. Diercks, Katz and
Wright (2026) — hereafter the FEDS paper — argue that Kalshi's macroeconomic
prediction markets add a third kind of instrument: a continuously updated,
distributionally rich, incentive-compatible measure that in several cases
covers variables (GDP, core CPI, per-meeting fed funds outcomes) for which no
options-implied distribution exists.

This section frames the project against that landscape. It does **not**
re-derive the FEDS paper's calibration methodology or accuracy results — the
strike-ladder-to-pdf conversion and the Figure 1 / Table 3 findings live in
`2_replication.md` and the notebooks. What it establishes here is the frame
the later sections stand on.

## Prediction markets as one expectations instrument among several

The FEDS paper positions Kalshi alongside surveys and derivatives rather than
as a replacement for them. The comparison below reproduces the *frame* of the
FEDS paper's instrument comparison and **adds a Polymarket column**, which the
FEDS paper does not carry — that column feeds the regulated-vs-unregulated
analysis in Section 5.

| Property | Surveys (SME, Bloomberg, SPF) | Derivatives (fed funds futures, OIS, TIPS, CPI fixings) | **Kalshi** | **Polymarket** |
|---|---|---|---|---|
| Update frequency | Periodic (stale between rounds) | Continuous | Continuous, intraday | Continuous, intraday |
| Distributional? | Rarely (mostly point/modal) | Sometimes (option-implied) | Yes — full risk-neutral pdf | Yes, if sibling markets assembled |
| Coverage of macro variables | Broad | Narrow (only traded contracts) | CPI, core CPI, PCE, unemployment, payrolls, GDP, recession, FOMC | Mostly FOMC / political; sparse macro |
| Incentive-compatible (real money) | No | Yes | Yes | Yes |
| Regulatory status | N/A | Regulated exchanges (CME, etc.) | **CFTC-regulated DCM** | Legal gray area |
| Settlement | N/A | USD | USD | USDC (on-chain) |

> **[DATA PLACEHOLDER]** The FEDS paper's own instrument-comparison table
> (Table 2) should be cited directly for the survey/derivative rows rather
> than re-characterized from memory; confirm exact wording against the PDF
> before finalizing.

## Kalshi's regulatory status — the load-bearing fact

Kalshi is the largest CFTC-approved prediction market in the United States,
operating since 2021 and classified as a **Designated Contract Market (DCM)**
— the same regulatory category as the Chicago Mercantile Exchange (FEDS paper,
p.2). Market making is provided by firms such as Susquehanna, and retail
traders reach Kalshi through brokerages like Robinhood and Webull. Each
contract is a simple Arrow–Debreu security paying $1 if a specified outcome
occurs, so the full risk-neutral pdf of an event can be reconstructed from the
set of contracts in a series.

This regulatory detail is not incidental colour — it is the fact Sections 3–5
turn on. The manipulation-risk analysis (Section 3) leans on the CFTC's
large-trader reporting and market-manipulation enforcement authority; the
institutional-legitimacy analysis (Section 4) leans on "regulated exchange"
status as the thing that makes official citation conceivable at all; and the
Polymarket comparison (Section 5) is, at bottom, a test of whether that DCM
status buys measurably better signal quality or merely a legitimacy label.

## Kalshi's macro-policy market list

The FEDS paper's Table 1 (p.8) enumerates the series most relevant to
macroeconomic policy, with their first-contract dates:

- **Inflation** — CPI MoM (Jun 2021), CPI YoY (Nov 2022), CPI for Year
  (2022), Core CPI MoM (Jun 2022), Core CPI YoY (Dec 2022), Core CPI for Year
  (2025).
- **Labor market** — Unemployment Rate (Jul 2021), Payroll Release (Mar 2023).
- **Growth** — GDP Growth quarterly (Q2 2021) and annual (2025), Probability
  of US Recession (2022, annual).
- **Monetary policy** — Federal Funds Rate Decision (May 2023) and Federal
  Funds Rate Target Rate (Dec 2021), meeting-by-meeting.

The spread of first-contract dates matters for later sections: the fed funds
rate series has a multi-year, deeply liquid history, whereas Core-CPI-for-Year
and annual GDP growth were only listed in 2025. That asymmetry is precisely
what makes the thin series the natural candidates for the manipulation-risk
analysis in Section 3.

## This project's five-part extension

The FEDS paper validates Kalshi as an accurate forecasting instrument. It does
not ask whether, or how, that instrument should enter the policy process. This
project takes up five questions that follow from that gap, mapped to the
section files:

1. **Manipulation and market-integrity risk** (`3_manipulation_risk.md`) —
   how exposed is a thin, pre-FOMC market to a motivated actor, given the $7M
   exposure cap and the very different liquidity of GDP/recession series?
2. **Institutional adoption pathway** (`4_institutional_pathway.md`) — what
   would formal Fed or Treasury use actually look like, and how does it
   compare to how OIS and TIPS breakevens are already used?
3. **Regulated vs. unregulated signal quality** (`5_polymarket_comparison.md`)
   — does CFTC regulation buy better signal, or just a legitimacy label,
   relative to Polymarket?
4. **A concrete policy recommendation** (`6_policy_recommendation.md`) — a
   specific, falsifiable proposal with named safeguards, rather than
   "further research is needed."
5. The replication that anchors all of the above (`2_replication.md`) — a
   confirmation of the FEDS paper's core accuracy result on independently
   pulled data.

## What this section deliberately does not duplicate

Calibration methodology, the strike-ladder-to-pdf conversion, and the core
accuracy results (Figure 1, Table 3) belong in `2_replication.md` and the
notebooks. The event-study results on how news moves the moments of the fed
funds distribution (FEDS Section 7) are outside this project's scope and are
cited, not reproduced.
