# References

Source papers bundled with this project. Each PDF is reproduced for reference
under its own terms; cite via the details below.

## Primary paper this project extends

**Diercks, Anthony M., Jared Dean Katz, and Jonathan H. Wright (2026).**
"Kalshi and the Rise of Macro Markets." Finance and Economics Discussion Series
2026-010. Washington: Board of Governors of the Federal Reserve System.
https://doi.org/10.17016/FEDS.2026.010
→ `diercks_katz_wright_2026.pdf`

Validates Kalshi as an accurate macro-forecasting instrument (fed funds, CPI,
PCE, unemployment, payrolls, GDP, recession probability, FOMC decisions) and
gives the model-free ladder-of-strikes → risk-neutral density method this
project's `src/kalshi_utils.py` implements.

## Supporting literature

**Sumner, Scott (2018).** "How Prediction Markets Can Improve Monetary Policy:
A Case Study." Policy Brief. Arlington, VA: Mercatus Center at George Mason
University. October 2018.
→ `sumner_2018.pdf`

A case study of the Mercatus/Hypermind nominal-GDP (NGDP) prediction markets
(2017–18 and 2018–19 contracts). Argues that a central bank should not merely
*read* market forecasts but could eventually *target the forecast* (Svensson) —
setting the policy instrument where the market consensus expects the target to
be hit — and calls for a Fed-funded NGDP futures market. Situates prediction
markets alongside the TIPS-breakeven precedent for market signals entering FOMC
deliberations. Relevant to the institutional-pathway (§4), macro-policy-
implementation (§6), and policy-recommendation (§7) sections.

**Snowberg, Erik, Justin Wolfers, and Eric Zitzewitz (2012).** "Prediction
Markets for Economic Forecasting." Prepared for the *Handbook of Economic
Forecasting*, Volume 2 (Elliott and Timmermann, eds.). NBER Working Paper 18222.
→ `snowberg_wolfers_zitzewitz_2012.pdf`

A survey of prediction markets for the economic-forecasting audience. Provides:
(i) the taxonomy of contract types — winner-take-all → probability, index →
expected mean/median, spread — that underpins the ladder → density conversion;
(ii) a body of empirical evidence that manipulation attempts are typically
transitory and self-correcting (Rhode & Strumpf's random IEM bets, Camerer's
cancelled horse-racing bets, Hanson–Oprea–Porter lab experiments), *with the
key caveat that thin markets lacking noise traders are where design failures
actually occur*; and (iii) the argument that event studies on co-movement in
market prices can uncover and test the economic model behind the forecast.
Relevant to the manipulation-risk (§3) and replication/event-study (§2)
sections. (The FEDS paper cites the related Hanson & Oprea (2009) result in one
sentence; this survey is the fuller treatment.)
