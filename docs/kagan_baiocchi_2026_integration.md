# Integrating Kagan & Baiocchi (2026), "Calibration in Prediction Markets"

Two concrete ways the Kalshi Research calibration paper
(`references/kagan_baiocchi_2026.pdf`) plugs into the existing draft. Each names
the section/file it touches so the work is a drop-in, not a rewrite. Companion
data lives in `references/kagan_baiocchi_2026_brier_by_category.csv` (Table 1,
transcribed).

**Status: integrated.** Both ideas are now woven into the section prose —
idea 1 into `2_replication.md` (the "Calibration — a third check, with an
external benchmark" subsection) and idea 2 into `3_manipulation_risk.md` (the
"Calibration adequacy: a second, independent case for the floor" subsection) and
`7_policy_recommendation.md` (the two-axis defense of the liquidity floor). The
follow-up `volume_stratified_calibration` helper sketched in §2 below is now
implemented and tested in `src/calibration.py`. The companion CSV has been
verified cell-for-cell against Table 1 of the source PDF. This note is retained
as the rationale record.

**What the paper is.** The first at-scale calibration study of a single
regulated exchange: 2,243,741 resolved Kalshi markets, 2021 through mid-2026,
across eleven categories. It scores exactly what `src/calibration.py` already
computes — Brier score, the Murphy reliability/resolution/uncertainty
decomposition, and reliability diagrams — but on the full resolved history rather
than on our (currently synthetic) pull. Headline results: Brier falls from ~0.087
at a 3-Month horizon to below 0.02 at Close; reliability diagrams track the 45°
line; and calibration improves near-monotonically with both trading volume and
unique-trader count.

**Provenance caveat — state it loudly.** This is a **Kalshi Research** working
paper (Kagan & Baiocchi), i.e. the exchange's own team, where Diercks–Katz–Wright
(2026) is a Federal Reserve Board working paper. This project's spine is
independence and the "regulated vs. unregulated signal" question, so cite Kagan &
Baiocchi as *corroborating, interested-party* evidence and name the conflict
explicitly — the same discipline the README already applies to the Bloomberg
consensus substitution. It strengthens the case precisely because the conflict is
named rather than leaned on silently. The numbers in the companion CSV were
transcribed from the PDF for this note and should be checked against the source
before being quoted as targets (same rule TODO.md applies to the FEDS figures).

## 1. Use it as the calibration benchmark for the Economics replication (§2)

`paper/sections/2_replication.md` and `notebooks/01_figure1_replication.ipynb`
currently reproduce the *shape* of the FEDS accuracy result on synthetic ladders,
with nothing external to check the probabilities-as-probabilities claim against.
Kagan & Baiocchi supply that missing target on the exact category this project
cares about:

- **Economics is their cleanest category.** Brier declines near-linearly and
  monotonically from 0.108 (3-Month) to 0.066 (Close) — no hump, no reversal —
  because Economics markets resolve against pre-scheduled, unambiguous releases
  (CPI, payrolls, GDP), which is precisely the price-discovery setting the FEDS
  paper builds its macro-benchmark case on. This is the complementary
  *calibration* result to the FEDS *accuracy* result: two independent lenses,
  same conclusion, same category.
- **Concrete use.** When the real Kalshi pull lands (TODO.md, item 1), run
  `calibration.calibration_report()` on the Economics-category "Yes" prices by
  horizon and compare the Brier column against
  `references/kagan_baiocchi_2026_brier_by_category.csv`. A pull that reproduces
  the ~0.108 → 0.066 monotone decline is independently validated against a
  published full-history number, not just against our own synthetic generator.
  This turns "reproduces the shape" into "matches an external benchmark" for the
  one category that matters here.

Suggested prose hook for `2_replication.md`: after the density-method paragraph,
note that the risk-neutral probabilities the ladder produces can be checked not
only for point accuracy (Table 3 machinery in `forecast_eval`) but for
calibration, and that Kagan & Baiocchi (2026) give a full-history Economics-
category benchmark (Brier ≈ 0.108 at 3-Mo → 0.066 at Close) for that check —
flagged as interested-party corroboration per the caveat above.

## 2. Make the liquidity floor calibration-adequate, not just manipulation-proof (§3, §7)

`paper/sections/3_manipulation_risk.md` and `7_policy_recommendation.md` argue for
a **minimum-liquidity floor**: thin series (GDP, recession probability) are the
manipulable ones, so a floor enforces the noise-trader condition SWZ identify as
the real failure mode. TODO.md wants that floor "calibrated to cost-to-move, not
picked out of the air." Kagan & Baiocchi add a **second, independent axis** for
setting the same number:

- **Calibration is a learning curve in volume.** Within every time horizon, Brier
  falls monotonically as the event-volume threshold rises (their Figures 12–15).
  Below some volume, a market is not just thin — it is measurably *worse
  calibrated*. That is a calibration-based argument for a floor that runs parallel
  to the manipulation-based one.
- **The threshold is category-specific.** They report that at the 1-Day horizon,
  Politics and Economics markets are already below the 0.05 Brier reference line
  at volumes of a few thousand dollars, while Sports and Mentions cross it at
  roughly two orders of magnitude more volume. So a single dollar floor is not
  category-neutral; the Economics/macro series clear the calibration bar at
  comparatively low volume, which *supports* starting there (the project's
  real-economy-first sequencing) while cautioning that the floor be expressed
  per-series.
- **Net framing.** The floor can now be defended two ways at once — a market must
  be deep enough that (a) a $7M position cannot move the implied probability by
  more than a few points (cost-to-move, §3) **and** (b) it sits on the flat,
  well-calibrated part of the volume→Brier curve (Kagan & Baiocchi). A safeguard
  justified on both manipulation-resistance and calibration-adequacy is
  materially stronger than either alone.

Note on data: the exact volume-at-crossing points are presented as figures, not a
clean table, in the paper; the two anchor points quoted above (§ few-thousand for
Politics/Economics vs. ~two orders of magnitude for Sports/Mentions, at the 1-Day
horizon, 0.05 Brier line) are the ones stated numerically in the text. Reproducing
the full curve on our own pull is the `volume_stratified_calibration` helper
sketched as a separate follow-up for `src/calibration.py` and
`notebooks/02_liquidity_comparison.ipynb`.

## Housekeeping

- ~~Add the PDF at `references/kagan_baiocchi_2026.pdf` and a one-line entry to
  `references/README(references).md`.~~ Done — the PDF is at that path and the
  references README carries a "Corroborating evidence (interested party)" entry.
- The paper also flags, as its own future work, a **conviction-weighted accuracy**
  measure (crediting a market in proportion to how far its price moved beyond 50
  cents). That is a natural complement to `forecast_eval` if the project ever
  extends beyond calibration into accuracy weighting — noted here, not pursued.
