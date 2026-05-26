# news_pipeline.py

import feedparser
import pandas as pd
import re
import os
from datetime import datetime
from location_engine import NIGERIAN_STATES, extract_state, classify_incident

# ── Nigerian News RSS Feeds (all free, no API key) ────────────────────────────
RSS_FEEDS = {
    "Vanguard":       "https://www.vanguardngr.com/feed/",
    "Punch":          "https://punchng.com/feed/",
    "Channels":       "https://www.channelstv.com/feed/",
    "Premium Times":  "https://www.premiumtimesng.com/feed/",
    "Daily Post":     "https://dailypost.ng/feed/",
    "The Nation":     "https://thenationonlineng.net/feed/",
    "Tribune":        "https://tribuneonlineng.com/feed/",
}

# ── Incident keywords to filter relevant articles ─────────────────────────────
INCIDENT_KEYWORDS = [
    "crash", "accident", "killed", "dead", "death", "deaths",
    "attack", "gunmen", "bandits", "kidnap", "abduct", "fire",
    "flood", "explosion", "blast", "bomb", "murder", "shooting",
    "robbery", "riot", "unrest", "casualt", "fatali", "injur",
    "massacre", "genocide", "violence", "crisis", "emergency",
    "disaster", "collapse", "drowning", "electrocution", "poisoning",
]

def is_incident(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in INCIDENT_KEYWORDS)


def extract_deaths_from_text(text: str) -> int:
    """Try to extract a death count from article title/summary."""
    text = text.lower()

    # Patterns like "kills 3", "3 dead", "3 killed", "3 persons dead"
    patterns = [
        r'(\d+)\s+(?:persons?|people|men|women|children|soldiers?|officers?)?\s*(?:killed|dead|die[sd]?)',
        r'kills?\s+(\d+)',
        r'(\d+)\s+(?:casualties|fatalities|deaths?)',
        r'claims?\s+(\d+)\s+lives?',
        r'(\d+)\s+lives?\s+(?:lost|claimed)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return 0


# ── Fetch & parse one RSS feed ────────────────────────────────────────────────
def fetch_feed(source: str, url: str) -> list:
    try:
        feed = feedparser.parse(url)
        articles = []

        for entry in feed.entries:
            title   = entry.get("title", "")
            summary = entry.get("summary", "")
            link    = entry.get("link", "")
            published = entry.get("published", str(datetime.now()))

            # Combine title + summary for analysis
            full_text = f"{title} {summary}"

            # Filter: only incident-related articles
            if not is_incident(full_text):
                continue

            # Extract state
            state = extract_state(full_text)

            # Extract deaths
            deaths = extract_deaths_from_text(full_text)

            # Classify incident
            category = classify_incident(full_text)

            articles.append({
                "Title":           title,
                "Summary":         summary[:300] if summary else "",
                "Source":          source,
                "URL":             link,
                "State":           state,
                "Category":        category,
                "Number of deaths": deaths,
                "Published":       published,
                "Fetched":         datetime.now().strftime("%Y-%m-%d %H:%M"),
            })

        return articles

    except Exception as e:
        print(f"⚠️  Failed to fetch {source}: {e}")
        return []


# ── Fetch all feeds ───────────────────────────────────────────────────────────
def fetch_all_feeds() -> pd.DataFrame:
    all_articles = []

    for source, url in RSS_FEEDS.items():
        print(f"📡 Fetching {source}...")
        articles = fetch_feed(source, url)
        all_articles.extend(articles)
        print(f"   ✅ {len(articles)} incidents found")

    if not all_articles:
        return pd.DataFrame()

    df = pd.DataFrame(all_articles)
    df = df.drop_duplicates(subset=["Title"])
    df = df.sort_values("Fetched", ascending=False).reset_index(drop=True)

    # Auto-save to database
    try:
        from database import create_tables, import_live_news_to_db
        create_tables()
        save_live_news(df)        # still saves CSV as backup
        import_live_news_to_db()  # also pushes to DB
    except Exception as e:
        print(f"⚠️  DB sync error: {e}")

    return df


# ── Save to CSV ───────────────────────────────────────────────────────────────
def save_live_news(df: pd.DataFrame, base_path: str = None):
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, "data", "live_news.csv")

    if os.path.exists(path):
        # Append new articles, avoid duplicates
        existing = pd.read_csv(path)
        combined = pd.concat([existing, df], ignore_index=True)
        combined = combined.drop_duplicates(subset=["Title"])
        combined.to_csv(path, index=False)
        print(f"\n💾 Updated → {path} ({len(combined)} total articles)")
    else:
        df.to_csv(path, index=False)
        print(f"\n💾 Saved → {path} ({len(df)} articles)")

    return path


# ── Load saved live news ──────────────────────────────────────────────────────
def load_live_news(base_path: str = None) -> pd.DataFrame:
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, "data", "live_news.csv")

    if not os.path.exists(path):
        return pd.DataFrame()

    return pd.read_csv(path)


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Nigeria Live News Intelligence Pipeline")
    print("=" * 45)

    df = fetch_all_feeds()

    if df.empty:
        print("\n❌ No incidents found. Check your internet connection.")
    else:
        print(f"\n📰 Total incidents fetched: {len(df)}")
        print(f"\nTop states affected:")
        print(df["State"].value_counts().head(10))
        print(f"\nTop categories:")
        print(df["Category"].value_counts())
        print(f"\nSample articles:")
        print(df[["Title", "State", "Category", "Number of deaths"]].head(10).to_string())

        save_live_news(df)