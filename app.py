# app.py
import streamlit as st
import pandas as pd
import time
from fetcher import fetch_all_categories, fetch_by_keyword, fetch_two_keywords, fetch_india_news
from analyzer import analyze_dataframe, get_summary_stats
from database import init_db, save_daily_sentiment, load_history
from summarizer import summarize_headline
from analysis.stats import (
    sentiment_by_category,
    top_sources,
    average_sentiment_by_category,
    most_negative_headlines,
    most_positive_headlines
)
from visualizations.charts import (
    sentiment_pie_chart,
    sentiment_bar_by_category,
    compound_score_histogram,
    avg_sentiment_bar,
    generate_wordcloud,
    source_bar_chart,
    keyword_comparison_chart,
    keyword_avg_score_chart,
    sentiment_over_time_chart
)

# ── Init DB ───────────────────────────────────────────────────
init_db()

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="NewsPulse",
    page_icon="📰",
    layout="wide"
)

# ── Custom CSS Theme ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
}

/* ── Main container ── */
.main .block-container {
    padding: 2rem 3rem;
    max-width: 1400px;
}

/* ── Title ── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 3rem !important;
    background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 50%, #ff006e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px !important;
    line-height: 1.1 !important;
}

/* ── Subheaders ── */
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #e8e8f0 !important;
    letter-spacing: -0.5px !important;
}

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #12121a, #1a1a2e);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 16px;
    padding: 1.2rem 1.5rem !important;
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.05), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

[data-testid="metric-container"]:hover {
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.15);
    transform: translateY(-2px);
}

[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #7b2ff7, #ff006e);
}

[data-testid="stMetricLabel"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    color: #888 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    color: #00d4ff !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #12121a 100%) !important;
    border-right: 1px solid rgba(0, 212, 255, 0.1) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #00d4ff !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 3px !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    color: #aaa !important;
    transition: color 0.2s !important;
}

[data-testid="stRadio"] label:hover {
    color: #00d4ff !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #00d4ff, #7b2ff7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0, 212, 255, 0.5) !important;
}

/* ── Download Button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1px solid rgba(0, 212, 255, 0.4) !important;
    color: #00d4ff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(0, 212, 255, 0.1) !important;
    border-color: #00d4ff !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #12121a !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Text Input ── */
[data-testid="stTextInput"] > div > div > input {
    background: #12121a !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

[data-testid="stTextInput"] > div > div > input:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
}

