"""
run_sql_queries.py
------------------
Loads scored_users.csv into an in-memory SQLite database,
then executes each query from fraud_queries.sql and prints
the results — no database server required!

Run:  python sql/run_sql_queries.py
Input:  data/scored_users.csv
"""

import os
import sqlite3
import pandas as pd

SCORED_FILE = os.path.join("data", "scored_users.csv")
SQL_FILE    = os.path.join("sql", "fraud_queries.sql")
DIVIDER     = "═" * 65


def run_queries():
    # ── Load CSV into SQLite ──────────────────────────────────────────────────
    df = pd.read_csv(SCORED_FILE)
    conn = sqlite3.connect(":memory:")          # in-memory database
    df.to_sql("scored_users", conn, index=False, if_exists="replace")
    print(f"✅  Loaded {len(df):,} rows into in-memory SQLite table 'scored_users'")

    # ── Read and split the SQL file into individual queries ──────────────────
    import re
    with open(SQL_FILE, "r") as f:
        raw = f.read()

    # Extract query labels from comment headers
    headers = re.findall(r"-- (Q\d+:.*)", raw)

    # Split on separator comment lines to isolate each query block
    # Each block starts after a "-- ──────" separator
    sections = re.split(r"-- ─{5,}", raw)

    # Pull SELECT/UNION statements from each section (skip pure-comment sections)
    blocks = []
    for section in sections:
        # Find all SELECT statements in this section (before the semicolon)
        match = re.search(r"(SELECT[\s\S]+?);", section, re.IGNORECASE)
        if match:
            blocks.append(match.group(1).strip())

    for i, sql in enumerate(blocks):
        label = headers[i] if i < len(headers) else f"Query {i+1}"
        print(f"\n{DIVIDER}")
        print(f"  {label}")
        print(DIVIDER)
        try:
            result = pd.read_sql_query(sql, conn)
            if result.empty:
                print("  (no rows returned)")
            else:
                print(result.to_string(index=False))
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

    conn.close()
    print(f"\n{DIVIDER}")
    print("  ✅  All queries complete.")
    print(DIVIDER)


if __name__ == "__main__":
    run_queries()