#!/usr/bin/env python3
"""
Pull a real Kalshi strike ladder and turn it into the daily mean/median/mode
frame that notebook 01 and forecast_error_by_horizon consume.

This is the keystone the README and TODO both point at: it is the thing that
turns "reproduces the shape on synthetic ladders" into an actual replication on
independently pulled data. It wraps the existing kalshi_api and kalshi_utils
modules, so it is a swap into the pipeline, not a rewrite of it.

What it does, end to end:

  1. Find the strike markets that make up one Kalshi event (for example a single
     FOMC fed funds decision), via kalshi_api.list_markets.
  2. Pull daily candlesticks for each strike market over a date window, via
     kalshi_api.get_market_candlesticks.
  3. Reduce each candle to a single daily "Yes" price in [0, 1].
  4. Assemble the per-strike frames into the dict shape documented in
     docs/data_schema.md and run kalshi_utils.candlesticks_to_daily_ladder.
  5. Write the raw candlesticks and the processed daily ladder into data/.

Offline behavior: if the Kalshi hosts are not reachable (CI, locked-down
egress), the script prints a clear message and exits non-zero rather than
pretending. The synthetic path in the notebooks is the offline story, not this.

Two things to verify against https://docs.kalshi.com before trusting a large
pull, both flagged in kalshi_api.py already:

  - The live vs. historical endpoint split (effective February 2026).
  - The exact field names for a market's strike and for a candle's price. The
    two helpers below (_market_strike and _candle_to_yes_price) try the common
    shapes and can be overridden from the command line, but the field names are
    the first thing to check if a pull looks wrong.

Example:

    python scripts/pull_kalshi_ladder.py \\
        --event-ticker KXFED-25DEC \\
        --series-ticker KXFED \\
        --start 2025-06-01 --end 2025-12-10 \\
        --out-prefix fed_funds_2025dec
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Make the src/ modules importable whether or not the package was installed with
# `pip install -e .`. Installed is the normal path, this is just a fallback so
# the script also runs from a bare checkout.
_SRC = Path(__file__).resolve().parent.parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import kalshi_api  # noqa: E402
from kalshi_utils import candlesticks_to_daily_ladder  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _to_unix_ts(date_str: str) -> int:
    """Parse a YYYY-MM-DD date into a UTC unix timestamp (seconds)."""
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _market_strike(market: pd.Series, strike_regex: str | None) -> float | None:
    """Best-effort read of a numeric strike from one market row.

    Kalshi has used a few conventions over time (floor_strike/cap_strike numeric
    fields, a strike encoded in the ticker, a human-readable subtitle). We try
    them in order. If none fit the series you are pulling, pass --strike-regex
    with a pattern whose first capture group is the number, matched against the
    ticker and then the subtitle.
    """
    for field in ("floor_strike", "cap_strike", "strike"):
        if field in market and pd.notna(market[field]):
            try:
                return float(market[field])
            except (TypeError, ValueError):
                pass

    if strike_regex:
        for field in ("ticker", "subtitle", "yes_sub_title", "title"):
            value = market.get(field)
            if isinstance(value, str):
                m = re.search(strike_regex, value)
                if m:
                    try:
                        return float(m.group(1))
                    except (TypeError, ValueError):
                        pass
    return None


def _candle_to_yes_price(candle: dict, price_field: str) -> float | None:
    """Reduce one candlestick to a daily "Yes" price in [0, 1].

    Kalshi has returned candle prices in cents (0 to 100) for binary markets,
    sometimes flat (a "close" field) and sometimes nested under a "price" object
    with open/high/low/close/mean. We look for the requested field in both
    shapes and divide by 100 to land in [0, 1]. Verify the real shape against
    https://docs.kalshi.com, this is the most likely thing to need a tweak.
    """
    raw = None
    if price_field in candle:
        raw = candle[price_field]
    elif isinstance(candle.get("price"), dict) and price_field in candle["price"]:
        raw = candle["price"][price_field]

    if raw is None:
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None

    # Cents to probability. If a future endpoint already returns 0..1, values
    # above 1 are the tell that it is still cents, so only scale when needed.
    return value / 100.0 if value > 1.0 else value


def _candle_date(candle: dict) -> pd.Timestamp | None:
    """Read a candle's date from whichever timestamp field is present."""
    for field in ("end_period_ts", "ts", "end_ts", "period_end_ts"):
        if field in candle and candle[field] is not None:
            return pd.to_datetime(int(candle[field]), unit="s", utc=True).normalize()
    return None


