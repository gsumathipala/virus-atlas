"""Virus Atlas — © 2026 Saranga Sumathipala. All rights reserved.
Proprietary. No licence granted; see LICENSE.

Near-real-time outbreak signals, mapped onto the ICTV taxonomy.

What this is
------------
Official outbreak reporting, pulled from keyless public endpoints, parsed, and
matched to the species in the atlas so a virus page can say what is happening
with that virus right now.

Sources, in order of authority:

  WHO    Disease Outbreak News. The OData feed behind who.int/emergencies/
         disease-outbreak-news. Verified, structured, global, and the closest
         thing to a reference standard for "WHO has formally reported this".

  UKHSA  the UK Health Security Agency's publications, through the documented
         and keyless gov.uk Search API. Narrower in scope than WHO -- it is a
         national agency -- but it publishes weekly surveillance and
         outbreak-monitoring reports, and it is current.

  ECDC   the weekly Communicable Disease Threats Report. The PDF is not
         parsed: what is offered is a verified link to the current week's
         report, because the ECDC endpoints that would give structured items
         do not.

Sources evaluated and deliberately NOT ingested:

  CDC        the reachable media RSS endpoints carry food-safety recalls or
             1,800 mixed items with no outbreak scoping. tools.cdc.gov
             /api/v2/resources/media/316422.rss, which looks promising, is
             the Food Safety channel.
  CIDRAP     a reputable aggregator, but its public RSS has not been updated
             since November 2022.
  FAO        EMPRES-i would be the right source for the animal side of
             zoonoses; /api/events returns the single-page-app HTML shell
             rather than data, and there is no documented open endpoint.
  WOAH       the WAHIS API rejects unauthenticated queries (HTTP 400).
  PAHO       no reachable feed for the epidemiological alerts series.
  ProMED     ISID terms restrict redistribution and the full archive is behind
             membership, so it is linked out from the interface, not ingested.
  HealthMap  the API was never formally public and the project is dormant.

What this is NOT
----------------
It is not incidence, and it is not a case count. A DON is published when WHO
decides an event warrants international attention, so the feed is a record of
*reporting activity*, heavily shaped by surveillance capacity and political
will. Absence of a signal means nobody filed a report that matched, not that
nothing is happening. Every surface that shows this data has to say so.

Matching
--------
Reports name diseases ("Ebola disease caused by Bundibugyo virus"), not ICTV
binomials, so DISEASES below maps report language to taxon ids. The patterns
are ordered most-specific first, because "Ebola disease caused by Bundibugyo
virus" must match the Bundibugyo species rather than the Ebola genus, and
"Avian Influenza A(H5N1)" must not simply match "influenza".

Caching
-------
Responses are cached to SQLite next to the atlas, with a TTL, so the app works
offline and does not hammer WHO. A failed refresh keeps serving the last good
copy and says how old it is.
"""

import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "surveillance.sqlite3"
UA = "virus-atlas/1.0 (educational; local use)"
TTL = 60 * 60 * 3          # three hours: DONs appear a few times a week
TIMEOUT = 25

WHO_URL = (
    "https://www.who.int/api/news/diseaseoutbreaknews"
    "?$orderby=PublicationDateAndTime%20desc&$top=100"   # 100 is the server cap
    "&$select=Title,PublicationDateAndTime,UrlName,Summary,DonId"
)


# ---------------------------------------------------------------------------
# Disease language -> taxonomy
# ---------------------------------------------------------------------------

