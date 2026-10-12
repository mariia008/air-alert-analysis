# air-alert-analysis
Analysis and visualization of air raid alert data in Ukraine using Python.
# Air Raid Alert Analysis — Chernihiv Oblast

## Overview

This project analyzes historical air raid alert starts in Chernihiv Oblast, Ukraine, using Python. It explores daily alert frequency, examines data coverage, and evaluates a simple baseline forecasting approach.

## Objectives

- Explore historical air raid alert records.
- Calculate daily alert-start counts.
- Investigate missing dates and data quality.
- Visualize daily patterns.
- Evaluate simple forecasting baselines.

## Data Source

The dataset is available from the [Ukrainian Air Raid Sirens Dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset).

The analysis uses the `volunteer_data_en.csv` dataset. Download the file from the source repository and place it in the local `data/` directory if it is required by the scripts.

The raw dataset is not included in this repository.

## Tools

- Python
- pandas
- matplotlib
- scikit-learn

## Project Structure

```text
air-alert-analysis/
├── data/                   # Local input data (not included)
├── outputs/
│   ├── chernihiv_daily_alerts.png
│   ├── chernihiv_forecast.png
│   └── chernihiv_monthly_coverage.csv
├── src/
│   ├── analyze_chernihiv.py
│   ├── forecast_chernihiv.py
│   ├── inspect_data.py
│   └── investigate_gaps.py
├── requirements.txt
└── README.md
```

## Running the Project

Create and activate a Python virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Download the source CSV and place it in the location expected by the Python scripts. Run the analysis and forecasting scripts from the project root:

```bash
python src/analyze_chernihiv.py
python src/forecast_chernihiv.py
```

## Forecasting Approach

The project compares simple baseline forecasts, including the previous-day and previous-week values. The previous-day baseline was selected based on its mean absolute error on a 28-day test period.

The forecast is an exploratory statistical exercise, not a reliable prediction of future threats.

## Limitations

Some dates have no recorded alert starts. These gaps cannot automatically be interpreted as days without alerts because they may reflect incomplete data. Forecast evaluation is limited and should not be treated as evidence of operational predictive accuracy.

## Disclaimer

This project is for educational and exploratory analysis only. It must not be used for real-time safety decisions or operational purposes.
