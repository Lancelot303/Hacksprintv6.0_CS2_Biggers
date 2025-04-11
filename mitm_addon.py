# mitm_addon.py
import json
from pathlib import Path
from mitmproxy import http

CACHE_FILE = Path("domain_cache.json")

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def request(flow: http.HTTPFlow):
    host = flow.request.pretty_host.lower()

    # Load the latest version of the cache on every request
    domain_cache = load_cache()

    if host not in domain_cache:
        domain_cache[host] = {"url": host, "access": "allowed"}
        save_cache(domain_cache)

    if domain_cache[host]["access"] == "blocked":
        flow.response = http.Response.make(
            403,
            b"<html><body><h1>Blocked by Admin</h1></body></html>",
            {"Content-Type": "text/html"}
        )