# (regex, taxon kind, taxon name, human-readable disease label)
# "species" matches an ICTV binomial; "genus"/"family" match a group node.
# Order matters: the first match wins, so specifics precede generics.
DISEASES = [
    # --- filoviruses: the subtype is named in the title, so resolve it ---
    (r"bundibugyo", "species", "Orthoebolavirus bundibugyoense", "Ebola disease (Bundibugyo virus)"),
    (r"sudan virus disease|ebola.*sudan|sudan.*ebolavirus", "species", "Orthoebolavirus sudanense", "Ebola disease (Sudan virus)"),
    (r"ta[iï] forest", "species", "Orthoebolavirus taiense", "Ebola disease (Taï Forest virus)"),
    (r"ebola", "species", "Orthoebolavirus zairense", "Ebola disease (Zaire ebolavirus)"),
    (r"marburg", "species", "Orthomarburgvirus marburgense", "Marburg virus disease"),

    # --- respiratory ---
    (r"\bmers\b|middle east respiratory", "species", "Betacoronavirus cameli", "MERS"),
    (r"covid-?19|sars-?cov-?2", "species", "Betacoronavirus pandemicum", "COVID-19"),
    (r"avian influenza.*h5n1|influenza a\(h5n1\)", "species", "Alphainfluenzavirus influenzae", "Avian influenza A(H5N1)"),
    (r"avian influenza.*h5n5|influenza a\(h5n5\)", "species", "Alphainfluenzavirus influenzae", "Avian influenza A(H5N5)"),
    (r"avian influenza.*h5n6|influenza a\(h5n6\)", "species", "Alphainfluenzavirus influenzae", "Avian influenza A(H5N6)"),
    (r"avian influenza.*h9n2|influenza a\(h9n2\)", "species", "Alphainfluenzavirus influenzae", "Avian influenza A(H9N2)"),
    (r"avian influenza.*h7n9|influenza a\(h7n9\)", "species", "Alphainfluenzavirus influenzae", "Avian influenza A(H7N9)"),
    (r"avian influenza|influenza a\(h\d+n\d+\)", "species", "Alphainfluenzavirus influenzae", "Zoonotic avian influenza"),
    (r"seasonal influenza|influenza.*global", "species", "Alphainfluenzavirus influenzae", "Seasonal influenza"),
    (r"metapneumovirus", "species", "Metapneumovirus hominis", "Human metapneumovirus"),
    (r"respiratory syncytial", "species", "Orthopneumovirus hominis", "RSV"),

    # --- vaccine-preventable / childhood ---
    (r"\bmeasles\b", "species", "Morbillivirus hominis", "Measles"),
    (r"\brubella\b", "species", "Rubivirus rubellae", "Rubella"),
    (r"\bmumps\b", "species", "Orthorubulavirus parotitidis", "Mumps"),
    (r"poliovirus|poliomyelitis|\bcvdpv", "species", "Enterovirus coxsackiepol", "Poliomyelitis / cVDPV"),
    (r"hepatitis a\b", "species", "Hepatovirus ahepa", "Hepatitis A"),
    (r"hepatitis b\b", "species", "Orthohepadnavirus hominoidei", "Hepatitis B"),
    (r"hepatitis e\b", "species", "Paslahepevirus balayani", "Hepatitis E"),

    # --- poxviruses ---
    (r"\bmpox\b|monkeypox", "species", "Orthopoxvirus monkeypox", "Mpox"),
    (r"\bsmallpox\b|variola", "species", "Orthopoxvirus variola", "Smallpox"),

    # --- arboviruses ---
    (r"yellow fever", "species", "Orthoflavivirus flavi", "Yellow fever"),
    (r"\bdengue\b", "species", "Orthoflavivirus denguei", "Dengue"),
    (r"\bzika\b", "species", "Orthoflavivirus zikaense", "Zika virus disease"),
    (r"west nile", "species", "Orthoflavivirus nilense", "West Nile fever"),
    (r"japanese encephalitis", "species", "Orthoflavivirus japonicum", "Japanese encephalitis"),
    (r"tick-?borne encephalitis", "species", "Orthoflavivirus zilberi", "Tick-borne encephalitis"),
    (r"\boropouche\b", "species", "Orthobunyavirus oropoucheense", "Oropouche fever"),
    (r"\bchikungunya\b", "species", "Alphavirus chikungunya", "Chikungunya"),
    (r"rift valley", "species", "Phlebovirus riftense", "Rift Valley fever"),
    (r"crimean-?congo", "species", "Orthonairovirus haemorrhagiae", "Crimean-Congo haemorrhagic fever"),
    (r"severe fever with thrombocytopenia", "species", "Bandavirus dabieense", "SFTS"),

    # --- zoonoses ---
    (r"\bnipah\b", "species", "Henipavirus nipahense", "Nipah virus disease"),
    (r"\bhendra\b", "species", "Henipavirus hendraense", "Hendra virus disease"),
    (r"\brabies\b", "species", "Lyssavirus rabies", "Rabies"),
    (r"\blassa\b", "species", "Mammarenavirus lassaense", "Lassa fever"),
    (r"\bchapare\b", "species", "Mammarenavirus chapareense", "Chapare haemorrhagic fever"),
    (r"\blujo\b", "species", "Mammarenavirus lujoense", "Lujo haemorrhagic fever"),
    (r"jun[ií]n|argentine h[ae]emorrhagic", "species", "Mammarenavirus juninense", "Argentine haemorrhagic fever"),
    (r"\bhantavirus\b|hantavirus pulmonary|haemorrhagic fever with renal", "genus", "Orthohantavirus", "Hantavirus disease"),

    # --- enteric ---
    (r"\bnorovirus\b", "species", "Norovirus norwalkense", "Norovirus gastroenteritis"),
    (r"\brotavirus\b", "species", "Rotavirus alphagastroenteritidis", "Rotavirus gastroenteritis"),

    # --- other ---
    (r"\bhiv\b|acquired immunodeficiency", "species", "Lentivirus humimdef1", "HIV"),
    (r"enterovirus\s*d?-?68|\bev-?d68\b", "species", "Enterovirus deconjuncti", "Enterovirus D68"),
    (r"hand,? foot,? and mouth", "species", "Enterovirus alphacoxsackie", "Hand, foot and mouth disease"),
    (r"chandipura", "species", "Vesiculovirus chandipura", "Chandipura virus encephalitis"),
    (r"\bmokola\b", "species", "Lyssavirus mokola", "Mokola virus disease"),
    (r"\bsindbis\b|pogosta|ockelbo", "species", "Alphavirus sindbis", "Sindbis fever"),
    (r"ross river", "species", "Alphavirus rossriver", "Ross River virus disease"),
    (r"\bmayaro\b", "species", "Alphavirus mayaro", "Mayaro fever"),
    (r"eastern equine encephalitis", "species", "Alphavirus eastern", "Eastern equine encephalitis"),
    (r"\busutu\b", "species", "Orthoflavivirus usutuense", "Usutu virus infection"),
    (r"powassan", "species", "Orthoflavivirus powassanense", "Powassan encephalitis"),
    (r"kyasanur|alkhu?mra", "species", "Orthoflavivirus kyasanurense", "Kyasanur Forest disease"),
    (r"\bjun[ií]n\b", "species", "Mammarenavirus juninense", "Argentine haemorrhagic fever"),
    (r"guanarito", "species", "Mammarenavirus guanaritoense", "Venezuelan haemorrhagic fever"),
    (r"machupo", "species", "Mammarenavirus machupoense", "Bolivian haemorrhagic fever"),
    (r"\bmolluscum\b", "species", "Molluscipoxvirus molluscum", "Molluscum contagiosum"),
    (r"varicella|chickenpox|\bshingles\b|herpes zoster", "species", "Varicellovirus humanalpha3", "Varicella / zoster"),
]

