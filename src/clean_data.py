"""
clean_data.py
-------------
Loads raw_users.csv, fixes data quality issues, and saves clean_users.csv.

Steps
-----
1. Drop exact duplicate rows
2. Fill missing numeric values with column medians
3. Clip outliers to realistic upper bounds
4. Validate and coerce types
5. Add a derived followers-to-following ratio column

Run:  python src/clean_data.py
Input:  data/raw_users.csv
Output: data/clean_users.csv
"""

import os
import pandas as pd
import numpy as np

RAW_FILE   = os.path.join("data", "raw_users.csv")
CLEAN_FILE = os.path.join("data", "clean_users.csv")


# ── Sensible upper bounds (domain knowledge) ──────────────────────────────────
# These cap values that are technically possible but statistically impossible
# for a human user — anything above these limits is almost certainly data error
# or extreme bot behaviour we clip before scoring.
CLIP_UPPER = {
    "posts_per_day"    : 500,
    "logins_per_day"   : 100,
    "location_changes" : 60,
    "failed_logins"    : 100,
    "followers"        : 1_000_000,
    "following"        : 50_000,
    "reports"          : 50,
}


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"📂  Loaded {len(df):,} rows from {path}")
    return df


def report_nulls(df: pd.DataFrame) -> None:
    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0]
    if null_counts.empty:
        print("   No null values found.")
    else:
        print("   Null counts:\n", null_counts.to_string())


def clean(df: pd.DataFrame) -> pd.DataFrame:
    original_len = len(df)

    # ── 1. Drop duplicate rows ────────────────────────────────────────────────
    df = df.drop_duplicates()
    print(f"\n🗑️   Dropped {original_len - len(df)} duplicate rows")

    # ── 2. Null audit before cleaning ─────────────────────────────────────────
    print("\n🔍  Null values before cleaning:")
    report_nulls(df)

    # ── 3. Fill missing numerics with the column median ───────────────────────
    # Median is more robust than mean when there are extreme bot values.
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f"   ✏️  Filled nulls in '{col}' with median = {median_val:.2f}")

    # ── 4. Clip outliers ──────────────────────────────────────────────────────
    for col, upper in CLIP_UPPER.items():
        if col in df.columns:
            n_clipped = (df[col] > upper).sum()
            df[col] = df[col].clip(upper=upper)
            if n_clipped:
                print(f"   ✂️  Clipped {n_clipped} values in '{col}' to max {upper}")

    # ── 5. Ensure profile_completeness stays in [0, 1] ────────────────────────
    df["profile_completeness"] = df["profile_completeness"].clip(0, 1)

    # ── 6. Coerce types ───────────────────────────────────────────────────────
    int_cols = ["account_age_days", "location_changes", "failed_logins",
                "followers", "following", "reports"]
    for col in int_cols:
        df[col] = df[col].astype(int)

    # ── 7. Derived feature: follower-to-following ratio ───────────────────────
    # Low ratio (< 0.1) is a strong bot signal — bots follow many, few follow back.
    # Add a small epsilon so we never divide by zero.
    df["ff_ratio"] = (df["followers"] / (df["following"] + 1)).round(4)

    print(f"\n✅  Clean dataset: {len(df):,} rows, {df.shape[1]} columns")
    return df


def main():
    df_raw   = load(RAW_FILE)
    df_clean = clean(df_raw)
    df_clean.to_csv(CLEAN_FILE, index=False)
    print(f"\n💾  Saved → {CLEAN_FILE}")
    print(df_clean.dtypes)


if __name__ == "__main__":
    main()