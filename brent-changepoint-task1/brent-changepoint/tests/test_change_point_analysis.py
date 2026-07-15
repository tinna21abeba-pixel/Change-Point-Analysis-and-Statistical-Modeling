from pathlib import Path

import pandas as pd

from src.change_point_analysis import (
    associate_change_point_with_events,
    load_price_series,
    prepare_log_returns,
)


def test_load_price_series_returns_expected_columns(tmp_path):
    missing_path = tmp_path / "missing.csv"
    df = load_price_series(raw_path=missing_path)

    assert isinstance(df, pd.DataFrame)
    assert {"Date", "Price"}.issubset(set(df.columns))
    assert len(df) > 100
    assert df["Price"].notna().all()


def test_prepare_log_returns_creates_stationary_series(tmp_path):
    missing_path = tmp_path / "missing.csv"
    df = load_price_series(raw_path=missing_path)
    returns = prepare_log_returns(df)

    assert "log_return" in returns.columns
    assert returns["log_return"].notna().all()
    assert returns.shape[0] == df.shape[0] - 1


def test_associate_change_point_with_events_returns_matches():
    events = pd.DataFrame(
        {
            "start_date": [pd.Timestamp("2020-03-08"), pd.Timestamp("2020-04-20")],
            "event_name": ["Oil price war", "OPEC+ cuts"],
            "category": ["OPEC Policy", "OPEC Policy"],
            "description": ["desc", "desc"],
        }
    )

    result = associate_change_point_with_events(
        change_point_date=pd.Timestamp("2020-03-10"),
        events_df=events,
        window_days=45,
    )

    assert not result.empty
    assert result.iloc[0]["event_name"] == "Oil price war"
    assert result.iloc[0]["days_from_change_point"] <= 45
