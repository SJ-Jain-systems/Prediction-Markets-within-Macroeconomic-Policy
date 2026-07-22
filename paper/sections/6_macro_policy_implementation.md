# 6. Macroeconomic Policy Implementation

Section 4 asks *whether* and *at what institutional level* Kalshi data should be
cited; Section 7 asks *under what safeguards*. Neither answers the question a
policy staff would reach next: once you trust the signal and have safeguarded
it, what do you *mechanically do* with a continuously-updated, distributionally
rich, market-implied measure that you cannot already do with a survey point
estimate or a single futures-implied probability? This section maps the concrete
channels of macroeconomic-policy conduct — monetary, fiscal / debt-management,
and macroprudential — through which such a signal could be operationalized. It
is deliberately even-handed: for each channel it separates what is *genuinely
enabled by the distribution* (the new object the FEDS paper delivers) from what
merely re-packages information officials already hold, and it names one channel
where the honest recommendation is *do not implement*.

The section is a public-policy argument, not a trading argument. The question is
not "can you make money on this data" but "does incorporating it improve the
quality, timeliness, or transparency of a public decision — and at what cost to
legitimacy and to the integrity of the signal itself."

## The unit of new information is the distribution, not the point

The discipline for this whole section: a Kalshi series' *mean* is largely
redundant with instruments the Fed already watches — the fed funds futures
strip, the OIS-implied path, TIPS breakevens. If all Kalshi added were another
point estimate of the modal rate path, the implementation payoff would be
marginal. The FEDS paper's actual contribution is the full risk-neutral pdf
reconstructed from the strike ladder (their Section 3; replicated in our
`2_replication.md`), and the marginal product of that pdf lives in its *higher
moments* — variance, skew, and the tails — for horizons and variables where no
option-implied distribution exists (per-meeting fed funds outcomes, core CPI,
GDP, recession).

The FEDS paper's own event study (their Section 7) shows that macro news and
FOMC communications move not just the mean but the variance and skewness of the
implied fed funds distribution. That is the load-bearing empirical fact for this
section: the higher moments *respond* to policy-relevant events, so they carry
information, so a policymaker who reads only the mean is discarding the part of
the signal that is genuinely new. Every channel below is evaluated on whether it
uses that new part.

## Channel 1 — Monetary policy conduct

### 1a. Calibrating and stress-testing forward guidance

The FOMC communicates a modal path — the quarterly Summary of Economic
Projections "dot plot" — while markets price a continuous distribution daily.
Two operational uses follow, both of which use the distribution rather than a
point:

- **Gap detection between SEP rounds.** The divergence between the SEP median
  dot and the Kalshi-implied median/mode for the *same* horizon is a
  continuously-updated read on whether the market has absorbed the Committee's
  signal, available on the ~80 days between quarterly SEP releases when the dot
  plot is silent. This is a "is guidance landing?" gauge the Fed does not
  currently have in distributional form.
- **Credibility of state-contingent guidance.** When the Committee signals
  "higher for longer," the test of whether that guidance is believed is whether
  the implied *distribution* for the relevant meetings shifts and tightens — not
  merely whether the modal expectation moves. Expectations management is the
  transmission channel; a distributional expectations measure lets the Fed
  observe the channel it is trying to act through.

### 1b. The risk-management approach to policy

The Fed's "risk-management" framing — weighing the whole distribution of
outcomes rather than only the central case, associated with the Greenspan era
and formalized in staff work on optimal policy under uncertainty — is inherently
distributional. A market-implied *variance and skew* of the fed funds and CPI
distributions is a real-time gauge of policy-relevant uncertainty and its
asymmetry: a market pricing a fat left tail on growth or a fat right tail on
inflation is exactly the input a risk-management framing consumes. Because the
FEDS event study shows these moments respond to FOMC communication, they double
as a feedback signal on whether the Committee's own risk-management message is
being priced.

### 1c. Recession-probability markets as a continuous, incentive-compatible nowcast

