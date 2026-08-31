"""Unit tests for the probability-calibration scoring in ``calibration``.

Pure and deterministic, no network and no RNG.

This is the correctly named home for the calibration tests. It supersedes both
``tests/test_callibration.py`` (an empty file with a misspelled name, called out
in TODO.md) and ``tests/test_calibration_new.py`` (the working tests under a
placeholder name). Delete those two files when you add this one so there is a
single, correctly named test module.
"""

from __future__ import annotations

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
        # All forecasts land in one bin, so exactly one row despite n_bins=10.
        table = cal.reliability_table([0.25, 0.25, 0.25], [0, 1, 0], n_bins=10)
        assert len(table) == 1
        assert table.iloc[0]["n"] == 3

    def test_gap_positive_when_overconfident(self):
        # Forecast 0.9 but the event happens only half the time, so a positive gap.
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


class TestVolumeStratifiedCalibration:
    def test_columns_and_one_row_per_nonempty_bucket(self):
        # Two markets in the low bucket, one in the high bucket.
        preds = [0.6, 0.4, 0.9]
        outs = [1, 0, 1]
        vols = [5_000.0, 8_000.0, 300_000.0]
        df = cal.volume_stratified_calibration(preds, outs, vols)
        assert list(df.columns) == [
            "bucket_lower",
            "bucket_upper",
            "n",
            "brier",
            "base_rate",
        ]
        # Default edges (0, 1e4, 5e4, 2e5, inf): low bucket has 2, top has 1.
        assert df["n"].tolist() == [2, 1]
        assert df.iloc[0]["bucket_lower"] == pytest.approx(0.0)
        assert df.iloc[1]["bucket_upper"] == float("inf")

    def test_brier_matches_manual_per_bucket(self):
        preds = [0.6, 0.4, 0.9]
        outs = [1, 0, 1]
        vols = [5_000.0, 8_000.0, 300_000.0]
        df = cal.volume_stratified_calibration(preds, outs, vols)
        # Low bucket: ((0.6-1)^2 + (0.4-0)^2) / 2 = (0.16 + 0.16) / 2 = 0.16.
        assert df.iloc[0]["brier"] == pytest.approx(0.16)
        # Top bucket: (0.9-1)^2 = 0.01.
        assert df.iloc[1]["brier"] == pytest.approx(0.01)

    def test_learning_curve_shape_is_recoverable(self):
        # Deeper markets priced sharper: Brier should fall down the buckets.
        preds = [0.55, 0.45, 0.8, 0.2, 0.97, 0.02]
        outs = [1, 0, 1, 0, 1, 0]
        vols = [1_000.0, 2_000.0, 60_000.0, 70_000.0, 500_000.0, 600_000.0]
        df = cal.volume_stratified_calibration(preds, outs, vols)
        briers = df["brier"].tolist()
        assert briers == sorted(briers, reverse=True)

    def test_custom_edges_for_trader_counts(self):
        traders = [5.0, 50.0, 500.0]
        df = cal.volume_stratified_calibration(
            [0.5, 0.5, 0.5], [1, 0, 1], traders, bucket_edges=[0, 20, 100, 1000]
        )
        assert df["n"].tolist() == [1, 1, 1]

    def test_misaligned_volumes_raise(self):
        with pytest.raises(ValueError):
            cal.volume_stratified_calibration([0.5, 0.5], [1, 0], [1000.0])

    def test_non_increasing_edges_raise(self):
        with pytest.raises(ValueError):
            cal.volume_stratified_calibration(
                [0.5], [1], [1000.0], bucket_edges=[0, 100, 100]
            )

    def test_negative_volume_raises(self):
        with pytest.raises(ValueError):
            cal.volume_stratified_calibration([0.5], [1], [-1.0])
