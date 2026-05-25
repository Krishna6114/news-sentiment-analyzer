# summarizer.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_headline(title, sentiment_label, compound_score):
    """
    Takes a headline + its sentiment and returns an AI explanation.
    """
    prompt = f"""
You are a news analyst. Analyze this headline briefly:

Headline: "{title}"
Sentiment detected: {sentiment_label} (score: {compound_score})

Give me:
1. A 2-sentence plain English summary of what this headline is about
2. One sentence explaining WHY it is {sentiment_label}
3. One sentence on potential impact

Keep total response under 100 words. Be direct and clear.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Summary unavailable: {str(e)}"