The Probability-of-Recession series is a market-validated complement to model
nowcasts (the Atlanta Fed's GDPNow, the New York Fed Nowcast) and to rule-based
real-time indicators (the Sahm rule). Its distinctive value is that it is a
*traded* probability, continuously updated and incentive-compatible, so it can
be read against model output: a persistent gap between a rising market-implied
recession probability and a stable model nowcast is itself a signal worth
investigating. The caveat is severe and points straight back to Section 3: this
is the thinnest, most manipulation-exposed series on the platform, so it is
precisely where the minimum-liquidity floor (Section 7) binds hardest, and it
should be read as a cross-check, never as a trigger (see Channel 2b).

## Channel 2 — Fiscal policy and Treasury debt management

### 2a. Debt issuance and maturity structure

Treasury's optimal maturity structure depends on the expected path *and the
uncertainty* of short rates, and the Treasury Borrowing Advisory Committee
(TBAC) already reasons about issuance against market-based rate expectations. A
continuously-updated distribution of the fed funds path — not just its mean — is
a plausible additional input to that reasoning: the variance of the rate
distribution maps onto the interest-cost risk of shorter issuance. This is a
lower-legitimacy-risk application than monetary use, because Treasury debt
management is not the thing the market is betting on, so the reflexivity problem
below is muted.

> **[DATA PLACEHOLDER — needs source verification]** Whether TBAC materials or
> Treasury's Office of Debt Management already reference market-implied rate
> *distributions* (as opposed to the futures-implied path). Cite the specific
> document or state explicitly that none was found; do not assert a practice
> that has not been verified.

### 2b. State-contingent fiscal stabilizers — the channel to rule out

Proposals for automatic fiscal stabilizers with statutory triggers (e.g., the
literature around unemployment-based recession triggers for automatically
extending unemployment insurance or stimulus) raise the tempting idea of using a
market-implied recession probability as a *leading* trigger. This section's
honest recommendation is: **do not.** A statutory trigger that disburses public
money must key off a tamper-proof official statistic, not a traded price that
Section 3 shows can be moved in a thin market — and whose incentive to be moved
would rise precisely because the trigger gives it fiscal consequences. Naming a
channel that *should not* be built is not a hedge; it is the discipline that
makes the channels this section does endorse credible, and it is the cleanest
illustration of the reflexivity principle developed next: never let a
manipulable market mechanically control a policy lever.

## Channel 3 — Financial stability and macroprudential policy

Market-implied tail scenarios — the left tail of the growth distribution, the
right tail of the CPI distribution — are a candidate cross-check on the severity
of the hypothetical adverse scenarios used in supervisory stress testing
(CCAR/DFAST) and in the countercyclical-capital-buffer discussion. The framing
must be modest: a market-implied tail is one external reference point on whether
a hand-designed adverse scenario is plausibly severe, not a scenario generator
and not a replacement for the deliberately-severe-by-construction supervisory
scenario. The same distributions feed real-time deterioration monitoring for
financial-stability reporting, where the value is timeliness rather than a new
decision rule.

## The reflexivity problem — the load-bearing implementation risk

The deepest implementation caveat is distinct from manipulation (Section 3) and
from optics (Section 4). It is *reflexivity*: once an official process **acts
on** a market that is itself **betting on that official's actions**, a feedback
loop forms, with two failure modes.

- **Goodhart / Campbell's law.** A measure adopted for control degrades as a
  measure. The moment Kalshi-implied odds become an official input, the payoff
  to moving them — the legal, narrative-shaping bet of Section 3 — rises, so the
  very signal quality the FEDS paper documents may not survive its own
  institutionalization. The accuracy result is measured on a market that is
  *not yet* an official input; adoption changes the object being measured.
- **Circular expectations.** The market prices what the Fed will do; the Fed
  reads the market to help decide what to do; in the limit the signal contains
  no information independent of the policymaker, only a self-referential
  consensus. This is the "hall of mirrors" problem in the central-bank
  communications literature and connects to the Morris–Shin result that public
  signals can crowd out private information and over-coordinate beliefs.

The implication is sharp and, at first, counter-intuitive. Prediction-market
signals are **safest in channels where the market prices something the
policymaker does not control** — CPI, GDP, recession, real-economy outcomes —
and **most fraught where it prices the policymaker's own choice** — the fed
funds decision itself. So the deepest, most liquid, most manipulation-resistant
series (fed funds) is the one where reflexivity bites *hardest*, while the thin
real-economy series (where manipulation bites hardest, per Section 3) are where
the signal is most genuinely *exogenous* to the decision. The two risks —
manipulation and reflexivity — trade off across the menu of series in opposite
directions. That tension is itself an argument for a distributional,
multi-series data product rather than a single headline "market expects a cut"
number: no one series is clean on both axes, but the panel read together, with
each series labeled by which risk dominates it, is far more defensible than any
one figure lifted out of it.

## Sequencing: an implementation ladder that mirrors Section 4's adoption ladder

Mapping the channels onto Section 4's (a)–(d) adoption rungs gives a concrete
order of operations, ranked by rising institutional commitment *and* rising
reflexivity risk:

| Channel | What the *distribution* adds beyond incumbents | Dominant risk | Adoption rung it fits | Recommendation |
|---|---|---|---|---|
| 1b Risk-management monitoring (variance/skew) | Real-time asymmetry of the outcome distribution | Manipulation (thin tails) | (a) internal | Implement early — lowest commitment |
| 1c Recession-probability nowcast cross-check | Continuous, incentive-compatible downside read | Manipulation (thinnest series) | (a)–(b) internal/staff | Implement as cross-check, never trigger |
| 3 Stress-scenario / stability cross-check | Market-validated tail severity | Manipulation (tails) | (a)–(b) internal/staff | Implement as one reference among several |
| 2a Treasury debt-management input | Uncertainty of the rate path, not just the path | Low (exogenous to Treasury) | (a)–(b) staff | Implement with source verification (2a placeholder) |
| 1a Forward-guidance gap detection | Distributional read on whether guidance lands | Reflexivity (rising) | (b)–(c) staff→communications | Implement internally; publish with care |
| — Communications-level citation of the fed funds distribution | (mostly re-packages futures) | Reflexivity (highest) | (c) | Defer — sharpest reflexivity + optics |
| 2b Statutory fiscal trigger | (spurious leading signal) | Manipulation *and* reflexivity | (d) statutory | **Do not implement** |

The through-line to Section 7: implement **real-economy-first** (CPI, GDP,
recession — where the signal is exogenous to the policy choice) and
**policy-rate-last** (fed funds — where reflexivity is sharpest), which is the
*mirror image* of the pure-liquidity ordering that would put the deep fed funds
series first. Reconciling those two orderings — liquidity says "fed funds
first," exogeneity says "fed funds last" — is a genuine finding of this section,
and it is why Section 7's concrete first step leads with the exogenous
distributions and treats the fed funds distribution as a labeled cross-check
rather than the headline.

## International / comparative note

The instrument is US-specific because the *regulated venue* is US-specific:
Kalshi is a US CFTC-designated contract market, and there is no equivalently
regulated macro prediction market in the UK, euro area, or Japan. Implementation
by a non-US central bank would require either standing up a comparable regulated
market or relying on Polymarket-style unregulated venues, in which case the
signal-quality and integrity caveats of Sections 3 and 5 apply with more force,
not less. This makes the US the natural first mover and makes "does regulation
buy real signal quality" (Section 5) a question with direct international-policy
stakes: it determines whether the model travels.

> **[DATA PLACEHOLDER — needs source verification]** Any reference to
> prediction-market data by a non-US central bank (BoE, ECB, BoJ) or
> international body (BIS, IMF). Reasonable prior: none in a formal capacity —
> which would reinforce the "US-specific, novel territory" framing. Verify or
> state explicitly that none was found.

## Deliverable for this section

The channel table above — policy channel × what the distribution adds ×
dominant risk × adoption rung × recommendation — is the section's core
deliverable, together with the real-economy-first sequencing rule it produces.
The prose commitments that must survive to the final draft: (i) the marginal
product of Kalshi is the *distribution's higher moments*, not another point
estimate; (ii) manipulation risk and reflexivity risk trade off in opposite
directions across the series menu; (iii) at least one channel (statutory fiscal
triggers, 2b) should be explicitly ruled out; and (iv) exogeneity, not
liquidity alone, sets the safe implementation order — the input that Section 7's
recommendation acts on.
