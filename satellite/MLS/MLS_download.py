"""
MLS (Aura) — Download ozone profile data for Sodankyla FMI
===========================================================
Products:
  - ML2O3   : Ozone vertical profile (Level 2, v5.1)
  - ML2HNO3 : Nitric acid profile    (Level 2, v5.1)  [optional]

Data source: NASA Earthdata (https://disc.gsfc.nasa.gov/)
Access: Requires NASA Earthdata Login account
  Register at: https://urs.earthdata.nasa.gov/

Note on co-location:
  MLS is a limb sounder — its horizontal footprint is large (~200 km along-track).
  Standard NDACC co-location radius for MLS vs sonde is 500 km (not 0.5° like OMI).
  The bounding box used here is therefore wider than for OMI/TROPOMI.

Dependencies:
    pip install requests python-dotenv
"""

import os
from dotenv import load_dotenv
load_dotenv()

import requests
from pathlib import Path
from datetime import datetime, timedelta

# ── SITE ─────────────────────────────────────────────────────────────────
LAT_SITE = 67.3668
LON_SITE = 26.6297

# MLS limb footprint is ~200 km along-track → use 5° bounding box (~500 km)
DELTA = 5.0

# ── DATE RANGE ───────────────────────────────────────────────────────────
DATE_START = "2026-04-15"
DATE_END   = "2026-04-30"

# ── CREDENTIALS (from .env) ───────────────────────────────────────────────
# Same .env as your OMI script:
#   EARTHDATA_USER=your_username
#   EARTHDATA_PASS=your_password
#   EARTHDATA_TOKEN=your_bearer_token   ← preferred, avoids Basic Auth issues
EARTHDATA_USER  = os.getenv("EARTHDATA_USER",  "your_username")
EARTHDATA_PASS  = os.getenv("EARTHDATA_PASS",  "your_password")
EARTHDATA_TOKEN = os.getenv("EARTHDATA_TOKEN", "")

# ── PRODUCTS ─────────────────────────────────────────────────────────────
# CMR concept IDs — MLS v5.1 on GES DISC
# Find current IDs at: https://cmr.earthdata.nasa.gov/search/
#   collections.json?short_name=ML2O3&version=005
PRODUCTS = {
    "ML2O3": {
        "concept_id":  "C1729925806-GES_DISC",   # MLS/Aura L2 O3 v5.1
        "dir":         Path("./satellite/MLS/mls_data/ozone"),
        "description": "MLS Ozone Vertical Profile (L2 v5.1)",
        "ext":         ".he5",
    },
    "ML2HNO3": {
        "concept_id":  "C1729925263-GES_DISC",   # MLS/Aura L2 HNO3 v5.1
        "dir":         Path("./satellite/MLS/mls_data/hno3"),
        "description": "MLS Nitric Acid Profile (L2 v5.1) [optional]",
        "ext":         ".he5",
    },
}

# Set to False to skip HNO3 download
DOWNLOAD_HNO3 = False

for key, info in PRODUCTS.items():
    info["dir"].mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# CMR SEARCH
# ═══════════════════════════════════════════════════════════════════════════

def search_cmr(concept_id: str,
               start: str,
               end: str,
               lat: float,
               lon: float,
               delta: float) -> list:
    """
    Search NASA CMR for MLS granules overlapping the site bounding box.

    MLS orbit is sun-synchronous polar, so Aura passes near Sodankyla
    (~67°N) roughly 14 times per day. Each daily granule file covers
    one full orbit day (all passes), so typically 1 file per day.
    """
    url = "https://cmr.earthdata.nasa.gov/search/granules.json"

    params = {
        "collection_concept_id": concept_id,
        "temporal": f"{start}T00:00:00Z,{end}T23:59:59Z",
        "bounding_box": f"{lon-delta},{lat-delta},{lon+delta},{lat+delta}",
        "page_size": 500,
        "sort_key": "start_date",
    }

    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    granules = resp.json().get("feed", {}).get("entry", [])
    print(f"  -> {len(granules)} granule(s) found")
    return granules


# ═══════════════════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════

def _get_headers() -> dict:
    """Return auth headers — Bearer token preferred over Basic Auth."""
    if EARTHDATA_TOKEN:
        return {"Authorization": f"Bearer {EARTHDATA_TOKEN}"}
    return {}


def _get_auth():
    """Return (user, pass) tuple if no token available."""
    if not EARTHDATA_TOKEN:
        return (EARTHDATA_USER, EARTHDATA_PASS)
    return None


