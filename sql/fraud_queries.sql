-- =============================================================
-- fraud_queries.sql
-- Fake Account Detector — SQL Analysis Queries
-- =============================================================
-- These queries are written in standard SQL. The run_sql_queries.py script loads scored_users.csv
-- into an in-memory SQLite database and executes each one.
-- =============================================================


-- ─────────────────────────────────────────────────────────────
-- Q1: ABNORMAL LOGIN FREQUENCY
-- Catches bots that constantly poll the platform.
-- Rule: logins_per_day > 10
-- ─────────────────────────────────────────────────────────────
SELECT
    user_id,
    logins_per_day,
    posts_per_day,
    risk_score,
    risk_tier
FROM scored_users
WHERE logins_per_day > 10
ORDER BY logins_per_day DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────────
-- Q2: MULTI-ACCOUNT FROM SAME IP ADDRESS
-- A single IP with multiple accounts is a strong fraud signal.
-- Legitimate users occasionally share IPs (e.g. family, office)
-- but 3+ accounts on one IP warrants review.
-- ─────────────────────────────────────────────────────────────
SELECT
    ip_address,
    COUNT(user_id)         AS account_count,
    ROUND(AVG(risk_score), 1) AS avg_risk_score,
    SUM(CASE WHEN risk_tier = 'High'   THEN 1 ELSE 0 END) AS high_risk_accounts,
    SUM(CASE WHEN risk_tier = 'Medium' THEN 1 ELSE 0 END) AS medium_risk_accounts
FROM scored_users
GROUP BY ip_address
HAVING COUNT(user_id) > 1
ORDER BY account_count DESC, avg_risk_score DESC
LIMIT 15;


-- ─────────────────────────────────────────────────────────────
-- Q3: NEW ACCOUNT BURST PATTERN
-- Brand-new accounts with extremely high post volumes.
-- Legitimate new users ramp up slowly; bots go full speed
-- from day 1.
-- Rule: account_age_days < 30 AND posts_per_day > 20
-- ─────────────────────────────────────────────────────────────
SELECT
    user_id,
    account_age_days,
    posts_per_day,
    logins_per_day,
    followers,
    following,
    risk_score
FROM scored_users
WHERE account_age_days < 30
  AND posts_per_day    > 20
ORDER BY posts_per_day DESC;


-- ─────────────────────────────────────────────────────────────
-- Q4: LOCATION HOPPERS (VPN / PROXY INDICATOR)
-- More than 5 location switches in 30 days suggests
-- the account is using VPNs or proxy rotation — common
-- in bot farms and coordinated inauthentic behaviour.
-- ─────────────────────────────────────────────────────────────
SELECT
    user_id,
    location_changes,
    failed_logins,
    ip_address,
    risk_score,
    risk_tier
FROM scored_users
WHERE location_changes > 5
ORDER BY location_changes DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────────────
-- Q5: PROFILE COMPLETENESS BY RISK TIER
-- KPI query: average completeness, posting rate, and FF ratio
-- grouped by risk tier — gives a snapshot of how bots differ
-- from normal users across multiple dimensions.
-- ─────────────────────────────────────────────────────────────
SELECT
    risk_tier,
    COUNT(*)                              AS user_count,
    ROUND(AVG(profile_completeness), 3)  AS avg_profile_completeness,
    ROUND(AVG(posts_per_day), 2)         AS avg_posts_per_day,
    ROUND(AVG(logins_per_day), 2)        AS avg_logins_per_day,
    ROUND(AVG(ff_ratio), 4)              AS avg_ff_ratio,
    ROUND(AVG(risk_score), 1)            AS avg_risk_score
FROM scored_users
GROUP BY risk_tier
ORDER BY avg_risk_score DESC;


-- ─────────────────────────────────────────────────────────────
-- Q6: FRAUD SIGNAL FREQUENCY REPORT
-- How often does each binary signal fire?
-- Useful for calibrating weights over time.
-- ─────────────────────────────────────────────────────────────
SELECT
    'high_login_freq'    AS signal,
    SUM(high_login_freq)    AS triggered,
    ROUND(100.0 * SUM(high_login_freq)    / COUNT(*), 1) AS pct
FROM scored_users
UNION ALL
SELECT 'new_high_activity', SUM(new_high_activity),
    ROUND(100.0 * SUM(new_high_activity) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'extreme_posts', SUM(extreme_posts),
    ROUND(100.0 * SUM(extreme_posts) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'low_ff_ratio', SUM(low_ff_ratio),
    ROUND(100.0 * SUM(low_ff_ratio) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'location_hopping', SUM(location_hopping),
    ROUND(100.0 * SUM(location_hopping) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'failed_login_flag', SUM(failed_login_flag),
    ROUND(100.0 * SUM(failed_login_flag) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'community_reported', SUM(community_reported),
    ROUND(100.0 * SUM(community_reported) / COUNT(*), 1) FROM scored_users
UNION ALL
SELECT 'incomplete_profile', SUM(incomplete_profile),
    ROUND(100.0 * SUM(incomplete_profile) / COUNT(*), 1) FROM scored_users
ORDER BY triggered DESC;


-- ─────────────────────────────────────────────────────────────
-- Q7: HIGH-RISK ACCOUNT SUMMARY (REVIEW QUEUE)
-- Accounts that triggered 3 or more signals AND are High risk.
-- These should be the first priority for manual review.
-- ─────────────────────────────────────────────────────────────
SELECT
    user_id,
    signals_triggered,
    risk_score,
    account_age_days,
    posts_per_day,
    logins_per_day,
    location_changes,
    failed_logins,
    profile_completeness,
    ff_ratio
FROM scored_users
WHERE risk_tier = 'High'
  AND signals_triggered >= 3
ORDER BY risk_score DESC
LIMIT 25;


-- ─────────────────────────────────────────────────────────────
-- Q8: TIME-SERIES PROXY — NEW ACCOUNTS BY AGE BUCKET
-- Groups accounts into age buckets to simulate a time series.
-- In production you would replace account_age_days with
-- a real created_at timestamp.
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN account_age_days < 7   THEN '0-7 days'
        WHEN account_age_days < 30  THEN '8-30 days'
        WHEN account_age_days < 90  THEN '31-90 days'
        WHEN account_age_days < 365 THEN '91-365 days'
        ELSE '1+ year'
    END AS age_bucket,
    COUNT(*)                                    AS total_accounts,
    SUM(CASE WHEN risk_tier='High' THEN 1 END)  AS high_risk,
    ROUND(100.0 * SUM(CASE WHEN risk_tier='High' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                AS high_risk_pct,
    ROUND(AVG(risk_score), 1)                   AS avg_risk_score
FROM scored_users
GROUP BY age_bucket
ORDER BY MIN(account_age_days);
