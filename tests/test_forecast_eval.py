"""Unit tests for the forecast-accuracy evaluation in ``forecast_eval``.

Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import forecast_eval as fe


class TestAccuracyMetrics:
    def test_known_values(self):
        df = pd.DataFrame({"mean": [4.0, 4.5]})
        out = fe.accuracy_metrics(df, realized_value=4.25)
        # errors = [-0.25, +0.25]
        assert out["n"] == 2
        assert out["mae"] == pytest.approx(0.25)
        assert out["rmse"] == pytest.approx(0.25)
        assert out["bias"] == pytest.approx(0.0)

    def test_bias_is_signed(self):
        df = pd.DataFrame({"mean": [4.5, 4.6]})
        out = fe.accuracy_metrics(df, realized_value=4.0)
        assert out["bias"] == pytest.approx(0.55)

    def test_hit_rate(self):
        df = pd.DataFrame({"mean": [4.0, 4.2, 5.0]})
        out = fe.accuracy_metrics(df, realized_value=4.1, hit_tol=0.15)
        # abs errors = [0.1, 0.1, 0.9]; within 0.15 -> 2/3
        assert out["hit_rate"] == pytest.approx(2 / 3)

    def test_missing_column_raises(self):
        with pytest.raises(ValueError):
            fe.accuracy_metrics(pd.DataFrame({"x": [1]}), 1.0, value_col="mean")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            fe.accuracy_metrics(pd.DataFrame({"mean": []}), 1.0)


class TestMetricsByHorizon:
    def test_pools_two_events_by_horizon(self):
        ev1 = (
            pd.DataFrame({"date": pd.to_datetime(["2026-03-10", "2026-03-15"]), "mean": [4.0, 4.2]}),
            4.25,
            pd.Timestamp("2026-03-20"),
        )
        ev2 = (
            pd.DataFrame({"date": pd.to_datetime(["2026-06-10", "2026-06-15"]), "mean": [4.5, 4.3]}),
            4.25,
            pd.Timestamp("2026-06-20"),
        )
        out = fe.metrics_by_horizon([ev1, ev2])
        assert list(out.columns) == ["days_before_event", "n", "rmse", "mae", "bias"]
        # horizons 10 and 5 days appear in both events -> n == 2 each
        assert set(out["days_before_event"]) == {10, 5}
        assert (out["n"] == 2).all()
        # horizon 10: errors -0.25 and +0.25 -> bias 0, mae 0.25
        h10 = out.loc[out["days_before_event"] == 10].iloc[0]
        assert h10["bias"] == pytest.approx(0.0)
        assert h10["mae"] == pytest.approx(0.25)

    def test_empty_events_raises(self):
        with pytest.raises(ValueError):
            fe.metrics_by_horizon([])


class TestDieboldMariano:
    def test_identical_errors_cannot_reject(self):
        e = np.array([0.1, -0.2, 0.3, -0.1, 0.05])
        stat, p = fe.diebold_mariano(e, e)
        assert stat == pytest.approx(0.0)
        assert p == pytest.approx(1.0)

    def test_sign_when_a_is_worse(self):
        # A strictly larger absolute errors than B -> A worse -> positive stat.
        b = np.array([0.05, -0.05, 0.05, -0.05, 0.05, -0.05])
        a = b * 3.0
        stat, p = fe.diebold_mariano(a, b)
        assert stat > 0
        assert 0.0 <= p <= 1.0

    def test_sign_when_a_is_better(self):
        a = np.array([0.05, -0.05, 0.05, -0.05, 0.05, -0.05])
        b = a * 3.0
        stat, _ = fe.diebold_mariano(a, b)
        assert stat < 0

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            fe.diebold_mariano([1.0, 2.0], [1.0])

    def test_too_few_obs_raises(self):
        with pytest.raises(ValueError):
            fe.diebold_mariano([1.0], [0.5])

    def test_newey_west_lags_run(self):
        rng = np.random.default_rng(0)
        a = rng.normal(size=50)
        b = rng.normal(size=50)
        stat, p = fe.diebold_mariano(a, b, h=4)
        assert np.isfinite(stat)
        assert 0.0 <= p <= 1.0
