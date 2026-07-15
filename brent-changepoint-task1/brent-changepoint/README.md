# Change Point Analysis and Statistical Modeling of Brent Oil Prices

**Birhan Energies — Data Science Consultancy Project**

Analyzing how major geopolitical events, OPEC policy decisions, and economic
shocks are associated with structural changes in Brent crude oil prices
(daily data, 20-May-1987 to 30-Sep-2022), using Bayesian change point
detection in PyMC.

## Status: Submission-Ready (Tasks 1–3)

This repository now includes the core deliverables for the full challenge:
Task 1 event compilation and initial EDA, Task 2 Bayesian change-point
modeling, and Task 3 a Flask backend plus a React dashboard for exploring
results.

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

## Deliverables

1. **Task 1** — event dataset and initial EDA notebook: `data/events/brent_oil_key_events.csv`, `notebooks/task1_eda.ipynb`
2. **Task 2** — Bayesian change-point analysis: `src/change_point_analysis.py`, `notebooks/task2_changepoint.ipynb`
3. **Task 3** — Flask API and React dashboard: `app.py`, `frontend/`

## Run the app

### Backend

```bash
python app.py
```

Then visit http://127.0.0.1:5000/api/health.

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Then open http://127.0.0.1:5173/.

## Run tests

```bash
python -m pytest -q
```

## Team

Tutors: Kerod, Feven, Mahbubah · Slack: `#all-week10`
