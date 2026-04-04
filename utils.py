# """
# utils.py
# --------
# Shared helpers:
#   identify_plant()  – PlantNet v2 API  → (name, confidence)
#   get_info()        – Wikipedia REST   → full rich summary text
# """

# import os
# import requests
# from urllib.parse import quote
# from dotenv import load_dotenv

# load_dotenv()

# PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY", "")


# def identify_plant(image_bytes: bytes) -> tuple:
#     """
#     Identify a plant/flower from raw JPEG/PNG bytes via PlantNet v2.

#     Returns:
#         (display_name: str, confidence: float)
#         display_name is 'Unknown' when identification fails or confidence < 0.15.
#     """
#     if not PLANTNET_API_KEY:
#         print("❌ PLANTNET_API_KEY not set in .env")
#         return "Unknown", 0.0

#     url = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}&lang=en&nb-results=5"

#     try:
#         response = requests.post(
#             url,
#             files={"images": ("image.jpg", image_bytes, "image/jpeg")},
#             data={"organs": "auto"},
#             timeout=15,
#         )

#         if response.status_code == 404:
#             url2 = f"https://my-api.plantnet.org/v2/identify/flower?api-key={PLANTNET_API_KEY}&lang=en"
#             response = requests.post(
#                 url2,
#                 files={"images": ("image.jpg", image_bytes, "image/jpeg")},
#                 data={"organs": "flower"},
#                 timeout=15,
#             )

#         if response.status_code != 200:
#             print(f"❌ PlantNet API error {response.status_code}: {response.text[:300]}")
#             return "Unknown", 0.0

#         data    = response.json()
#         results = data.get("results", [])
#         if not results:
#             print("⚠️  PlantNet: no results returned")
#             return "Unknown", 0.0

#         best    = results[0]
#         species = best.get("species", {})
#         sci     = species.get("scientificNameWithoutAuthor", "Unknown")
#         commons = species.get("commonNames", [])
#         common  = commons[0] if commons else sci
#         score   = float(best.get("score", 0.0))


#         if score < 0.15:
#             print(f"⚠️  PlantNet very low confidence: {score:.2f} for {sci}")
#             return "Unknown", 0.0

#         display = f"{common} ({sci})" if common.lower() != sci.lower() else sci
#         print(f"✅ PlantNet identified: {display}  [{score:.2%}]")
#         return display, score

#     except requests.Timeout:
#         print("❌ PlantNet request timed out")
#     except requests.RequestException as exc:
#         print(f"❌ PlantNet network error: {exc}")
#     except Exception as exc:
#         print(f"❌ identify_plant unexpected error: {exc}")

#     return "Unknown", 0.0


# def get_info(name: str) -> str:
#     """
#     Fetch rich Wikipedia information for *name*.

#     Strategy (tries each in order until we get a solid result):
#       1. Common name only  (e.g. "Rose")
#       2. Scientific name   (e.g. "Rosa canina")
#       3. Wikipedia opensearch API to find the best matching page title
#       4. Full name as-is

#     Returns a detailed multi-sentence extract, or 'No info found' on failure.
#     """
#     if not name or name in ("Unknown", "Error", "None", "No object detected"):
#         return "No info found"

#     if "(" in name and name.endswith(")"):
#         common_part = name.split("(")[0].strip()
#         sci_part    = name[name.index("(") + 1 : name.rindex(")")].strip()
#     else:
#         common_part = name.strip()
#         sci_part    = ""

#     candidates = [common_part]
#     if sci_part and sci_part.lower() != common_part.lower():
#         candidates.append(sci_part)
#     candidates.append(name)   

#     for query in candidates:
#         result = _wiki_fetch(query)
#         if result and len(result) > 80:
#             return result

#     # Last resort: use Wikipedia opensearch to find the closest page title
#     search_result = _wiki_search_then_fetch(common_part or name)
#     if search_result and len(search_result) > 80:
#         return search_result

#     print(f"⚠️  Wikipedia found nothing useful for '{name}'")
#     return "No info found"


# def _wiki_fetch(query: str) -> str:
#     """Fetch the Wikipedia page summary extract for a given query string."""
#     try:
#         url = (
#             "https://en.wikipedia.org/api/rest_v1/page/summary/"
#             + quote(query)
#             + "?redirect=true"
#         )
#         res = requests.get(url, timeout=8, headers={"User-Agent": "FlowerApp/2.0"})
#         if res.status_code == 200:
#             data    = res.json()
#             extract = data.get("extract", "").strip()
#             # Skip disambiguation pages and very short stubs
#             if extract and len(extract) > 80 and "may refer to" not in extract[:120]:
#                 print(f"✅ Wikipedia: got info for '{query}' ({len(extract)} chars)")
#                 return extract
#     except Exception as exc:
#         print(f"❌ _wiki_fetch({query!r}): {exc}")
#     return ""


