"""
generate_data.py
----------------
Creates a synthetic dataset of 500 social media users.
Some users are 'normal', others are seeded with bot/fake-account patterns
so our detection pipeline has real signal to find.

Run:  python src/generate_data.py
Output: data/raw_users.csv
"""

import numpy as np
import pandas as pd
import random
import os

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ── Config ────────────────────────────────────────────────────────────────────
N_USERS   = 500          # total accounts to generate
BOT_FRAC  = 0.30         # ~30 % will have suspicious patterns
OUT_DIR   = "data"
OUT_FILE  = os.path.join(OUT_DIR, "raw_users.csv")


# ── Helper: generate a fake IP address ───────────────────────────────────────
def random_ip(shared_pool=None):
    """
    If shared_pool is provided we pick from it (simulates multi-account IP).
    Otherwise we generate a fresh random IP.
    """
    if shared_pool and random.random() < 0.5:
        return random.choice(shared_pool)
    return f"{random.randint(1,254)}.{random.randint(0,255)}." \
           f"{random.randint(0,255)}.{random.randint(1,254)}"


# ── Shared IP pool (used by bot accounts to simulate same-IP clusters) ────────
SHARED_IPS = [random_ip() for _ in range(15)]   # 15 "suspicious" IPs


# ── Build one user row ────────────────────────────────────────────────────────
def make_user(user_id, is_bot=False):
    """
    Returns a dict of behavioural features for one account.

    Normal users  → plausible human ranges
    Bot users     → inflated activity, new accounts, suspicious IPs, etc.
    """

    if is_bot:
        # --- Bot / fake account patterns ---
        account_age_days     = np.random.randint(1, 45)          # very new
        posts_per_day        = round(np.random.uniform(20, 150), 1)   # extreme posting
        logins_per_day       = round(np.random.uniform(8, 30), 1)     # constant logins
        ip_address           = random_ip(shared_pool=SHARED_IPS)      # often shared
        location_changes     = np.random.randint(3, 20)          # hopping locations
        failed_logins        = np.random.randint(3, 20)          # repeated failures
        followers            = np.random.randint(0, 200)          # low followers
        following            = np.random.randint(500, 5000)       # follows many
        reports              = np.random.randint(1, 10)           # reported by others
        profile_completeness = round(np.random.uniform(0.05, 0.38), 2)  # incomplete
    else:
        # --- Normal human patterns ---
        account_age_days     = np.random.randint(30, 2000)
        posts_per_day        = round(np.random.uniform(0, 10), 1)
        logins_per_day       = round(np.random.uniform(0.5, 5), 1)
        ip_address           = random_ip()                         # fresh IP
        location_changes     = np.random.randint(0, 4)
        failed_logins        = np.random.randint(0, 3)
        followers            = np.random.randint(50, 10000)
        following            = np.random.randint(10, 2000)
        reports              = np.random.randint(0, 2)
        profile_completeness = round(np.random.uniform(0.40, 1.0), 2)

    return {
        "user_id"             : f"U{user_id:04d}",
        "account_age_days"    : account_age_days,
        "posts_per_day"       : posts_per_day,
        "logins_per_day"      : logins_per_day,
        "ip_address"          : ip_address,
        "location_changes"    : location_changes,       # in last 30 days
        "failed_logins"       : failed_logins,          # in last 7 days
        "followers"           : followers,
        "following"           : following,
        "reports"             : reports,                # community reports
        "profile_completeness": profile_completeness,   # 0–1 scale
        "is_bot_label"        : int(is_bot),            # ground truth (cheat sheet)
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Decide which users are bots
    n_bots   = int(N_USERS * BOT_FRAC)
    bot_flags = [True] * n_bots + [False] * (N_USERS - n_bots)
    random.shuffle(bot_flags)

    rows = [make_user(i + 1, is_bot=flag) for i, flag in enumerate(bot_flags)]

    df = pd.DataFrame(rows)

    # Introduce ~3 % missing values to make cleaning realistic
    for col in ["posts_per_day", "profile_completeness", "failed_logins"]:
        mask = np.random.rand(N_USERS) < 0.03
        df.loc[mask, col] = np.nan

    df.to_csv(OUT_FILE, index=False)
    print(f"✅  Dataset saved → {OUT_FILE}  ({len(df)} rows, {n_bots} bot accounts)")
    print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    main()