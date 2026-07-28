"""
Translate a Kalshi fed funds ladder into the monetary-policy signal an FOMC
watcher actually reads.

This module is the code behind Section 6 (``6_macro_policy_implementation.md``)
and the README's fifth question: *what does the full risk-neutral distribution
add beyond the point estimates (fed funds futures, OIS) officials already have?*

``kalshi_utils.ladder_to_pdf`` returns a continuous, binned distribution whose
bin labels sit at strike-interval *midpoints*. A policy rate is not continuous:
it moves in discrete 25-basis-point steps and only ever takes values on the
FOMC's grid. So this module reads the ladder on that **discrete decision grid**
directly -- the same logic as a CME-FedWatch-style "probability of a hike" table,
but sourced from Kalshi and extended to the whole distribution:

  * for a ladder of "rate >= strike" prices on the 25bp grid, the probability the
    target lands exactly at a grid level is the drop in "Yes" price across that
    level (``yes[i] - yes[i+1]``); the mass below the lowest strike is one more
    step down; and
  * each grid level is expressed as a signed number of 25bp moves from the
    current target, so the distribution becomes a probability over
    {..., -2 cuts, -1 cut, hold, +1 hike, +2 hikes, ...}.

From that discrete move distribution we report the cut/hold/hike probabilities, a
modal and expected move, the dispersion (policy uncertainty), and -- the point of
Section 6 -- the ``opposite_tail_prob``: the probability of a move *against* the
expected direction, which is exactly the two-sided risk a single point forecast
(a futures quote, an OIS-implied path) collapses away.

Ladders are screened with ``ladder_validation.validate_ladder`` first, so an
arbitraged or malformed pull raises rather than silently producing a signal.
Pure and offline -- no network, no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import ladder_validation as lv


@dataclass
class PolicySignal:
    """Discrete monetary-policy read of a fed funds ladder.

    All rates are in the ladder's native units (percentage points); "move"
    quantities are in basis points so they read the way FOMC commentary does.

    Attributes
    ----------
    current_rate
        The target rate the moves are measured from.
    step
        The policy grid spacing in rate units (0.25 = one 25bp move).
    move_probabilities
        ``{signed_steps: probability}`` over the discrete decision grid, e.g.
        ``{-1: 0.30, 0: 0.40, 1: 0.30}``. Keys are integer numbers of ``step``
        moves from ``current_rate``; values sum to 1.
    prob_cut, prob_hold, prob_hike
        Probability the target ends below / at / above ``current_rate``.
    modal_move, modal_prob
        The single most likely number of moves and its probability.
    expected_move_bps
        Probability-weighted mean move, in basis points (the market's central
        expectation, comparable to a futures/OIS-implied path point).
    uncertainty_bps
        Standard deviation of the move distribution, in basis points -- the
        dispersion a point forecast throws away.
    skew
        Standardized third central moment of the move distribution. Negative = a
        long tail toward *cuts* with mass piled toward hikes; positive = the
        reverse. ``nan`` for a degenerate (single-outcome) distribution.
    opposite_tail_prob
        Probability of a move *against* the expected direction: ``prob_cut`` when
        the market expects a hike on net, ``prob_hike`` when it expects a cut, and
        ``min(prob_cut, prob_hike)`` when the expected move is flat. This is the
        two-sided risk a single point estimate cannot express -- the concrete
        "what the distribution adds" number for Section 6.
    """

    current_rate: float
    step: float
    move_probabilities: dict[int, float] = field(default_factory=dict)
    prob_cut: float = 0.0
    prob_hold: float = 0.0
    prob_hike: float = 0.0
    modal_move: int = 0
    modal_prob: float = 0.0
    expected_move_bps: float = 0.0
    uncertainty_bps: float = 0.0
    skew: float = float("nan")
    opposite_tail_prob: float = 0.0

    def as_dict(self) -> dict:
        """Flat dict of the scalar fields (drops ``move_probabilities``) for tables."""
        return {
            "current_rate": self.current_rate,
            "step": self.step,
            "prob_cut": self.prob_cut,
            "prob_hold": self.prob_hold,
            "prob_hike": self.prob_hike,
            "modal_move": self.modal_move,
            "modal_prob": self.modal_prob,
            "expected_move_bps": self.expected_move_bps,
            "uncertainty_bps": self.uncertainty_bps,
            "skew": self.skew,
            "opposite_tail_prob": self.opposite_tail_prob,
        }


def _grid_level_masses(
    strikes: np.ndarray, yes_prices: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Probability mass at each discrete grid level implied by a "rate >= strike" ladder.

    Returns ``(levels, mass)`` where ``levels`` are the rate values that can
    carry mass -- one grid step below the lowest strike, then each strike -- and
    ``mass`` the probability the target lands exactly there. For a discrete policy
    rate the mass between strike ``i`` and ``i+1`` belongs to level ``strike[i]``
    (the rate sits there until it reaches the next strike), and ``1 - yes[0]`` of
    mass sits one step below the lowest strike.
    """
    step = float(strikes[1] - strikes[0]) if len(strikes) > 1 else 0.25
    below_level = strikes[0] - step
    # Mass at each strike: yes[i] - yes[i+1], with a virtual yes[n] = 0 so the
    # top strike keeps its own "Yes" price as the mass at (or above) that level.
    at_strike = yes_prices - np.append(yes_prices[1:], 0.0)
    below_mass = 1.0 - yes_prices[0]

    levels = np.concatenate(([below_level], strikes))
    mass = np.concatenate(([below_mass], at_strike))
    mass = np.clip(mass, 0.0, None)
    total = mass.sum()
    if total <= 0:
        raise ValueError("ladder implies zero total probability mass")
    return levels, mass / total