_COMPILED = [(re.compile(rx, re.I), kind, taxon, label)
             for rx, kind, taxon, label in DISEASES]

# Reports WHO files that are not viral at all. Recognised so they can be
# counted and dropped rather than silently vanishing into "unmatched".
NON_VIRAL = re.compile(
    r"cholera|anthrax|diphtheria|meningococc|plague|malaria|legionell|"
    r"salmonell|listeri|botulism|cereulide|food safety|lead poisoning|"
    r"nodding syndrome|leptospir|typhoid|chemical|klebsiella|"
    r"antimicrobial resistance|shigell|brucell|tularem|histoplasm|"
    r"candida auris|mycetoma|rabies-like bacterium", re.I)


def classify(title, summary=""):
    """Map a report to a taxon. Returns (kind, taxon, label) or None.

    The title is tried on its own first. WHO summaries routinely mention other
    diseases in passing -- a differential, a co-circulating pathogen, a
    laboratory that also tests for malaria -- so matching on title+summary
    together attributed reports to the wrong virus.
    """
    for rx, kind, taxon, label in _COMPILED:
        if rx.search(title):
            return kind, taxon, label
    for rx, kind, taxon, label in _COMPILED:
        if rx.search(summary or ""):
            return kind, taxon, label
    return None


def is_non_viral(title, summary=""):
    """Title only: a summary that mentions cholera is not a cholera report."""
    return bool(NON_VIRAL.search(title))


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _db():
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS feed ("
                "source TEXT PRIMARY KEY, fetched_at REAL, payload TEXT)")
    return con


