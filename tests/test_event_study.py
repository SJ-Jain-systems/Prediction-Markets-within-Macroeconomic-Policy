"""Unit tests for the higher-moment event study in ``event_study``.

Pure and deterministic -- no network, no RNG.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import event_study as es


def _daily_moments(dates, variance, skewness=None, mean=None):
    n = len(dates)
    return pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "mean": mean if mean is not None else np.full(n, 4.25),
            "variance": variance,
            "skewness": skewness if skewness is not None else np.zeros(n),
        }
    )


class TestEventWindow:
    def test_slices_and_indexes_relative_days(self):
        dates = pd.date_range("2026-03-15", "2026-03-25", freq="D")
        df = _daily_moments(dates, variance=np.arange(len(dates), dtype=float))
        out = es.event_window(df, event_date=pd.Timestamp("2026-03-20"), pre=2, post=2)
        assert out["days_relative_to_event"].tolist() == [-2, -1, 0, 1, 2]
        # ascending and includes the moment columns
        assert "variance" in out.columns

    def test_empty_window_returns_empty(self):
        dates = pd.date_range("2026-03-01", "2026-03-05", freq="D")
        df = _daily_moments(dates, variance=np.ones(5))
        out = es.event_window(df, event_date=pd.Timestamp("2026-12-01"), pre=1, post=1)
        assert len(out) == 0

    def test_negative_window_raises(self):
        df = _daily_moments(pd.date_range("2026-03-01", periods=3), variance=np.ones(3))
        with pytest.raises(ValueError):
            es.event_window(df, pd.Timestamp("2026-03-02"), pre=-1)


class TestMomentShifts:
    def test_recovers_injected_variance_jump(self):
        # Flat variance 1.0 before the event, 3.0 after -> shift of +2.0.
        dates = pd.date_range("2026-03-15", "2026-03-25", freq="D")
        event = pd.Timestamp("2026-03-20")
        rel = (dates - event).days
        variance = np.where(rel >= 1, 3.0, 1.0)
        df = _daily_moments(dates, variance=variance)
        out = es.moment_shifts(df, [event], pre=3, post=3, moments=("variance",))
        # last row is the ALL average
        assert out.iloc[-1]["event_date"] == "ALL"
        assert out.iloc[0]["d_variance"] == pytest.approx(2.0)
        assert out.iloc[-1]["d_variance"] == pytest.approx(2.0)

    def test_averages_across_events(self):
        dates = pd.date_range("2026-01-01", "2026-12-31", freq="D")
        e1 = pd.Timestamp("2026-03-20")
        e2 = pd.Timestamp("2026-06-20")
        rel1 = (dates - e1).days
        rel2 = (dates - e2).days
        # Baseline 1.0 everywhere; a +2 jump only in e1's post-window and a +4
        # jump only in e2's post-window keep the two events independent, so the
        # ALL average is (2 + 4) / 2 = 3.
        variance = np.full(len(dates), 1.0)
        variance[(rel1 >= 1) & (rel1 <= 3)] = 3.0  # +2 vs pre=1
        variance[(rel2 >= 1) & (rel2 <= 3)] = 5.0  # +4 vs pre=1
        df = _daily_moments(dates, variance=variance)
        out = es.moment_shifts(df, [e1, e2], pre=3, post=3, moments=("variance",))
        shifts = out.set_index("event_date")["d_variance"]
        assert shifts.loc[pd.Timestamp(e1)] == pytest.approx(2.0)
        assert shifts.loc[pd.Timestamp(e2)] == pytest.approx(4.0)
        assert shifts.loc["ALL"] == pytest.approx(3.0)

    def test_empty_side_gives_nan(self):
        # Only post-window data exists -> pre-window empty -> NaN shift.
        dates = pd.date_range("2026-03-20", "2026-03-25", freq="D")
        df = _daily_moments(dates, variance=np.ones(len(dates)))
        out = es.moment_shifts(df, [pd.Timestamp("2026-03-20")], pre=3, post=3, moments=("variance",))
        assert np.isnan(out.iloc[0]["d_variance"])

    def test_missing_moment_column_raises(self):
        df = _daily_moments(pd.date_range("2026-03-01", periods=5), variance=np.ones(5))
        with pytest.raises(ValueError):
            es.moment_shifts(df, [pd.Timestamp("2026-03-03")], moments=("kurtosis",))

    def test_empty_events_raises(self):
        df = _daily_moments(pd.date_range("2026-03-01", periods=5), variance=np.ones(5))
        with pytest.raises(ValueError):
            es.moment_shifts(df, [])
