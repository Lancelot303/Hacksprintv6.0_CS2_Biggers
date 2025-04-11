import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import os

def extract_website_metadata(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        domain = urlparse(url).netloc
        title = soup.title.string.strip() if soup.title else "N/A"

        description = "N/A"
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and 'content' in desc_tag.attrs:
            description = desc_tag["content"].strip()

        metadata = {
            "url": url,
            "domain": domain,
            "title": title,
            "description": description
        }

        return metadata

    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching {url}: {e}")
        return None

def save_all_to_json(metadata_list, filename="website_metadata.json"):
    with open(filename, "w") as f:
        json.dump(metadata_list, f, indent=4, ensure_ascii=False)

def read_urls_from_file(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    input_file = "input_urls.txt"
    urls = read_urls_from_file(input_file)

    all_metadata = []

    for url in urls:
        print(f"[*] Processing: {url}")
        metadata = extract_website_metadata(url)
        if metadata:
            all_metadata.append(metadata)

    if all_metadata:
        save_all_to_json(all_metadata)
        print(f"[+] Extracted metadata for {len(all_metadata)} URLs saved to website_metadata.json")
    else:
        print("[!] No metadata extracted.")