/* ── Alert boxes ── */
.stSuccess {
    background: rgba(0, 255, 120, 0.05) !important;
    border: 1px solid rgba(0, 255, 120, 0.3) !important;
    border-radius: 12px !important;
    border-left: 3px solid #00ff78 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}

.stError {
    background: rgba(255, 0, 110, 0.05) !important;
    border: 1px solid rgba(255, 0, 110, 0.3) !important;
    border-radius: 12px !important;
    border-left: 3px solid #ff006e !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}

.stInfo {
    background: rgba(0, 212, 255, 0.05) !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    border-radius: 12px !important;
    border-left: 3px solid #00d4ff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}

.stWarning {
    background: rgba(255, 180, 0, 0.05) !important;
    border: 1px solid rgba(255, 180, 0, 0.3) !important;
    border-radius: 12px !important;
    border-left: 3px solid #ffb400 !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.3), transparent) !important;
    margin: 2rem 0 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #12121a !important;
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 12px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(0, 212, 255, 0.15) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #00d4ff !important;
}

/* ── Caption / small text ── */
[data-testid="stCaptionContainer"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #555 !important;
    letter-spacing: 1px !important;
}

/* ── Plotly charts background ── */
.js-plotly-plot {
    border-radius: 16px !important;
    border: 1px solid rgba(0, 212, 255, 0.1) !important;
    overflow: hidden !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #00d4ff44; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }

/* ── Page load animation ── */
.main .block-container {
    animation: fadeInUp 0.6s ease forwards;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 50%, #0a1a2e 100%);
    border: 1px solid rgba(0, 212, 255, 0.15);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(0,212,255,0.05) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(123,47,247,0.05) 0%, transparent 50%);
    pointer-events: none;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #00d4ff 0%, #7b2ff7 50%, #ff006e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #666;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
}

.hero-badge {
    display: inline-block;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: #00d4ff;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    margin-bottom: 1rem;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #00d4ff;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,212,255,0.3), transparent);
}
</style>
""", unsafe_allow_html=True)

# ── Auto Refresh ──────────────────────────────────────────────
REFRESH_INTERVAL = 600  # 10 minutes in seconds

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

time_since_refresh = time.time() - st.session_state.last_refresh
time_until_next = int(REFRESH_INTERVAL - time_since_refresh)

if time_since_refresh > REFRESH_INTERVAL:
    st.cache_data.clear()
    st.session_state.last_refresh = time.time()
    st.rerun()

# ── Title ─────────────────────────────────────────────────────
# ── Hero Banner ───────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">⚡ Live Intelligence</div>
    <p class="hero-title">📰 NewsPulse</p>
    <p class="hero-subtitle">AI-Powered News Sentiment Intelligence · VADER &amp; Groq</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.header("⚙️ Controls")

mode = st.sidebar.radio(
    "Select Mode",
    ["All Categories", "Search by Keyword", "Compare Two Keywords", "Sentiment Over Time"]
)

country = st.sidebar.selectbox(
    "Country",
    ["us", "in", "gb", "au"],
    format_func=lambda x: {"us": "🇺🇸 USA", "in": "🇮🇳 India", "gb": "🇬🇧 UK", "au": "🇦🇺 Australia"}[x]
)

# ── Data Loading ──────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_all_data(country):
    df = fetch_all_categories(country=country)
    return analyze_dataframe(df)

@st.cache_data(ttl=600)
def load_india_data():
    df = fetch_india_news()
    return analyze_dataframe(df)

@st.cache_data(ttl=600)
def load_keyword_data(keyword):
    df = fetch_by_keyword(keyword)
    return analyze_dataframe(df)

@st.cache_data(ttl=600)
def load_two_keywords(k1, k2):
    df1, df2 = fetch_two_keywords(k1, k2)
    return analyze_dataframe(df1), analyze_dataframe(df2)


# ══════════════════════════════════════════════════════════════
# MODE 1 — ALL CATEGORIES
# ══════════════════════════════════════════════════════════════
if mode == "All Categories":
    with st.spinner("Fetching latest headlines..."):
      if country == "in":
        df = load_india_data()
      else:
        df = load_all_data(country)

    if df.empty:
        st.error("No data fetched. Check your API key or internet connection.")
        st.stop()

    # Save to DB for trend tracking
    save_daily_sentiment(df)

    # Metrics
    stats = get_summary_stats(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📄 Total Articles", stats["total"])
    col2.metric("😊 Positive", f"{stats['positive']} ({stats['positive_pct']}%)")
    col3.metric("😠 Negative", f"{stats['negative']} ({stats['negative_pct']}%)")
    col4.metric("😐 Neutral", f"{stats['neutral']} ({stats['neutral_pct']}%)")
    st.divider()

    # Charts Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(sentiment_pie_chart(df), use_container_width=True)
    with col2:
        st.plotly_chart(compound_score_histogram(df), use_container_width=True)

    # Charts Row 2
    col1, col2 = st.columns(2)
    with col1:
        grouped = sentiment_by_category(df)
        st.plotly_chart(sentiment_bar_by_category(grouped), use_container_width=True)
    with col2:
        avg_df = average_sentiment_by_category(df)
        st.plotly_chart(avg_sentiment_bar(avg_df), use_container_width=True)

    # WordCloud
    st.subheader("☁️ Trending Words in Headlines")
    st.pyplot(generate_wordcloud(df))

    # Top Sources
    st.subheader("📡 Top News Sources")
    source_df = top_sources(df)
    st.plotly_chart(source_bar_chart(source_df), use_container_width=True)

    # Most Positive & Negative
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🟢 Most Positive Headlines")
        pos_df = most_positive_headlines(df)
        for _, row in pos_df.iterrows():
            st.success(f"**{row['title']}** — *{row['source']}* (Score: {row['compound']})")

    with col2:
        st.subheader("🔴 Most Negative Headlines")
        neg_df = most_negative_headlines(df)
        for _, row in neg_df.iterrows():
            st.error(f"**{row['title']}** — *{row['source']}* (Score: {row['compound']})")

    # AI Summarizer
    st.divider()
    st.subheader("🤖 AI Headline Summarizer")
    st.markdown("Pick any headline and get an AI-powered explanation of why it's positive or negative.")

    headline_options = df["title"].tolist()
    selected_headline = st.selectbox("Choose a headline", headline_options)

    if st.button("✨ Summarize with AI"):
        selected_row = df[df["title"] == selected_headline].iloc[0]
        with st.spinner("Analyzing with AI..."):
            summary = summarize_headline(
                selected_row["title"],
                selected_row["sentiment"],
                selected_row["compound"]
            )
        sentiment = selected_row["sentiment"]
        if sentiment == "Positive":
            st.success(f"**Sentiment: {sentiment}** (Score: {selected_row['compound']})\n\n{summary}")
        elif sentiment == "Negative":
            st.error(f"**Sentiment: {sentiment}** (Score: {selected_row['compound']})\n\n{summary}")
        else:
            st.info(f"**Sentiment: {sentiment}** (Score: {selected_row['compound']})\n\n{summary}")

    # Download Button
    st.divider()
    st.download_button(
        label="📥 Download Full Report as CSV",
        data=df[["title", "source", "category", "sentiment", "compound", "publishedAt"]].to_csv(index=False),
        file_name="sentiment_report.csv",
        mime="text/csv"
    )

    # Raw Data
    with st.expander("📊 View Raw Data Table"):
        st.dataframe(
            df[["title", "source", "category", "sentiment", "compound", "publishedAt"]].sort_values("compound"),
            use_container_width=True
        )


# ══════════════════════════════════════════════════════════════
# MODE 2 — SEARCH BY KEYWORD
# ══════════════════════════════════════════════════════════════
elif mode == "Search by Keyword":
    keyword = st.sidebar.text_input("Enter keyword", placeholder="e.g. AI, cricket, budget")
    search_btn = st.sidebar.button("🔍 Search")

    if search_btn and keyword:
        with st.spinner(f"Searching for '{keyword}'..."):
            df = load_keyword_data(keyword)

        if df.empty:
            st.warning(f"No results found for '{keyword}'.")
            st.stop()

        st.subheader(f"Results for: **{keyword}**")
        stats = get_summary_stats(df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📄 Total Articles", stats["total"])
        col2.metric("😊 Positive", f"{stats['positive']} ({stats['positive_pct']}%)")
        col3.metric("😠 Negative", f"{stats['negative']} ({stats['negative_pct']}%)")
        col4.metric("😐 Neutral", f"{stats['neutral']} ({stats['neutral_pct']}%)")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(sentiment_pie_chart(df), use_container_width=True)
        with col2:
            st.plotly_chart(compound_score_histogram(df), use_container_width=True)

        st.pyplot(generate_wordcloud(df))

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🟢 Most Positive")
            for _, row in most_positive_headlines(df).iterrows():
                st.success(f"**{row['title']}** (Score: {row['compound']})")
        with col2:
            st.subheader("🔴 Most Negative")
            for _, row in most_negative_headlines(df).iterrows():
                st.error(f"**{row['title']}** (Score: {row['compound']})")

        # AI Summarizer
        st.divider()
        st.subheader("🤖 AI Headline Summarizer")
        selected = st.selectbox("Choose a headline", df["title"].tolist())
        if st.button("✨ Summarize with AI"):
            row = df[df["title"] == selected].iloc[0]
            with st.spinner("Analyzing..."):
                summary = summarize_headline(row["title"], row["sentiment"], row["compound"])
            st.info(f"**{row['sentiment']}** (Score: {row['compound']})\n\n{summary}")

    else:
        st.info("Enter a keyword in the sidebar and click Search.")


# ══════════════════════════════════════════════════════════════
# MODE 3 — COMPARE TWO KEYWORDS
# ══════════════════════════════════════════════════════════════
elif mode == "Compare Two Keywords":
    st.subheader("⚔️ Keyword Sentiment Battle")
    st.markdown("Compare how the media covers two different topics.")

    col1, col2 = st.columns(2)
    with col1:
        keyword1 = st.text_input("Keyword 1", placeholder="e.g. AI")
    with col2:
        keyword2 = st.text_input("Keyword 2", placeholder="e.g. Crypto")

    if st.button("⚔️ Compare Now") and keyword1 and keyword2:
        with st.spinner(f"Comparing '{keyword1}' vs '{keyword2}'..."):
            df1, df2 = load_two_keywords(keyword1, keyword2)

        if df1.empty or df2.empty:
            st.warning("Not enough data for one or both keywords. Try different ones.")
            st.stop()

        # Metrics side by side
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🔵 {keyword1}")
            s1 = get_summary_stats(df1)
            st.metric("Articles", s1["total"])
            st.metric("Avg Score", s1["avg_compound"])
            st.metric("😊 Positive", f"{s1['positive_pct']}%")
            st.metric("😠 Negative", f"{s1['negative_pct']}%")

        with col2:
            st.markdown(f"### 🟠 {keyword2}")
            s2 = get_summary_stats(df2)
            st.metric("Articles", s2["total"])
            st.metric("Avg Score", s2["avg_compound"])
            st.metric("😊 Positive", f"{s2['positive_pct']}%")
            st.metric("😠 Negative", f"{s2['negative_pct']}%")

        st.divider()

        # Comparison Charts
        st.plotly_chart(keyword_comparison_chart(df1, df2, keyword1, keyword2), use_container_width=True)
        st.plotly_chart(keyword_avg_score_chart(df1, df2, keyword1, keyword2), use_container_width=True)

        # Winner Banner
        st.divider()
        avg1 = df1["compound"].mean()
        avg2 = df2["compound"].mean()
        winner = keyword1 if avg1 > avg2 else keyword2
        st.success(f"🏆 **{winner}** has more positive media coverage overall!")

    else:
        st.info("Enter two keywords above and click Compare.")


# ══════════════════════════════════════════════════════════════
# MODE 4 — SENTIMENT OVER TIME
# ══════════════════════════════════════════════════════════════
elif mode == "Sentiment Over Time":
    st.subheader("📈 Sentiment Trend Over Time")
    st.markdown("Tracks how the mood of news changes day by day across categories.")

    history_df = load_history()

    if history_df.empty:
        st.info("No historical data yet. Run the app in **All Categories** mode today and come back tomorrow to see trends!")
    else:
        fig = sentiment_over_time_chart(history_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("📊 Historical Data Table")
        st.dataframe(history_df, use_container_width=True)