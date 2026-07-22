# 6. Policy Recommendation

The FEDS paper ends where academic papers usually end: "this is an accurate
forecasting tool… our goal is to facilitate further research" (p.4). That is
the right ending for a validation paper. It is the wrong ending for this one.
The whole point of the project is to take the one step the FEDS paper declines
to take — from "Kalshi is accurate" to "here is specifically how, and under
what conditions, a central bank should use it" — and to commit to a concrete,
falsifiable recommendation rather than hedging into "more research is needed."
Section 6 laid out the full menu of policy-conduct channels the data could
serve; this section selects the *minimal* defensible entry point onto that menu
and the safeguards that gate any move further along it.

## Thesis

> A Kalshi-based distributional dashboard should **supplement, not replace**,
> existing Fed expectations tools (SME, Bloomberg consensus, SPF, fed funds
> futures), and a given series should be cited in official communications or
> publications only once three safeguards are in place.

Supplement-not-replace is not timidity; it is the correct relationship. The
FEDS paper's own results show Kalshi is *comparable to*, not dominant over,
professional forecasters on most series — statistically similar to Bloomberg
for core CPI and unemployment, better for headline CPI, on par with the SME
for the fed funds rate (Sections 2, 4 of the FEDS paper). An instrument that
ties or modestly beats the incumbents, updates continuously, and adds a full
distribution is a valuable *addition* to the panel, not a replacement for it.

## Three safeguards

Each safeguard is grounded in an earlier section's finding, so the
recommendation follows from this project's evidence rather than from taste.

1. **A minimum liquidity/volume floor before a series is citable.** Grounded in
   Section 3. The fed funds rate series (hundred-million-contract volumes,
   FEDS Figure 3) is a fundamentally different object from a GDP or
   recession-probability series with a two-to-four-year history and a
   correspondingly shallow book. Propose a concrete threshold — e.g., a minimum
   open interest or trailing 7-day volume — below which a contract's price is
   *not* treated as a citable expectations measure, modeled on how the Fed
   already treats thin or sparse financial-market data with explicit caution.

   > **[DATA PLACEHOLDER]** Set the numeric threshold from Section 3's
   > cost-to-move and liquidity results (`notebooks/02`), so the floor is
   > calibrated to "deep enough that a $7M position cannot move the implied
   > probability by more than a few points," not chosen arbitrarily.

2. **Position-concentration monitoring in the pre-FOMC window**, leveraging
   Kalshi's existing CFTC large-trader reporting obligations as a DCM.
   Concretely: internally flag any FOMC-week price move attributable to a small
   number of large accounts *before* that move is treated as informative
   "market expectations" rather than one trader's bet. This directly answers
   the narrative-shaping scenario in Section 3 — the risk is not (only) illegal
   insider trading but a legal, headline-seeking large bet in a thin market —
   and it uses regulatory infrastructure that already exists for a DCM and does
   not exist for Polymarket (Section 5).

3. **Distributional framing, not point-estimate framing, with an explicit
   disclaimer.** Present mean/median/mode/variance/skew together — which the
   FEDS paper's own methodology naturally supports — rather than a single
   headline number, and label it clearly as a *retail-market-derived* measure:
   "what traders are pricing," not "what the Fed expects." This preserves the
   separation the Fed already maintains between market-implied measures and
   staff/SEP projections, and it answers the optics question from Sections 4–5:
   an official could reference it the way they already reference fed funds
   futures probabilities, without implying endorsement of betting markets as a
   policy input.

## Recommended concrete first step

Propose the *minimal* defensible step, not a sweeping one. Concretely, one of:

- a **quarterly appendix chart in the Monetary Policy Report** showing the
  Kalshi-implied fed funds distribution alongside the existing market-based
  measures, explicitly sourced to Kalshi with the three safeguards noted
  alongside; or
- a **NY Fed markets-desk-style public webpage**, paralleling how SOFR and repo
  reference data are already published, carrying only series that clear the
  liquidity floor and labeled as a retail-market measure.

This is deliberately more conservative than "cite it in the FOMC statement."
The justification is the legitimacy/optics analysis of Sections 4–5: rung (c)
communications-level citation raises the "central bank points at a market
betting on its own decisions" problem in its sharpest form, while a sourced,
safeguarded, clearly-labeled *data product* (rung (d) done carefully, or a
modest MPR appendix) delivers most of the value at much lower legitimacy risk.
Concretely, it moves Kalshi from rung (a)–(b) to a guarded (d)-flavored data
product without ever passing through the riskiest (c) form.

One refinement carries over from Section 6's reflexivity analysis. The fed
funds distribution is the deepest, most manipulation-resistant series — the
natural first candidate for an MPR appendix on liquidity grounds — but it is
also the series most exposed to reflexivity, because it prices the Committee's
*own* decision. The real-economy series (CPI, GDP, recession probability) are
the reverse: thinner and more manipulation-exposed, but genuinely exogenous to
the policy choice. The recommendation therefore favors a **displayed panel that
leads with the exogenous real-economy distributions** (subject to the liquidity
floor) and treats the fed funds distribution as a labeled cross-check rather
than the headline — so the first official-facing product is anchored on the
series where the signal is most independent of the policymaker reading it.
This is the fourth, implicit safeguard: *sequence by exogeneity, not just by
liquidity.*

## What this section must not do

It must not end on "more research is needed." That is the FEDS paper's own
ending, and reproducing it would defeat the project's purpose. The
recommendation above is specific and falsifiable: a named instrument
relationship (supplement, not replace), three named safeguards each tied to an
empirical finding, and one concrete minimal first step. Where the numbers are
not yet filled in (the liquidity threshold, the concentration-flag trigger),
the *mechanism* is still committed to — the placeholders set the value, not
whether the safeguard exists.
