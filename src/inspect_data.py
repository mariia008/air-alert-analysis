
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/raw")

FILES = [
    "volunteer_data_en.csv",
    "official_data_en.csv",
]


def inspect_file(filename):
    path = DATA_DIR / filename

    print(f"\n{'=' * 60}")
    print(f"FILE: {filename}")
    print(f"{'=' * 60}")

    if not path.exists():
        print(f"File not found: {path.resolve()}")
        return

    # Load the original CSV without changing its contents.
    df = pd.read_csv(path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.columns.tolist()}")

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print(f"\nExact duplicate rows: {df.duplicated().sum():,}")

    # Parse timestamps as UTC; invalid values become NaT.
    for column in ["started_at", "finished_at"]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column], errors="coerce", utc=True
            )
            print(
                f"{column}: invalid or missing = "
                f"{df[column].isna().sum():,}"
            )

    if "started_at" in df.columns:
        valid = df["started_at"].dropna()

        if not valid.empty:
            print(f"\nFirst timestamp (UTC): {valid.min()}")
            print(f"Last timestamp (UTC):  {valid.max()}")

            # Check which calendar dates have at least one record.
            observed_days = valid.dt.floor("D").nunique()
            full_days = (
                valid.max().normalize() - valid.min().normalize()
            ).days + 1

            print(f"Observed calendar days: {observed_days:,}")
            print(f"Calendar days in range: {full_days:,}")
            print(
                "Days without a recorded start: "
                f"{full_days - observed_days:,}"
            )

    if "level" in df.columns:
        print("\nGeographic levels:")
        print(df["level"].value_counts(dropna=False).to_string())

    if "oblast" in df.columns:
        print("\nOblast values containing 'Chernihiv':")
        matches = df["oblast"].astype("string").str.contains(
            "Chernihiv", case=False, na=False
        )
        print(df.loc[matches, "oblast"].value_counts().to_string())

    if "region" in df.columns:
        print("\nRegion values containing 'Chernihiv':")
        matches = df["region"].astype("string").str.contains(
            "Chernihiv", case=False, na=False
        )
        print(df.loc[matches, "region"].value_counts().to_string())

    if "naive" in df.columns:
        print("\nEstimated end-time flag:")
        print(df["naive"].value_counts(dropna=False).to_string())


for filename in FILES:
    inspect_file(filename)
