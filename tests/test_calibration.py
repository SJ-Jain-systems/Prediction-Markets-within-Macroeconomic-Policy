"""Unit tests for the probability-calibration scoring in ``calibration``.

Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

import numpy as np
import pytest

import calibration as cal


class TestBrierScore:
    def test_perfect_forecast_is_zero(self):
        assert cal.brier_score([1.0, 0.0, 1.0], [1, 0, 1]) == pytest.approx(0.0)

    def test_worst_forecast_is_one(self):
        assert cal.brier_score([0.0, 1.0], [1, 0]) == pytest.approx(1.0)

    def test_coin_flip_forecast(self):
        # (0.5 - 1)^2 and (0.5 - 0)^2 both equal 0.25.
        assert cal.brier_score([0.5, 0.5], [1, 0]) == pytest.approx(0.25)

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            cal.brier_score([1.2, 0.3], [1, 0])

    def test_non_binary_outcome_raises(self):
        with pytest.raises(ValueError):
            cal.brier_score([0.5, 0.5], [1, 0.5])

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            cal.brier_score([], [])


class TestReliabilityTable:
    def test_columns(self):
        table = cal.reliability_table([0.2, 0.8], [0, 1])
        assert list(table.columns) == [
            "bin_lower",
            "bin_upper",
            "n",
            "mean_pred",
            "obs_freq",
            "gap",
        ]

    def test_prob_one_lands_in_last_bin(self):
        table = cal.reliability_table([1.0], [1], n_bins=10)
        assert len(table) == 1
        row = table.iloc[0]
        assert row["bin_lower"] == pytest.approx(0.9)
        assert row["bin_upper"] == pytest.approx(1.0)

    def test_empty_bins_are_omitted(self):
        # All forecasts land in one bin -> exactly one row despite n_bins=10.
        table = cal.reliability_table([0.25, 0.25, 0.25], [0, 1, 0], n_bins=10)
        assert len(table) == 1
        assert table.iloc[0]["n"] == 3

    def test_gap_positive_when_overconfident(self):
        # Forecast 0.9 but the event happens only half the time -> positive gap.
        table = cal.reliability_table([0.9, 0.9], [1, 0])
        assert table.iloc[0]["gap"] == pytest.approx(0.4)


class TestCalibrationReport:
    def _well_calibrated_data(self):
        # 0.2 bin: 1 of 5 outcomes is 1 (obs freq 0.2, matches the forecast).
        # 0.8 bin: 4 of 5 outcomes is 1 (obs freq 0.8, matches the forecast).
        preds = [0.2] * 5 + [0.8] * 5
        outs = [1, 0, 0, 0, 0] + [1, 1, 1, 1, 0]
        return preds, outs

    def test_base_rate_and_uncertainty(self):
        preds, outs = self._well_calibrated_data()
        r = cal.calibration_report(preds, outs)
        assert r.n == 10
        assert r.base_rate == pytest.approx(0.5)
        assert r.uncertainty == pytest.approx(0.25)  # 0.5 * (1 - 0.5)

    def test_well_calibrated_has_near_zero_reliability(self):
        preds, outs = self._well_calibrated_data()
        r = cal.calibration_report(preds, outs)
        assert r.reliability == pytest.approx(0.0)
        assert r.ece == pytest.approx(0.0)
        assert r.resolution > 0.0  # the forecasts do separate the two bins

    def test_murphy_decomposition_identity(self):
        # With identical forecasts inside each bin there is no within-bin
        # variance, so brier == reliability - resolution + uncertainty exactly.
        preds, outs = self._well_calibrated_data()
        r = cal.calibration_report(preds, outs)
        rebuilt = r.reliability - r.resolution + r.uncertainty
        assert rebuilt == pytest.approx(r.brier)

    def test_shape_mismatch_raises(self):
        with pytest.raises(ValueError):
            cal.calibration_report([0.5, 0.5], [1])