# def _wiki_search_then_fetch(query: str) -> str:
#     """Use Wikipedia opensearch to find the best page title, then fetch its summary."""
#     try:
#         res = requests.get(
#             "https://en.wikipedia.org/w/api.php",
#             params={
#                 "action": "opensearch",
#                 "search": query,
#                 "limit":  5,
#                 "format": "json",
#             },
#             timeout=8,
#             headers={"User-Agent": "FlowerApp/2.0"},
#         )
#         if res.status_code == 200:
#             data   = res.json()
#             titles = data[1] if len(data) > 1 else []
#             for title in titles:
#                 result = _wiki_fetch(title)
#                 if result and len(result) > 80:
#                     return result
#     except Exception as exc:
#         print(f"❌ _wiki_search_then_fetch({query!r}): {exc}")
#     return "No info found"



# utils.py
# --------
# Shared helpers:
#   identify_plant()         – PlantNet v2 API  → (name, confidence)
#   get_info()               – Wikipedia REST   → rich multi-sentence summary
#   _wiki_fetch()            – single Wikipedia page summary fetch
#   _wiki_search_then_fetch()– opensearch fallback

# """
# utils.py
# --------
# Shared helpers:
#   identify_plant()  – PlantNet v2 API  → (name, confidence)
#   get_info()        – Wikipedia REST   → full rich summary text
# """

# import os
# import requests
# from urllib.parse import quote
# from dotenv import load_dotenv

# load_dotenv()

# PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY", "")


# def identify_plant(image_bytes: bytes) -> tuple:
#     """
#     Identify a plant/flower from raw JPEG/PNG bytes via PlantNet v2.

#     Returns:
#         (display_name: str, confidence: float)
#         display_name is 'Unknown' when identification fails or confidence < 0.15.
#     """
#     if not PLANTNET_API_KEY:
#         print("❌ PLANTNET_API_KEY not set in .env")
#         return "Unknown", 0.0

#     url = f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}&lang=en&nb-results=5"

#     try:
#         response = requests.post(
#             url,
#             files={"images": ("image.jpg", image_bytes, "image/jpeg")},
#             data={"organs": "auto"},
#             timeout=15,
#         )

#         if response.status_code == 404:
#             url2 = f"https://my-api.plantnet.org/v2/identify/flower?api-key={PLANTNET_API_KEY}&lang=en"
#             response = requests.post(
#                 url2,
#                 files={"images": ("image.jpg", image_bytes, "image/jpeg")},
#                 data={"organs": "flower"},
#                 timeout=15,
#             )

#         if response.status_code != 200:
#             print(f"❌ PlantNet API error {response.status_code}: {response.text[:300]}")
#             return "Unknown", 0.0

#         data    = response.json()
#         results = data.get("results", [])
#         if not results:
#             print("⚠️  PlantNet: no results returned")
#             return "Unknown", 0.0

#         best    = results[0]
#         species = best.get("species", {})
#         sci     = species.get("scientificNameWithoutAuthor", "Unknown")
#         commons = species.get("commonNames", [])
#         common  = commons[0] if commons else sci
#         score   = float(best.get("score", 0.0))


#         if score < 0.15:
#             print(f"⚠️  PlantNet very low confidence: {score:.2f} for {sci}")
#             return "Unknown", 0.0

#         display = f"{common} ({sci})" if common.lower() != sci.lower() else sci
#         print(f"✅ PlantNet identified: {display}  [{score:.2%}]")
#         return display, score

#     except requests.Timeout:
#         print("❌ PlantNet request timed out")
#     except requests.RequestException as exc:
#         print(f"❌ PlantNet network error: {exc}")
#     except Exception as exc:
#         print(f"❌ identify_plant unexpected error: {exc}")

#     return "Unknown", 0.0


# def get_info(name: str) -> str:
#     """
#     Fetch rich Wikipedia information for *name*.

#     Strategy (tries each in order until we get a solid result):
#       1. Common name only  (e.g. "Rose")
#       2. Scientific name   (e.g. "Rosa canina")
#       3. Wikipedia opensearch API to find the best matching page title
#       4. Full name as-is

