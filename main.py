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
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=20&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    data = response.json()

    results = []
    for article in data.get("articles", []):
        title = article["title"]
        description = article.get("description", "")
        text = f"{title}. {description}"

        sentiment = {"label": analyze_sentiment(text[:512])}

        is_trump_related = any(k in text.lower() for k in trump_keywords)

        results.append({
            "title": title,
            "sentiment": sentiment["label"],
            "trump_related": is_trump_related,
            "url": article["url"]
        })

    return results

@app.route("/news")
def news():
    return jsonify(get_analyzed_news())

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
