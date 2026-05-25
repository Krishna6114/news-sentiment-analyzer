# fetcher.py
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()  # loads your .env file

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/top-headlines"

CATEGORIES = ["business", "technology", "sports", "health", "entertainment", "science"]

def fetch_headlines(category="technology", country="us", page_size=100):
    """
    Fetches headlines from NewsAPI for a given category.
    Returns a clean pandas DataFrame.
    """
    params = {
        "apiKey": API_KEY,
        "category": category,
        "country": country,
        "pageSize": page_size
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # throws error if request failed
        data = response.json()

        articles = data.get("articles", [])

        if not articles:
            return pd.DataFrame()  # return empty if nothing found

        df = pd.DataFrame(articles)

        # Keep only useful columns
        df = df[["title", "description", "source", "publishedAt", "url"]]

        # Clean up source column (it's a dict like {"id": "...", "name": "BBC"})
        df["source"] = df["source"].apply(lambda x: x.get("name", "Unknown"))

        # Add category column
        df["category"] = category

        # Drop rows where title is missing
        df = df.dropna(subset=["title"])

        # Clean publishedAt to just date
        df["publishedAt"] = pd.to_datetime(df["publishedAt"]).dt.date

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return pd.DataFrame()


def fetch_all_categories(country="us"):
    """
    Fetches headlines for ALL categories and combines them.
    """
    all_data = []

    for category in CATEGORIES:
        df = fetch_headlines(category=category, country=country)
        if not df.empty:
            all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


def fetch_by_keyword(keyword, page_size=50):
    """
    Searches news by a custom keyword.
    Uses /everything endpoint instead of top-headlines.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": API_KEY,
        "q": keyword,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            return pd.DataFrame()

        df = pd.DataFrame(articles)
        df = df[["title", "description", "source", "publishedAt", "url"]]
        df["source"] = df["source"].apply(lambda x: x.get("name", "Unknown"))
        df["category"] = f"keyword: {keyword}"
        df = df.dropna(subset=["title"])
        df["publishedAt"] = pd.to_datetime(df["publishedAt"]).dt.date

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching keyword news: {e}")
        return pd.DataFrame()
    
def fetch_two_keywords(keyword1, keyword2, page_size=30):
    """
    Fetches headlines for two keywords separately.
    Returns two DataFrames for comparison.
    """
    df1 = fetch_by_keyword(keyword1, page_size)
    df2 = fetch_by_keyword(keyword2, page_size)
    return df1, df2

def fetch_india_news(page_size=100):
    """
    Fetches Indian news using keyword search since free plan
    doesn't support country=in for top-headlines.
    """
    url = "https://newsapi.org/v2/everything"
    
    india_queries = [
        "India politics", 
        "India economy",
        "India technology",
        "India sports",
        "India business",
        "India health"
    ]
    
    all_data = []
    
    for query in india_queries:
        params = {
            "apiKey": API_KEY,
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])

            if not articles:
                continue

            df = pd.DataFrame(articles)
            df = df[["title", "description", "source", "publishedAt", "url"]]
            df["source"] = df["source"].apply(lambda x: x.get("name", "Unknown"))
            df["category"] = query.replace("India ", "")
            df = df.dropna(subset=["title"])
            df["publishedAt"] = pd.to_datetime(df["publishedAt"]).dt.date
            all_data.append(df)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {query}: {e}")
            continue

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()