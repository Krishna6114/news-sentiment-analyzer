# analyzer.py
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize VADER once (no need to reload every time)
sia = SentimentIntensityAnalyzer()


def get_sentiment_label(compound_score):
    """
    Converts VADER compound score to a readable label.
    VADER compound score ranges from -1 (most negative) to +1 (most positive)
    """
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def analyze_dataframe(df):
    """
    Takes a DataFrame with a 'title' column.
    Adds sentiment score and label columns.
    Returns enriched DataFrame.
    """
    if df.empty:
        return df

    scores = []

    for title in df["title"]:
        score = sia.polarity_scores(str(title))
        scores.append({
            "neg": score["neg"],
            "neu": score["neu"],
            "pos": score["pos"],
            "compound": score["compound"]
        })

    scores_df = pd.DataFrame(scores)

    # Add scores back to original dataframe
    df = df.reset_index(drop=True)
    df = pd.concat([df, scores_df], axis=1)

    # Add human-readable label
    df["sentiment"] = df["compound"].apply(get_sentiment_label)

    return df


def get_summary_stats(df):
    """
    Returns a summary dict with counts and percentages.
    Useful for showing quick stats in the dashboard.
    """
    if df.empty:
        return {}

    total = len(df)
    counts = df["sentiment"].value_counts()

    summary = {
        "total": total,
        "positive": counts.get("Positive", 0),
        "negative": counts.get("Negative", 0),
        "neutral": counts.get("Neutral", 0),
        "positive_pct": round(counts.get("Positive", 0) / total * 100, 1),
        "negative_pct": round(counts.get("Negative", 0) / total * 100, 1),
        "neutral_pct": round(counts.get("Neutral", 0) / total * 100, 1),
        "avg_compound": round(df["compound"].mean(), 3)
    }

    return summary