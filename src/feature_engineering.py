"""
feature_engineering.py
-----------------------
Turns cleaned user data into fraud signals and a final Risk Score.

Each signal is a binary flag (0 or 1).  Each flag carries a weight
that reflects how strongly it indicates fraud.  The Risk Score is
the weighted sum of all active flags, capped at 100.

Signal weights (total possible = 120, normalised to 100 later):
  high_login_freq         → 20   (logins/day > 10)
  new_high_activity       → 20   (age < 60d AND posts > 20/day)
  extreme_posts           → 25   (posts/day > 100)
  low_ff_ratio            → 15   (followers/following < 0.1)
  location_hopping        → 15   (location_changes > 5 in 30d)
  failed_login_flag       → 15   (failed_logins > 5 in 7d)
  community_reported      → 20   (reports >= 3)
  incomplete_profile      → 10   (completeness < 0.40 OR no meaningful profile)

Risk tiers (after normalisation to 0–100):
  Low    0 – 24
  Medium 25 – 54
  High   55 +

Run:  python src/feature_engineering.py
Input:  data/clean_users.csv
Output: data/scored_users.csv  +  data/review_queue.csv (High-risk only)
"""

import os
import pandas as pd
import numpy as np

CLEAN_FILE  = os.path.join("data", "clean_users.csv")
SCORED_FILE = os.path.join("data", "scored_users.csv")
REVIEW_FILE = os.path.join("data", "review_queue.csv")

# ── Signal definitions ────────────────────────────────────────────────────────
# Each entry: (signal_column_name, weight, description)
SIGNALS = [
    ("high_login_freq"   , 20, "logins/day > 10"),
    ("new_high_activity" , 20, "account <60d AND posts >20/day"),
    ("extreme_posts"     , 25, "posts/day > 100"),
    ("low_ff_ratio"      , 15, "followers/following < 0.1"),
    ("location_hopping"  , 15, "location_changes > 5 in 30d"),
    ("failed_login_flag" , 15, "failed_logins > 5 in 7d"),
    ("community_reported", 20, "reports >= 3"),
    ("incomplete_profile", 10, "profile_completeness < 0.40"),
]

MAX_RAW_SCORE = sum(w for _, w, _ in SIGNALS)   # 120


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"📂  Loaded {len(df):,} users from {path}")
    return df


# ── Individual signal functions ───────────────────────────────────────────────
# Each returns a Pandas Series of 0 / 1 values.

def flag_high_login_freq(df):
    """Bots login constantly to post or scrape content."""
    return (df["logins_per_day"] > 10).astype(int)

def flag_new_high_activity(df):
    """A 2-week-old account posting 30 times a day is suspicious."""
    return ((df["account_age_days"] < 60) & (df["posts_per_day"] > 20)).astype(int)

def flag_extreme_posts(df):
    """No human posts >100 times a day organically."""
    return (df["posts_per_day"] > 100).astype(int)

def flag_low_ff_ratio(df):
    """Bots follow thousands but nobody follows back."""
    return (df["ff_ratio"] < 0.1).astype(int)

def flag_location_hopping(df):
    """More than 5 location switches in 30 days indicates VPN/proxy cycling."""
    return (df["location_changes"] > 5).astype(int)

def flag_failed_logins(df):
    """Repeated failures suggest credential stuffing or account testing."""
    return (df["failed_logins"] > 5).astype(int)

def flag_community_reported(df):
    """Three or more community reports is a strong social signal."""
    return (df["reports"] >= 3).astype(int)

def flag_incomplete_profile(df):
    """Bots rarely bother completing profiles."""
    return (df["profile_completeness"] < 0.40).astype(int)


# Map signal column names → functions
SIGNAL_FUNCS = {
    "high_login_freq"   : flag_high_login_freq,
    "new_high_activity" : flag_new_high_activity,
    "extreme_posts"     : flag_extreme_posts,
    "low_ff_ratio"      : flag_low_ff_ratio,
    "location_hopping"  : flag_location_hopping,
    "failed_login_flag" : flag_failed_logins,
    "community_reported": flag_community_reported,
    "incomplete_profile": flag_incomplete_profile,
}


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ── Compute each signal flag ───────────────────────────────────────────────
    print("\n📊  Computing fraud signals …")
    for col, weight, desc in SIGNALS:
        df[col] = SIGNAL_FUNCS[col](df)
        triggered = df[col].sum()
        print(f"   {col:<22} (wt {weight:>2})  →  {triggered:>4} users  [{desc}]")

    # ── Raw score = weighted sum of active flags ───────────────────────────────
    df["raw_score"] = sum(
        df[col] * weight for col, weight, _ in SIGNALS
    )

    # ── Normalise to 0–100 ────────────────────────────────────────────────────
    df["risk_score"] = (df["raw_score"] / MAX_RAW_SCORE * 100).round(1)

    # ── Signals triggered count ───────────────────────────────────────────────
    signal_cols = [col for col, _, _ in SIGNALS]
    df["signals_triggered"] = df[signal_cols].sum(axis=1)

    # ── Risk tier ─────────────────────────────────────────────────────────────
    def tier(score):
        if score < 25:
            return "Low"
        elif score < 55:
            return "Medium"
        else:
            return "High"

    df["risk_tier"] = df["risk_score"].apply(tier)

    # ── Summary ───────────────────────────────────────────────────────────────
    tier_counts = df["risk_tier"].value_counts()
    print(f"\n🎯  Risk tier distribution:")
    for t in ["Low", "Medium", "High"]:
        n   = tier_counts.get(t, 0)
        pct = n / len(df) * 100
        print(f"   {t:<8}  {n:>4} users  ({pct:.1f}%)")

    return df


def main():
    df = load(CLEAN_FILE)
    df = engineer(df)

    # Save full scored dataset
    df.to_csv(SCORED_FILE, index=False)
    print(f"\n💾  Scored dataset saved → {SCORED_FILE}")

    # Save high-risk queue for manual review
    review = df[df["risk_tier"] == "High"].sort_values("risk_score", ascending=False)
    review.to_csv(REVIEW_FILE, index=False)
    print(f"🚨  High-risk review queue saved → {REVIEW_FILE}  ({len(review)} accounts)")


if __name__ == "__main__":
    main()