#     Returns a detailed multi-sentence extract, or 'No info found' on failure.
#     """
#     if not name or name in ("Unknown", "Error", "None", "No object detected"):
#         return "No info found"

#     if "(" in name and name.endswith(")"):
#         common_part = name.split("(")[0].strip()
#         sci_part    = name[name.index("(") + 1 : name.rindex(")")].strip()
#     else:
#         common_part = name.strip()
#         sci_part    = ""

#     candidates = [common_part]
#     if sci_part and sci_part.lower() != common_part.lower():
#         candidates.append(sci_part)
#     candidates.append(name)   

#     for query in candidates:
#         result = _wiki_fetch(query)
#         if result and len(result) > 80:
#             return result

#     # Last resort: use Wikipedia opensearch to find the closest page title
#     search_result = _wiki_search_then_fetch(common_part or name)
#     if search_result and len(search_result) > 80:
#         return search_result

#     print(f"⚠️  Wikipedia found nothing useful for '{name}'")
#     return "No info found"


# def _wiki_fetch(query: str) -> str:
#     """Fetch the Wikipedia page summary extract for a given query string."""
#     try:
#         url = (
#             "https://en.wikipedia.org/api/rest_v1/page/summary/"
#             + quote(query)
#             + "?redirect=true"
#         )
#         res = requests.get(url, timeout=8, headers={"User-Agent": "FlowerApp/2.0"})
#         if res.status_code == 200:
#             data    = res.json()
#             extract = data.get("extract", "").strip()
#             # Skip disambiguation pages and very short stubs
#             if extract and len(extract) > 80 and "may refer to" not in extract[:120]:
#                 print(f"✅ Wikipedia: got info for '{query}' ({len(extract)} chars)")
#                 return extract
#     except Exception as exc:
#         print(f"❌ _wiki_fetch({query!r}): {exc}")
#     return ""


# def _wiki_search_then_fetch(query: str) -> str:
#     """Use Wikipedia opensearch to find the best page title, then fetch its summary."""
#     try:
#         res = requests.get(
#             "https://en.wikipedia.org/w/api.php",
#             params={
#                 "action": "opensearch",
#                 "search": query,
#                 "limit":  5,
#                 "format": "json",
#             },
#             timeout=8,
#             headers={"User-Agent": "FlowerApp/2.0"},
#         )
#         if res.status_code == 200:
#             data   = res.json()
#             titles = data[1] if len(data) > 1 else []
#             for title in titles:
#                 result = _wiki_fetch(title)
#                 if result and len(result) > 80:
#                     return result
#     except Exception as exc:
#         print(f"❌ _wiki_search_then_fetch({query!r}): {exc}")
#     return "No info found"



# utils.py
# --------
# Shared helpers:
#   identify_plant()         – PlantNet v2 API  → (name, confidence)
#   get_info()               – Wikipedia REST   → rich multi-sentence summary
#   _wiki_fetch()            – single Wikipedia page summary fetch
#   _wiki_search_then_fetch()– opensearch fallback


"""
utils.py
--------
identify_plant()  – PlantNet v2  → (name, confidence)
get_info()        – Wikipedia    → flower-specific structured info string

KEY FIX: get_info() now:
  1. Tries scientific name FIRST (avoids person/place name collisions)
  2. Verifies the Wikipedia page is actually a plant page via categories
  3. Filters out irrelevant sentences — keeps only botanical content
  4. Returns a clean, flower-focused paragraph
"""

import os
import re
import requests
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY", "")
_HEADERS = {"User-Agent": "FlowerClassificationApp/4.0 (academic-project)"}

# ── Keywords that confirm a Wikipedia page is about a plant ──────────────────
_PLANT_CATEGORIES = {
    "plant", "flower", "flora", "botany", "botanical", "genus", "species",
    "family", "angiosperm", "gymnosperm", "shrub", "tree", "herb", "vine",
    "perennial", "annual", "ornamental", "garden", "horticulture",
    "rosaceae", "asteraceae", "liliaceae", "orchidaceae", "fabaceae",
    "solanaceae", "ranunculaceae", "apiaceae", "lamiaceae", "poaceae",
}

