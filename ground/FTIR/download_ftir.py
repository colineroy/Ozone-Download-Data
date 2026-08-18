"""
FTIR -- Direct download for Sodankyla (BIRA-IASB / aeronomie.be)
=================================================================
Downloads the NDACC GEOMS HDF4 file for the Sodankyla FTIR instrument
directly from the BIRA-IASB data portal -- no login required.

Dataset page: https://data.aeronomie.be/dataset/ftir-ozone-o3-groundbased-remote-sensing-at-sodankyla-from-hr125-fts-fmi-instrument
"""

from pathlib import Path

import requests

FILE_URL = (
    "https://data.aeronomie.be/dataset/ec3fa252-5986-4dca-8d66-14c89403a22d/"
    "resource/89258459-9cdf-4931-8aa5-89b002a80314/download/"
    "groundbased_ftir.o3_fmi001_sodankyla_20120329t070932z_20210926t110630z_001.hdf"
)
OUT_DIR = Path(__file__).parent
OUT_PATH = OUT_DIR / FILE_URL.split("/")[-1]


def main():
    print("=== FTIR download -- Sodankyla (BIRA-IASB) ===\n")
    if OUT_PATH.exists():
        print(f"  [skip] {OUT_PATH.name} already present ({OUT_PATH.stat().st_size / 1e6:.1f} MB)")
        return

    print(f"  [dl] {FILE_URL}")
    with requests.get(FILE_URL, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        with open(OUT_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1048576):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    print(f"\r        {downloaded/total*100:5.1f}%  "
                          f"({downloaded/1e6:.1f} / {total/1e6:.1f} MB)", end="")
    print(f"\n\nDone. Saved to: {OUT_PATH}")


if __name__ == "__main__":
    main()
