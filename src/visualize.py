"""
visualize.py
------------
Generates 6 publication-quality charts and saves them to visuals/.

Charts
------
01_risk_distribution.png   — Pie chart of Low / Medium / High risk tiers
02_risk_score_histogram.png — Distribution of risk scores across all users
03_signal_heatmap.png       — Which signals fire together (correlation matrix)
04_logins_vs_posts.png      — Scatter: logins/day vs posts/day coloured by tier
05_ff_ratio_by_tier.png     — Box plot of follower-following ratio per tier
06_age_vs_risk.png          — Account age vs risk score coloured by tier

Run:  python src/visualize.py
Input:  data/scored_users.csv
Output: visuals/01_*.png … visuals/06_*.png
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (works on any machine)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

warnings.filterwarnings("ignore")

SCORED_FILE = os.path.join("data", "scored_users.csv")
OUT_DIR     = "visuals"

# ── Colour palette ─────────────────────────────────────────────────────────────
TIER_COLORS = {"Low": "#4caf50", "Medium": "#ff9800", "High": "#f44336"}
BG          = "#0d1117"    # dark background
TEXT        = "#e6edf3"
ACCENT      = "#58a6ff"

def apply_dark_theme():
    plt.rcParams.update({
        "figure.facecolor"   : BG,
        "axes.facecolor"     : "#161b22",
        "axes.edgecolor"     : "#30363d",
        "axes.labelcolor"    : TEXT,
        "xtick.color"        : TEXT,
        "ytick.color"        : TEXT,
        "text.color"         : TEXT,
        "grid.color"         : "#21262d",
        "grid.linestyle"     : "--",
        "grid.alpha"         : 0.5,
        "font.family"        : "monospace",
        "figure.dpi"         : 130,
    })

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"📂  Loaded {len(df):,} rows")
    return df

def save(name: str):
    path = os.path.join(OUT_DIR, name)
    plt.savefig(path, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"   💾  Saved → {path}")


# ── Chart 1: Risk tier pie ─────────────────────────────────────────────────────
def chart_risk_distribution(df: pd.DataFrame):
    counts = df["risk_tier"].value_counts().reindex(["Low", "Medium", "High"])
    colors = [TIER_COLORS[t] for t in counts.index]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=3),
    )
    for t in texts + autotexts:
        t.set_color(TEXT)
        t.set_fontsize(12)

    ax.set_title("Risk Tier Distribution\n500 Social Media Accounts",
                 color=TEXT, fontsize=14, pad=20)
    save("01_risk_distribution.png")


# ── Chart 2: Risk score histogram ─────────────────────────────────────────────
def chart_score_histogram(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))

    # colour bars by tier
    bins = np.linspace(0, 100, 30)
    for tier, color in TIER_COLORS.items():
        subset = df[df["risk_tier"] == tier]["risk_score"]
        ax.hist(subset, bins=bins, color=color, alpha=0.85, label=tier, edgecolor=BG)

    ax.axvline(25, color="#ff9800", linewidth=1.5, linestyle="--", alpha=0.7)
    ax.axvline(55, color="#f44336", linewidth=1.5, linestyle="--", alpha=0.7)
    ax.set_xlabel("Risk Score (0 – 100)")
    ax.set_ylabel("Number of Accounts")
    ax.set_title("Risk Score Distribution")
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=TEXT)
    ax.grid(True, axis="y")
    save("02_risk_score_histogram.png")


# ── Chart 3: Signal co-occurrence heatmap ─────────────────────────────────────
def chart_signal_heatmap(df: pd.DataFrame):
    signal_cols = [
        "high_login_freq", "new_high_activity", "extreme_posts",
        "low_ff_ratio", "location_hopping", "failed_login_flag",
        "community_reported", "incomplete_profile",
    ]
    short_names = [
        "High Logins", "New+Active", "Extreme Posts",
        "Low FF Ratio", "Location Hop", "Failed Login",
        "Reported", "Incomplete",
    ]
    corr = df[signal_cols].corr()
    corr.columns = short_names
    corr.index   = short_names

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(
        corr, ax=ax, annot=True, fmt=".2f",
        cmap="RdYlGn_r",
        linewidths=0.5, linecolor=BG,
        annot_kws={"size": 8},
        vmin=-0.5, vmax=1,
    )
    ax.set_title("Fraud Signal Correlation Matrix\n(how often signals fire together)")
    plt.xticks(rotation=35, ha="right")
    plt.yticks(rotation=0)
    save("03_signal_heatmap.png")


# ── Chart 4: Logins vs Posts scatter ──────────────────────────────────────────
def chart_logins_vs_posts(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))

    for tier in ["Low", "Medium", "High"]:
        sub = df[df["risk_tier"] == tier]
        ax.scatter(
            sub["logins_per_day"], sub["posts_per_day"],
            c=TIER_COLORS[tier], label=tier,
            alpha=0.65, s=35, edgecolors="none",
        )

    ax.axvline(10,  color="#ff9800", linewidth=1.2, linestyle="--", alpha=0.6, label="Login threshold")
    ax.axhline(100, color="#f44336", linewidth=1.2, linestyle="--", alpha=0.6, label="Post threshold")
    ax.set_xlabel("Logins per Day")
    ax.set_ylabel("Posts per Day")
    ax.set_title("Login Frequency vs Posting Rate\n(coloured by risk tier)")
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=TEXT)
    ax.grid(True)
    save("04_logins_vs_posts.png")


# ── Chart 5: FF ratio box plot ─────────────────────────────────────────────────
def chart_ff_ratio_boxplot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 5))

    data_by_tier = [df[df["risk_tier"] == t]["ff_ratio"].values
                    for t in ["Low", "Medium", "High"]]
    colors = [TIER_COLORS[t] for t in ["Low", "Medium", "High"]]

    bp = ax.boxplot(
        data_by_tier,
        patch_artist=True,
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(color=TEXT),
        capprops=dict(color=TEXT),
        flierprops=dict(marker="o", color=ACCENT, alpha=0.4, markersize=3),
    )
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    ax.set_xticklabels(["Low", "Medium", "High"])
    ax.set_xlabel("Risk Tier")
    ax.set_ylabel("Follower / Following Ratio")
    ax.set_title("Follower-to-Following Ratio by Risk Tier\n(bots follow many, few follow back)")
    ax.axhline(0.1, color="#f44336", linewidth=1.2, linestyle="--", alpha=0.7, label="Threshold 0.1")
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=TEXT)
    ax.grid(True, axis="y")
    save("05_ff_ratio_by_tier.png")


# ── Chart 6: Account age vs risk score ────────────────────────────────────────
def chart_age_vs_risk(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))

    for tier in ["Low", "Medium", "High"]:
        sub = df[df["risk_tier"] == tier]
        ax.scatter(
            sub["account_age_days"], sub["risk_score"],
            c=TIER_COLORS[tier], label=tier,
            alpha=0.60, s=30, edgecolors="none",
        )

    ax.axvline(60, color="#ff9800", linewidth=1.2, linestyle="--", alpha=0.6, label="60-day threshold")
    ax.set_xlabel("Account Age (days)")
    ax.set_ylabel("Risk Score")
    ax.set_title("Account Age vs Risk Score\n(new accounts cluster at high risk)")
    ax.legend(facecolor="#21262d", edgecolor="#30363d", labelcolor=TEXT)
    ax.grid(True)
    save("06_age_vs_risk.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    apply_dark_theme()

    df = load(SCORED_FILE)

    print("\n🎨  Generating charts …")
    chart_risk_distribution(df)
    chart_score_histogram(df)
    chart_signal_heatmap(df)
    chart_logins_vs_posts(df)
    chart_ff_ratio_boxplot(df)
    chart_age_vs_risk(df)

    print(f"\n✅  All 6 charts saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()