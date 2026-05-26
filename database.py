# database.py

import sqlite3
import pandas as pd
import os
from datetime import datetime

# ── Database path ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "data", "nigeria_incidents.db")


# ── Connect ───────────────────────────────────────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Create all tables ─────────────────────────────────────────────────────────
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Main incidents table (from your CSV)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            state         TEXT,
            category      TEXT,
            deaths        INTEGER DEFAULT 0,
            start_date    TEXT,
            end_date      TEXT,
            year          INTEGER,
            month         INTEGER,
            source        TEXT DEFAULT 'dataset',
            created_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Live news table (from RSS feeds)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS live_news (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT NOT NULL,
            summary       TEXT,
            source        TEXT,
            url           TEXT,
            state         TEXT,
            category      TEXT,
            deaths        INTEGER DEFAULT 0,
            published     TEXT,
            fetched_at    TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title)
        )
    """)

    # Location queries log (tracks what users search)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            query         TEXT,
            resolved_state TEXT,
            risk_level    TEXT,
            queried_at    TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Risk snapshots (daily state risk summary)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_snapshots (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            state         TEXT,
            total_incidents INTEGER,
            total_deaths  INTEGER,
            risk_level    TEXT,
            snapshot_date TEXT,
            UNIQUE(state, snapshot_date)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Tables created successfully")


# ── Import historical CSV into incidents table ────────────────────────────────
def import_csv_to_db(csv_path: str = None):
    if csv_path is None:
        csv_path = os.path.join(BASE, "data", "incidents.csv")

    from location_engine import extract_state, classify_incident

    df = pd.read_csv(csv_path)
    df["Number of deaths"] = pd.to_numeric(
        df["Number of deaths"], errors="coerce"
    ).fillna(0)
    df["Start date"] = pd.to_datetime(df["Start date"], errors="coerce")
    df["State"]    = df["Title"].apply(extract_state)
    df["Category"] = df["Title"].apply(classify_incident)

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    skipped  = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO incidents
                    (title, state, category, deaths,
                     start_date, year, month, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row.get("Title", "")),
                str(row.get("State", "Unknown")),
                str(row.get("Category", "Other")),
                int(row.get("Number of deaths", 0)),
                str(row["Start date"]) if pd.notna(row["Start date"]) else None,
                int(row["Start date"].year)  if pd.notna(row["Start date"]) else None,
                int(row["Start date"].month) if pd.notna(row["Start date"]) else None,
                "dataset"
            ))
            inserted += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"✅ Imported {inserted} incidents ({skipped} skipped)")


# ── Import live news CSV into live_news table ─────────────────────────────────
def import_live_news_to_db(csv_path: str = None):
    if csv_path is None:
        csv_path = os.path.join(BASE, "data", "live_news.csv")

    if not os.path.exists(csv_path):
        print("⚠️  No live_news.csv found. Fetch news first.")
        return

    df = pd.read_csv(csv_path)
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    skipped  = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO live_news
                    (title, summary, source, url,
                     state, category, deaths, published, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row.get("Title", "")),
                str(row.get("Summary", "")),
                str(row.get("Source", "")),
                str(row.get("URL", "")),
                str(row.get("State", "Unknown")),
                str(row.get("Category", "Other")),
                int(row.get("Number of deaths", 0)),
                str(row.get("Published", "")),
                str(row.get("Fetched",   "")),
            ))
            inserted += 1
        except Exception:
            skipped += 1

    conn.commit()
    conn.close()
    print(f"✅ Imported {inserted} live news articles ({skipped} skipped/duplicate)")


# ── Log a location query ──────────────────────────────────────────────────────
def log_query(query: str, state: str, risk_level: str):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO query_log (query, resolved_state, risk_level, queried_at)
            VALUES (?, ?, ?, ?)
        """, (query, state, risk_level, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️  Query log error: {e}")


# ── Save daily risk snapshot ──────────────────────────────────────────────────
def save_risk_snapshot(state: str, incidents: int, deaths: int, risk: str):
    try:
        conn = get_connection()
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute("""
            INSERT OR REPLACE INTO risk_snapshots
                (state, total_incidents, total_deaths, risk_level, snapshot_date)
            VALUES (?, ?, ?, ?, ?)
        """, (state, incidents, deaths, risk, today))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️  Snapshot error: {e}")


# ── Query functions ───────────────────────────────────────────────────────────
def get_incidents_by_state(state: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM incidents
        WHERE LOWER(state) = LOWER(?)
        ORDER BY start_date DESC
    """, conn, params=(state,))
    conn.close()
    return df


def get_live_news_by_state(state: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM live_news
        WHERE LOWER(state) = LOWER(?)
        ORDER BY fetched_at DESC
    """, conn, params=(state,))
    conn.close()
    return df


def get_top_dangerous_states(limit: int = 10) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT state,
               COUNT(*)   AS total_incidents,
               SUM(deaths) AS total_deaths
        FROM incidents
        WHERE state != 'Unknown'
        GROUP BY state
        ORDER BY total_deaths DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df


def get_recent_live_news(limit: int = 20) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM live_news
        ORDER BY fetched_at DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df


def get_query_log(limit: int = 50) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT * FROM query_log
        ORDER BY queried_at DESC
        LIMIT ?
    """, conn, params=(limit,))
    conn.close()
    return df


def get_db_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    for table in ["incidents", "live_news", "query_log", "risk_snapshots"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    conn.close()
    return stats


# ── CLI setup ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Setting up Nigeria Incident Database")
    print("=" * 45)

    create_tables()
    import_csv_to_db()
    import_live_news_to_db()

    print("\n📊 Database Stats:")
    stats = get_db_stats()
    for table, count in stats.items():
        print(f"   {table:<20} {count} records")

    print("\n🏆 Top 5 Dangerous States:")
    print(get_top_dangerous_states(5).to_string(index=False))