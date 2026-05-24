#!/usr/bin/env python3
"""Lucien Studio Server — serves static files + article content proxy."""

import requests
import trafilatura
from flask import Flask, request, jsonify, send_from_directory, abort
from urllib.parse import urlparse
import os

app = Flask(__name__)
WWW_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(WWW_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve any static file from www directory."""
    safe = os.path.normpath(filename)
    if safe.startswith("..") or safe.startswith("/"):
        abort(403)
    return send_from_directory(WWW_DIR, safe)


@app.route("/api/fetch")
def fetch_article():
    """Follow Google News redirect, extract article text."""
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    # Only allow Google News RSS links
    if "news.google.com/rss/articles" not in url:
        return jsonify({"error": "Only Google News RSS links supported"}), 400

    try:
        # Follow Google News redirect to get real article URL
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        resp = session.get(url, allow_redirects=True, timeout=15)
        real_url = resp.url

        # Extract text content
        downloaded = trafilatura.fetch_url(real_url)
        if not downloaded:
            # Fallback: try fetching via session
            downloaded = resp.text

        text = trafilatura.extract(
            downloaded,
            include_links=False,
            include_images=False,
            include_tables=False,
            output_format="markdown",
            with_metadata=True,
        )

        if not text:
            # Fallback: return first 2000 chars of HTML as text
            from html.parser import HTMLParser

            class Stripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []

                def handle_data(self, data):
                    self.text.append(data.strip())

            s = Stripper()
            s.feed(resp.text)
            text = "\n".join(s.text)[:3000]

        return jsonify({
            "url": real_url,
            "text": text or "(无法提取文章内容)",
            "length": len(text) if text else 0,
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)