def build_ladder(
    event_ticker: str,
    series_ticker: str,
    start_ts: int,
    end_ts: int,
    price_field: str,
    strike_regex: str | None,
) -> tuple[pd.DataFrame, dict[float, pd.DataFrame]]:
    """Pull every strike market in an event and assemble the daily ladder.

    Returns the processed daily frame and the per-strike frames it was built
    from, so the caller can cache both.
    """
    markets = kalshi_api.list_markets(event_ticker=event_ticker, series_ticker=series_ticker)
    if markets.empty:
        raise SystemExit(
            f"No markets returned for event_ticker={event_ticker!r}, "
            f"series_ticker={series_ticker!r}. Check the tickers against "
            f"https://docs.kalshi.com (try kalshi_api.list_events first)."
        )

    candles_by_strike: dict[float, pd.DataFrame] = {}
    skipped: list[str] = []

    for _, market in markets.iterrows():
        ticker = market.get("ticker")
        if not isinstance(ticker, str):
            continue
        strike = _market_strike(market, strike_regex)
        if strike is None:
            skipped.append(ticker)
            continue

        candles = kalshi_api.get_market_candlesticks(
            series_ticker=series_ticker,
            ticker=ticker,
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=1440,
        )
        if candles.empty:
            skipped.append(ticker)
            continue

        rows = []
        for candle in candles.to_dict("records"):
            date = _candle_date(candle)
            yes_price = _candle_to_yes_price(candle, price_field)
            if date is not None and yes_price is not None:
                rows.append({"date": date, "yes_price": yes_price})
        if rows:
            candles_by_strike[strike] = pd.DataFrame(rows)
        else:
            skipped.append(ticker)

    if skipped:
        print(
            f"Note: {len(skipped)} market(s) skipped for missing strike or price data. "
            f"First few: {skipped[:5]}",
            file=sys.stderr,
        )

    if len(candles_by_strike) < 2:
        raise SystemExit(
            "Fewer than two usable strikes were assembled, which is not a ladder. "
            "This usually means the strike or price field names have drifted. "
            "Check _market_strike / _candle_to_yes_price against a raw response, "
            "or pass --strike-regex / --price-field."
        )

    daily = candlesticks_to_daily_ladder(candles_by_strike)
    return daily, candles_by_strike


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--event-ticker", required=True, help="Kalshi event ticker, e.g. KXFED-25DEC")
    parser.add_argument("--series-ticker", required=True, help="Kalshi series ticker, e.g. KXFED")
    parser.add_argument("--start", required=True, help="Window start, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="Window end, YYYY-MM-DD")
    parser.add_argument(
        "--out-prefix",
        default=None,
        help="File name stem written into data/. Defaults to the event ticker.",
    )
    parser.add_argument(
        "--price-field",
        default="close",
        help="Candle price field to use as the daily Yes price (default: close).",
    )
    parser.add_argument(
        "--strike-regex",
        default=r"(\d+(?:\.\d+)?)",
        help="Fallback regex whose first group is the numeric strike, matched "
        "against ticker then subtitle. Only used if numeric strike fields are absent.",
    )
    args = parser.parse_args()

    start_ts = _to_unix_ts(args.start)
    end_ts = _to_unix_ts(args.end)
    if end_ts <= start_ts:
        raise SystemExit("--end must be after --start")

    out_prefix = args.out_prefix or args.event_ticker.replace("/", "_")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        daily, candles_by_strike = build_ladder(
            event_ticker=args.event_ticker,
            series_ticker=args.series_ticker,
            start_ts=start_ts,
            end_ts=end_ts,
            price_field=args.price_field,
            strike_regex=args.strike_regex,
        )
    except OSError as exc:
        # Network is down or the host is blocked. Say so plainly and point at the
        # offline story rather than failing with a raw traceback.
        print(
            "Could not reach Kalshi. The market-data hosts may be blocked in this "
            "environment (CI or locked-down egress). Run this where outbound HTTPS "
            "to api.kalshi.com is allowed. For an offline run, use the synthetic "
            f"generators in the notebooks instead.\nUnderlying error: {exc}",
            file=sys.stderr,
        )
        return 2

    processed_path = DATA_DIR / f"{out_prefix}_daily_ladder.csv"
    raw_path = DATA_DIR / f"{out_prefix}_raw_candles.json"

    daily.to_csv(processed_path, index=False)
    raw_payload = {
        str(strike): frame.assign(date=frame["date"].astype(str)).to_dict("records")
        for strike, frame in candles_by_strike.items()
    }
    raw_path.write_text(json.dumps(raw_payload, indent=2))

    print(f"Strikes assembled: {sorted(candles_by_strike)}")
    print(f"Days in ladder:    {len(daily)}")
    print(f"Processed ladder:  {processed_path}")
    print(f"Raw candles:       {raw_path}")
    print(
        "\nNext: point notebook 01 at the processed CSV in place of "
        "generate_synthetic_kalshi_ladder, and overlay real fed funds futures "
        "settlement as step 2 of that notebook's 'Next steps' cell."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
