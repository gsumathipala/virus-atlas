"""User corrections to pathogenicity tiers, persisted to disk.

The curated layers are incomplete by construction, so the interface has to let
a reader fix a tier they know to be wrong. Corrections live in a single JSON
file next to the dataset rather than in the built atlas, so rebuilding the
taxonomy from a new ICTV release never discards them.

Each entry records what was changed, to what, why, and when, keyed by the ICTV
species binomial -- not by node id, so a correction survives a rebuild that
reshuffles the tree.

    {
      "Morbillivirus hominis": {
        "tier": "established",
        "note": "Measles. Obviously.",
        "by": "local",
        "at": "2026-10-11T12:00:00Z",
        "was": "no-evidence"
      }
    }

This is a single-user local store: it takes a file lock for the read-modify-
write cycle but makes no attempt at multi-writer conflict resolution.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from threading import Lock

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "overrides.json")

_lock = Lock()


def load():
    """Every stored correction, or {} when the file is absent or unreadable."""
    try:
        with open(PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write(data):
    """Replace the file atomically, so a crash cannot leave it half-written."""
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PATH), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def set_tier(species, tier, note="", was=None, by="local"):
    """Record a correction and return the stored entry."""
    entry = {
        "tier": tier,
        "note": (note or "").strip(),
        "by": by,
        "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat()
              .replace("+00:00", "Z"),
    }
    if was:
        entry["was"] = was
    with _lock:
        data = load()
        data[species] = entry
        _write(data)
    return entry


def clear(species):
    """Drop a correction. Returns the entry that was removed, or None."""
    with _lock:
        data = load()
        gone = data.pop(species, None)
        if gone is not None:
            _write(data)
    return gone


def count():
    return len(load())