def rate_decision_signal(
    strikes: list[float],
    yes_prices: list[float],
    current_rate: float,
    step: float = 0.25,
    price_tol: float = 1e-9,
) -> PolicySignal:
    """Read a fed funds ladder as a discrete cut/hold/hike policy signal.

    Parameters
    ----------
    strikes : list[float]
        Candidate target rates on the policy grid, strictly increasing (e.g.
        ``[4.00, 4.25, 4.50, 4.75]``).
    yes_prices : list[float]
        "Yes" price (0-1) for "rate >= this strike", aligned with ``strikes``.
    current_rate : float
        The current target rate that moves are measured against.
    step : float
        Policy grid spacing in rate units (0.25 = one 25bp move). Grid levels are
        rounded to the nearest ``step`` (half rounded up) before counting moves.
    price_tol : float
        Tolerance passed to ``ladder_validation.validate_ladder``; the ladder is
        screened for no-arbitrage/shape and a failure raises
        ``LadderArbitrageError`` rather than producing a misleading signal.

    Returns
    -------
    PolicySignal
        The discrete move distribution and its policy-relevant summaries.
    """
    if step <= 0:
        raise ValueError("step must be positive")
    lv.validate_ladder(strikes, yes_prices, price_tol=price_tol).raise_if_invalid()

    strikes_arr = np.asarray(strikes, dtype=float)
    yes_arr = np.asarray(yes_prices, dtype=float)

    levels, mass = _grid_level_masses(strikes_arr, yes_arr)

    # Express each level as a signed integer number of `step` moves from the
    # current rate. Half rounds up (floor(x + 0.5)) so the mapping is
    # deterministic on exact half-steps, unlike banker's rounding.
    moves = np.floor((levels - current_rate) / step + 0.5).astype(int)

    # Aggregate mass that maps to the same number of moves.
    move_probs: dict[int, float] = {}
    for k, m in zip(moves, mass, strict=True):
        move_probs[int(k)] = move_probs.get(int(k), 0.0) + float(m)
    move_probs = {k: move_probs[k] for k in sorted(move_probs)}

    ks = np.array(sorted(move_probs), dtype=float)
    ps = np.array([move_probs[int(k)] for k in ks], dtype=float)
    move_bps = ks * step * 100.0

    prob_cut = float(ps[ks < 0].sum())
    prob_hold = float(ps[ks == 0].sum())
    prob_hike = float(ps[ks > 0].sum())

    modal_idx = int(np.argmax(ps))
    modal_move = int(ks[modal_idx])
    modal_prob = float(ps[modal_idx])

    expected_bps = float(np.sum(ps * move_bps))
    variance_bps2 = float(np.sum(ps * (move_bps - expected_bps) ** 2))
    uncertainty_bps = float(np.sqrt(variance_bps2))
    if uncertainty_bps > 0:
        skew = float(np.sum(ps * (move_bps - expected_bps) ** 3) / uncertainty_bps**3)
    else:
        skew = float("nan")

    if expected_bps > 0:
        opposite_tail = prob_cut
    elif expected_bps < 0:
        opposite_tail = prob_hike
    else:
        opposite_tail = min(prob_cut, prob_hike)

    return PolicySignal(
        current_rate=float(current_rate),
        step=float(step),
        move_probabilities=move_probs,
        prob_cut=prob_cut,
        prob_hold=prob_hold,
        prob_hike=prob_hike,
        modal_move=modal_move,
        modal_prob=modal_prob,
        expected_move_bps=expected_bps,
        uncertainty_bps=uncertainty_bps,
        skew=skew,
        opposite_tail_prob=opposite_tail,
    )


def point_forecast_gap(signal: PolicySignal) -> float:
    """The two-sided risk a point forecast at the expected move would miss.

    A futures quote or an OIS-implied path is a single number: it says "the market
    expects roughly a hike" (or a cut, or a hold) and stops. It cannot say that,
    *at the same time*, the market prices a material chance of the opposite move.
    This returns exactly that omitted probability -- ``signal.opposite_tail_prob``
    -- as the scalar cost of collapsing the distribution to its mean, the number
    Section 6 uses to argue the distribution is worth carrying alongside OIS.
    """
    return signal.opposite_tail_prob
