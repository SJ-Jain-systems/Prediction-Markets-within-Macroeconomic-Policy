"""Unit tests for the discrete monetary-policy read in ``policy_signals``.

Pure and deterministic -- no network, no RNG. The two worked ladders below are
hand-checked in the comments so the expected numbers are auditable.
"""

from __future__ import annotations

import math

import pytest

import ladder_validation as lv
import policy_signals as ps

# A symmetric ladder around a 4.25 target on the 25bp grid.
#   strikes: 4.00 4.25 4.50 4.75 ;  yes = P(rate >= strike)
#   level masses -> below-4.00: 0.05, 4.00: 0.25, 4.25: 0.40, 4.50: 0.25, 4.75: 0.05
#   as moves from 4.25:  -2:0.05  -1:0.25  0:0.40  +1:0.25  +2:0.05  (sums to 1)
SYM_STRIKES = [4.00, 4.25, 4.50, 4.75]
SYM_YES = [0.95, 0.70, 0.30, 0.05]

# A hike-tilted ladder around the same 4.25 target.
#   level masses -> below-4.00: 0.05, 4.00: 0.05, 4.25: 0.10, 4.50: 0.20, 4.75: 0.60
#   as moves:  -2:0.05  -1:0.05  0:0.10  +1:0.20  +2:0.60
HIKE_STRIKES = [4.00, 4.25, 4.50, 4.75]
HIKE_YES = [0.95, 0.90, 0.80, 0.60]


class TestSymmetricLadder:
    def test_move_probabilities(self):
        sig = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        assert sig.move_probabilities == pytest.approx(
            {-2: 0.05, -1: 0.25, 0: 0.40, 1: 0.25, 2: 0.05}
        )
        assert sum(sig.move_probabilities.values()) == pytest.approx(1.0)

    def test_cut_hold_hike_split(self):
        sig = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        assert sig.prob_cut == pytest.approx(0.30)
        assert sig.prob_hold == pytest.approx(0.40)
        assert sig.prob_hike == pytest.approx(0.30)
        assert sig.prob_cut + sig.prob_hold + sig.prob_hike == pytest.approx(1.0)

    def test_symmetry_gives_zero_expected_move_and_no_skew(self):
        sig = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        assert sig.expected_move_bps == pytest.approx(0.0)
        assert sig.skew == pytest.approx(0.0, abs=1e-9)
        assert sig.modal_move == 0
        assert sig.modal_prob == pytest.approx(0.40)

    def test_opposite_tail_is_the_smaller_side_when_flat(self):
        # Expected move is zero, so the two-sided risk is min(cut, hike).
        sig = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        assert sig.opposite_tail_prob == pytest.approx(0.30)
        assert ps.point_forecast_gap(sig) == pytest.approx(0.30)


class TestHikeTiltedLadder:
    def test_hike_probability_dominates(self):
        sig = ps.rate_decision_signal(HIKE_STRIKES, HIKE_YES, current_rate=4.25)
        assert sig.prob_hike == pytest.approx(0.80)
        assert sig.prob_hold == pytest.approx(0.10)
        assert sig.prob_cut == pytest.approx(0.10)
        assert sig.modal_move == 2

    def test_expected_move_is_positive(self):
        # (-2*.05 -1*.05 +1*.20 +2*.60) moves * 25bp = 1.25 moves * 25 = 31.25bp
        sig = ps.rate_decision_signal(HIKE_STRIKES, HIKE_YES, current_rate=4.25)
        assert sig.expected_move_bps == pytest.approx(31.25)

    def test_opposite_tail_is_the_cut_probability(self):
        # Market expects a hike on net, so the risk a point forecast misses is
        # the cut probability.
        sig = ps.rate_decision_signal(HIKE_STRIKES, HIKE_YES, current_rate=4.25)
        assert sig.opposite_tail_prob == pytest.approx(sig.prob_cut)
        assert sig.opposite_tail_prob == pytest.approx(0.10)

    def test_left_tail_gives_negative_skew(self):
        # Mass piled at +2 with a thin tail toward cuts -> long left tail.
        sig = ps.rate_decision_signal(HIKE_STRIKES, HIKE_YES, current_rate=4.25)
        assert sig.skew < 0.0


class TestUncertaintyAndDispersion:
    def test_wider_ladder_has_more_uncertainty(self):
        # A near-certain hold has almost no dispersion; the symmetric ladder has
        # real two-sided mass, so more uncertainty.
        near_certain = ps.rate_decision_signal(
            [4.00, 4.25, 4.50, 4.75], [0.999, 0.999, 0.001, 0.001], current_rate=4.25
        )
        spread = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        assert near_certain.uncertainty_bps < spread.uncertainty_bps

    def test_degenerate_distribution_has_nan_skew(self):
        # All mass on a single hold outcome (yes[0]=1, everything above 0) ->
        # zero dispersion, undefined skew.
        sig = ps.rate_decision_signal(
            [4.00, 4.25, 4.50], [1.0, 0.0, 0.0], current_rate=4.00
        )
        assert sig.prob_hold == pytest.approx(1.0)
        assert sig.uncertainty_bps == pytest.approx(0.0)
        assert math.isnan(sig.skew)


class TestValidationAndErrors:
    def test_arbitraged_ladder_raises(self):
        # Non-monotone "Yes" prices are a static arbitrage -> rejected up front.
        with pytest.raises(lv.LadderArbitrageError):
            ps.rate_decision_signal([4.00, 4.25], [0.3, 0.6], current_rate=4.00)

    def test_out_of_range_price_raises(self):
        with pytest.raises(lv.LadderArbitrageError):
            ps.rate_decision_signal([4.00, 4.25], [1.4, 0.2], current_rate=4.00)

    def test_bad_step_raises(self):
        with pytest.raises(ValueError):
            ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25, step=0.0)

    def test_as_dict_has_scalar_fields(self):
        sig = ps.rate_decision_signal(SYM_STRIKES, SYM_YES, current_rate=4.25)
        d = sig.as_dict()
        assert "move_probabilities" not in d
        assert d["prob_hold"] == pytest.approx(0.40)
        assert set(d) == {
            "current_rate",
            "step",
            "prob_cut",
            "prob_hold",
            "prob_hike",
            "modal_move",
            "modal_prob",
            "expected_move_bps",
            "uncertainty_bps",
            "skew",
            "opposite_tail_prob",
        }
