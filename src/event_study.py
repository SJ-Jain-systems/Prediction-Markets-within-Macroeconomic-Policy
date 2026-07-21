"""
Event study on the higher moments of the Kalshi-implied distribution.

FEDS Section 7 shows that macro news and FOMC communications move not just the
*mean* of the implied fed funds rate distribution but its *variance* and
*skewness* -- markets reprice the whole shape, and the tails in particular,
around scheduled events. ``kalshi_utils`` already produces ``variance`` and
``skewness`` per day (see ``ImpliedDistribution`` and
``candlesticks_to_daily_ladder``); this module measures how those moments *jump*
across a window around each event.

  * ``event_window`` -- the daily moment rows in a symmetric window around one
    event, indexed by days relative to the event.
  * ``moment_shifts`` -- the pre -> post change in each moment per event, plus an
    across-events average: the event-study table behind a "markets reprice tail
    risk on FOMC days" claim.

Both consume the frame emitted by
``kalshi_utils.candlesticks_to_daily_ladder``:
``['date', 'mean', 'median', 'mode', 'variance', 'skewness']``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_MOMENTS = ("mean", "variance", "skewness")


def _with_datetime_index(daily_moments: pd.DataFrame) -> pd.DataFrame:
    df = daily_moments.copy()
    if "date" in df.columns:
        df = df.set_index(pd.to_datetime(df["date"]))
    df.index = pd.to_datetime(df.index)
    return df.sort_index()


def event_window(
    daily_moments: pd.DataFrame,
    event_date: pd.Timestamp,
    pre: int = 5,
    post: int = 5,
) -> pd.DataFrame:
    """Daily moments in a ``[-pre, +post]`` day window around one event.

    Parameters
    ----------
    daily_moments : pd.DataFrame
        Frame with a ``date`` column (or DatetimeIndex) and moment columns.
    event_date : pd.Timestamp
        The event (e.g. an FOMC decision or CPI release date).
    pre, post : int
        Window half-widths in calendar days.

    Returns
    -------
    pd.DataFrame
        The in-window rows with an added ``days_relative_to_event`` column
        (negative before, 0 on, positive after the event), sorted ascending.
        May be empty if no observations fall in the window.
    """
    if pre < 0 or post < 0:
        raise ValueError("pre and post must be non-negative")
    df = _with_datetime_index(daily_moments)
    rel = (df.index - pd.to_datetime(event_date)).days
    mask = (rel >= -pre) & (rel <= post)
    out = df.loc[mask].copy()
    out.insert(0, "days_relative_to_event", rel[mask])
    return out.reset_index(drop=True).sort_values("days_relative_to_event").reset_index(drop=True)


def moment_shifts(
    daily_moments: pd.DataFrame,
    event_dates: list[pd.Timestamp],
    pre: int = 5,
    post: int = 5,
    moments: tuple[str, ...] = DEFAULT_MOMENTS,
) -> pd.DataFrame:
    """Pre -> post change in each moment per event, with an across-events average.

    For each event the pre-window average (days ``[-pre, -1]``) is subtracted from
    the post-window average (days ``[+1, +post]``); day 0 itself is excluded so the
    shift measures repricing *across* the event rather than partly on it.

    Parameters
    ----------
    daily_moments : pd.DataFrame
        Frame with a ``date`` column (or DatetimeIndex) and moment columns.
    event_dates : list[pd.Timestamp]
        The events to study.
    pre, post : int
        Window half-widths in calendar days.
    moments : tuple[str, ...]
        Which moment columns to measure (default mean/variance/skewness).

    Returns
    -------
    pd.DataFrame
        One row per event plus a final ``event_date="ALL"`` row holding the mean
        shift across events. Columns are ``event_date`` followed by
        ``d_<moment>`` for each requested moment. Events with an empty pre- or
        post-window yield NaN shifts (and are ignored in the ALL average).
    """
    if not event_dates:
        raise ValueError("event_dates is empty")
    for m in moments:
        if m not in daily_moments.columns:
            raise ValueError(f"daily_moments has no column {m!r}")

    df = _with_datetime_index(daily_moments)
    rel_all = df.index

    rows = []
    for event_date in event_dates:
        rel = (rel_all - pd.to_datetime(event_date)).days
        pre_mask = (rel >= -pre) & (rel <= -1)
        post_mask = (rel >= 1) & (rel <= post)
        row: dict = {"event_date": pd.to_datetime(event_date)}
        for m in moments:
            pre_vals = df.loc[pre_mask, m]
            post_vals = df.loc[post_mask, m]
            if len(pre_vals) == 0 or len(post_vals) == 0:
                row[f"d_{m}"] = np.nan
            else:
                row[f"d_{m}"] = float(post_vals.mean() - pre_vals.mean())
        rows.append(row)

    result = pd.DataFrame(rows)
    avg = {"event_date": "ALL"}
    for m in moments:
        avg[f"d_{m}"] = float(result[f"d_{m}"].mean(skipna=True))
    return pd.concat([result, pd.DataFrame([avg])], ignore_index=True)
