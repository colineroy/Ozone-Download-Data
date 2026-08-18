"""
Ozonesonde (ECC) -- WOUDC API download for Sodankyla
=====================================================
Downloads the homogenized WOUDC extCSV ozonesonde archive for Sodankyla
(WOUDC station_id 262) via the public WOUDC API -- no login required.

API docs: https://api.woudc.org/openapi
Python client alternative: https://github.com/woudc/pywoudc
"""

import time
from pathlib import Path

import requests

STATION_ID = 262  # Sodankyla
API_BASE = "https://api.woudc.org/collections/ozonesonde/items"
OUT_DIR = Path(__file__).parent / "sondes_data" / "woudc"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_SIZE = 100


def list_records():
    """Page through the ozonesonde collection for this station, yielding
    each record's public file URL."""
    offset = 0
    total = None
    while total is None or offset < total:
        params = {"station_id": STATION_ID, "limit": PAGE_SIZE, "offset": offset, "f": "json"}
        r = requests.get(API_BASE, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        total = data.get("numberMatched", 0)
        features = data.get("features", [])
        if not features:
            break
        for feat in features:
            url = feat["properties"].get("url")
            if url:
                yield url
        offset += len(features)


def download(url: str) -> str:
    fname = url.split("/")[-1]
    out_path = OUT_DIR / fname
    if out_path.exists():
        return "skipped"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    out_path.write_bytes(r.content)
    return "downloaded"


def main():
    print("=== Ozonesonde WOUDC API download -- Sodankyla (station 262) ===\n")
    stats = {"downloaded": 0, "skipped": 0, "failed": 0}
    urls = list(list_records())
    print(f"Found {len(urls)} records\n")
    for i, url in enumerate(urls, 1):
        try:
            status = download(url)
            stats[status] += 1
        except requests.RequestException as e:
            stats["failed"] += 1
            print(f"  [!] {url}: {e}")
        if i % 50 == 0 or i == len(urls):
            print(f"  [{i}/{len(urls)}] {stats}")
        time.sleep(0.05)  # light rate-limiting courtesy to the WOUDC server

    print(f"\nDone. {stats}")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    main()
