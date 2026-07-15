from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

from src.change_point_analysis import (
    associate_change_point_with_events,
    fit_bayesian_change_point,
    load_price_series,
    prepare_log_returns,
)

ROOT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = ROOT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_PATH = REPORTS_DIR / "task2_summary.json"
EVENTS_PATH = ROOT_DIR / "data" / "events" / "brent_oil_key_events.csv"
RAW_PATH = ROOT_DIR / "data" / "raw" / "BrentOilPrices.csv"

app = Flask(__name__)
CORS(app)


def build_analysis_payload(force_refresh: bool = False) -> dict[str, Any]:
    if not force_refresh and CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    price_df = load_price_series(RAW_PATH)
    returns = prepare_log_returns(price_df)
    events_df = pd.read_csv(EVENTS_PATH, parse_dates=["start_date"])
    fit_result = fit_bayesian_change_point(returns, draws=600, tune=400)

    trace = fit_result["trace"]
    tau_samples = trace.posterior["tau"].values.flatten()
    change_point_index = int(round(float(np.median(tau_samples))))
    change_point_date = returns["Date"].iloc[change_point_index]
    event_matches = associate_change_point_with_events(change_point_date, events_df, window_days=45)

    events_payload = events_df.copy()
    events_payload["start_date"] = events_payload["start_date"].dt.strftime("%Y-%m-%d")

    payload = {
        "change_point_date": pd.Timestamp(change_point_date).isoformat(),
        "change_point_index": change_point_index,
        "summary": fit_result["summary"].reset_index().rename(columns={"index": "parameter"}).to_dict(orient="records"),
        "events": events_payload.to_dict(orient="records"),
        "event_matches": event_matches.copy().assign(
            start_date=lambda df: df["start_date"].dt.strftime("%Y-%m-%d")
        ).to_dict(orient="records"),
        "prices": [
            {"date": pd.Timestamp(row["Date"]).isoformat(), "price": float(row["Price"])}
            for _, row in price_df.head(500).iterrows()
        ],
        "returns": [
            {"date": pd.Timestamp(row["Date"]).isoformat(), "log_return": float(row["log_return"])}
            for _, row in returns.iterrows()
        ],
        "metrics": {
            "n_observations": int(len(returns)),
            "mean_return": float(returns["log_return"].mean()),
            "std_return": float(returns["log_return"].std()),
        },
    }

    CACHE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


@app.get("/api/health")
def health() -> tuple[Any, int]:
    return jsonify({"status": "ok", "service": "brent-change-point-api"}), 200


@app.get("/api/summary")
def summary() -> tuple[Any, int]:
    payload = build_analysis_payload()
    return jsonify(payload), 200


@app.get("/api/prices")
def prices() -> tuple[Any, int]:
    payload = build_analysis_payload()
    return jsonify(payload["prices"]), 200


@app.get("/api/returns")
def returns_data() -> tuple[Any, int]:
    payload = build_analysis_payload()
    return jsonify(payload["returns"]), 200


@app.get("/api/events")
def events() -> tuple[Any, int]:
    payload = build_analysis_payload()
    return jsonify(payload["event_matches"] if payload["event_matches"] else payload["events"]), 200


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
