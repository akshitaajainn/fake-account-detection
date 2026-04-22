"""
analysis.py
-----------
Calculates KPIs and runs SQL-style Pandas queries to surface
suspicious patterns in the scored user dataset.

Think of this file as "the analyst's notebook" — the questions a
Risk / Fraud Analyst would answer for a weekly fraud review meeting.

Run:  python src/analysis.py
Input:  data/scored_users.csv
Output: printed report  +  data/kpi_summary.csv
"""

import os
import pandas as pd
import numpy as np

SCORED_FILE = os.path.join("data", "scored_users.csv")
KPI_FILE    = os.path.join("data", "kpi_summary.csv")

DIVIDER = "─" * 60


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"📂  Loaded {len(df):,} scored users")
    return df


# ═════════════════════════════════════════════════════════════════════════════
# KPI FUNCTIONS
# Each function answers one business question and returns a dict or DataFrame.
# ═════════════════════════════════════════════════════════════════════════════

def kpi_overview(df: pd.DataFrame) -> dict:
    """
    Top-level numbers for an executive dashboard card.
    """
    total          = len(df)
    high_risk      = (df["risk_tier"] == "High").sum()
    medium_risk    = (df["risk_tier"] == "Medium").sum()
    low_risk       = (df["risk_tier"] == "Low").sum()

    # Bot detection rate = how many flagged accounts match the ground-truth label
    # (only possible because we generated synthetic data with a known label)
    if "is_bot_label" in df.columns:
        high_risk_bots      = df[(df["risk_tier"] == "High") & (df["is_bot_label"] == 1)]
        true_bots           = df["is_bot_label"].sum()
        bot_detection_rate  = len(high_risk_bots) / true_bots * 100 if true_bots else 0

        false_positives     = df[(df["risk_tier"] == "High") & (df["is_bot_label"] == 0)]
        false_positive_rate = len(false_positives) / (total - true_bots) * 100

        new_acct_high = df[(df["account_age_days"] < 60) & (df["risk_tier"] == "High")]
        new_acct_rate = len(new_acct_high) / high_risk * 100 if high_risk else 0
    else:
        bot_detection_rate  = None
        false_positive_rate = None
        new_acct_rate       = None

    return {
        "total_users"          : total,
        "high_risk_count"      : high_risk,
        "medium_risk_count"    : medium_risk,
        "low_risk_count"       : low_risk,
        "high_risk_pct"        : round(high_risk / total * 100, 1),
        "bot_detection_rate"   : round(bot_detection_rate, 1) if bot_detection_rate else "N/A",
        "false_positive_rate"  : round(false_positive_rate, 1) if false_positive_rate else "N/A",
        "new_acct_high_risk_pct": round(new_acct_rate, 1) if new_acct_rate else "N/A",
        "avg_risk_score"       : round(df["risk_score"].mean(), 1),
        "median_risk_score"    : round(df["risk_score"].median(), 1),
    }


