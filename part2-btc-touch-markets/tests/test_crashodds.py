import numpy as np
import pandas as pd

from touchmkt import crashodds as C
from touchmkt import pricing as P


def test_hist_touch_matches_the_options_reflection_with_flat_vol():
    vol_d, days = 0.03, 3.0
    for direction, k in (("reach", 104.0), ("dip", 95.0)):
        h = C.touch_hist(np.array([direction]), np.array([100.0]), np.array([k]), np.array([vol_d ** 2]), np.array([days]))[0]
        t = days / 365
        fits = [(t, (vol_d ** 2 * days, 0.0, 0.0))]
        d_up = P.digital_above(100.0, k, t, fits, ref=100.0)
        assert abs(h - P.touch_reflection(direction, d_up)) < 1e-4


def test_har_variance_recovers_constant_hourly_vol_and_uses_closed_hours():
    idx = pd.date_range("2026-01-01", periods=60 * 24 * 40, freq="min", tz="UTC")
    rng = np.random.default_rng(0)
    steps = np.zeros(len(idx))
    steps[::60] = rng.choice([-0.01, 0.01], size=len(steps[::60]))  # one 1% move at the start of each hour
    close = pd.Series(100 * np.exp(np.cumsum(steps)), index=idx)
    v = C.har_daily_var(close).dropna()
    assert abs(v.iloc[-1] - 24 * 0.01 ** 2) < 1e-6
    assert v.index.min() >= idx[0] + pd.Timedelta(hours=648)  # needs 90% of the 30-day window
