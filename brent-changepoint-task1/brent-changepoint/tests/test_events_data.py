import pandas as pd
from pathlib import Path

EVENTS_PATH = Path(__file__).resolve().parents[1] / "data" / "events" / "brent_oil_key_events.csv"


def load_events():
    return pd.read_csv(EVENTS_PATH, parse_dates=["start_date"])


def test_events_file_exists():
    assert EVENTS_PATH.exists()


def test_minimum_event_count():
    df = load_events()
    assert len(df) >= 10, "Assignment requires at least 10-15 documented events"


def test_required_columns_present():
    df = load_events()
    required = {"event_id", "start_date", "event_name", "category", "description"}
    assert required.issubset(set(df.columns))


def test_no_missing_dates_or_names():
    df = load_events()
    assert df["start_date"].isna().sum() == 0
    assert df["event_name"].isna().sum() == 0


def test_dates_within_dataset_range():
    df = load_events()
    assert df["start_date"].min() >= pd.Timestamp("1987-05-20")
    assert df["start_date"].max() <= pd.Timestamp("2022-09-30")
