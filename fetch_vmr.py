"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Download the current ICTV Virus Metadata Resource spreadsheet.

The VMR filename encodes the Master Species List release and date, so this
scrapes the download page rather than hard-coding a URL that goes stale with
each ICTV ratification.

Usage:  python fetch_vmr.py
"""

import datetime
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

PAGE = "https://ictv.global/vmr"
BASE = "https://ictv.global"
DEST = Path(__file__).resolve().parent / "data" / "raw" / "vmr.xlsx"
# The download is saved under a fixed name so the rest of the build does not
# have to guess at it, which threw away the one part of the upstream filename
# that matters -- the release. This records it beside the file, so a page can
# say which Master Species List it is showing and when it was taken, instead
# of the uninformative "vmr.xlsx".
STAMP = DEST.with_suffix(".source.json")
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


def stamp(url, blob):
    """Record which release this is, beside the file it describes."""
    release = url.rsplit("/", 1)[-1]
    msl = re.search(r"MSL(\d+)(?:\.v(\d+))?", release)
    date = re.search(r"(20\d{2})(\d{2})(\d{2})", release)
    STAMP.write_text(json.dumps({
        "release": release,
        "url": url,
        "msl": f"MSL{msl.group(1)}" + (f".v{msl.group(2)}" if msl and msl.group(2) else "")
               if msl else None,
        "released": "-".join(date.groups()) if date else None,
        "fetched": datetime.date.today().isoformat(),
        "bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
    }, indent=1) + "\n", encoding="utf-8")
    return release


def main():
    url = latest_url()
    print(f"downloading {url}")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    DEST.write_bytes(blob)
    release = stamp(url, blob)
    print(f"wrote {DEST} ({len(blob) / 1e6:.1f} MB) -- {release}")
    print("next:  python -m atlas.build")


if __name__ == "__main__":
    sys.exit(main())
