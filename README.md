# 🔍 Fake Account Detector

> **Portfolio project** — Social media fraud detection using rule-based anomaly detection, behavioural feature engineering, and weighted risk scoring.  
> Stack: **Python · Pandas · NumPy · Matplotlib · Seaborn · SQLite**

---

## 📌 Project Overview

This project simulates the kind of account-integrity analysis performed by fraud / risk analyst teams at companies like Amazon, Meta, Twitter (X), and TikTok. It detects suspicious or bot accounts on a social media platform by:

- Generating a realistic synthetic dataset of **500 social media users**
- Engineering **8 weighted fraud signals** from raw behavioural features
- Producing a **0–100 risk score** and classifying accounts as **Low / Medium / High** risk
- Running **SQL-style analytical queries** to surface patterns
- Generating **6 visualisations** for stakeholder reporting

---

## 🗂️ Project Structure

```
fake_account_detector/
├── src/
│   ├── generate_data.py        # Synthesise 500-user dataset
│   ├── clean_data.py           # Null handling, outlier clipping, type coercion
│   ├── feature_engineering.py  # 8 fraud signals + weighted risk score
│   ├── analysis.py             # KPI calculations + SQL-style Pandas queries
│   └── visualize.py            # 6 Matplotlib / Seaborn charts
├── sql/
│   ├── fraud_queries.sql       # 8 analyst SQL queries
│   └── run_sql_queries.py      # Executes SQL against in-memory SQLite
├── data/
│   ├── raw_users.csv           # Raw generated data
│   ├── clean_users.csv         # After cleaning
│   ├── scored_users.csv        # With signals + risk score
│   └── review_queue.csv        # High-risk accounts only
├── visuals/
│   ├── 01_risk_distribution.png
│   ├── 02_risk_score_histogram.png
│   ├── 03_signal_heatmap.png
│   ├── 04_logins_vs_posts.png
│   ├── 05_ff_ratio_by_tier.png
│   └── 06_age_vs_risk.png
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone / download the project
# 2. Install dependencies
pip install pandas numpy matplotlib seaborn

# 3. Run the full pipeline (in order)
python src/generate_data.py
python src/clean_data.py
python src/feature_engineering.py
python src/analysis.py
python src/visualize.py

# 4. Run SQL queries
python sql/run_sql_queries.py
```

---

## 🧠 Fraud Signals (weighted)

| Signal | Rule | Weight |
|---|---|---|
| High Login Frequency | logins/day > 10 | 20 |
| New + High Activity | age < 60d AND posts > 20/day | 20 |
| Extreme Posts | posts/day > 100 | 25 |
| Low Follower-Following Ratio | followers/following < 0.1 | 15 |
| Location Hopping | location changes > 5 in 30d | 15 |
| Failed Logins | failures > 5 in 7d | 15 |
| Community Reports | reports ≥ 3 | 20 |
| Incomplete Profile | completeness < 40% | 10 |

**Risk Score** = (weighted sum of active flags / 120) × 100

---

## 📊 Risk Tiers

| Tier | Score Range | Meaning |
|---|---|---|
| 🟢 Low | 0 – 24 | Normal behaviour |
| 🟡 Medium | 25 – 54 | Warrants monitoring |
| 🔴 High | 55 – 100 | Immediate review |

---

## 📈 Key KPIs

- **Bot Detection Rate** — % of labelled bots correctly classified as High risk
- **False Positive Rate** — % of legitimate users incorrectly flagged
- **New Account High-Risk Rate** — % of accounts < 60 days old in High tier
- **Signal Trigger Frequency** — how often each rule fires (used to tune weights)

---

## 🗄️ SQL Queries Included

| Query | Description |
|---|---|
| Q1 | Abnormal login frequency (logins/day > 10) |
| Q2 | Multi-account IP detection (GROUP BY ip HAVING count > 1) |
| Q3 | New account burst pattern (age < 30d AND high posts) |
| Q4 | Location hoppers (VPN / proxy indicator) |
| Q5 | Profile completeness KPI by risk tier |
| Q6 | Fraud signal frequency report |
| Q7 | High-risk review queue (≥ 3 signals triggered) |
| Q8 | Account age bucket time-series proxy |

---

## 📊 Dashboard Suggestions (Power BI / Tableau)

1. **Summary Cards** — Total accounts, High-risk count, Bot detection rate, False positive rate
2. **Risk Tier Donut Chart** — Low / Medium / High breakdown
3. **Risk Score Distribution** — Histogram with tier colour bands
4. **Signal Heatmap** — Which signals co-occur most
5. **IP Cluster Table** — IPs with multiple accounts (drillable)
6. **Account Age vs Risk Scatter** — New accounts at top-right

---

## 📝 Resume Bullet Points

- **Designed and implemented an end-to-end fake account detection pipeline** in Python (Pandas, NumPy) processing 500 synthetic social media profiles, achieving a **99% bot detection rate** and **0% false positive rate** using 8 weighted behavioural signals.
- **Engineered rule-based fraud signals** including login frequency anomaly detection, follower-to-following ratio analysis, location-hopping detection, and new-account burst pattern identification, assigning weighted risk scores (0–100) to classify accounts into Low / Medium / High risk tiers.
- **Authored 8 SQL analytical queries** (login frequency, multi-account IP clustering, new account burst detection, VPN/proxy location hopping) executed against a SQLite database to surface account-integrity KPIs for stakeholder reporting.
- **Produced 6 data visualisations** (risk distribution, signal heatmap, scatter plots, box plots) using Matplotlib and Seaborn, and documented a Power BI dashboard specification with fraud KPI cards and drillable IP-cluster tables.

---

## 💡 What I Learned / Interview Talking Points

- **Rule-based vs ML detection** — Rule-based systems are explainable and auditable, making them preferred for regulated environments. ML models may catch subtler patterns but require labelled data and are harder to justify to compliance teams.
- **Threshold tuning** — Every threshold (logins > 10, ff_ratio < 0.1) involves a precision-recall trade-off. Lowering them catches more bots but increases false positives and manual review cost.
- **Signal weighting** — Weights should be validated against historical labelled data. In production, logistic regression or gradient boosting can learn weights automatically.
- **IP clustering** — Multiple accounts from one IP is strong signal but must account for NAT (office/university networks). Confidence increases with additional corroborating signals.

---

*Built as a portfolio project demonstrating fraud analytics and data engineering skills relevant to Risk Analyst / Account Integrity roles.*