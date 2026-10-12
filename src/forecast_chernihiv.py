
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = Path("data/raw/volunteer_data_en.csv")
OUTPUT_DIR = Path("outputs")
PLOT_PATH = OUTPUT_DIR / "chernihiv_forecast.png"

REGION = "Chernihivska oblast"
TIMEZONE = "Europe/Kyiv"
TEST_DAYS = 28


def main():
    # 1. Load and filter the data.
    df = pd.read_csv(DATA_PATH)

    df = df.loc[
        df["region"].astype("string").str.strip().str.casefold()
        == REGION.casefold()
    ].copy()

    df["started_at"] = pd.to_datetime(
        df["started_at"], errors="coerce", utc=True
    )
    df = df.dropna(subset=["started_at"])

    df["date"] = (
        df["started_at"].dt.tz_convert(TIMEZONE).dt.date
    )

    # 2. Count recorded alert starts per day.
    daily = df.groupby("date").size().sort_index()
    daily.index = pd.DatetimeIndex(daily.index)
    daily.name = "actual"

    # Do not assume missing dates mean zero alerts.
    calendar = pd.date_range(
        daily.index.min(), daily.index.max(), freq="D"
    )
    missing = calendar.difference(daily.index)

        # Find the latest continuous segment with no missing dates.
    observed_dates = set(daily.index)
    latest_date = daily.index.max()
    start_date = latest_date

    while start_date - pd.Timedelta(days=1) in observed_dates:
        start_date -= pd.Timedelta(days=1)

    daily = daily.loc[start_date:latest_date].copy()

    print(f"Latest continuous segment: {start_date.date()} "
          f"to {latest_date.date()}")
    print(f"Days in segment: {len(daily)}")

    if len(daily) <= TEST_DAYS + 7:
        raise ValueError(
            "The latest continuous segment is too short "
            "for a 28-day test. Reduce TEST_DAYS or investigate coverage."
        )

    # 3. Evaluate on the latest 28 days.
    # Predictions use only earlier observations.
    results = pd.DataFrame({"actual": daily})
    results["previous_day"] = daily.shift(1)
    results["previous_week"] = daily.shift(7)

    test = results.iloc[-TEST_DAYS:].copy()

    for model in ["previous_day", "previous_week"]:
        mae = (test["actual"] - test[model]).abs().mean()
        print(f"{model} MAE: {mae:.3f}")

    # 4. Select the baseline with lower MAE.
    errors = {
        model: (test["actual"] - test[model]).abs().mean()
        for model in ["previous_day", "previous_week"]
    }
    best_model = min(errors, key=errors.get)

    print(f"\nSelected baseline: {best_model}")
    print(f"Evaluation days: {len(test)}")

    # 5. Forecast the next day using all available observations.
    if best_model == "previous_day":
        next_forecast = daily.iloc[-1]
    else:
        next_forecast = daily.iloc[-7]

    print(f"Last observed date: {daily.index[-1].date()}")
    print(f"Forecast for next calendar day: {next_forecast:.0f}")
    print(
        "Important: this is a simple baseline, "
        "not a reliable warning or safety prediction."
    )

    # 6. Save evaluation plot.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(test.index, test["actual"], label="Actual")
    ax.plot(
        test.index, test[best_model],
        label=f"Forecast: {best_model}"
    )
    ax.set_title("Chernihiv Oblast — 28-Day Baseline Evaluation")
    ax.set_xlabel("Date (Europe/Kyiv)")
    ax.set_ylabel("Recorded alert starts")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    plt.close(fig)

    print(f"Plot saved to: {PLOT_PATH.resolve()}")


if __name__ == "__main__":
    main()