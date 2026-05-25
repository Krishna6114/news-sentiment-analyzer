# analysis/stats.py
import pandas as pd


def sentiment_by_category(df):
    """
    Groups data by category and counts sentiment labels.
    Returns a DataFrame ready for plotting.
    """
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["category", "sentiment"]).size().reset_index(name="count")
    return grouped


def top_sources(df, n=10):
    """
    Returns top N news sources by article count.
    """
    if df.empty:
        return pd.DataFrame()

    return df["source"].value_counts().head(n).reset_index()


def average_sentiment_by_category(df):
    """
    Returns average compound sentiment score per category.
    Useful for comparing which category is most positive/negative.
    """
    if df.empty:
        return pd.DataFrame()

    return df.groupby("category")["compound"].mean().reset_index().sort_values("compound")


def most_negative_headlines(df, n=5):
    """Returns the N most negative headlines."""
    return df.nsmallest(n, "compound")[["title", "source", "category", "compound"]]


def most_positive_headlines(df, n=5):
    """Returns the N most positive headlines."""
    return df.nlargest(n, "compound")[["title", "source", "category", "compound"]]