# ── Sentence keywords that indicate botanical/flower content ──────────────────
_BOTANICAL_KEYWORDS = [
    "flower", "plant", "bloom", "petal", "leaf", "leaves", "stem", "root",
    "genus", "species", "family", "native", "grows", "garden", "ornamental",
    "perennial", "annual", "shrub", "tree", "herb", "fragrant", "aroma",
    "pollinator", "bees", "nectar", "seeds", "fruit", "cultivar", "variety",
    "medicinal", "traditional medicine", "habitat", "found in", "distributed",
    "height", "cm", "metre", "meter", "colour", "color", "red", "white",
    "yellow", "pink", "purple", "blue", "orange", "lavender", "violet",
    "tropical", "temperate", "asia", "europe", "africa", "america",
    "classification", "order", "kingdom", "botanic", "botanical",
    "edible", "toxic", "poisonous", "fragrance", "scent", "pollen",
    "national flower", "state flower", "symbol",
]

# ── Sentences to EXCLUDE (irrelevant to a flower project) ─────────────────────
_IRRELEVANT_PATTERNS = [
    r"\b(singer|musician|actor|actress|film|movie|album|song|band|artist)\b",
    r"\b(politician|president|minister|senator|governor)\b",
    r"\b(born|died|marriage|married|husband|wife|children|son|daughter)\b",
    r"\b(novel|book|author|writer|poet|poem|literature)\b",
    r"\b(company|corporation|brand|trademark|product|software)\b",
    r"\bmay refer to\b",
    r"\bdisambiguation\b",
    r"\bsee also\b",
    r"\bother uses\b",
]
_IRRELEVANT_RE = re.compile("|".join(_IRRELEVANT_PATTERNS), re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# PlantNet identification
# ─────────────────────────────────────────────────────────────────────────────

def identify_plant(image_bytes: bytes) -> tuple:
    """
    Identify a flower from JPEG/PNG bytes via PlantNet v2.
    Returns (display_name, confidence).  Name is 'Unknown' on failure.
    """
    if not PLANTNET_API_KEY:
        print("❌ PLANTNET_API_KEY not set in .env")
        return "Unknown", 0.0

    endpoints = [
        (f"https://my-api.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}&lang=en&nb-results=5", "auto"),
        (f"https://my-api.plantnet.org/v2/identify/flower?api-key={PLANTNET_API_KEY}&lang=en&nb-results=5", "flower"),
    ]

    for url, organ in endpoints:
        try:
            resp = requests.post(
                url,
                files={"images": ("flower.jpg", image_bytes, "image/jpeg")},
                data={"organs": organ},
                timeout=18,
            )
            if resp.status_code == 200:
                return _parse_plantnet(resp.json())
            if resp.status_code in (400, 404):
                print(f"⚠️  PlantNet {resp.status_code} organ={organ} — trying next")
                continue
            print(f"❌ PlantNet {resp.status_code}: {resp.text[:150]}")
            return "Unknown", 0.0
        except requests.Timeout:
            print("❌ PlantNet timed out")
            return "Unknown", 0.0
        except Exception as exc:
            print(f"❌ identify_plant: {exc}")
            return "Unknown", 0.0

    return "Unknown", 0.0


def _parse_plantnet(data: dict) -> tuple:
    results = data.get("results", [])
    if not results:
        return "Unknown", 0.0
    best    = results[0]
    species = best.get("species", {})
    sci     = species.get("scientificNameWithoutAuthor", "Unknown")
    commons = species.get("commonNames", [])
    common  = commons[0] if commons else sci
    score   = float(best.get("score", 0.0))
    if score < 0.12:
        print(f"⚠️  Low confidence {score:.2%} for '{sci}'")
        return "Unknown", 0.0
    display = f"{common} ({sci})" if common.lower() != sci.lower() else sci
    print(f"✅ PlantNet → {display!r} [{score:.2%}]")
    return display, score


# ─────────────────────────────────────────────────────────────────────────────
# Wikipedia flower-specific info
# ─────────────────────────────────────────────────────────────────────────────

def get_info(name: str) -> str:
    """
    Return clean, flower-specific information for a detected plant name.

    Strategy:
      1. Try SCIENTIFIC name first (e.g. "Rosa canina") — avoids person/place hits
      2. Try common name (e.g. "Rose")
      3. Fallback: Wikipedia opensearch → verify it's a plant page
      4. Filter result to keep only botanical sentences
    """
    if not name or name in ("Unknown", "Error", "None", "No object detected", "Waiting…"):
        return "No info found"

    # Parse "Common Name (Scientific name)" format
    sci_part, common_part = "", name.strip()
    if "(" in name and name.rstrip().endswith(")"):
        common_part = name[: name.index("(")].strip()
        sci_part    = name[name.index("(") + 1 : name.rindex(")")].strip()

    # ── Try scientific name FIRST (most specific, avoids disambiguation) ─────
    candidates = []
    if sci_part:
        candidates.append(sci_part)
    candidates.append(common_part)
    if name not in candidates:
        candidates.append(name)

    for query in candidates:
        raw = _wiki_fetch(query)
        if raw:
            cleaned = _filter_botanical(raw, query)
            if cleaned:
                print(f"✅ Info ready for '{query}' ({len(cleaned)} chars)")
                return cleaned

    # ── Opensearch fallback ───────────────────────────────────────────────────
    for query in [sci_part or common_part, common_part]:
        raw = _wiki_search_then_fetch(query)
        if raw:
            cleaned = _filter_botanical(raw, query)
            if cleaned:
                return cleaned

    print(f"⚠️  No flower info found for '{name}'")
    return "No info found"


def _wiki_fetch(query: str) -> str:
    """
    Fetch Wikipedia page summary.  Returns raw extract or "" on failure.
    Rejects disambiguation pages and non-plant pages.
    """
    if not query:
        return ""
    try:
        url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + quote(query.strip(), safe="")
            + "?redirect=true"
        )
        res = requests.get(url, timeout=10, headers=_HEADERS)
        if res.status_code != 200:
            return ""

        payload   = res.json()
        page_type = payload.get("type", "")
        extract   = payload.get("extract", "").strip()
        title     = payload.get("title", "").lower()

        # Reject disambiguation pages
        if page_type == "disambiguation":
            print(f"⚠️  '{query}' → disambiguation page, skipping")
            return ""

        # Reject very short stubs
        if not extract or len(extract) < 80:
            return ""

        # Reject obvious disambiguation text
        if "may refer to" in extract[:150] or "disambiguation" in extract[:150].lower():
            return ""

        # ── PLANT PAGE VERIFICATION ──────────────────────────────────────────
        # Check the description field (Wikipedia REST API includes it)
        description = payload.get("description", "").lower()
        is_plant = _is_plant_content(extract + " " + description + " " + title)

        if not is_plant:
            print(f"⚠️  '{query}' page doesn't appear to be about a plant — skipping")
            return ""

        return extract

    except requests.Timeout:
        print(f"⚠️  Wikipedia timeout for '{query}'")
    except Exception as exc:
        print(f"❌ _wiki_fetch('{query}'): {exc}")
    return ""


