"""
Convert a ladder of Kalshi "exceeds strike X" contract prices into a
risk-neutral probability distribution, following the method described in
Diercks, Katz and Wright (2026), Section 3 ("Converting Kalshi into
Probability Distributions").

Kalshi's macro contracts are typically structured as a series of binary
options that each pay $1 if the realized outcome exceeds a given strike.
The "Yes" price of such a contract is treated as the risk-neutral
probability that the outcome exceeds that strike. The probability mass
between two adjacent strikes is the difference between their "Yes" prices.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ImpliedDistribution:
    strikes: np.ndarray
    bin_labels: np.ndarray  # midpoint of each strike interval
    pmf: np.ndarray
    mean: float
    median: float
    mode: float
    variance: float
    skewness: float


def ladder_to_pdf(strikes: list[float], yes_prices: list[float]) -> ImpliedDistribution:
    """
    strikes: increasing list of strike thresholds, e.g. [4.00, 4.25, 4.50, ...]
    yes_prices: "Yes" price (0-1) for the contract "outcome exceeds this strike",
                same length and order as `strikes`.

    Returns the implied probability mass on each [strikes[i], strikes[i+1])
    bin, plus summary moments, using the FEDS-paper convention of
    subtracting consecutive "Yes" prices. The top bin (above the last
    strike) and bottom bin (below the first strike) are included using the
    boundary "Yes" prices directly.
    """
    strikes = np.asarray(strikes, dtype=float)
    yes_prices = np.asarray(yes_prices, dtype=float)
    if strikes.ndim != 1 or yes_prices.shape != strikes.shape:
        raise ValueError("strikes and yes_prices must be 1-D arrays of equal length")
    if not np.all(np.diff(strikes) > 0):
        raise ValueError("strikes must be strictly increasing")

    # P(below first strike) = 1 - Yes price of "exceeds first strike"
    p_below_first = 1.0 - yes_prices[0]
    # P(between strike i and i+1) = Yes(strike i) - Yes(strike i+1)
    p_between = -np.diff(yes_prices)
    # P(above last strike) = Yes price of "exceeds last strike"
    p_above_last = yes_prices[-1]

    pmf = np.concatenate(([p_below_first], p_between, [p_above_last]))
    pmf = np.clip(pmf, 0, None)
    pmf = pmf / pmf.sum()  # renormalize away small negative/rounding drift

    # bin midpoints: extend one strike-width beyond the outer strikes for the tails
    step = np.diff(strikes)
    outer_step = step[0] if len(step) else 1.0
    edges = np.concatenate(([strikes[0] - outer_step], strikes, [strikes[-1] + outer_step]))
    bin_labels = (edges[:-1] + edges[1:]) / 2

    mean = float(np.sum(pmf * bin_labels))
    variance = float(np.sum(pmf * (bin_labels - mean) ** 2))
    std = np.sqrt(variance) if variance > 0 else np.nan
    skewness = float(np.sum(pmf * (bin_labels - mean) ** 3) / std**3) if std and not np.isnan(std) else np.nan

    cdf = np.cumsum(pmf)
    median_idx = int(np.searchsorted(cdf, 0.5))
    median = float(bin_labels[min(median_idx, len(bin_labels) - 1)])
    mode = float(bin_labels[int(np.argmax(pmf))])

    return ImpliedDistribution(
        strikes=strikes,
        bin_labels=bin_labels,
        pmf=pmf,
        mean=mean,
        median=median,
        mode=mode,
        variance=variance,
        skewness=skewness,
    )


def forecast_error_by_horizon(
    daily_forecasts: pd.DataFrame,
    realized_value: float,
    event_date: pd.Timestamp,
    value_col: str = "mean",
) -> pd.DataFrame:
    """
    daily_forecasts: DataFrame with a DatetimeIndex (or a 'date' column) and
                      forecast columns (e.g. 'mean', 'median', 'mode').
    realized_value:  the outcome that actually occurred.
    event_date:      the date the outcome was determined (e.g. FOMC date).

    Returns a DataFrame with 'days_before_event' and 'abs_error' columns,
    matching the x-axis convention of Figure 1 in the FEDS paper (mean
    absolute forecast error plotted against days before the event).
    """
    df = daily_forecasts.copy()
    if "date" in df.columns:
        df = df.set_index(pd.to_datetime(df["date"]))
    df.index = pd.to_datetime(df.index)

    days_before = (pd.to_datetime(event_date) - df.index).days
    abs_error = (df[value_col] - realized_value).abs()

    return pd.DataFrame({"days_before_event": days_before, "abs_error": abs_error}).reset_index(drop=True)


def candlesticks_to_daily_ladder(
    candles_by_strike: dict[float, pd.DataFrame],
    price_col: str = "yes_price",
    date_col: str = "date",
) -> pd.DataFrame:
    """
    Assemble a per-day strike ladder from one candlestick series per strike
    and run `ladder_to_pdf` on each day, producing the daily mean/median/mode
    frame that Figure 1 (and the notebooks) consume.

    This closes the gap that `notebooks/01_figure1_replication.ipynb` flags in
    its "Next steps" cell: `kalshi_api.get_market_candlesticks` returns one
    OHLC-style frame *per market (strike)*, but `ladder_to_pdf` needs one
    ladder *per day*. This helper does the pivot-and-convert in between.

    Parameters
    ----------
    candles_by_strike : dict[float, pd.DataFrame]
        Maps each strike threshold (e.g. 4.25) to a DataFrame that has, at
        minimum, a date column and a daily "Yes" price column (0-1). The
        natural way to build this is to loop over the strike markets in a
        Kalshi event, call `kalshi_api.get_market_candlesticks` for each,
        and reduce each candle to its daily "Yes" price (e.g. the daily
        close). Strikes are read from the dict keys, so they need not be
        pre-sorted.
    price_col : str
        Name of the daily "Yes" price column in each per-strike frame.
    date_col : str
        Name of the date column in each per-strike frame.

    Returns
    -------
    pd.DataFrame
        One row per date on which *every* strike has a price, with columns
        ['date', 'mean', 'median', 'mode', 'variance', 'skewness'] — the same
        column contract emitted by the synthetic generator in notebook 01 and
        consumed by `forecast_error_by_horizon`.

    Notes
    -----
    Verify the live/historical candlestick endpoint split and exact field
    names against https://docs.kalshi.com before trusting a real pull -- the
    same caveat documented at the top of ``kalshi_api.py`` applies here
    (Kalshi split market data into "live" and "historical" tiers effective
    February 2026). Days on which any strike is missing a price are dropped,
    because a partial ladder cannot be converted without imputation.
    """
    if not candles_by_strike:
        raise ValueError("candles_by_strike is empty")

    strikes = sorted(candles_by_strike.keys())

    # Build a wide date x strike table of Yes prices.
    series_by_strike = {}
    for strike in strikes:
        frame = candles_by_strike[strike]
        if date_col not in frame.columns or price_col not in frame.columns:
            raise ValueError(
                f"strike {strike}: frame must contain '{date_col}' and '{price_col}' columns"
            )
        s = frame.set_index(pd.to_datetime(frame[date_col]))[price_col]
        s = s[~s.index.duplicated(keep="last")]  # one price per day
        series_by_strike[strike] = s

    wide = pd.DataFrame(series_by_strike)  # index=date, columns=strikes
    wide = wide.sort_index().dropna(how="any")  # keep only fully-populated ladders

    rows = []
    for date, ladder in wide.iterrows():
        dist = ladder_to_pdf(list(strikes), [float(ladder[k]) for k in strikes])
        rows.append(
            {
                "date": date,
                "mean": dist.mean,
                "median": dist.median,
                "mode": dist.mode,
                "variance": dist.variance,
                "skewness": dist.skewness,
            }
        )

    return pd.DataFrame(rows)
