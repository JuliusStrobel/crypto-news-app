from flask import Flask, jsonify, render_template
import requests
from transformers import pipeline

app = Flask(__name__)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    device=-1  # Nur CPU – vermeidet RAM-Probleme
)




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

        sentiment = sentiment_analyzer(text[:512])[0]
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