def _is_plant_content(text: str) -> bool:
    """Return True if the text appears to be about a plant/flower."""
    text_lower = text.lower()
    # Must contain at least 2 plant-related keywords
    hits = sum(1 for kw in _PLANT_CATEGORIES if kw in text_lower)
    return hits >= 2


def _filter_botanical(text: str, flower_name: str) -> str:
    """
    Filter Wikipedia extract to keep only flower/plant relevant sentences.
    Removes sentences about cultural figures, products, etc.
    Returns a clean multi-sentence botanical description.
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    kept = []
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue

        # Skip sentences matching irrelevant patterns
        if _IRRELEVANT_RE.search(s):
            continue

        # Keep sentence if it contains any botanical keyword
        s_lower = s.lower()
        has_botanical = any(kw in s_lower for kw in _BOTANICAL_KEYWORDS)

        # Always keep the first sentence (usually the best definition)
        if not kept:
            # First sentence must contain something plant-related OR the flower name
            name_in_text = any(
                part.lower() in s_lower
                for part in flower_name.replace("(", " ").replace(")", " ").split()
                if len(part) > 3
            )
            if has_botanical or name_in_text:
                kept.append(s)
        elif has_botanical:
            kept.append(s)

        # Stop after collecting enough good sentences (prevents info overload)
        if len(kept) >= 8:
            break

    if not kept:
        # Fallback: return first 3 sentences if filtering was too aggressive
        fallback = sentences[:3]
        return " ".join(s.strip() for s in fallback if s.strip())

    return " ".join(kept)


def _wiki_search_then_fetch(query: str) -> str:
    """Use Wikipedia opensearch to find the best plant page title, then fetch."""
    if not query:
        return ""
    try:
        res = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action":    "opensearch",
                "search":    query + " plant",   # append "plant" to bias results
                "limit":     6,
                "format":    "json",
                "redirects": "resolve",
            },
            timeout=10,
            headers=_HEADERS,
        )
        if res.status_code != 200:
            return ""
        data   = res.json()
        titles = data[1] if len(data) > 1 else []
        for title in titles:
            raw = _wiki_fetch(title)
            if raw:
                print(f"✅ Opensearch hit: '{title}'")
                return raw
    except Exception as exc:
        print(f"❌ _wiki_search_then_fetch('{query}'): {exc}")
    return ""