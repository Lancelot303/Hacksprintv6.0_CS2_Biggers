#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import threading
import json
from pathlib import Path
import subprocess
from bs4 import BeautifulSoup

app = Flask(__name__)

# Output file (JSON Lines format: 1 JSON per line)
OUTPUT_FILE = Path("scraper_output.json")
FRIEND_URL = "http://192.168.197.77:5005/predict"
file_lock = threading.Lock()


def fetch_metadata(domain):
    for scheme in ["https://", "http://"]:
        url = f"{scheme}{domain}"
        try:
            result = subprocess.run(
                ["wget", "-q", "-O", "-", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            html = result.stdout.decode("utf-8", errors="ignore")
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "No Title"
            )
            desc_tag = soup.find("meta", attrs={"name": "description"})
            description = (
                desc_tag["content"].strip()
                if desc_tag and "content" in desc_tag.attrs
                else "No Description"
            )
            return title, description

        except Exception as e:
            continue

    return "Fetch Failed", "Could not retrieve metadata"


def process_domain(domain):
    title, description = fetch_metadata(domain)
    result = {"domain": domain, "title": title, "description": description}
    if title not in ["Fetch Failed", "No Title"] and title.strip():
        try:
            requests.post(FRIEND_URL, json=result, timeout=2)
            print("Done")
        except:
            pass
        with file_lock:
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps(result) + "\n")


@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    domain = data.get("url")
    if not domain:
        return jsonify({"error": "No URL provided"}), 400

    threading.Thread(target=process_domain, args=(domain,), daemon=True).start()
    return jsonify({"queued": domain}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