def _cached(source):
    con = _db()
    try:
        row = con.execute("SELECT fetched_at, payload FROM feed WHERE source=?",
                          (source,)).fetchone()
    finally:
        con.close()
    if not row:
        return None, None
    return row[0], json.loads(row[1])


def _store(source, items):
    con = _db()
    try:
        con.execute("REPLACE INTO feed VALUES (?,?,?)",
                    (source, time.time(), json.dumps(items)))
        con.commit()
    finally:
        con.close()


def _get(url, accept="application/json"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _strip(html):
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
                .replace("&quot;", '"'))
    return re.sub(r"\s+", " ", text).strip()


def fetch_who():
    raw = json.loads(_get(WHO_URL))
    out = []
    for r in raw.get("value", []):
        url_name = r.get("UrlName") or ""
        out.append({
            "source": "WHO",
            "title": (r.get("Title") or "").strip(),
            "date": (r.get("PublicationDateAndTime") or "")[:10],
            "summary": _strip(r.get("Summary"))[:600],
            "url": f"https://www.who.int/emergencies/disease-outbreak-news/item/{url_name}",
        })
    return out



UKHSA_URL = (
    "https://www.gov.uk/api/search.json"
    "?filter_organisations=uk-health-security-agency"
    "&count=100&order=-public_timestamp"
    "&fields=title,link,public_timestamp,description"
)

# UKHSA publishes a great deal that is not an outbreak signal: vaccine
# leaflets, consultations, job notices, statistics releases. Only the
# surveillance and outbreak series are kept, and the filter is stated rather
# than hidden so it can be argued with.
UKHSA_KEEP = re.compile(
    r"outbreak|surveillance|incident|cluster|cases? of|"
    r"epidemiolog|risk assessment|health protection report|"
    r"rapid risk|situation (?:report|update)|detected", re.I)
UKHSA_DROP = re.compile(
    r"\bleaflet\b|consultation|vacanc|job description|annual report|"
    r"terms of reference|minutes of|guidance for parents|"
    r"patient information|\bform\b|freedom of information|"
    # Series that report activity without naming a pathogen. Useful to a
    # national agency, but nothing here can attach them to a virus.
    r"all-cause mortality|syndromic surveillance|ambulance|"
    r"out-of-hours|emergency department|\bNHS 111\b", re.I)


def _series_key(title):
    """Collapse a weekly series to its stem, so one entry stands for it.

    UKHSA republishes "National flu and COVID-19 surveillance report, week N"
    every week and the API returns all of them, which buried everything else
    under four weeks of the same report.
    """
    stem = re.sub(r"[,:]?\s*(week|wk)\s*\d+.*$", "", title, flags=re.I)
    stem = re.sub(r"\b(19|20)\d{2}(\s*(to|-|/)\s*(19|20)?\d{2})?\b", "", stem)
    return re.sub(r"\s+", " ", stem).strip().lower()


def fetch_ukhsa():
    raw = json.loads(_get(UKHSA_URL))
    out, seen = [], set()
    for r in raw.get("results", []):
        title = (r.get("title") or "").strip()
        if not UKHSA_KEEP.search(title) or UKHSA_DROP.search(title):
            continue
        key = _series_key(title)
        if key in seen:                 # keep only the newest of a series
            continue
        seen.add(key)
        link = r.get("link") or ""
        out.append({
            "source": "UKHSA",
            "title": title,
            "date": (r.get("public_timestamp") or "")[:10],
            "summary": _strip(r.get("description"))[:600],
            "url": link if link.startswith("http") else "https://www.gov.uk" + link,
        })
    return out


