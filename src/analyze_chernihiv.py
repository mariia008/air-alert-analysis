
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# Paths are relative to the project root.
DATA_PATH = Path("data/raw/volunteer_data_en.csv")
OUTPUT_DIR = Path("outputs")
PLOT_PATH = OUTPUT_DIR / "chernihiv_daily_alerts.png"

REGION_NAME = "Chernihivska oblast"
TIMEZONE = "Europe/Kyiv"


def main():
    # 1. Check that the input file exists.
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH.resolve()}\n"
            "Run this script from your project root."
        )

    # 2. Load the original CSV.
    df = pd.read_csv(DATA_PATH)

    required_columns = {"region", "started_at"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    print(f"Total source records: {len(df):,}")

    # 3. Select records for Chernihiv Oblast.
    region_mask = (
        df["region"]
        .astype("string")
        .str.strip()
        .str.casefold()
        == REGION_NAME.casefold()
    )

    region_df = df.loc[region_mask].copy()

    print(f"Chernihiv records: {len(region_df):,}")

    if region_df.empty:
        raise ValueError(
            f"No records found for region {REGION_NAME!r}. "
            "Inspect the actual values in the region column."
        )

    # 4. Parse timestamps as UTC.
    region_df["started_at"] = pd.to_datetime(
        region_df["started_at"],
        errors="coerce",
        utc=True,
    )

    invalid_count = int(region_df["started_at"].isna().sum())

    print(f"Invalid or missing start timestamps: {invalid_count:,}")

    # Do not silently count records with invalid timestamps.
    valid_df = region_df.loc[
        region_df["started_at"].notna()
    ].copy()

    if valid_df.empty:
        raise ValueError("No valid start timestamps to analyze.")

    # 5. Convert UTC timestamps to the Kyiv time zone.
    valid_df["started_at_kyiv"] = (
        valid_df["started_at"].dt.tz_convert(TIMEZONE)
    )

    # Use the local calendar date, not the UTC calendar date.
    valid_df["kyiv_date"] = (
        valid_df["started_at_kyiv"].dt.date
    )

    # 6. Check repeated start timestamps.
    # This counts repeated timestamp values, not necessarily
    # duplicate alerts: separate events may share a timestamp.
    repeated_mask = valid_df["started_at"].duplicated(keep=False)

    repeated_records = valid_df.loc[repeated_mask].sort_values(
        "started_at"
    )

    repeated_groups = int(
        valid_df.loc[repeated_mask, "started_at"].nunique()
    )

    print("\nRepeated start timestamps")
    print(f"Records involved: {len(repeated_records):,}")
    print(f"Distinct repeated timestamps: {repeated_groups:,}")

    if not repeated_records.empty:
        print(
            repeated_records[
                ["region", "started_at", "started_at_kyiv"]
            ].head(20).to_string(index=False)
        )

        if len(repeated_records) > 20:
            print("Showing only the first 20 repeated records.")

    # 7. Count recorded alert starts per Kyiv calendar day.
    daily_counts = (
        valid_df.groupby("kyiv_date")
        .size()
        .sort_index()
    )

    daily_counts.index = pd.DatetimeIndex(daily_counts.index)
    daily_counts.name = "alert_starts"

    # 8. Find missing dates without filling them with zeros.
    first_date = daily_counts.index.min()
    last_date = daily_counts.index.max()

    expected_dates = pd.date_range(
        start=first_date,
        end=last_date,
        freq="D",
    )

    missing_dates = expected_dates.difference(daily_counts.index)

    print("\nDaily series summary")
    print(f"First date: {first_date.date()}")
    print(f"Last date: {last_date.date()}")
    print(f"Observed dates: {len(daily_counts):,}")
    print(f"Calendar dates in range: {len(expected_dates):,}")
    print(f"Missing dates: {len(missing_dates):,}")

    if len(missing_dates) > 0:
        print("\nMissing dates (not filled with zero):")
        for date in missing_dates:
            print(date.date())
    else:
        print("No missing calendar dates within the observed range.")

    print("\nDaily count statistics")
    print(f"Minimum: {daily_counts.min():.0f}")
    print(f"Maximum: {daily_counts.max():.0f}")
    print(f"Mean: {daily_counts.mean():.2f}")

    # 9. Plot the observed daily counts.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        daily_counts.index,
        daily_counts.values,
        linewidth=0.8,
    )

    ax.set_title(
        "Daily Recorded Air Alert Starts — Chernihiv Oblast"
    )
    ax.set_xlabel("Date (Europe/Kyiv)")
    ax.set_ylabel("Recorded alert starts")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(PLOT_PATH, dpi=150)
    plt.close(fig)

    print(f"\nPlot saved to: {PLOT_PATH.resolve()}")


if __name__ == "__main__":
    main()
