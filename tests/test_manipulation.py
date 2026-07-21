"""Unit tests for the manipulation cost-to-move model in ``manipulation``.

Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

import pytest

import manipulation as mp


# A symmetric fed-funds-style ladder around 4.25.
STRIKES = [4.00, 4.25, 4.50]
YES = [0.75, 0.50, 0.25]


class TestCostToMove:
    def test_zero_shift_is_free(self):
        assert mp.cost_to_move(STRIKES, YES, target_mean_shift=0.0, depth_dollars=1e6) == pytest.approx(0.0)

    def test_larger_shift_costs_more(self):
        small = mp.cost_to_move(STRIKES, YES, 0.10, depth_dollars=1e6)
        large = mp.cost_to_move(STRIKES, YES, 0.25, depth_dollars=1e6)
        assert large > small > 0

    def test_thinner_market_is_cheaper(self):
        deep = mp.cost_to_move(STRIKES, YES, 0.20, depth_dollars=1e8)
        thin = mp.cost_to_move(STRIKES, YES, 0.20, depth_dollars=1e4)
        assert thin < deep

    def test_cost_scales_linearly_with_depth(self):
        c1 = mp.cost_to_move(STRIKES, YES, 0.20, depth_dollars=1e6)
        c2 = mp.cost_to_move(STRIKES, YES, 0.20, depth_dollars=2e6)
        assert c2 == pytest.approx(2 * c1)

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError):
            mp.cost_to_move(STRIKES, YES, 0.1, depth_dollars=-1.0)


class TestProbabilityMoveCost:
    def test_linear_in_target(self):
        c = mp.probability_move_cost(STRIKES, YES, strike=4.25, target_prob_shift=0.1, depth_dollars=1e6)
        assert c == pytest.approx(0.1 * 1e6)

    def test_sign_ignored(self):
        up = mp.probability_move_cost(STRIKES, YES, 4.25, 0.1, 1e6)
        down = mp.probability_move_cost(STRIKES, YES, 4.25, -0.1, 1e6)
        assert up == pytest.approx(down)

    def test_unknown_strike_raises(self):
        with pytest.raises(ValueError):
            mp.probability_move_cost(STRIKES, YES, strike=9.99, target_prob_shift=0.1, depth_dollars=1e6)


class TestExposureVsCap:
    def test_ratio(self):
        assert mp.exposure_vs_cap(3_500_000) == pytest.approx(0.5)

    def test_below_one_flags_vulnerable(self):
        assert mp.exposure_vs_cap(1_000_000) < 1.0

    def test_custom_cap(self):
        assert mp.exposure_vs_cap(2_000_000, cap=1_000_000) == pytest.approx(2.0)

    def test_nonpositive_cap_raises(self):
        with pytest.raises(ValueError):
            mp.exposure_vs_cap(1.0, cap=0.0)