FEEDS = {"WHO": fetch_who, "UKHSA": fetch_ukhsa}


def ecdc_threat_report():
    """A verified link to the current week's ECDC threat report.

    The PDF is 2-3 MB and parsing it would be fragile, so this only confirms
    that a given week's report exists and hands back the link. Recent weeks
    return HTTP 200 with a zero-length body -- present but not yet populated —
    so a report counts only when it actually has bytes in it.
    """
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date()
    for back in range(0, 6):
        day = today - datetime.timedelta(weeks=back)
        year, week, _ = day.isocalendar()
        url = ("https://www.ecdc.europa.eu/sites/default/files/documents/"
               f"communicable-disease-threats-report-week-{week}-{year}.pdf")
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as fh:
                size = int(fh.headers.get("Content-Length") or 0)
            if size > 100_000:
                return {"source": "ECDC",
                        "title": f"Communicable Disease Threats Report, "
                                 f"week {week} of {year}",
                        "url": url, "week": week, "year": year,
                        "bytes": size}
        except (urllib.error.URLError, OSError, ValueError):
            continue
    return None


def refresh(source, force=False):
    """Fetch one feed if the cache is stale. Never raises: returns status."""
    fetched_at, cached = _cached(source)
    fresh = fetched_at and (time.time() - fetched_at) < TTL
    if cached is not None and fresh and not force:
        return {"source": source, "items": cached, "fetched_at": fetched_at,
                "state": "cached", "error": None}
    try:
        items = FEEDS[source]()
        _store(source, items)
        return {"source": source, "items": items, "fetched_at": time.time(),
                "state": "fetched", "error": None}
    except (urllib.error.URLError, OSError, ValueError,
            json.JSONDecodeError) as err:
        # Serving stale data beats serving nothing, as long as the age is shown.
        return {"source": source, "items": cached or [], "fetched_at": fetched_at,
                "state": "stale" if cached else "failed", "error": str(err)[:200]}


def all_signals(force=False):
    """Every cached or freshly fetched report, newest first, with its taxon."""
    reports, sources = [], []
    for source in FEEDS:
        res = refresh(source, force=force)
        sources.append({k: res[k] for k in ("source", "fetched_at", "state", "error")})
        for item in res["items"]:
            hit = classify(item["title"], item["summary"])
            item = dict(item)
            if hit:
                item["kind"], item["taxon"], item["disease"] = hit
            elif is_non_viral(item["title"], item["summary"]):
                item["kind"] = "non-viral"
            else:
                item["kind"] = "unmatched"
            reports.append(item)
    reports.sort(key=lambda r: r["date"], reverse=True)
    return reports, sources


def cache_stats():
    con = _db()
    try:
        rows = con.execute("SELECT source, fetched_at FROM feed").fetchall()
    finally:
        con.close()
    return {s: {"fetched_at": t, "age_s": round(time.time() - t)} for s, t in rows}


if __name__ == "__main__":  # python -m atlas.surveil
    import sys
    reports, sources = all_signals(force="--force" in sys.argv)
    for s in sources:
        print(f"{s['source']:<5} {s['state']:<8} {s['error'] or ''}")
    matched = [r for r in reports if r.get("taxon")]
    print(f"\n{len(reports)} reports, {len(matched)} matched to a taxon, "
          f"{sum(1 for r in reports if r['kind'] == 'non-viral')} non-viral, "
          f"{sum(1 for r in reports if r['kind'] == 'unmatched')} unmatched\n")
    for r in reports[:25]:
        tag = r.get("disease") or r["kind"]
        print(f"  {r['date']}  {r['source']:<5} {tag[:34]:<35} {r['title'][:60]}")
    print("\nUNMATCHED (would need a DISEASES pattern):")
    for r in reports:
        if r["kind"] == "unmatched":
            print(f"  {r['date']}  {r['source']:<5} {r['title'][:90]}")
