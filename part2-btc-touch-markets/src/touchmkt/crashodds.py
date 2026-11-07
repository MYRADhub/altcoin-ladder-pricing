"""Do betting markets forecast drawdowns better than history? Plan: research.md, "Follow-up: do betting markets forecast
drawdowns better than history?".

    python -m touchmkt.crashodds
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from . import download, evaluate

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
HAR_H = (24, 168, 720)


def har_daily_var(close_1m: pd.Series) -> pd.Series:
    """Daily variance by hour close: mean of 24 x mean squared hourly log return over the last 1, 7 and 30 days."""
    h = close_1m.resample("1h", label="right", closed="left").last().dropna()  # bars opening in [H-1h, H), all closed by H
    r2 = np.log(h / h.shift(1)) ** 2
    parts = [24 * r2.rolling(n, min_periods=int(0.9 * n)).mean() for n in HAR_H]
    return pd.concat(parts, axis=1).mean(axis=1, skipna=False)


def touch_hist(direction: np.ndarray, s: np.ndarray, k: np.ndarray, var_daily: np.ndarray, days: np.ndarray) -> np.ndarray:
    """2 x P(finish beyond K) under a driftless-price lognormal with total variance var_daily x days, capped at 1."""
    w = np.maximum(var_daily * days, 1e-12)
    sd = np.sqrt(w)
    d2 = (np.log(s / k) - 0.5 * w) / sd
    beyond = np.where(direction == "reach", norm.cdf(d2), norm.cdf(-d2))
    return np.minimum(1.0, 2.0 * beyond)


def asof(series: pd.Series, times: pd.Series) -> np.ndarray:
    idx = series.index.searchsorted(pd.DatetimeIndex(times), side="right") - 1
    return np.where(idx >= 0, series.to_numpy()[np.clip(idx, 0, None)], np.nan)


def brier_tests(tr: pd.DataFrame) -> dict:
    t = tr.assign(b_mkt=(tr["p"] - tr["y"]) ** 2, b_opt=(tr["FAIR"] - tr["y"]) ** 2, b_hist=(tr["HIST"] - tr["y"]) ** 2)
    e = evaluate.event_means(t, ["b_mkt", "b_opt", "b_hist"])
    days = e["day"].to_numpy()
    out = {"events": int(len(e)), "brier": {"market": float(e["b_mkt"].mean()), "options": float(e["b_opt"].mean()),
                                            "history": float(e["b_hist"].mean())}}
    out["tests"] = evaluate.holm({"market minus history": evaluate.test_mean((e["b_mkt"] - e["b_hist"]).to_numpy(), days),
                                  "options minus history": evaluate.test_mean((e["b_opt"] - e["b_hist"]).to_numpy(), days)})
    return out


def main() -> dict:
    tr = pd.read_csv(DATA / "derived" / "trades.csv.gz")
    for c in ("t", "end"):
        tr[c] = pd.to_datetime(tr[c], utc=True, format="ISO8601")
    tr["day"] = pd.to_datetime(tr["day"])
    close = download.load_klines(DATA / "binance")["close"]
    var = har_daily_var(close)
    tr["hist_var"] = asof(var, tr["t"])
    tr["days_left"] = (tr["end"] - tr["t"]).dt.total_seconds() / 86400
    tr["HIST"] = touch_hist(tr["direction"].to_numpy(), tr["spot"].to_numpy(), tr["strike"].to_numpy(), tr["hist_var"].to_numpy(),
                            tr["days_left"].to_numpy())
    tr = tr[np.isfinite(tr["HIST"])].copy()
    dip, reach = tr[tr["direction"] == "dip"], tr[tr["direction"] == "reach"]
    w = dip["size"].to_numpy()
    out = {"primary_dip": brier_tests(dip), "reach": brier_tests(reach),
           "dip_by_kind": {k: brier_tests(g) for k, g in dip.groupby("kind")},
           "dip_5pct_or_more_below": brier_tests(dip[dip["x"] <= np.log(0.95)]),
           "calibration_dip": {m: evaluate.calibration(dip[m].to_numpy(), dip["y"].to_numpy(), w) for m in ("p", "FAIR", "HIST")},
           "median_ratio_hist_to_options_vol": float(np.nanmedian(np.sqrt(tr["hist_var"] * tr["days_left"] / np.maximum(tr["w"], 1e-12))))}
    (ROOT / "results" / "crash_odds.json").write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    o = main()
    p = o["primary_dip"]
    print(json.dumps({"dip": {"brier": p["brier"], "tests": p["tests"]}, "reach_brier": o["reach"]["brier"],
                      "reach_tests": o["reach"]["tests"], "vol_ratio": o["median_ratio_hist_to_options_vol"]}, indent=1))
