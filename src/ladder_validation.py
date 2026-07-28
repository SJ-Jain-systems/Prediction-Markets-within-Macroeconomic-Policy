"""
No-arbitrage validation for a Kalshi "exceeds strike X" price ladder.

``kalshi_utils.ladder_to_pdf`` converts a ladder of binary "Yes" prices into a
risk-neutral distribution, but it does so *defensively*: it clips negative
implied masses to zero and renormalizes, so a malformed or arbitraged ladder is
silently turned into a plausible-looking pdf. That is the right behavior for a
production pipeline, but it means a data-quality problem can pass unnoticed into
the forecasts the paper's claims rest on.

This module makes the arbitrage-free conditions *explicit and checkable*. For a
contract that pays $1 when the outcome exceeds a strike, the arbitrage-free
"Yes" price ladder must satisfy (FEDS 2026, Section 3, "Converting Kalshi into
Probability Distributions"):

  * each "Yes" price lies in ``[0, 1]`` (it is a probability); and
  * "Yes" prices are **non-increasing** as the strike rises -- a higher bar can
    only be *less* likely to be exceeded. A price that rises with the strike is a
    static arbitrage: buy the cheaper high-strike "Yes", sell the dearer
    low-strike "Yes", and collect a risk-free spread.

Use ``validate_ladder`` to screen a pull before feeding it to
``ladder_to_pdf``; ``raise_if_invalid`` turns a failed screen into an exception
for a strict pipeline. Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


class LadderArbitrageError(ValueError):
    """Raised when a ladder violates the no-arbitrage / well-formedness conditions."""


@dataclass
class LadderValidation:
    """Result of validating a strike ladder for no-arbitrage and shape.

    Attributes
    ----------
    ok
        ``True`` iff no violations were found. ``bool(result)`` is an alias, so a
        validation result can be used directly in an ``if`` or ``assert``.
    violations
        Human-readable strings, one per problem found (empty when ``ok``).
    n_strikes
        Number of strikes seen (length of the ``strikes`` argument).
    """

    ok: bool
    violations: list[str] = field(default_factory=list)
    n_strikes: int = 0

    def __bool__(self) -> bool:
        return self.ok

    def raise_if_invalid(self) -> LadderValidation:
        """Return ``self`` if valid, else raise ``LadderArbitrageError``.

        Lets a strict caller write ``validate_ladder(...).raise_if_invalid()`` and
        get either the (valid) result back for chaining or an exception whose
        message lists every violation.
        """
        if not self.ok:
            raise LadderArbitrageError(
                "ladder failed no-arbitrage validation: " + "; ".join(self.violations)
            )
        return self


def validate_ladder(
    strikes: list[float],
    yes_prices: list[float],
    price_tol: float = 1e-9,
) -> LadderValidation:
    """Check a strike ladder for the no-arbitrage and shape conditions.

    Parameters
    ----------
    strikes : list[float]
        Strike thresholds, expected strictly increasing (e.g. ``[4.00, 4.25, ...]``).
    yes_prices : list[float]
        "Yes" price (0-1) for "outcome exceeds this strike", aligned with
        ``strikes``.
    price_tol : float
        Absolute tolerance absorbing rounding noise: a price is treated as in
        ``[0, 1]`` if within ``price_tol`` of the bounds, and a strike-to-strike
        *increase* in "Yes" price counts as an arbitrage only if it exceeds
        ``price_tol`` (so an exactly flat step, or a sub-tick wobble, passes).

    Returns
    -------
    LadderValidation
        ``ok`` / ``violations`` / ``n_strikes``. The checks are, in order:
        length agreement (short-circuits, since nothing else is well-defined on
        mismatched inputs), non-emptiness, strictly increasing strikes, prices in
        ``[0, 1]``, and non-increasing prices (the no-arbitrage monotonicity). The
        monotonicity check is skipped when the strikes are not strictly
        increasing, because "as the strike rises" is undefined there.
    """
    violations: list[str] = []
    n_strikes = len(strikes)

    # Length mismatch makes every downstream check ill-defined -> short-circuit.
    if len(strikes) != len(yes_prices):
        violations.append(
            f"length mismatch: {len(strikes)} strikes vs {len(yes_prices)} yes prices"
        )
        return LadderValidation(ok=False, violations=violations, n_strikes=n_strikes)

    if n_strikes == 0:
        violations.append("empty ladder: no strikes to validate")
        return LadderValidation(ok=False, violations=violations, n_strikes=n_strikes)

    strikes_arr = np.asarray(strikes, dtype=float)
    yes_arr = np.asarray(yes_prices, dtype=float)

    strikes_increasing = bool(np.all(np.diff(strikes_arr) > 0)) if n_strikes > 1 else True
    if not strikes_increasing:
        violations.append("strikes must be strictly increasing")

    # Prices are probabilities: they must lie in [0, 1] up to the tolerance.
    out_of_range = np.where((yes_arr < -price_tol) | (yes_arr > 1.0 + price_tol))[0]
    for i in out_of_range:
        violations.append(
            f"yes price {yes_arr[i]:.6g} at strike {strikes_arr[i]:.6g} is out of [0, 1]"
        )

    # No-arbitrage monotonicity: "Yes" prices must not rise with the strike.
    # Only meaningful once the strikes themselves are properly ordered.
    if strikes_increasing and n_strikes > 1:
        rises = np.diff(yes_arr)
        for i in np.where(rises > price_tol)[0]:
            violations.append(
                "arbitrage: yes price rises from "
                f"{yes_arr[i]:.6g} (strike {strikes_arr[i]:.6g}) to "
                f"{yes_arr[i + 1]:.6g} (strike {strikes_arr[i + 1]:.6g}); "
                "a higher strike cannot be more likely to be exceeded"
            )

    return LadderValidation(ok=not violations, violations=violations, n_strikes=n_strikes)
