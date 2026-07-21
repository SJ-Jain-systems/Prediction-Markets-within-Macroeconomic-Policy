"""
Quantify the manipulation exposure of a Kalshi macro market.

Section 3 of this project (``paper/sections/3_manipulation_risk.md``) argues that
the thin macro series -- GDP growth, recession probability, core-CPI-annual --
are far more exposed to a motivated actor than the deeply liquid fed funds rate
series, and that Kalshi's $7M per-market position cap is the relevant benchmark.
The FEDS paper treats this qualitatively; this module makes it a number.

The model is deliberately simple and transparent (a *prototype*, not a
market-microstructure engine):

  * A manipulator moves the implied distribution by pushing the ladder's "Yes"
    prices. Translating the whole distribution by ``target_mean_shift`` implies a
    specific change in each strike's exceedance probability, which we read off
    the pmf from ``kalshi_utils.ladder_to_pdf``.
  * The total absolute "Yes"-price displacement summed across strikes is the
    *price impact* the manipulator must create.
  * ``depth_dollars`` is a per-market liquidity parameter: the dollar order flow
    required to move a single strike's "Yes" price across its full [0, 1] range.
    Cost scales linearly with it -- so a **thin** market (small ``depth_dollars``)
    is **cheap** to move, which is exactly Section 3's point.

Calibrate ``depth_dollars`` from a real pull (e.g. trailing volume / open
interest per series via ``notebooks/02_liquidity_comparison.ipynb``) before
reading any dollar figure as more than an order-of-magnitude estimate.
"""

from __future__ import annotations

import numpy as np

import kalshi_utils as ku


def _shifted_yes_prices(dist: ku.ImpliedDistribution, strikes: np.ndarray, shift: float) -> np.ndarray:
    """Yes prices at ``strikes`` if the implied distribution is translated by ``shift``.

    With the pmf placed on ``bin_labels + shift``, the "Yes" price of "exceeds
    strike s" is the mass sitting strictly above ``s``.
    """
    shifted_labels = dist.bin_labels + shift
    return np.array(
        [float(dist.pmf[shifted_labels > s].sum()) for s in strikes],
        dtype=float,
    )


def cost_to_move(
    strikes: list[float],
    yes_prices: list[float],
    target_mean_shift: float,
    depth_dollars: float,
) -> float:
    """Estimated dollar cost to shift a market's implied mean by ``target_mean_shift``.

    Parameters
    ----------
    strikes, yes_prices : list[float]
        The current strike ladder and "Yes" prices, as passed to
        ``kalshi_utils.ladder_to_pdf``.
    target_mean_shift : float
        Desired change in the implied mean (same units as the strikes, e.g.
        percentage points of the fed funds rate). Sign is respected; magnitude is
        what drives cost.
    depth_dollars : float
        Liquidity of this market: dollars of order flow needed to move one
        strike's "Yes" price across its full [0, 1] range. Larger = deeper =
        costlier to manipulate.

    Returns
    -------
    float
        Estimated dollar cost. Larger target shifts and deeper markets both cost
        more; thin markets cost less.
    """
    if depth_dollars < 0:
        raise ValueError("depth_dollars must be non-negative")
    strikes_arr = np.asarray(strikes, dtype=float)
    dist = ku.ladder_to_pdf(list(strikes), list(yes_prices))
    new_yes = _shifted_yes_prices(dist, strikes_arr, float(target_mean_shift))
    price_impact = float(np.sum(np.abs(new_yes - np.asarray(yes_prices, dtype=float))))
    return price_impact * float(depth_dollars)


def probability_move_cost(
    strikes: list[float],
    yes_prices: list[float],
    strike: float,
    target_prob_shift: float,
    depth_dollars: float,
) -> float:
    """Estimated dollar cost to move one "exceeds ``strike``" probability.

    A single-contract analogue of ``cost_to_move`` for the case where the
    manipulator only cares about one headline probability (e.g. "P(Fed hikes)").
    Cost is the absolute probability move times ``depth_dollars``.
    """
    if depth_dollars < 0:
        raise ValueError("depth_dollars must be non-negative")
    strikes_arr = np.asarray(strikes, dtype=float)
    match = np.isclose(strikes_arr, float(strike))
    if not match.any():
        raise ValueError(f"strike {strike} is not in the ladder {list(strikes)}")
    # yes_prices validated for shape/monotonicity by ladder_to_pdf.
    ku.ladder_to_pdf(list(strikes), list(yes_prices))
    return abs(float(target_prob_shift)) * float(depth_dollars)


def exposure_vs_cap(cost: float, cap: float = 7_000_000.0) -> float:
    """Ratio of manipulation cost to Kalshi's per-market position cap ($7M default).

    A value **below 1** means a single actor operating within the cap could fund
    the move -- the red flag Section 3 is looking for. Above 1 means the cap alone
    would stop a lone manipulator.
    """
    if cap <= 0:
        raise ValueError("cap must be positive")
    return float(cost) / float(cap)
