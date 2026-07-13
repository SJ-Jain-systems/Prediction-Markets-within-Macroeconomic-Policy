"""
Minimal read-only client for Polymarket's public data APIs, structured to
mirror ``src/kalshi_api.py`` so the two platforms can be pulled the same way
for the Kalshi-vs-Polymarket comparison (see paper/sections/5 and
notebooks/03_polymarket_comparison.ipynb).

Two public endpoints are used, neither of which requires authentication:

  * Gamma API (https://gamma-api.polymarket.com) -- market/event *metadata*:
    questions, outcomes, token ids, volume, liquidity, resolution.
  * CLOB API (https://clob.polymarket.com) -- order-book and price data keyed
    by the ERC-1155 token id ("clobTokenId") of a given YES/NO outcome.

IMPORTANT -- differences from Kalshi that matter for the comparison:

  1. Contract structure. Kalshi macro series are a *ladder* of "exceeds
     strike X" binaries that convert cleanly to a pdf via
     ``kalshi_utils.ladder_to_pdf``. Polymarket typically lists a Fed
     decision as a set of *sibling* YES/NO markets ("Fed cuts 25 bps in
     March?", "Fed holds in March?", ...) rather than one strike ladder. To
     get a comparable distribution you assemble the sibling markets into a
     ladder yourself, then feed their YES prices to the same
     ``ladder_to_pdf``. ``fed_ladder_from_markets`` below is a starting
     point for that assembly.
  2. Settlement is in USDC on-chain, the user base is pseudonymous and
     crypto-native, and position limits are looser than a CFTC-regulated
     DCM. These are confounds for any "regulation improves signal quality"
     claim -- see paper/sections/5.
  3. Endpoints and field names drift. These paths reflect the public Gamma /
     CLOB structure as generally documented, but were NOT verified against
     the live API from the build environment (outbound access to
     gamma-api.polymarket.com is blocked there). Verify against
     https://docs.polymarket.com before relying on this beyond a prototype.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

GAMMA_URL = "https://gamma-api.polymarket.com"
CLOB_URL = "https://clob.polymarket.com"


def _get(base: str, path: str, params: dict | None = None) -> dict | list:
    resp = requests.get(f"{base}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def search_markets(query: str, limit: int = 50, closed: bool | None = None) -> pd.DataFrame:
    """
    Look up markets by free-text query via the Gamma API, e.g.
    search_markets("Fed rate March") to find FOMC-decision markets. Returns
    the raw market metadata (question, outcomes, clobTokenIds, volume,
    liquidity, resolution) as a DataFrame.
    """
    params: dict = {"limit": limit}
    if query:
        params["search"] = query
    if closed is not None:
        params["closed"] = str(closed).lower()
    data = _get(GAMMA_URL, "/markets", params=params)
    markets = data if isinstance(data, list) else data.get("data", data.get("markets", []))
    return pd.DataFrame(markets)


def list_event_markets(event_slug: str) -> pd.DataFrame:
    """
    All markets grouped under a Gamma *event* (e.g. a single FOMC meeting
    whose child markets are the individual rate-decision outcomes). Returns
    the child markets as a DataFrame, which is the natural input to
    ``fed_ladder_from_markets``.
    """
    data = _get(GAMMA_URL, "/events", params={"slug": event_slug})
    events = data if isinstance(data, list) else data.get("data", [])
    markets: list = []
    for ev in events:
        markets.extend(ev.get("markets", []))
    return pd.DataFrame(markets)


def get_price_history(clob_token_id: str, interval: str = "1d", fidelity: int = 1440) -> pd.DataFrame:
    """
    Daily price history for one YES/NO outcome token from the CLOB API. The
    returned 'p' is the traded price in [0, 1], read as the risk-neutral
    probability of that outcome -- the Polymarket analogue of a Kalshi "Yes"
    price. Columns are normalized to ['date', 'yes_price'] so the result can
    be dropped straight into ``kalshi_utils.candlesticks_to_daily_ladder``.
    """
    data = _get(
        CLOB_URL,
        "/prices-history",
        params={"market": clob_token_id, "interval": interval, "fidelity": fidelity},
    )
    history = data.get("history", []) if isinstance(data, dict) else data
    df = pd.DataFrame(history)
    if df.empty:
        return pd.DataFrame(columns=["date", "yes_price"])
    # Gamma/CLOB return unix seconds in 't' and price in 'p'.
    df["date"] = pd.to_datetime(df["t"], unit="s").dt.normalize()
    df["yes_price"] = df["p"].astype(float)
    return df[["date", "yes_price"]]


def fed_ladder_from_markets(
    markets: pd.DataFrame,
    strike_col: str = "strike",
    token_col: str = "clobTokenId",
    pause_s: float = 0.2,
) -> dict[float, pd.DataFrame]:
    """
    Assemble a Kalshi-style strike ladder out of Polymarket's sibling
    FOMC-decision markets so the *same* ``kalshi_utils`` pipeline can be run
    on both platforms.

    ``markets`` must carry, per row, a numeric strike/threshold and the
    clobTokenId of that outcome's YES token. (Polymarket does not label a
    "rate exceeds X" threshold natively -- you map each sibling outcome to a
    strike yourself, e.g. "Fed target above 4.25% after March" -> 4.25 --
    which is exactly the judgement call paper/sections/5 flags as part of the
    comparison's confound.)

    Returns a ``{strike: DataFrame[date, yes_price]}`` dict, the input shape
    expected by ``kalshi_utils.candlesticks_to_daily_ladder``.
    """
    if strike_col not in markets.columns or token_col not in markets.columns:
        raise ValueError(f"markets must contain '{strike_col}' and '{token_col}' columns")

    ladder: dict[float, pd.DataFrame] = {}
    for _, row in markets.iterrows():
        strike = float(row[strike_col])
        ladder[strike] = get_price_history(str(row[token_col]))
        time.sleep(pause_s)
    return ladder
