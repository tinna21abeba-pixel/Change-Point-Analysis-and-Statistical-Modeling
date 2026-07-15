from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns


ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT_DIR / "data" / "raw" / "BrentOilPrices.csv"
EVENTS_PATH = ROOT_DIR / "data" / "events" / "brent_oil_key_events.csv"
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_price_series(raw_path: Optional[Path] = None) -> pd.DataFrame:
    """Load Brent price data, or create a synthetic fallback for demoability."""
    path = raw_path or RAW_PATH

    if path.exists() and path.stat().st_size > 0:
        df = pd.read_csv(path)
        if "Date" not in df.columns or "Price" not in df.columns:
            raise ValueError("Expected columns 'Date' and 'Price' in price data")
    else:
        dates = pd.date_range("1987-05-20", "2022-09-30", freq="B")
        n = len(dates)
        rng = np.random.default_rng(7)
        shocks = rng.normal(0, 0.008, size=n)
        shocks[1200:2500] += 0.014
        shocks[2500:] -= 0.012
        log_price = np.cumsum(shocks) + np.log(40)
        log_price[1500:] += 0.18
        log_price[2500:] -= 0.1
        price = np.exp(log_price) + 10
        df = pd.DataFrame({"Date": dates, "Price": price})

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date", "Price"]).sort_values("Date").reset_index(drop=True)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"]).reset_index(drop=True)
    return df


def prepare_log_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Create log returns and a simple volatility proxy."""
    out = price_df.copy()
    out = out.sort_values("Date").reset_index(drop=True)
    out["log_price"] = np.log(out["Price"])
    out["log_return"] = out["log_price"].diff()
    out = out.dropna(subset=["log_return"]).reset_index(drop=True)
    return out


def associate_change_point_with_events(
    change_point_date: pd.Timestamp,
    events_df: pd.DataFrame,
    window_days: int = 45,
) -> pd.DataFrame:
    """Return events within a window around a detected change point."""
    if events_df.empty:
        return pd.DataFrame(columns=["event_name", "start_date", "days_from_change_point"])

    events_df = events_df.copy()
    events_df["start_date"] = pd.to_datetime(events_df["start_date"], errors="coerce")
    events_df = events_df.dropna(subset=["start_date"]).copy()
    events_df["days_from_change_point"] = (
        events_df["start_date"] - change_point_date
    ).dt.days.abs()
    return events_df.loc[events_df["days_from_change_point"] <= window_days].sort_values(
        "days_from_change_point"
    ).reset_index(drop=True)


def fit_bayesian_change_point(returns: pd.DataFrame, draws: int = 1200, tune: int = 800) -> dict:
    """Fit a simple Bayesian mean-change model to the log returns."""
    y = returns["log_return"].to_numpy(dtype=float)
    n = len(y)
    if n < 10:
        raise ValueError("Not enough observations for Bayesian change point analysis")

    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=1, upper=n - 1)
        mu1 = pm.Normal("mu1", mu=0, sigma=0.1)
        mu2 = pm.Normal("mu2", mu=0, sigma=0.1)
        sigma = pm.HalfNormal("sigma", sigma=0.1)

        time_idx = np.arange(n)
        mu = pm.math.switch(time_idx < tau, mu1, mu2)
        obs = pm.Normal("obs", mu=mu, sigma=sigma, observed=y)
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=4,
            cores=1,
            progressbar=False,
            random_seed=7,
            target_accept=0.95,
        )

    summary = az.summary(trace, var_names=["mu1", "mu2", "sigma", "tau"])
    return {"model": model, "trace": trace, "summary": summary}


def plot_results(returns: pd.DataFrame, fit_result: dict, events_df: Optional[pd.DataFrame] = None) -> None:
    """Generate summary plots and save them to the reports folder."""
    trace = fit_result["trace"]
    summary = fit_result["summary"]

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    tau_samples = trace.posterior["tau"].values.flatten()
    change_point_index = int(np.median(tau_samples))
    change_point_date = returns["Date"].iloc[change_point_index]

    ax = axes[0, 0]
    ax.plot(returns["Date"], returns["log_return"], color="#1f4e79", linewidth=0.8)
    ax.axvline(change_point_date, color="firebrick", linestyle="--", linewidth=1.5)
    ax.set_title("Log returns with posterior median change point")
    ax.set_xlabel("Date")
    ax.set_ylabel("Log return")

    ax = axes[0, 1]
    ax.hist(trace.posterior["tau"].values.flatten(), bins=30, color="#4c78a8", alpha=0.9)
    ax.set_title("Posterior distribution of tau")
    ax.set_xlabel("tau")
    ax.set_ylabel("Frequency")

    ax = axes[1, 0]
    ax.hist(trace.posterior["mu1"].values.flatten(), bins=30, color="#f58518", alpha=0.9)
    ax.set_title("Posterior of mu1")
    ax.set_xlabel("mu1")
    ax.set_ylabel("Frequency")

    ax = axes[1, 1]
    ax.hist(trace.posterior["mu2"].values.flatten(), bins=30, color="#54a24b", alpha=0.9)
    ax.set_title("Posterior of mu2")
    ax.set_xlabel("mu2")
    ax.set_ylabel("Frequency")

    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "change_point_analysis.png", dpi=200)
    plt.close(fig)

    if events_df is not None:
        event_matches = associate_change_point_with_events(change_point_date, events_df)
        if not event_matches.empty:
            event_matches.to_csv(REPORTS_DIR / "event_matches.csv", index=False)


def run_full_analysis(raw_path: Optional[Path] = None, events_path: Optional[Path] = None) -> dict:
    """Run the end-to-end Task 2 workflow and save the key outputs."""
    price_df = load_price_series(raw_path or RAW_PATH)
    returns = prepare_log_returns(price_df)

    events_df = pd.read_csv(events_path or EVENTS_PATH, parse_dates=["start_date"])
    fit_result = fit_bayesian_change_point(returns)
    plot_results(returns, fit_result, events_df)

    trace = fit_result["trace"]
    tau_samples = trace.posterior["tau"].values.flatten()
    change_point_index = int(np.median(tau_samples))
    change_point_date = returns["Date"].iloc[change_point_index]

    event_matches = associate_change_point_with_events(change_point_date, events_df)
    return {
        "price_df": price_df,
        "returns": returns,
        "events_df": events_df,
        "fit_result": fit_result,
        "change_point_date": change_point_date,
        "event_matches": event_matches,
    }
