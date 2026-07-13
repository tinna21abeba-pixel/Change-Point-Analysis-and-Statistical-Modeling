# Change Point Analysis and Statistical Modeling of Brent Oil Prices

**Birhan Energies — Data Science Consultancy Project**

Analyzing how major geopolitical events, OPEC policy decisions, and economic
shocks are associated with structural changes in Brent crude oil prices
(daily data, 20-May-1987 to 30-Sep-2022), using Bayesian change point
detection in PyMC.

## Status: Interim Submission (Task 1)

This submission covers Task 1 — analysis workflow definition, event
compilation, and initial exploratory data analysis. Tasks 2 (Bayesian change
point modeling) and 3 (Flask/React dashboard) follow in the final
submission.

## Project Structure

```
├── .github/workflows/unittests.yml   # CI: runs pytest on push/PR
├── .vscode/settings.json
├── data/
│   ├── raw/                          # Place BrentOilPrices.csv here (gitignored)
│   └── events/
│       └── brent_oil_key_events.csv  # 19 curated key events, 1990-2022
├── notebooks/
│   └── task1_eda.ipynb               # Trend, stationarity, volatility EDA
├── reports/
│   └── interim_report.docx           # Workflow + assumptions/limitations
├── scripts/                          # Shared data-loading utilities
├── src/                              # Package code (Task 2+ modeling code)
├── tests/                            # Unit tests
└── requirements.txt
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Place the raw Brent oil price file at `data/raw/BrentOilPrices.csv` with
columns `Date` (format `dd-Mon-yy`) and `Price` (USD/barrel), then run
`notebooks/task1_eda.ipynb`. If no file is found, the notebook falls back
to a clearly-labeled synthetic series so the analysis code can still be
reviewed and exercised end-to-end.

## Task 1 Deliverables

1. **Analysis workflow document** — `reports/interim_report.docx`
2. **Key events dataset** — `data/events/brent_oil_key_events.csv` (19 events)
3. **Assumptions & limitations** — included in `reports/interim_report.docx`
4. **Initial EDA** — `notebooks/task1_eda.ipynb`

## Roadmap

- **Task 2:** Bayesian single/multiple change point model in PyMC on log
  returns; posterior analysis of `tau`, before/after means; association
  with events in the compiled dataset; quantified impact statements.
- **Task 3:** Flask API serving price, change point, and event data; React
  dashboard with date filtering and event-highlight functionality.

## Team

Tutors: Kerod, Feven, Mahbubah · Slack: `#all-week10`
