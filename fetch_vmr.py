"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Download the current ICTV Virus Metadata Resource spreadsheet.

The VMR filename encodes the Master Species List release and date, so this
scrapes the download page rather than hard-coding a URL that goes stale with
each ICTV ratification.

Usage:  python fetch_vmr.py
"""

import re
import sys
import urllib.request
from pathlib import Path

PAGE = "https://ictv.global/vmr"
BASE = "https://ictv.global"
DEST = Path(__file__).resolve().parent / "data" / "raw" / "vmr.xlsx"
UA = {"User-Agent": "virus-atlas/1.0 (educational taxonomy browser)"}


def latest_url():
    req = urllib.request.Request(PAGE, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        html = r.read().decode("utf-8", "replace")
    links = re.findall(r'href="(/sites/default/files/VMR/[^"]*\.xlsx)"', html)
    if not links:
        raise SystemExit(f"No VMR .xlsx link found on {PAGE} — check the page layout.")

    def sort_key(href):
        # VMR_MSL41.v1.20260729.xlsx -> (41, 1, 20260729)
        msl = re.search(r"MSL(\d+)", href)
        ver = re.search(r"\.v(\d+)", href)
        date = re.search(r"(20\d{6})", href)
        return (
            int(msl.group(1)) if msl else 0,
            int(ver.group(1)) if ver else 0,
            int(date.group(1)) if date else 0,
        )

    return BASE + max(links, key=sort_key)


def main():
    url = latest_url()
    print(f"downloading {url}")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r, DEST.open("wb") as fh:
        fh.write(r.read())
    print(f"wrote {DEST} ({DEST.stat().st_size / 1e6:.1f} MB)")
    print("next:  python -m atlas.build")


if __name__ == "__main__":
    sys.exit(main())
