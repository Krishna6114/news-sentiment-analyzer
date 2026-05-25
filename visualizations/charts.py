# visualizations/charts.py
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd


SENTIMENT_COLORS = {
    "Positive": "#2ecc71",
    "Negative": "#e74c3c",
    "Neutral": "#95a5a6"
}

def apply_dark_theme(fig):
    """Applies consistent dark theme to all plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Mono, monospace", color="#e8e8f0", size=11),
        title_font=dict(family="Syne, sans-serif", size=16, color="#e8e8f0"),
        legend=dict(
            bgcolor="rgba(18,18,26,0.8)",
            bordercolor="rgba(0,212,255,0.2)",
            borderwidth=1
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)")
    )
    return fig


def sentiment_pie_chart(df):
    """Pie chart of overall sentiment distribution."""
    counts = df["sentiment"].value_counts().reset_index()
    counts.columns = ["sentiment", "count"]

    fig = px.pie(
        counts,
        names="sentiment",
        values="count",
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        title="Overall Sentiment Distribution",
        hole=0.4  # makes it a donut chart — looks cleaner
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_dark_theme(fig)


def sentiment_bar_by_category(grouped_df):
    """
    Grouped bar chart: sentiment breakdown per category.
    grouped_df should come from stats.sentiment_by_category()
    """
    fig = px.bar(
        grouped_df,
        x="category",
        y="count",
        color="sentiment",
        color_discrete_map=SENTIMENT_COLORS,
        barmode="group",
        title="Sentiment Breakdown by Category",
        labels={"count": "Number of Articles", "category": "Category"}
    )
    fig.update_layout(xaxis_tickangle=-30)
    return apply_dark_theme(fig)


def compound_score_histogram(df):
    """Histogram of compound sentiment scores."""
    fig = px.histogram(
        df,
        x="compound",
        nbins=30,
        color_discrete_sequence=["#3498db"],
        title="Distribution of Sentiment Scores",
        labels={"compound": "Compound Score (-1 to +1)"}
    )
    fig.add_vline(x=0.05, line_dash="dash", line_color="green", annotation_text="Positive threshold")
    fig.add_vline(x=-0.05, line_dash="dash", line_color="red", annotation_text="Negative threshold")
    return apply_dark_theme(fig)


def avg_sentiment_bar(avg_df):
    """
    Horizontal bar chart of average sentiment per category.
    avg_df should come from stats.average_sentiment_by_category()
    """
    fig = px.bar(
        avg_df,
        x="compound",
        y="category",
        orientation="h",
        title="Average Sentiment Score by Category",
        color="compound",
        color_continuous_scale="RdYlGn",  # Red = negative, Green = positive
        labels={"compound": "Avg Compound Score", "category": "Category"}
    )
    fig.add_vline(x=0, line_dash="dash", line_color="black")
    return apply_dark_theme(fig)


def generate_wordcloud(df):
    """
    Generates a WordCloud from all headlines.
    Returns a matplotlib figure (Streamlit can display this directly).
    """
    text = " ".join(df["title"].dropna().tolist())

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        colormap="viridis",
        max_words=100,
        collocations=False
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Most Frequent Words in Headlines", fontsize=16)
    plt.tight_layout()
    return fig


def source_bar_chart(source_df):
    """Bar chart of top news sources."""
    fig = px.bar(
        source_df,
        x="source",
        y="count",
        title="Top News Sources",
        color_discrete_sequence=["#9b59b6"],
        labels={"count": "Number of Articles", "source": "Source"}
    )
    fig.update_layout(xaxis_tickangle=-30)
    return apply_dark_theme(fig)

def keyword_comparison_chart(df1, df2, keyword1, keyword2):
    """
    Side by side donut charts comparing sentiment of two keywords.
    """
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=[f"'{keyword1}'", f"'{keyword2}'"]
    )

    for i, (df, keyword) in enumerate([(df1, keyword1), (df2, keyword2)], 1):
        counts = df["sentiment"].value_counts()
        fig.add_trace(
            go.Pie(
                labels=counts.index.tolist(),
                values=counts.values.tolist(),
                hole=0.4,
                marker_colors=[SENTIMENT_COLORS.get(l, "#ccc") for l in counts.index]
            ),
            row=1, col=i
        )

    fig.update_layout(title_text="Keyword Sentiment Comparison", height=400)
    return apply_dark_theme(fig)


def keyword_avg_score_chart(df1, df2, keyword1, keyword2):
    """
    Bar chart comparing average compound scores of two keywords.
    """
    import plotly.graph_objects as go

    avg1 = round(df1["compound"].mean(), 3)
    avg2 = round(df2["compound"].mean(), 3)

    colors = [
        "#2ecc71" if avg1 > 0 else "#e74c3c",
        "#2ecc71" if avg2 > 0 else "#e74c3c"
    ]

    fig = go.Figure(go.Bar(
        x=[keyword1, keyword2],
        y=[avg1, avg2],
        marker_color=colors,
        text=[avg1, avg2],
        textposition="outside"
    ))

    fig.update_layout(
        title="Average Sentiment Score Comparison",
        yaxis_title="Compound Score",
        yaxis=dict(range=[-1, 1]),
        height=400
    )
    fig.add_hline(y=0, line_dash="dash", line_color="black")
    return apply_dark_theme(fig)


def sentiment_over_time_chart(history_df):
    """
    Line chart showing sentiment trend over time per category.
    """
    if history_df.empty:
        return None

    fig = px.line(
        history_df,
        x="date",
        y="avg_compound",
        color="category",
        title="Sentiment Trend Over Time (by Category)",
        labels={"avg_compound": "Avg Sentiment Score", "date": "Date"},
        markers=True
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
    fig.update_layout(height=450)
    return apply_dark_theme(fig)