def download_granule(granule: dict,
                     output_dir: Path,
                     ext: str = ".he5") -> Path | None:
    """
    Download one MLS granule (HDF5 .he5 file).

    MLS files are ~40–80 MB per day (full orbit), much larger than OMI
    granules. Each file contains all species measurements for one orbit day.
    """
    # Extract download URL (data link)
    urls = [
        link["href"]
        for link in granule.get("links", [])
        if (link.get("rel") == "http://esipfed.org/ns/fedsearch/1.1/data#"
            and link["href"].endswith(ext))
    ]

    if not urls:
        # Fallback: any .he5 link
        urls = [
            link["href"]
            for link in granule.get("links", [])
            if link["href"].endswith(ext)
        ]

    if not urls:
        title = granule.get("title", "unknown")
        print(f"  [skip]  no {ext} URL for {title}")
        return None

    url      = urls[0]
    filename = url.split("/")[-1]
    out_path = output_dir / filename

    if out_path.exists():
        print(f"  [skip]  {filename}  (already exists)")
        return out_path

    print(f"  [dl]    {filename}")

    with requests.get(
        url,
        headers=_get_headers(),
        auth=_get_auth(),
        stream=True,
        timeout=300,
    ) as r:
        r.raise_for_status()
        total      = int(r.headers.get("Content-Length", 0))
        downloaded = 0

        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=131072):  # 128 KB chunks
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    mb  = downloaded / 1e6
                    tot = total / 1e6
                    print(f"\r          {pct:5.1f}%  ({mb:.1f} / {tot:.1f} MB)",
                          end="", flush=True)
        print()

    return out_path


# ═══════════════════════════════════════════════════════════════════════════
# VERIFY TOKEN
# ═══════════════════════════════════════════════════════════════════════════

def check_credentials():
    """Quick check that Earthdata credentials are configured."""
    if EARTHDATA_TOKEN:
        print("  Auth mode : Bearer token (EARTHDATA_TOKEN)")
    elif EARTHDATA_USER != "your_username":
        print(f"  Auth mode : Basic auth (user: {EARTHDATA_USER})")
        print("  Tip: Bearer token is more reliable.")
        print("  Get one at: https://urs.earthdata.nasa.gov/profile")
    else:
        print("  [!] No credentials found in .env")
        print("      Set EARTHDATA_TOKEN or EARTHDATA_USER + EARTHDATA_PASS")
        print("      Register at: https://urs.earthdata.nasa.gov/")
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 55)
    print("  MLS (Aura) Download — Sodankylä FMI")
    print("=" * 55)
    print(f"\n  Period : {DATE_START}  ->  {DATE_END}")
    print(f"  Site   : {LAT_SITE}°N  {LON_SITE}°E  ±{DELTA}°")
    print(f"  (~{DELTA*111:.0f} km radius — standard MLS co-location)\n")

    if not check_credentials():
        return

    for product, info in PRODUCTS.items():

        # Skip optional products
        if product == "ML2HNO3" and not DOWNLOAD_HNO3:
            print(f"\n--- {info['description']} --- [skipped, DOWNLOAD_HNO3=False]")
            continue

        print(f"\n--- {info['description']} ({product}) ---")

        granules = search_cmr(
            concept_id=info["concept_id"],
            start=DATE_START,
            end=DATE_END,
            lat=LAT_SITE,
            lon=LON_SITE,
            delta=DELTA,
        )

        if not granules:
            print("  No granules found. Check concept ID or date range.")
            continue

        downloaded = 0
        skipped    = 0

        for g in granules:
            path = download_granule(g, info["dir"], ext=info["ext"])
            if path:
                if "skip" not in str(path):
                    downloaded += 1
                else:
                    skipped += 1

        print(f"\n  Summary : {downloaded} downloaded, {skipped} already cached")
        print(f"  Output  : {info['dir'].resolve()}")

    print("\n" + "=" * 55)
    print("  Done.")
    print("=" * 55)

    print("""
File naming: MLS-Aura_L2GP-O3_v05-01-c01_<year>d<doy>.he5
  e.g.       MLS-Aura_L2GP-O3_v05-01-c01_2026d105.he5   (April 15 = day 105)

See satellite/MLS/README.md for the HDF-EOS5 field layout (O3 swath,
quality flags) needed to read these files.
""")


if __name__ == "__main__":
    main()