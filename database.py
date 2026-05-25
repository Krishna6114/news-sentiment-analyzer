# database.py
import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "sentiment_history.db"

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            avg_compound REAL,
            positive_count INTEGER,
            negative_count INTEGER,
            neutral_count INTEGER
        )
    """)
    conn.commit()
    conn.close()


def save_daily_sentiment(df):
    """
    Takes analyzed DataFrame and saves daily averages per category.
    Skips if today's data already saved.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = str(date.today())

    # Check if today's data already exists
    cursor.execute("SELECT COUNT(*) FROM daily_sentiment WHERE date = ?", (today,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # already saved today

    # Group by category and save
    grouped = df.groupby("category")
    for category, group in grouped:
        avg_compound = round(group["compound"].mean(), 4)
        positive_count = len(group[group["sentiment"] == "Positive"])
        negative_count = len(group[group["sentiment"] == "Negative"])
        neutral_count = len(group[group["sentiment"] == "Neutral"])

        cursor.execute("""
            INSERT INTO daily_sentiment 
            (date, category, avg_compound, positive_count, negative_count, neutral_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (today, category, avg_compound, positive_count, negative_count, neutral_count))

    conn.commit()
    conn.close()


def load_history():
    """Loads all historical sentiment data as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM daily_sentiment ORDER BY date ASC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df