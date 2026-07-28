# Integrating Sumner (2018) and Snowberg–Wolfers–Zitzewitz (2012)

Three concrete ways the two newly-added references
(`references/sumner_2018.pdf`, `references/snowberg_wolfers_zitzewitz_2012.pdf`)
plug into the existing draft. Each names the section/file it touches so the work
is a drop-in, not a rewrite.

**Status: integrated.** All three are now woven into the section prose —
idea 1 into `3_manipulation_risk.md` (new "manipulation record beyond
Hanson–Oprea" subsection + the weak-form-efficiency diagnostic), idea 2 into
`6_macro_policy_implementation.md` and `7_policy_recommendation.md` (the
exogeneity note and the "far pole: targeting the forecast" subsection), and
idea 3 into `2_replication.md` (contract-taxonomy grounding of the ladder→pdf
method) and `6_macro_policy_implementation.md` (event-study model-testing lens).
This note is retained as the rationale record.

## 1. Give the manipulation-risk section its empirical backbone (§3)

`paper/sections/3_manipulation_risk.md` currently rests on the single
Hanson & Oprea (2009) sentence the FEDS paper cites. Snowberg, Wolfers &
Zitzewitz (2012) is the fuller record and — crucially — it cuts *both* ways,
which is exactly the asymmetry this project already argues:

- **Manipulation is usually transitory and self-correcting** in liquid markets:
  Rhode & Strumpf's random $500 IEM bets that reverted, Camerer's cancelled
  horse-racing bets that produced no bandwagon, the Hanson–Oprea–Porter (2006)
  and Hanson et al. (2011) lab experiments, and the Clinton-2008 Intrade episode
  where the manipulator took large losses and moved the price for only one media
  cycle.
- **The exception is thin markets** — "design flaws … generally lead to a lack
  of noise traders (or thin markets) that reduces incentives for discovering,
  and trading on the basis of, private information." That is precisely the
  GDP / recession-probability series the project flags, and it reframes the
  proposed **minimum-liquidity-floor safeguard** (§7) as *enforcing the
  noise-trader condition SWZ identify as the actual failure mode.*

Optional original extension for `notebooks/02_liquidity_comparison.ipynb`: apply
the weak-form-efficiency diagnostic SWZ cite (Leigh–Wolfers–Zitzewitz's ADF /
KPSS random-walk tests) to the deep fed funds series vs. the thin series. A
series that fails the random-walk test is showing the exploitable predictability
SWZ associate with too few noise traders — a data-driven way to set the
liquidity floor instead of a round-number cap.

## 2. Frame the policy recommendation against Sumner's "target the forecast" (§6–§7)

The project deliberately stops at *read the distribution as an input* and warns
that reflexivity makes it unsafe to *target* a market that bets on the Fed's own
decisions. Sumner (2018) is the strongest statement of the opposite pole —
Svensson's "target the forecast," implemented via a Fed-funded NGDP futures
market where policy is set wherever the market expects the target to be hit.
Using him as the explicit foil sharpens, rather than threatens, the project's
thesis:

- Sumner's NGDP contract prices an **outcome the Fed does not directly control**,
  which is exactly why it sidesteps the reflexivity trap the project attributes
  to the deep *fed funds* series. That is independent support for the project's
  **real-economy-first sequencing** (§6): the GDP / recession series are the
  safe place to start *because* they are one step removed from the policy
  instrument.
- Sumner's **TIPS-breakeven precedent** (created 1997, discussed in FOMC
  meetings soon after) is the same institutional-adoption analogy §4 already
  uses for OIS — cite him for the "market signals graduate into the policy
  conversation" claim.
- Net framing: this project maps the cautious near-term rung (read the
  distribution, with safeguards); Sumner maps the aspirational far rung (target
  the market). Naming both makes §7 a position on a spectrum rather than an
  isolated proposal.

## 3. Ground the ladder→density method and upgrade the event study (§2, `src/kalshi_utils.py`)

SWZ's Table 1 taxonomy — winner-take-all → probability, index → expected
mean/median, spread — is the canonical vocabulary for what the pipeline does. A
Kalshi "exceeds strike X" ladder is a family of winner-take-all contracts whose
price schedule *is* the risk-neutral CDF; differencing across strikes yields the
density. Citing SWZ gives `2_replication.md` a textbook grounding for the method
beyond the FEDS paper's own derivation.

Further, SWZ argue event studies on **co-movement in prices can uncover and test
the economic model** traders hold. That upgrades the §2 event-study replication
from "we reproduced their mean/variance/skew response to FOMC news" to "we use
the co-movement of the implied distribution to test *which* reaction function
traders are pricing" (e.g., does the density shift as a Phillips-curve response
would predict?). That is an original analytical step the FEDS paper's
descriptive event study does not take.
