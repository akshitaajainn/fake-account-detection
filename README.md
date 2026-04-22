# Fake Account Detection

This project is focused on detecting suspicious or bot accounts on a social media platform using rule-based anomaly detection, behavioural feature engineering, and weighted risk scoring.

---

## Tech Stack
  • Python
  • Pandas
  • NumPy
  • Matplotlib
  • Seaborn
  • SQL

---

## Project Goal

The goal of this project is to simulate how fraud or risk analytics teams identify suspicious accounts on large social media platforms. The project builds a small analytical pipeline that generates user data, cleans it, engineers fraud-related behavioural signals, assigns a risk score, and produces insights through SQL queries and visual analysis.

The final output helps identify accounts that require manual investigation and demonstrates a simple explainable approach to fraud detection.

---

## Dataset Pipeline

The project follows a step-by-step data pipeline:

1. **Data Generation**
   - A synthetic dataset of 500 social media users is created.
   - Each user contains attributes such as account age, posts per day, login behaviour, followers, following count, and profile completeness.

2. **Data Cleaning**
   - Missing values are handled
   - Numeric values are clipped to remove unrealistic outliers
   - Data types are standardized

3. **Feature Engineering**
   - Behaviour-based fraud signals are created from raw attributes
   - Each signal represents suspicious behaviour patterns

4. **Risk Scoring**
   - Each fraud signal has a weight
   - Signals are combined into a **0–100 risk score**

5. **Risk Classification**
   - Accounts are categorized into Low, Medium, or High risk tiers

6. **Analytics & Visualization**
   - KPIs are calculated
   - SQL-style analysis is performed
   - Visualizations are generated for reporting

---

## Project Structure

```
fake_account_detector/
├── src/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── feature_engineering.py
│   ├── analysis.py
│   └── visualize.py
│
├── sql/
│   ├── fraud_queries.sql
│   └── run_sql_queries.py
│
├── data/
│   ├── raw_users.csv
│   ├── clean_users.csv
│   ├── scored_users.csv
│   ├── kpi_summary.csv
│   └── review_queue.csv
│
├── visuals/
│   ├── 01_risk_distribution.png
│   ├── 02_risk_score_histogram.png
│   ├── 03_signal_heatmap.png
│   ├── 04_logins_vs_posts.png
│   ├── 05_ff_ratio_by_tier.png
│   └── 06_age_vs_risk.png
│
└── README.md
```

---

## Running the Project

Install required libraries:

```
pip install pandas numpy matplotlib seaborn
```

Run the pipeline in the following order:

```
python src/generate_data.py
python src/clean_data.py
python src/feature_engineering.py
python src/analysis.py
python src/visualize.py
```

To execute SQL queries:

```
python sql/run_sql_queries.py
```

---

## Fraud Signals

The model uses rule-based signals derived from behavioural patterns.

| Signal | Rule | Weight |
|------|------|------|
| High Login Frequency | logins/day > 10 | 20 |
| New Account With High Activity | account_age < 60 days AND posts/day > 20 | 20 |
| Extreme Posting Activity | posts/day > 100 | 25 |
| Low Follower Ratio | followers/following < 0.1 | 15 |
| Frequent Location Changes | location changes > 5 in 30 days | 15 |
| Multiple Failed Logins | failures > 5 in 7 days | 15 |
| Community Reports | reports ≥ 3 | 20 |
| Incomplete Profile | profile completeness < 40% | 10 |

Risk score calculation:

```
Risk Score = (weighted sum of triggered signals / 120) * 100
```

---

## Risk Tiers

| Tier | Score Range | Interpretation |
|------|-------------|---------------|
| Low | 0 – 24 | Normal user behaviour |
| Medium | 25 – 54 | Requires monitoring |
| High | 55 – 100 | Requires manual investigation |

Accounts in the High risk tier are added to a **review queue for investigation**.

---

## Key Metrics Generated

The analysis step produces several useful metrics:

- Bot detection rate
- False positive rate
- High-risk rate for newly created accounts
- Frequency of each fraud signal

These metrics help understand the effectiveness of the rule-based detection system.

---

## SQL Analysis

The project includes SQL queries that simulate analyst workflows.

| Query | Purpose |
|------|--------|
| Q1 | Identify users with abnormal login frequency |
| Q2 | Detect multiple accounts using the same IP address |
| Q3 | Detect burst posting behaviour from new accounts |
| Q4 | Identify frequent location changes (possible VPN use) |
| Q5 | Profile completeness statistics by risk tier |
| Q6 | Frequency of fraud signals |
| Q7 | Generate review queue of high-risk accounts |
| Q8 | Distribution of account age across risk tiers |

These queries demonstrate how SQL can be used to explore suspicious activity patterns.

---

## Visual Insights

The project generates multiple charts for analysis and reporting.

📊 Risk Tier Distribution  
📊 Risk Score Histogram  
📊 Fraud Signal Correlation Heatmap  
📊 Logins vs Posts Scatter Plot  
📊 Follower-Following Ratio by Risk Tier  
📊 Account Age vs Risk Score

These visualizations help identify patterns commonly associated with automated or fraudulent accounts.

---

## Key Takeaways

- Rule-based fraud detection systems are simple, explainable, and easy to audit.
- Behavioural signals can reveal suspicious activity without requiring machine learning models.
- Threshold selection directly affects the balance between detecting fraud and minimizing false positives.
- Combining multiple weak signals often produces stronger indicators of suspicious behaviour.

---
