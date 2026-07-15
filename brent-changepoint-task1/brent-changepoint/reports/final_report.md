# Final Submission Report

## Change Point Analysis and Statistical Modeling of Brent Oil Prices

### Project Summary
This project analyzes Brent crude oil price behavior to identify structural changes in the log-return series and link them to major geopolitical, economic, and OPEC-related events. The repository contains:
- Task 1: event catalog and exploratory data analysis
- Task 2: Bayesian change point model using PyMC
- Task 3: Flask backend and React dashboard for results visualization

---

## 1. Business Context
Brent oil markets are highly sensitive to political decisions, regional conflicts, economic shocks, and production policy changes. Investors, analysts, and policymakers require robust insights into how these events alter price regimes so they can make better decisions for risk management, forecasting, and policy design.

### Objectives
1. Identify key events that significantly impacted Brent oil prices.
2. Quantify the effect of those events using statistical modeling.
3. Deliver actionable insights through analysis, visualizations, and a dashboard.

---

## 2. Data and Event Catalog
### Price Data
- Expected file: `data/raw/BrentOilPrices.csv`
- Required columns: `Date`, `Price`
- Date range targeted: daily Brent crude price history through 1987–2022
- The code supports a synthetic fallback dataset for demonstration if the raw file is absent.

### Event Dataset
- File: `data/events/brent_oil_key_events.csv`
- Contains 19 curated events relevant to Brent oil market behavior
- Categories include conflict, OPEC policy, economic shock, sanctions, and market extremes

Key events in the dataset:
- Iraq invades Kuwait (1990)
- Operation Desert Storm begins (1991)
- Asian Financial Crisis (1997)
- OPEC production cut agreement (1999)
- September 11 attacks (2001)
- Lehman Brothers collapse (2008)
- Russia invades Ukraine (2022)

---

## 3. Task 1 — Exploratory Data Analysis
### Workflow
- Load raw price data and parse dates
- Compute log returns for stationarity analysis
- Examine price trend, volatility, and structural behavior
- Develop an event catalog that aligns plausible causes with major changes in the oil market

### Key findings
- The raw Brent price series is non-stationary, with long-term trend behavior and large regime shifts.
- Log returns are more stable, making them appropriate for the simple Bayesian change point model.
- Volatility clusters appear around major shocks, consistent with theory and historical event timing.

### Assumptions and Limitations
- The model assumes a single change point in the log-return series.
- Associations with events are exploratory and not proof of causation.
- The analysis focuses on mean shifts rather than a full volatility regime model.

---

## 4. Task 2 — Bayesian Change Point Modeling
### Model approach
A simple Bayesian model detects a single structural break in the log-return series:
- `tau` is modeled as a discrete uniform change point over all possible days
- `mu1` and `mu2` represent the mean log return before and after the change point
- `sigma` is the common observation volatility
- Observed log returns follow `Normal(mu, sigma)` where `mu` switches at `tau`

### Implementation
- Code located in `src/change_point_analysis.py`
- Notebook: `notebooks/task2_changepoint.ipynb`
- End-to-end workflow packaged in `run_full_analysis()` and `plot_results()`

### Model output
From the current analysis artifacts:
- Detected median change point date: **2000-03-15**
- Posterior mean for `mu1`: 0.003
- Posterior mean for `mu2`: -0.001
- Posterior mean for `sigma`: 0.0083

### Interpretation
The model suggests a shift from a slightly positive average log-return regime to a slightly negative one around mid-March 2000. This implies a structural break in average price behavior, with potential links to the market recovery from the late-1990s slump and supply-side adjustments around that period.

### Model diagnostics
- Current MCMC results show convergence warnings in effective sample size and `r_hat` for some parameters.
- This indicates the need for additional samples, stronger tuning, or more advanced posterior sampling for production-level certainty.

---

## 5. Task 3 — Dashboard and API
### Backend
- File: `app.py`
- Flask API endpoints:
  - `/api/health`
  - `/api/summary`
  - `/api/prices`
  - `/api/returns`
  - `/api/events`
- The backend loads the price series, computes log returns, fits the change point model, and returns summary metrics, event matches, and series data.

### Frontend
- Directory: `frontend/`
- Built with React and Recharts
- Displays:
  - detected change point date
  - summary metrics (observations, mean, std)
  - historical price series
  - log returns
  - nearby event matches

### Dashboard functionality
- Clean summary cards for key values
- Interactive charts for price and return series
- Event listing for the change point association result

---

## 6. Key Insights
- The analysis pipeline correctly transforms the raw price series into log returns for stationarity.
- A single Bayesian mean-shift model successfully detects a structural break in the log-return data.
- Event alignment capability is built in, enabling stakeholders to compare detected change points with curated historical events.
- The dashboard provides an accessible interface for exploring model output and event context.

---

## 7. Limitations and Future Work
### Limitations
- A single change point model is a simplification; oil markets may exhibit multiple regime changes.
- Event matching is based on temporal proximity only, not causal inference.
- Model diagnostics currently show room for improvement in posterior convergence.

### Future improvements
- Extend the model to multiple change points or regime-switching frameworks
- Add volatility-change detection in addition to mean changes
- Incorporate macro variables such as production levels, exchange rates, or demand proxies
- Add dashboard filters for date ranges and event categories
- Improve model sampling quality with longer MCMC runs or advanced samplers

---

## 8. Reproducibility and Setup
### Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run notebooks
- `notebooks/task1_eda.ipynb`
- `notebooks/task2_changepoint.ipynb`

### Run backend
```bash
python app.py
```

### Run frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

### Run tests
```bash
python -m pytest -q
```

---

## 9. Submission Deliverables
- `README.md`
- `reports/final_report.md`
- `data/events/brent_oil_key_events.csv`
- `notebooks/task1_eda.ipynb`
- `notebooks/task2_changepoint.ipynb`
- `src/change_point_analysis.py`
- `app.py`
- `frontend/`
- `tests/`

---

## 10. Conclusion
This final report summarizes the analysis pipeline, model implementation, and dashboard deliverables for Brent oil change point modeling. The repository is structured to satisfy Tasks 1–3, subject to supplying the raw price dataset and refining model convergence for tighter statistical conclusions.
