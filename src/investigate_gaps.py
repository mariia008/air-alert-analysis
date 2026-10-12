
from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/volunteer_data_en.csv")
REGION_NAME = "Chernihivska oblast"
TIMEZONE = "Europe/Kyiv"


def main():
    df = pd.read_csv(DATA_PATH)

    df = df.loc[
        df["region"].astype("string").str.strip().str.casefold()
        == REGION_NAME.casefold()
    ].copy()

    df["started_at"] = pd.to_datetime(
        df["started_at"], errors="coerce", utc=True
    )

    df = df.dropna(subset=["started_at"])

    df["local_date"] = (
        df["started_at"]
        .dt.tz_convert(TIMEZONE)
        .dt.date
    )

    # Count records on each date that has at least one alert start.
    daily = df.groupby("local_date").size().sort_index()

    # Construct the calendar only for comparison.
    calendar = pd.date_range(
        start=pd.Timestamp(daily.index.min()),
        end=pd.Timestamp(daily.index.max()),
        freq="D",
    )

    observed = pd.DatetimeIndex(
        pd.to_datetime(daily.index)
    )

    missing = calendar.difference(observed)

    print(f"Observed dates: {len(observed)}")
    print(f"Missing dates: {len(missing)}")

    # Group consecutive missing dates into gap intervals.
    if len(missing):
        gaps = []
        gap_start = missing[0]
        previous = missing[0]

        for date in missing[1:]:
            if (date - previous).days > 1:
                gaps.append((gap_start, previous))
                gap_start = date

            previous = date

        gaps.append((gap_start, previous))

        print("\nConsecutive missing-date intervals:")
        for start, end in gaps:
            length = (end - start).days + 1
            print(
                f"{start.date()} to {end.date()}: "
                f"{length} day(s)"
            )

    # Monthly coverage: observed dates versus calendar dates.
    daily.index = pd.to_datetime(daily.index)

    monthly_records = daily.resample("MS").sum()
    monthly_observed = daily.resample("MS").count()

    month_calendar = pd.Series(
        1, index=calendar
    ).resample("MS").sum()

    monthly = pd.DataFrame({
        "recorded_starts": monthly_records,
        "observed_dates": monthly_observed,
        "calendar_dates": month_calendar,
    }).fillna(0)

    monthly["dates_without_starts"] = (
        monthly["calendar_dates"] - monthly["observed_dates"]
    ).astype(int)

    print("\nMonthly coverage:")
    print(monthly.to_string())

    print("\nMonthly summary saved for inspection.")
    output = Path("outputs")
    output.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(output / "chernihiv_monthly_coverage.csv")


if __name__ == "__main__":
    main()