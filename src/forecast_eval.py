"""
Forecast-accuracy evaluation for the Kalshi-implied point forecasts.

The FEDS paper's headline finding is that Kalshi's fed funds rate forecasts are
*statistically indistinguishable from* (and on some metrics better than) the
NY Fed SME and fed funds futures, and that its CPI forecasts significantly beat
the Bloomberg consensus (Table 3). ``kalshi_utils`` gives you the daily implied
forecast and ``forecast_error_by_horizon`` gives the error path, but nothing here
computed the *summary metrics* or the *significance test* those claims rest on.

This module adds:

  * ``accuracy_metrics`` -- RMSE / MAE / bias (and optional hit-rate) for a
    forecast frame against a realized outcome.
  * ``metrics_by_horizon`` -- the same metrics aggregated by "days before the
    event" across one or more events, the x-axis convention of Figure 1. It
    reuses the exact date-handling convention of
    ``kalshi_utils.forecast_error_by_horizon``.
  * ``diebold_mariano`` -- the Diebold-Mariano test of equal predictive accuracy
    between two aligned error series, which is what backs an "indistinguishable
    from" or "significantly beats" statement.

All functions are pure and offline; ``scipy`` (already a project dependency)
supplies the normal tail probability for the DM p-value.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def accuracy_metrics(
    forecasts: pd.DataFrame,
    realized_value: float,
    value_col: str = "mean",
    hit_tol: float | None = None,
) -> dict:
    """Summary accuracy of a forecast column against a single realized outcome.

    Parameters
    ----------
    forecasts : pd.DataFrame
        Frame carrying a forecast column (e.g. the ``mean`` emitted by
        ``kalshi_utils.candlesticks_to_daily_ladder``).
    realized_value : float
        The outcome that actually occurred.
    value_col : str
        Which forecast column to score.
    hit_tol : float, optional
        If given, also report ``hit_rate`` = fraction of forecasts whose absolute
        error is within ``hit_tol`` (e.g. one strike spacing for a rate decision).

    Returns
    -------
    dict
        ``{n, rmse, mae, bias}`` (plus ``hit_rate`` when ``hit_tol`` is set),
        where ``bias`` is the mean *signed* error (forecast minus realized).
    """
    if value_col not in forecasts.columns:
        raise ValueError(f"forecasts has no column {value_col!r}")
    errors = forecasts[value_col].to_numpy(dtype=float) - float(realized_value)
    if errors.size == 0:
        raise ValueError("forecasts is empty")

    out = {
        "n": int(errors.size),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mae": float(np.mean(np.abs(errors))),
        "bias": float(np.mean(errors)),
    }
    if hit_tol is not None:
        out["hit_rate"] = float(np.mean(np.abs(errors) <= hit_tol))
    return out


def metrics_by_horizon(
    events: list[tuple[pd.DataFrame, float, pd.Timestamp]],
    value_col: str = "mean",
) -> pd.DataFrame:
    """RMSE / MAE / bias by "days before event", pooled across events.

    Parameters
    ----------
    events : list of (daily_forecasts, realized_value, event_date)
        One tuple per event. ``daily_forecasts`` follows the same shape
        ``kalshi_utils.forecast_error_by_horizon`` accepts: a DatetimeIndex (or a
        ``date`` column) plus the forecast columns. Pooling many FOMC/CPI events
        is what makes a per-horizon curve meaningful (a single event has one
        observation per horizon).
    value_col : str
        Forecast column to score.

    Returns
    -------
    pd.DataFrame
        Columns ``['days_before_event', 'n', 'rmse', 'mae', 'bias']``, sorted by
        horizon. Uses the same ``(event_date - date).days`` convention as
        ``forecast_error_by_horizon`` so the horizons line up with Figure 1.
    """
    if not events:
        raise ValueError("events is empty")

    frames = []
    for daily_forecasts, realized_value, event_date in events:
        df = daily_forecasts.copy()
        if "date" in df.columns:
            df = df.set_index(pd.to_datetime(df["date"]))
        df.index = pd.to_datetime(df.index)
        if value_col not in df.columns:
            raise ValueError(f"an event frame has no column {value_col!r}")
        days_before = (pd.to_datetime(event_date) - df.index).days
        error = df[value_col].to_numpy(dtype=float) - float(realized_value)
        frames.append(pd.DataFrame({"days_before_event": days_before, "error": error}))

    pooled = pd.concat(frames, ignore_index=True)
    grouped = pooled.groupby("days_before_event")["error"]
    out = pd.DataFrame(
        {
            "n": grouped.size(),
            "rmse": grouped.apply(lambda s: float(np.sqrt(np.mean(s.to_numpy() ** 2)))),
            "mae": grouped.apply(lambda s: float(np.mean(np.abs(s.to_numpy())))),
            "bias": grouped.mean(),
        }
    ).reset_index()
    return out.sort_values("days_before_event").reset_index(drop=True)


def diebold_mariano(
    errors_a: np.ndarray | list[float],
    errors_b: np.ndarray | list[float],
    power: int = 2,
    h: int = 1,
) -> tuple[float, float]:
    """Diebold-Mariano test of equal predictive accuracy between two forecasters.

    Tests H0: forecasters A and B have equal expected loss, against the two-sided
    alternative. The loss differential is ``d_t = |e_a,t|**power - |e_b,t|**power``
    (``power=2`` for squared error, ``power=1`` for absolute error). A **positive**
    statistic means A has the larger loss (A is worse than B).

    Parameters
    ----------
    errors_a, errors_b : array-like
        Aligned forecast-error series (same length, same observations).
    power : int
        Loss power: 2 for MSE-style, 1 for MAE-style.
    h : int
        Forecast horizon. For ``h > 1`` a Newey-West long-run variance with
        ``h - 1`` lags is used (serial correlation of multi-step errors);
        ``h = 1`` uses the plain sample variance.

    Returns
    -------
    (stat, p_value) : tuple of float
        The DM statistic and its two-sided normal p-value. A large ``|stat|`` /
        small ``p_value`` rejects "equal accuracy"; failing to reject is what
        licenses an "indistinguishable from" claim.
    """
    a = np.asarray(errors_a, dtype=float)
    b = np.asarray(errors_b, dtype=float)
    if a.ndim != 1 or a.shape != b.shape:
        raise ValueError("errors_a and errors_b must be 1-D arrays of equal length")
    n = a.size
    if n < 2:
        raise ValueError("need at least 2 observations for the DM test")
    if h < 1:
        raise ValueError("h must be >= 1")

    d = np.abs(a) ** power - np.abs(b) ** power
    dbar = float(d.mean())

    # Long-run variance of d (Newey-West, Bartlett weights, h-1 lags).
    demeaned = d - dbar
    var = float(np.mean(demeaned**2))  # gamma_0
    for lag in range(1, h):
        cov = float(np.mean(demeaned[lag:] * demeaned[:-lag]))
        weight = 1.0 - lag / h
        var += 2.0 * weight * cov

    if var <= 0:
        # Degenerate loss differential (e.g. identical error series): no variance
        # to test against. Equal means -> can't reject; unequal -> reject hard.
        if dbar == 0:
            return 0.0, 1.0
        return (float("inf") if dbar > 0 else float("-inf")), 0.0

    stat = dbar / np.sqrt(var / n)
    p_value = float(2.0 * norm.sf(abs(stat)))
    return float(stat), p_value
