import requests
import pandas as pd

from bs4 import BeautifulSoup

# =========================================
# NEWS SOURCES
# =========================================

sources = {

    "Punch": "https://punchng.com/topics/security/",

    "Channels": "https://www.channelstv.com/category/news/",

    "Vanguard": "https://www.vanguardngr.com/category/national-news/",

    "Guardian": "https://guardian.ng/category/news/"
}

# =========================================
# INCIDENT KEYWORDS
# =========================================

keywords = [

    "kidnap",
    "bandit",
    "attack",
    "gunmen",
    "terrorist",
    "explosion",
    "crash",
    "violence",
    "killed",
    "herdsmen"
]

# =========================================
# STORAGE
# =========================================

news_data = []

# =========================================
# SCRAPE NEWS
# =========================================

for source_name, url in sources.items():

    try:

        response = requests.get(
            url,
            timeout=10
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        headlines = soup.find_all([
            "h1",
            "h2",
            "h3"
        ])

        for item in headlines:

            title = item.get_text().strip()

            if len(title) < 15:
                continue

            lower_title = title.lower()

            # =================================
            # INCIDENT DETECTION
            # =================================

            matched = False

            for word in keywords:

                if word in lower_title:
                    matched = True
                    break

            if matched:

                news_data.append({

                    "Source": source_name,

                    "Headline": title,

                    "KeywordMatch": True
                })

    except Exception as e:

        print(
            f"Error scraping {source_name}: {e}"
        )

# =========================================
# CREATE DATAFRAME
# =========================================

df = pd.DataFrame(news_data)

# =========================================
# REMOVE DUPLICATES
# =========================================

df = df.drop_duplicates()

# =========================================
# SAVE DATA
# =========================================

df.to_csv(
    "data/live_news_incidents.csv",
    index=False
)

# =========================================
# OUTPUT
# =========================================

print("\nLIVE NEWS SCRAPING COMPLETE\n")

print(df.head(20))