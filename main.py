from flask import Flask, jsonify, render_template
import requests
from textblob import TextBlob

import os
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))


def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        return "POSITIVE"
    elif polarity < -0.1:
        return "NEGATIVE"
    else:
        return "NEUTRAL"




NEWSAPI_KEY = "401a014dce5c429091d4bc9022e7d6dd"

trump_keywords = ["trump", "zoll", "tariff", "trade war", "import tax"]

def get_analyzed_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=15&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    data = response.json()

    results = []
    trump_articles = []

    pos_count, neg_count = 0, 0

    for article in data.get("articles", []):
        title = article["title"]
        description = article.get("description", "")
        text = f"{title}. {description}"

        sentiment_label = analyze_sentiment(text)
        if sentiment_label == "POSITIVE":
            pos_count += 1
        elif sentiment_label == "NEGATIVE":
            neg_count += 1

        is_trump_related = any(k in text.lower() for k in trump_keywords)
        if is_trump_related:
            trump_articles.append(f"{title} - {description}")

        results.append({
            "title": title,
            "sentiment": sentiment_label,
            "trump_related": is_trump_related,
            "url": article["url"]
        })

    # Markttrend basierend auf Mehrheit
    if pos_count > neg_count:
        market_trend = "📈 Markt tendiert nach oben"
    elif neg_count > pos_count:
        market_trend = "📉 Markt tendiert nach unten"
    else:
        market_trend = "➖ Markt neutral"

    return {
        "articles": results,
        "market_trend": market_trend,
        "trump_info": trump_articles
    }


@app.route("/news")
def news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=15&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)
        data = response.json()

        # Prüfe ob API erfolgreich war
        if data.get("status") != "ok":
            return jsonify({
                "market_trend": "❌ Fehler beim Abrufen der News",
                "articles": [],
                "trump_info": [f"Fehler: {data.get('code')} – {data.get('message')}"]
            })

        # Weiterverarbeitung
        results = []
        trump_articles = []
        pos_count, neg_count = 0, 0

        for article in data.get("articles", []):
            title = article.get("title", "")
            description = article.get("description", "")
            text = f"{title}. {description}"

            sentiment_label = analyze_sentiment(text)
            if sentiment_label == "POSITIVE":
                pos_count += 1
            elif sentiment_label == "NEGATIVE":
                neg_count += 1

            is_trump_related = any(k in text.lower() for k in trump_keywords)
            if is_trump_related:
                trump_articles.append(f"{title} – {description}")

            results.append({
                "title": title,
                "sentiment": sentiment_label,
                "trump_related": is_trump_related,
                "url": article.get("url", "#")
            })

        market_trend = (
            "📈 Markt tendiert nach oben" if pos_count > neg_count else
            "📉 Markt tendiert nach unten" if neg_count > pos_count else
            "➖ Markt neutral"
        )

        return jsonify({
            "market_trend": market_trend,
            "articles": results,
            "trump_info": trump_articles
        })

    except Exception as e:
        # Fehlerausgabe als JSON (wird im Frontend angezeigt)
        return jsonify({
            "market_trend": "❌ Fehler im Server",
            "articles": [],
            "trump_info": [str(e)]
        }), 500


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