def q1_abnormal_login_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    SQL equivalent:
        SELECT user_id, logins_per_day, risk_score, risk_tier
        FROM scored_users
        WHERE logins_per_day > 10
        ORDER BY logins_per_day DESC
        LIMIT 10;
    """
    return (
        df[df["logins_per_day"] > 10]
        [["user_id", "logins_per_day", "risk_score", "risk_tier"]]
        .sort_values("logins_per_day", ascending=False)
        .head(10)
    )


def q2_multi_account_ip(df: pd.DataFrame) -> pd.DataFrame:
    """
    SQL equivalent:
        SELECT ip_address, COUNT(*) AS account_count,
               AVG(risk_score) AS avg_risk
        FROM scored_users
        GROUP BY ip_address
        HAVING COUNT(*) > 1
        ORDER BY account_count DESC
        LIMIT 10;
    """
    ip_counts = (
        df.groupby("ip_address")
        .agg(
            account_count=("user_id", "count"),
            avg_risk_score=("risk_score", "mean"),
            high_risk_count=("risk_tier", lambda x: (x == "High").sum()),
        )
        .reset_index()
    )
    return (
        ip_counts[ip_counts["account_count"] > 1]
        .sort_values("account_count", ascending=False)
        .head(10)
        .round(1)
    )


def q3_new_account_burst(df: pd.DataFrame) -> pd.DataFrame:
    """
    SQL equivalent:
        SELECT user_id, account_age_days, posts_per_day, risk_score
        FROM scored_users
        WHERE account_age_days < 30 AND posts_per_day > 20
        ORDER BY posts_per_day DESC;
    """
    return (
        df[(df["account_age_days"] < 30) & (df["posts_per_day"] > 20)]
        [["user_id", "account_age_days", "posts_per_day", "risk_score", "risk_tier"]]
        .sort_values("posts_per_day", ascending=False)
        .head(10)
    )


def q4_location_hoppers(df: pd.DataFrame) -> pd.DataFrame:
    """
    SQL equivalent:
        SELECT user_id, location_changes, failed_logins, risk_score
        FROM scored_users
        WHERE location_changes > 5
        ORDER BY location_changes DESC;
    """
    return (
        df[df["location_changes"] > 5]
        [["user_id", "location_changes", "failed_logins", "risk_score", "risk_tier"]]
        .sort_values("location_changes", ascending=False)
        .head(10)
    )


def q5_profile_completeness_by_tier(df: pd.DataFrame) -> pd.DataFrame:
    """
    SQL equivalent:
        SELECT risk_tier,
               AVG(profile_completeness) AS avg_completeness,
               COUNT(*) AS user_count
        FROM scored_users
        GROUP BY risk_tier
        ORDER BY avg_completeness;
    """
    return (
        df.groupby("risk_tier")
        .agg(
            user_count=("user_id", "count"),
            avg_completeness=("profile_completeness", "mean"),
            avg_posts_per_day=("posts_per_day", "mean"),
            avg_logins_per_day=("logins_per_day", "mean"),
            avg_ff_ratio=("ff_ratio", "mean"),
        )
        .round(3)
        .reindex(["Low", "Medium", "High"])
    )


def q6_signal_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """
    How often does each fraud signal fire?
    Helps tune weights over time.
    """
    signal_cols = [
        "high_login_freq", "new_high_activity", "extreme_posts",
        "low_ff_ratio", "location_hopping", "failed_login_flag",
        "community_reported", "incomplete_profile",
    ]
    counts = df[signal_cols].sum().sort_values(ascending=False)
    pcts   = (counts / len(df) * 100).round(1)
    return pd.DataFrame({"triggered_count": counts, "triggered_pct": pcts})


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    df = load(SCORED_FILE)

    # ── 1. KPI Overview ──────────────────────────────────────────────────────
    print(f"\n{DIVIDER}")
    print("  📊  KPI OVERVIEW")
    print(DIVIDER)
    kpis = kpi_overview(df)
    for k, v in kpis.items():
        print(f"  {k:<30} {v}")

    # Save KPIs
    kpi_df = pd.DataFrame(list(kpis.items()), columns=["metric", "value"])
    kpi_df.to_csv(KPI_FILE, index=False)
    print(f"\n  💾 KPIs saved → {KPI_FILE}")

    # ── 2. SQL-style queries ─────────────────────────────────────────────────
    queries = [
        ("Q1 — Abnormal Login Frequency (top 10)"     , q1_abnormal_login_frequency),
        ("Q2 — Multi-Account IP Detection (top 10)"   , q2_multi_account_ip),
        ("Q3 — New Account Burst Pattern (top 10)"    , q3_new_account_burst),
        ("Q4 — Location Hoppers (top 10)"             , q4_location_hoppers),
        ("Q5 — Profile Completeness by Risk Tier"     , q5_profile_completeness_by_tier),
        ("Q6 — Fraud Signal Frequency"                , q6_signal_frequency),
    ]

    for title, func in queries:
        print(f"\n{DIVIDER}")
        print(f"  🔍  {title}")
        print(DIVIDER)
        result = func(df)
        print(result.to_string())


if __name__ == "__main__":
    main()