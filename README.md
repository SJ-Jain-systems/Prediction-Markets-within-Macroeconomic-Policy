# Kalshi and the Institutionalization of Macro Prediction Markets

PErHAPS RECREATE ORIGINAL AND THEN DO THIS

This project extends **Diercks, Katz, and Wright (2026), "Kalshi and the Rise of
Macro Markets,"** Finance and Economics Discussion Series 2026-010, Federal
Reserve Board (the "FEDS paper"). A copy is included at
`references/diercks_katz_wright_2026.pdf`.

## What the FEDS paper already establishes (not duplicated here)

- Kalshi is the largest CFTC-approved prediction market (a "Designated
  Contract Market," the same regulatory category as the CME), trading
  contracts on CPI, core CPI, PCE, unemployment, payrolls, GDP growth,
  recession probability, and FOMC rate decisions (Table 1).
- A model-free method for converting a ladder of binary "exceeds strike X"
  contract prices into a full risk-neutral probability density function
  (Section 3).
- Kalshi's fed funds rate forecasts are statistically indistinguishable from
  (and on some metrics better than) the NY Fed's Survey of Market
  Expectations and fed funds futures (Figure 1, Table 3); headline CPI
  forecasts significantly beat the Bloomberg consensus.
- Event-study evidence that macro news and FOMC communications move not just
  the mean but the variance and skewness of the implied fed funds rate
  distribution (Sections 7).

## The gap this project addresses

The FEDS paper validates Kalshi as an accurate forecasting instrument. It
does **not** ask whether, or how, that instrument should be built into the
policy process. Five questions follow from that gap:

1. **Institutional adoption pathway** — What would it actually mean for the
   Fed or Treasury to use Kalshi data formally (dashboard, Beige Book
   citation, standing data feed), and how does that compare to how OIS and
   TIPS breakevens are already used?
2. **Manipulation and market integrity risk** — The FEDS paper cites Hanson
   and Oprea (2009) in one sentence. Given Kalshi's $7M per-market exposure
   cap and the much thinner liquidity in series like GDP growth and
   recession probability (vs. the multi-million-to-hundred-million-dollar
   volumes seen in the fed funds rate series, Figures 2–3 of the FEDS
   paper), how exposed is a pre-FOMC market to a motivated actor?
3. **Political economy and optics** — Should a central bank reference a
   market where the public is betting on its own decisions? This is a
   legitimacy question distinct from forecast accuracy, and the FEDS paper
   does not raise it.
4. **Regulated vs. unregulated signal quality** — The FEDS paper mentions
   Polymarket only to dismiss it as operating "in a legal gray area" with
   lower liquidity and looser position limits. It does not run a
   side-by-side comparison. Eichengreen, Viswanath-Natraj, Wang and Wang
   (2025), cited in passing by the FEDS paper, use Polymarket data on Fed
   independence questions — a natural bridge for that comparison.
5. **A concrete policy recommendation** — The FEDS paper stops at
   validation. This project ends with an actual proposal and named
   safeguards.

## Repo structure

```
kalshi-macro-policy/
├── data/                          # raw + processed Kalshi/Polymarket pulls (gitignored by default)
├── notebooks/
│   └── 01_figure1_replication.ipynb   # baseline: replicates FEDS Figure 1 methodology
├── paper/
│   └── sections/
│       ├── 1_background.md            # framing vs. the FEDS paper
│       ├── 2_replication.md           # your validation of their findings
│       ├── 3_manipulation_risk.md     # new: exposure limits, thin markets, manipulation
│       ├── 4_institutional_pathway.md # new: how the Fed could formally use this
│       ├── 5_polymarket_comparison.md # new: regulated vs. unregulated signal quality
│       └── 6_policy_recommendation.md # new: the actual proposal
├── src/
│   ├── kalshi_utils.py            # ladder-of-strikes -> pdf -> mean/median/mode (paper's Section 3 method)
│   └── kalshi_api.py              # thin client for Kalshi's public market-data API
├── references/
│   └── diercks_katz_wright_2026.pdf
├── requirements.txt
└── README.md
```

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/01_figure1_replication.ipynb
```

The notebook ships with a **synthetic data generator** so it runs end to end
with no credentials. Swap in real pulls via `src/kalshi_api.py` (Kalshi's
market-data endpoints are public and unauthenticated) once you're ready to
reproduce Figure 1 on real trade-level data. See `paper/sections/2_replication.md`
for what a faithful replication additionally needs (NY Fed SME PDFs,
Bloomberg consensus — the latter is proprietary and will need a substitute
or a data-sharing arrangement).

## Suggested order of work

1. Run the notebook as-is (synthetic data) to confirm the pipeline works.
2. Point `kalshi_api.py` at real Kalshi fed funds rate series and re-run —
   this gives you an actual replication of Figure 1, which anchors
   `2_replication.md`.
3. Pull volume/open-interest data for the *thin* series (GDP, recession
   probability, core CPI annual) the same way, to ground
   `3_manipulation_risk.md` in real numbers instead of the FEDS paper's
   qualitative treatment.
4. Research and draft `4_institutional_pathway.md` and
   `5_polymarket_comparison.md` (these are literature/policy sections, not
   data sections — see the outlines already in each file).
5. Write `6_policy_recommendation.md` last, once 3–5 give you concrete
   evidence to cite in the safeguards.

## Citation

Diercks, Anthony M., Jared Dean Katz, and Jonathan H. Wright (2026). "Kalshi
and the Rise of Macro Markets," Finance and Economics Discussion Series
2026-010. Washington: Board of Governors of the Federal Reserve System,
https://doi.org/10.17016/FEDS.2026.010.
