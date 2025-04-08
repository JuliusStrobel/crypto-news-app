from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def is_crypto_related(text):
    """Prüft, ob ein Artikel Krypto-relevante Begriffe enthält."""
    keywords = ["bitcoin", "blockchain", "ethereum", "crypto", "btc", "nft"]
    text = text.lower()
    return any(keyword in text for keyword in keywords)

@app.route("/check-news", methods=["POST"])
def check_news():
    try:
        data = request.get_json()

        if not data or "topic" not in data:
            return jsonify({"error": "Kein Thema angegeben"}), 400

        topic = data["topic"]
        url = f"https://www.tagesschau.de/suche2.html?searchText={topic}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({
                "error": "Fehler beim Abrufen der Daten",
                "status_code": response.status_code,
                "body": response.text[:500]  # nur Ausschnitt zur Sicherheit
            }), 502

        # Inhalt ist HTML, kein JSON
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Artikelüberschriften extrahieren
        results = []
        for article in soup.find_all("article"):
            headline_tag = article.find(["h2", "h3"])
            paragraph = article.find("p")
            if headline_tag and paragraph:
                headline = headline_tag.get_text(strip=True)
                summary = paragraph.get_text(strip=True)
                full_text = f"{headline} {summary}"
                crypto_related = is_crypto_related(full_text)
                results.append({
                    "headline": headline,
                    "summary": summary,
                    "crypto_related": crypto_related
                })

        if not results:
            return jsonify({
                "message": "Keine relevanten Artikel gefunden.",
                "articles": []
            })

        return jsonify({
            "topic": topic,
            "articles": results
        })

    except Exception as e:
        return jsonify({
            "error": "Serverfehler",
            "details": str(e)
        }), 500


@app.route("/", methods=["GET"])
def home():
    return "<h1>Crypto News Checker</h1><p>Die API läuft korrekt.</p>"

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

