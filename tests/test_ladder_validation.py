"""Unit tests for the no-arbitrage ladder validation in ``ladder_validation``.

Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

import pytest

import ladder_validation as lv


class TestValidLadder:
    def test_well_formed_ladder_passes(self):
        res = lv.validate_ladder([4.0, 4.25, 4.5], [0.9, 0.6, 0.2])
        assert res.ok
        assert res.violations == []
        assert res.n_strikes == 3
        assert bool(res) is True

    def test_flat_ladder_passes(self):
        # Non-increasing allows equality (zero implied mass between strikes).
        res = lv.validate_ladder([1.0, 2.0], [0.5, 0.5])
        assert res.ok

    def test_rounding_within_tolerance_passes(self):
        # A tiny increase and a price a hair above 1 are treated as noise.
        res = lv.validate_ladder([1.0, 2.0], [1.0 + 1e-12, 0.4], price_tol=1e-9)
        assert res.ok


class TestArbitrageViolations:
    def test_non_monotone_yes_prices_flagged(self):
        # 0.3 -> 0.5 across increasing strikes is an arbitrage.
        res = lv.validate_ladder([4.0, 4.25], [0.3, 0.5])
        assert not res.ok
        assert any("arbitrage" in v for v in res.violations)

    def test_price_above_one_flagged(self):
        res = lv.validate_ladder([1.0, 2.0], [1.4, 0.2])
        assert not res.ok
        assert any("out of [0, 1]" in v for v in res.violations)

    def test_price_below_zero_flagged(self):
        res = lv.validate_ladder([1.0, 2.0], [0.5, -0.2])
        assert not res.ok
        assert any("out of [0, 1]" in v for v in res.violations)

    def test_raise_if_invalid_raises(self):
        res = lv.validate_ladder([4.0, 4.25], [0.3, 0.5])
        with pytest.raises(lv.LadderArbitrageError):
            res.raise_if_invalid()

    def test_raise_if_invalid_returns_self_when_ok(self):
        res = lv.validate_ladder([1.0, 2.0], [0.6, 0.3])
        assert res.raise_if_invalid() is res


class TestShapeProblems:
    def test_length_mismatch_short_circuits(self):
        res = lv.validate_ladder([1.0, 2.0], [0.5])
        assert not res.ok
        assert any("length mismatch" in v for v in res.violations)

    def test_non_increasing_strikes_flagged(self):
        res = lv.validate_ladder([2.0, 1.0], [0.6, 0.3])
        assert not res.ok
        assert any("strictly increasing" in v for v in res.violations)

    def test_empty_ladder_flagged(self):
        res = lv.validate_ladder([], [])
        assert not res.ok
        assert any("empty" in v for v in res.violations)


class TestAgreesWithLadderToPdf:
    def test_valid_ladder_converts_cleanly(self):
        # A ladder this validator accepts should feed ladder_to_pdf without the
        # silent clipping kicking in (pmf already non-negative and normalized).
        ku = pytest.importorskip("kalshi_utils")
        strikes, yes = [4.0, 4.25, 4.5], [0.9, 0.6, 0.2]
        assert lv.validate_ladder(strikes, yes).ok
        dist = ku.ladder_to_pdf(strikes, yes)
        assert dist.pmf.min() >= 0.0
        assert float(dist.pmf.sum()) == pytest.approx(1.0)
