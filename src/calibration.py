"""
Probability calibration for Kalshi/Polymarket "Yes" prices read as forecasts.

The FEDS paper's headline claim -- and this project's premise -- is that a
Kalshi "Yes" price *is* an accurate risk-neutral probability. ``forecast_eval``
scores the implied *point* forecasts (RMSE/MAE/bias, Diebold-Mariano), but a
point-forecast metric never tests the probabilities *as probabilities*. A
market can have a low mean-absolute error and still be badly calibrated (e.g.
its "70%" events happen only half the time). This module scores that.

It works on the raw binary contract: a series of (predicted probability,
realized 0/1 outcome) pairs -- for a single "exceeds strike X" contract across
many events, or pooled across contracts. Two views:

  * ``brier_score`` -- the mean squared probability error, the standard scalar
    scoring rule for binary probability forecasts (lower is better).
  * ``calibration_report`` -- the Brier score plus its Murphy decomposition
    (reliability - resolution + uncertainty), the expected calibration error,
    and a per-bin reliability table (mean forecast vs. observed frequency) --
    the numbers behind a reliability diagram and a "well calibrated" claim.

All functions are pure and offline; only numpy/pandas are used.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class CalibrationResult:
    """Calibration scoring of a set of probability forecasts against outcomes.

    Attributes
    ----------
    n
        Number of (forecast, outcome) pairs scored.
    base_rate
        Fraction of outcomes that were 1 (the unconditional event frequency).
    brier
        Mean squared error of the probabilities, ``mean((p - y) ** 2)`` -- the
        raw Brier score, in ``[0, 1]``, lower is better.
    reliability, resolution, uncertainty
        Murphy decomposition of the **binned** Brier score:
        ``brier_binned = reliability - resolution + uncertainty``. Reliability is
        the calibration penalty (0 = perfectly calibrated); resolution rewards
        forecasts that separate high- from low-frequency bins; uncertainty is
        ``base_rate * (1 - base_rate)``, the irreducible floor set by the data.
        The identity holds for the forecasts collapsed to their bin means, so
        ``reliability - resolution + uncertainty`` may differ from ``brier`` by
        the within-bin variance (smaller with more bins).
    ece
        Expected calibration error: count-weighted mean absolute gap between a
        bin's mean forecast and its observed frequency (an L1 reliability
        summary, 0 = perfectly calibrated).
    table
        Per-bin reliability table (see ``reliability_table``).
    """

    n: int
    base_rate: float
    brier: float
    reliability: float
    resolution: float
    uncertainty: float
    ece: float
    table: pd.DataFrame


def _validate(pred_probs: np.ndarray, outcomes: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(pred_probs, dtype=float)
    y = np.asarray(outcomes, dtype=float)
    if p.ndim != 1 or p.shape != y.shape:
        raise ValueError("pred_probs and outcomes must be 1-D arrays of equal length")
    if p.size == 0:
        raise ValueError("need at least one (forecast, outcome) pair")
    if np.any(p < 0.0) or np.any(p > 1.0):
        raise ValueError("pred_probs must all lie in [0, 1]")
    if not np.all(np.isin(y, (0.0, 1.0))):
        raise ValueError("outcomes must be binary (0 or 1)")
    return p, y


def brier_score(pred_probs: np.ndarray | list[float], outcomes: np.ndarray | list[float]) -> float:
    """Mean squared error of probability forecasts against binary outcomes.

    ``brier = mean((p - y) ** 2)`` where ``p`` is the forecast probability and
    ``y`` the realized 0/1 outcome. Ranges in ``[0, 1]``; lower is better; a
    forecast that always emits the base rate scores ``base_rate * (1 - base_rate)``.
    """
    p, y = _validate(np.asarray(pred_probs), np.asarray(outcomes))
    return float(np.mean((p - y) ** 2))


def reliability_table(
    pred_probs: np.ndarray | list[float],
    outcomes: np.ndarray | list[float],
    n_bins: int = 10,
) -> pd.DataFrame:
    """Bin forecasts and compare each bin's mean forecast to its observed frequency.

    Forecasts are grouped into ``n_bins`` equal-width bins over ``[0, 1]`` (a
    forecast of exactly 1.0 falls in the top bin). Empty bins are omitted.

    Returns
    -------
    pd.DataFrame
        Columns ``['bin_lower', 'bin_upper', 'n', 'mean_pred', 'obs_freq',
        'gap']`` sorted by bin, where ``obs_freq`` is the fraction of outcomes
        that were 1 in that bin and ``gap = mean_pred - obs_freq`` (positive =
        the market was over-confident in that bin). Plotting ``obs_freq`` against
        ``mean_pred`` is the reliability diagram.
    """
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")
    p, y = _validate(np.asarray(pred_probs), np.asarray(outcomes))

    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # Right-closed on the final edge so p == 1.0 lands in the last bin.
    idx = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, n_bins - 1)

    rows = []
    for b in range(n_bins):
        mask = idx == b
        count = int(mask.sum())
        if count == 0:
            continue
        mean_pred = float(p[mask].mean())
        obs_freq = float(y[mask].mean())
        rows.append(
            {
                "bin_lower": float(edges[b]),
                "bin_upper": float(edges[b + 1]),
                "n": count,
                "mean_pred": mean_pred,
                "obs_freq": obs_freq,
                "gap": mean_pred - obs_freq,
            }
        )
    return pd.DataFrame(
        rows, columns=["bin_lower", "bin_upper", "n", "mean_pred", "obs_freq", "gap"]
    )


def calibration_report(
    pred_probs: np.ndarray | list[float],
    outcomes: np.ndarray | list[float],
    n_bins: int = 10,
) -> CalibrationResult:
    """Full calibration scoring: Brier, Murphy decomposition, ECE, reliability table.

    Parameters
    ----------
    pred_probs : array-like of float in [0, 1]
        Forecast probabilities (e.g. daily "Yes" prices for one "exceeds strike
        X" contract, or such prices pooled across contracts/events).
    outcomes : array-like of {0, 1}
        The realized binary outcome for each forecast (1 if the outcome exceeded
        the strike, else 0).
    n_bins : int
        Number of equal-width probability bins for the decomposition and table.

    Returns
    -------
    CalibrationResult
        See the dataclass. ``reliability`` near 0 with ``resolution`` well above
        0 is the well-calibrated, informative case the paper needs to show.
    """
    p, y = _validate(np.asarray(pred_probs), np.asarray(outcomes))
    n = int(p.size)
    base_rate = float(y.mean())
    brier = float(np.mean((p - y) ** 2))
    uncertainty = base_rate * (1.0 - base_rate)

    table = reliability_table(p, y, n_bins=n_bins)
    if table.empty:
        reliability = resolution = ece = 0.0
    else:
        weights = table["n"].to_numpy(dtype=float) / n
        reliability = float(np.sum(weights * (table["mean_pred"] - table["obs_freq"]) ** 2))
        resolution = float(np.sum(weights * (table["obs_freq"] - base_rate) ** 2))
        ece = float(np.sum(weights * np.abs(table["mean_pred"] - table["obs_freq"])))

    return CalibrationResult(
        n=n,
        base_rate=base_rate,
        brier=brier,
        reliability=reliability,
        resolution=resolution,
        uncertainty=uncertainty,
        ece=ece,
        table=table,
    )


def volume_stratified_calibration(
    pred_probs: np.ndarray | list[float],
    outcomes: np.ndarray | list[float],
    volumes: np.ndarray | list[float],
    bucket_edges: np.ndarray | list[float] = (0.0, 1e4, 5e4, 2e5, np.inf),
) -> pd.DataFrame:
    """Brier score stratified by an event-level depth measure (volume or traders).

    Kagan and Baiocchi (2026) document that Kalshi's calibration behaves like a
    "learning curve" in participation: within a fixed time horizon, Brier score
    falls near-monotonically as event volume (or unique-trader count) rises. This
    is the second, independent axis -- alongside cost-to-move -- for setting the
    minimum-liquidity floor argued in the paper's Sections 3 and 7. This helper
    reproduces that curve on an independent pull: it buckets each market by a
    depth measure and scores the Brier of each bucket, the shape of their Table 2
    and Table 3.

    Parameters
    ----------
    pred_probs : array-like of float in [0, 1]
        Forecast probabilities, one per resolved market (e.g. the "Yes" price at
        a fixed horizon).
    outcomes : array-like of {0, 1}
        The realized binary outcome for each market.
    volumes : array-like of float >= 0
        The depth measure to stratify on -- dollar volume or unique-trader count
        -- one value per market, aligned with ``pred_probs``.
    bucket_edges : array-like of float
        Monotone-increasing bucket boundaries; each market falls in
        ``[edge_i, edge_{i+1})``. The default mirrors the paper's event-volume
        buckets (<$10K, $10K-$50K, $50K-$200K, >=$200K). Use finite edges for a
        trader-count stratification. Needs at least two edges.

    Returns
    -------
    pd.DataFrame
        One row per non-empty bucket, columns ``['bucket_lower', 'bucket_upper',
        'n', 'brier', 'base_rate']`` sorted by bucket. A monotone-decreasing
        ``brier`` down the rows is the learning-curve-in-depth pattern; the
        bucket at which it crosses a reference level (the paper uses 0.05) is the
        empirical anchor for a per-series liquidity floor.
    """
    p, y = _validate(np.asarray(pred_probs), np.asarray(outcomes))
    v = np.asarray(volumes, dtype=float)
    if v.shape != p.shape:
        raise ValueError("volumes must be a 1-D array aligned with pred_probs")
    if np.any(v < 0.0):
        raise ValueError("volumes must all be non-negative")
    edges = np.asarray(bucket_edges, dtype=float)
    if edges.ndim != 1 or edges.size < 2:
        raise ValueError("bucket_edges must be a 1-D array of at least two edges")
    if np.any(np.diff(edges) <= 0.0):
        raise ValueError("bucket_edges must be strictly increasing")

    rows = []
    for b in range(edges.size - 1):
        lo, hi = edges[b], edges[b + 1]
        mask = (v >= lo) & (v < hi)
        count = int(mask.sum())
        if count == 0:
            continue
        rows.append(
            {
                "bucket_lower": float(lo),
                "bucket_upper": float(hi),
                "n": count,
                "brier": float(np.mean((p[mask] - y[mask]) ** 2)),
                "base_rate": float(y[mask].mean()),
            }
        )
    return pd.DataFrame(
        rows, columns=["bucket_lower", "bucket_upper", "n", "brier", "base_rate"]
    )
