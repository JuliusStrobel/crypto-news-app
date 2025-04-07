import zipfile
import os

# Ordnerstruktur vorbereiten
project_dir = "crypto-news-app"
templates_dir = os.path.join(project_dir, "templates")
os.makedirs(templates_dir, exist_ok=True)

# main.py
main_py = """from flask import Flask, jsonify, render_template
import requests
from transformers import pipeline

app = Flask(__name__)
sentiment_analyzer = pipeline("sentiment-analysis")

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
"""

# index.html
index_html = """<!DOCTYPE html>
<html>
<head>
  <title>Crypto News Checker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; padding: 1rem; }
    .card { border: 1px solid #ccc; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }
    .POSITIVE { background-color: #d4edda; }
    .NEGATIVE { background-color: #f8d7da; }
    .NEUTRAL { background-color: #fff3cd; }
  </style>
</head>
<body>
  <h1>📈 Crypto News Checker</h1>
  <div id="news"></div>

  <script>
    fetch("/news")
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById("news");
        data.forEach(item => {
          const div = document.createElement("div");
          div.className = `card ${item.sentiment.toUpperCase()}`;
          div.innerHTML = `
            <h3>${item.title}</h3>
            <p><strong>Sentiment:</strong> ${item.sentiment}</p>
            <p><strong>Trump/Zölle:</strong> ${item.trump_related ? "✅ Ja" : "❌ Nein"}</p>
            <a href="${item.url}" target="_blank">Zur Quelle</a>
          `;
          container.appendChild(div);
        });
      });
  </script>
</body>
</html>
"""

# requirements.txt
requirements_txt = """Flask
requests
transformers
torch
"""

# Procfile
procfile = "web: python main.py"

# Dateien schreiben
with open(os.path.join(project_dir, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_py)

with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

with open(os.path.join(project_dir, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write(requirements_txt)

with open(os.path.join(project_dir, "Procfile"), "w", encoding="utf-8") as f:
    f.write(procfile)

# ZIP-Datei erstellen
zip_path = "crypto-news-app.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, project_dir)
            zipf.write(full_path, arcname=rel_path)

print("✅ ZIP-Datei erstellt:", zip_path)
