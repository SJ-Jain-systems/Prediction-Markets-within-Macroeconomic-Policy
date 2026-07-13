# 3. Manipulation and Market Integrity Risk

The FEDS paper gives market manipulation a single sentence — a citation to
Hanson and Oprea (2009) in its discussion of why prediction markets can remain
informative (around p.6). For a paper whose thesis is "this instrument is
accurate enough for researchers and policymakers to use," that is a thin
treatment of the question a policymaker would ask first: *can this number be
pushed around, and if so, where?* This section is the empirical core of the
"should the Fed trust this" argument. Its claim is narrow and defensible:
Kalshi's most-watched series is very hard to move, but the FEDS paper's own
framing obscures how different the thin series are, and it is the thin series
that a motivated actor would target.

## Facts already in the FEDS paper to build from

- **The $7 million per-market exposure cap.** "Kalshi's maximum exposure per
  market currently reaches $7 million" (p.8, "Competing Platforms"). The FEDS
  paper presents this as a *maturity advantage* over Polymarket and PredictIt.
  It is also, read from the other side, the ceiling a single manipulator's
  legal position must fit inside — or evade, via multiple accounts.
- **The fed funds rate series is demonstrably deep.** The FEDS paper documents
  daily volumes "frequently above a million" and peaking near ~100 million
  contracts around a September FOMC meeting (Figure 3, p.12). This is the most
  liquid, most FOMC-attention-grabbing series on the platform. Against
  hundred-million-contract volume, a $7M position is a rounding error, and the
  Hanson–Oprea robustness argument is at its strongest.
- **The thin series have no equivalent volume figures.** The paper gives no
  volume data for GDP growth, probability of recession, or core CPI-for-year —
  series with much shorter listing histories (Table 1: Core-CPI-for-Year began
  2025, Probability-of-Recession began 2022, annual GDP growth 2025). These
  are the natural candidates for thin-market risk, and the FEDS paper simply
  does not look at them from this angle.
- **What Hanson and Oprea (2009) actually shows.** Prediction markets can stay
  informative *in the presence of* manipulation, because a manipulator who
  distorts the price effectively subsidizes informed traders who profit by
  trading against the distortion. This is an equilibrium result about
  robustness on average. It does **not** guarantee that any individual
  pre-announcement snapshot is manipulation-proof — least of all in a thin
  market over a short window (the 24–48 hours before an FOMC decision), where
  informed counter-trading may simply not arrive in time to correct a push.

## Research questions to answer with real data

1. **Cost-to-move.** For the thinnest series (GDP growth, recession
   probability), what does order-book depth look like a day or two before a
   scheduled release, and how many dollars would it take to move the implied
   probability by, say, 10 percentage points? Compare that figure to (a) the
   $7M cap and (b) the size of position a bank, hedge fund, or PAC could
   plausibly and legally take.

   > **[DATA PLACEHOLDER]** Cost-to-move dollar estimates per thin series, from
   > real order-book depth in the pre-release window. See
   > `notebooks/02_liquidity_comparison.ipynb`, which builds the liquidity
   > comparison and leaves an explicit seam for the depth-based cost-to-move
   > calculation once real book data is pulled.

2. **Does the $7M cap bind where it matters?** The cap is almost certainly
   irrelevant for the fed funds rate market (hundred-million-contract volumes
   make $7M trivial) but may be highly binding — or, conversely, trivially
   evadable via multiple accounts — in a thin GDP or recession market where
   $7M could be a large share of total open interest.

   > **[DATA PLACEHOLDER]** For each series, report trailing volume / open
   > interest and express $7M as a share of it. The bar chart in
   > `notebooks/02_liquidity_comparison.ipynb` (cell 5) is the scaffold for
   > this; swap synthetic volumes for a real pull.

3. **Regulatory backstop.** Kalshi's DCM status subjects it to CFTC oversight
   — large-trader reporting and market-manipulation enforcement authority that
   do not apply to Polymarket. Research whether the CFTC has taken any
   manipulation-related enforcement action against a DCM prediction market, and
   assess the *actual* deterrent value versus a purely theoretical backstop.

   > **[DATA PLACEHOLDER — needs source verification]** Any CFTC enforcement
   > action against a DCM prediction market for manipulation. Cite the specific
   > action or state explicitly that none was found; do not assert a deterrent
   > record that has not been verified against CFTC records.

4. **The scenario the paper doesn't model.** The FEDS paper's own July 2025
   example (p.4) — the implied probability of a July rate cut rising to 25%
   after remarks from Governors Waller and Bowman, then falling on a stronger
   June jobs report — shows how sharply these markets react to communications.
   Now invert it: a bank or PAC with a communications edge trades *ahead* of an
   anticipated dovish signal on a thin Kalshi market, specifically to shape the
   "markets expect X" narrative that press and commentary then repeat.
   Distinguish carefully:
   - **Illegal insider trading** — trading on material non-public information
     obtained improperly. Already unlawful; a legal question, not a market-
     design one.
   - **Legal but narrative-shaping large directional bets** — a permissible
     position taken in a thin market whose *point* is the headline it
     generates, not the P&L. This is the harder case, and the one a citation
     policy has to price in, because it is not obviously illegal and is exactly
     what a thin, publicly quoted, Fed-adjacent market invites.

## What the supporting notebook builds

`notebooks/02_liquidity_comparison.ipynb` pulls daily volume/open-interest for
**every** Table 1 series (not just the fed funds rate) and plots liquidity by
series on a common log scale, with the $7M cap overlaid. The single chart —
"here is how much thinner GDP and recession markets are than the fed funds
market the FEDS paper focuses on" — is the most persuasive original piece of
evidence this project can add. It ships with a synthetic volume generator so it
runs offline; the real pull is a drop-in once outbound Kalshi access exists.

## The section's conclusion (to firm up once the numbers land)

The fed funds rate series is robust enough that the Fed could treat it much as
it treats fed funds futures. The thin series are a different animal, and the
$7M cap that reassures in the deep market is either binding-but-evadable or
simply large relative to the book in the shallow ones. That asymmetry is the
empirical basis for the **minimum-liquidity-floor safeguard** proposed in
Section 6: a series should not be citable as an expectations measure until its
depth clears a threshold, precisely so that the manipulation surface analyzed
here is closed before any official reliance begins.
