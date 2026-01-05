import re
import requests
import time


def fetch_wikitext(title):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "format": "json",
        "formatversion": "2"
    }

    r = requests.get(URL, params=params, headers=HEADERS)
    r.raise_for_status()
    data = r.json()

    pages = data.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        return None

    revisions = pages[0].get("revisions", [])
    if not revisions:
        return None

    return revisions[0]["slots"]["main"]["content"]


def extract_templates(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    templates = []

    for tpl in wikicode.filter_templates(recursive=True):
        templates.append({
            "template_name": str(tpl.name).strip(),
            "parameters": {
                str(param.name).strip(): str(param.value).strip()
                for param in tpl.params
            }
        })

    return templates


def process_user(username):
    results = []

    for page_type, title in [
        ("user", f"User:{username}"),
        ("user_talk", f"User talk:{username}")
    ]:
        try:
            wikitext = fetch_wikitext(title)
            if not wikitext:
                continue

            templates = extract_templates(wikitext)

            for tpl in templates:
                results.append({
                    "username": username,
                    "page_type": page_type,
                    "template_name": tpl["template_name"],
                    "parameters": tpl["parameters"]
                })

        except Exception as e:
            print(f"[ERROR] {username} ({page_type}): {e}")

        time.sleep(SLEEP_TIME)

    return results


def run():
    all_results = []

    for user in tqdm(top10_users, desc="Processing users"):
        all_results.extend(process_user(user))

    # Save JSON (full fidelity)
    with open("user_templates_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # Save CSV (easy inspection)
    with open("user_templates_raw.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["username", "page_type", "template_name", "parameters"]
        )
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

    print("✔ Extraction complete")


def get_revision_id(title, direction):
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 1,
        "rvdir": direction,
        "rvprop": "ids",
        "format": "json"
    }

    response = requests.get(API, params=params, headers=HEADERS)

    # If Wikipedia returns HTML instead of JSON
    if "application/json" not in response.headers.get("Content-Type", ""):
        return None

    data = response.json()

    try:
        pages = data["query"]["pages"]
        page = next(iter(pages.values()))
        return page["revisions"][0]["revid"]
    except Exception as e:
        return None

URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "DH_Project/1.0 (maxime.garambois@epfl.ch)"
}

CONTENTIOUS_KEYWORDS = ["contentious topics/"]

def get_talk_wikitext(title):
    """Retrieve raw wikitext of the Talk page."""
    params = {
        "action": "query",
        "titles": f"Talk:{title}",
        "prop": "revisions",
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": "2",
        "format": "json"
    }
    response = requests.get(url=URL, params=params, headers=HEADERS)
    data = response.json()

    page = data["query"]["pages"][0]
    if "missing" in page:
        return None  # talk page doesn't exist

    return page["revisions"][0]["slots"]["main"]["content"]


def parse_assessments(wikitext):
    """Parse class, importance values, and contentious-topic status from wikitext."""
    code = mwparserfromhell.parse(wikitext)

    results = {
        "class": None,
        "importance": {},
        "contentious": False
    }

    for template in code.filter_templates():
        name = template.name.strip().lower()

        # GLOBAL CLASS (from banner shell)
        if "banner shell" in name:
            if template.has("class"):
                results["class"] = str(template.get("class").value).strip()

        # PER-WIKIPROJECT IMPORTANCE
        if "wikiproject" in name and not "banner shell" in name:
            project = template.name.strip().replace("WikiProject", "").strip()

            # look for either "importance" or "priority"
            if template.has("importance"):
                imp = str(template.get("importance").value).strip()
                results["importance"][project] = imp
            elif template.has("priority"):
                # Some projects use "priority" (e.g., Mathematics)
                imp = str(template.get("priority").value).strip()
                results["importance"][project] = imp

        # CONTENTIOUS TOPICS DETECTION
        temp_text = str(template).lower()
        if any(keyword in name for keyword in CONTENTIOUS_KEYWORDS):
            results["contentious"] = True

    return results


def get_article_assessment(title):
    """Main wrapper: fetch talk page and parse assessment."""
    wikitext = get_talk_wikitext(title)
    if not wikitext:
        return {"error": "Talk page does not exist"}

    return parse_assessments(wikitext)

def extract_relevant_importance(importance_dict):
    """
    From all WikiProject importance values:
    - If 'Ukraine' exists -> return that value.
    - Else -> return the first value in the dict.
    - If dict empty -> return None.
    """
    if not importance_dict:
        return None

    # Prefer Ukraine rating if present
    if "Ukraine" in importance_dict:
        return importance_dict["Ukraine"]

    # Otherwise take the first key in the dict
    first_key = next(iter(importance_dict))
    return importance_dict[first_key]

def get_data(articles_list, out_csv):
    rows = []

    for article in articles_list:
        assessment = get_article_assessment(article)

        # Extract global class
        article_class = assessment.get("class")

        # Extract importance from rules
        importance = extract_relevant_importance(assessment.get("importance", {}))

        # Contentious topic boolean
        contentious = assessment.get("contentious")

        rows.append({
            "article": article,
            "class": article_class,
            "importance": importance,
            "contentious": contentious
        })

    # Save CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["article", "class", "importance", "contentious"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV saved at: {out_csv}")

import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re

API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "DH_Project/1.0 (maxime.garambois@epfl.ch)"}

def mw_normalize_and_redirects(title):
    """Return canonical title + any redirects (all with underscores)."""
    params = {
        "action": "query",
        "titles": title,
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    r = requests.get(API, params=params, headers=HEADERS).json()
    pages = r.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        # fall back to the provided title
        return {title.replace(" ", "_")}
    canonical = pages[0]["title"].replace(" ", "_")
    candidates = {canonical}
    for redir in r["query"].get("redirects", []):
        candidates.add(redir["from"].replace(" ", "_"))
        candidates.add(redir["to"].replace(" ", "_"))
    return candidates

def parse_page_html(title):
    """Fetch parsed HTML for a wiki page title."""
    params = {"action": "parse", "page": title, "prop": "text", "format": "json"}
    r = requests.get(API, params=params, headers=HEADERS).json()
    if "error" in r:
        return None
    return r["parse"]["text"]["*"]

def collect_level_subpages(level):
    """
    From the root VA page for a level, collect all subpages like:
    Wikipedia:Vital articles/Level/<level>/People, /History, etc.
    Include the root too (some levels have direct links).
    """
    root = f"Wikipedia:Vital articles/Level/{level}"
    html = parse_page_html(root)
    subpages = set()
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            title = a.get("title", "")
            # Prefer title (cleaner), but fall back to href if needed
            if title.startswith(f"Wikipedia:Vital articles/Level/{level}/"):
                subpages.add(title)
            elif href.startswith("/wiki/Wikipedia:Vital_articles/Level/"):
                # Extract after /wiki/
                target = href[len("/wiki/"):]
                if re.match(rf"Wikipedia:Vital_articles/Level/{level}\b", target):
                    subpages.add(target)
    subpages.add(root)
    return subpages

def vital_level_via_lists(article_title):
    """
    Search Vital Articles lists (levels 1..5) and return the level number
    where the article appears, or None if not found.
    """
    acceptable = {t.lower() for t in mw_normalize_and_redirects(article_title)}

    for level in range(1, 6):
        for subpage in collect_level_subpages(level):
            html = parse_page_html(subpage)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a"):
                # Use the title attribute: it's the canonical page title
                if a.has_attr("title"):
                    link_title = a["title"].replace(" ", "_").lower()
                    if link_title in acceptable:
                        return level
                else:
                    # Fallback to href if no title (rare)
                    href = a.get("href", "")
                    if href.startswith("/wiki/"):
                        target = href[len("/wiki/"):].split("#", 1)[0]
                        target = unquote(target).replace(" ", "_").lower()
                        if target in acceptable:
                            return level
    return None

# Try to store the article's metadata changes in a timeline
WIKI_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "DH_Project/1.0 (maxime.garambois@epfl.ch)"
SLEEP = 0.5

def request_api(params):
    """Send a request to the API with retry and user-agent."""
    headers = {"User-Agent": USER_AGENT}
    while True:
        try:
            response = requests.get(WIKI_API, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Retrying due to error: {e}")
            time.sleep(2)

def fetch_talk_revisions(article_title):
    """
    Fetch all wikitext revisions of the Talk:Article page.
    Returns a list of dicts: {rev_id, timestamp, content}
    """
    talk_title = f"Talk:{article_title}"
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": talk_title,
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "rvlimit": "500",
    }

    revisions = []
    cont = True

    while cont:
        data = request_api(params)

        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "revisions" in page:
            for rev in page["revisions"]:
                revisions.append({
                    "rev_id": rev["revid"],
                    "timestamp": rev["timestamp"],
                    "content": rev["slots"]["main"].get("*", ""),
                })

        if "continue" in data:
            params.update(data["continue"])
        else:
            cont = False

        time.sleep(SLEEP)

    # sort from oldest → newest
    revisions.sort(key=lambda r: r["timestamp"])
    return revisions

# Regex patterns for WikiProject templates, quality, and importance
WIKIPROJECT_RE = re.compile(r"\{\{[Ww]ikiProject [^|}]+(?:\|[^}]+)?\}\}")
CLASS_RE = re.compile(r"class\s*=\s*([A-Za-z]+)", re.IGNORECASE)
IMPORTANCE_RE = re.compile(r"importance\s*=\s*([A-Za-z]+)", re.IGNORECASE)


def extract_metadata(wikitext):
    """Extract class, importance, vital-level metadata from a talk page revision."""
    
    class_rating = None
    importance_rating = None

    # 1. Parse WikiProject templates
    for template in WIKIPROJECT_RE.findall(wikitext):
        class_match = CLASS_RE.search(template)
        if class_match:
            class_rating = class_match.group(1).upper()

        imp_match = IMPORTANCE_RE.search(template)
        if imp_match:
            importance_rating = imp_match.group(1).capitalize()

    return {
        "class": class_rating,
        "importance": importance_rating,
    }

def build_metadata_timeline(talk_revisions):
    """
    Returns a list of metadata changes:
    [
        {
            "timestamp": "...",
            "rev_id": ...,
            "class": "C",
            "importance": "High",
        },
        ...
    ]
    Only stores metadata when it changes.
    """
    timeline = []
    last_state = {"class": None, "importance": None}

    for rev in talk_revisions:
        meta = extract_metadata(rev["content"])

        if meta != last_state:
            timeline.append({
                "timestamp": rev["timestamp"],
                "rev_id": rev["rev_id"],
                **meta
            })
            last_state = meta.copy()

    return timeline    

def extract_article_metadata_timeline(article_title):
    print(f"\n=== Fetching Talk Page revisions for: {article_title} ===")
    talk_revs = fetch_talk_revisions(article_title)
    print(f"Fetched {len(talk_revs)} talk revisions.")

    print("=== Parsing metadata changes (Option B) ===")
    timeline = build_metadata_timeline(talk_revs)

    print(f"Metadata change points: {len(timeline)}")
    return timeline


import requests
import time

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)"
}

def get_user_revisions(username, max_edits=None):
    """
    Retrieve *all* contributions for a user via Wikipedia API pagination.
    Optionally limit total retrieved edits with `max_edits`.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "usercontribs",
        "ucuser": username,
        "ucprop": "ids|title|timestamp|comment|size|flags",
        "uclimit": 500  # maximum allowed per query
    }

    all_edits = []
    cont = True
    uccontinue = None

    while cont:
        if uccontinue:
            PARAMS["uccontinue"] = uccontinue

        R = session.get(URL, params=PARAMS)
        R.raise_for_status()
        DATA = R.json()

        contribs = DATA.get("query", {}).get("usercontribs", [])
        for c in contribs:
            c["username"] = username
        all_edits.extend(contribs)

        uccontinue = DATA.get("continue", {}).get("uccontinue")
        cont = bool(uccontinue)

        # optional stopping condition
        if max_edits and len(all_edits) >= max_edits:
            all_edits = all_edits[:max_edits]
            break

        time.sleep(0.5)  # polite delay

    return all_edits

def get_user_babel_from_wikitext(username, max_retries=3, backoff=1.0):
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
        "action": "query",
        "page": f"User:{username}",
        "prop": "wikitext",
        "format": "json"
    }

    for attempt in range(max_retries):
        try:
            response = session.get(URL, params=params, timeout=10)

            if response.status_code != 200:
                return {"user": username, "error": f"HTTP {response.status_code}"}

            data = response.json()

            if "parse" not in data or "wikitext" not in data["parse"]:
                return {"user": username, "languages": []}

            text = data["parse"]["wikitext"]["*"]

            # Match {{Babel|en-3|ru|uk-4}}
            match = re.search(r"\{\{\s*Babel\s*\|([^}]*)\}\}", text, re.IGNORECASE)
            if not match:
                return {"user": username, "languages": []}

            entries = match.group(1).split("|")

            languages = []
            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue

                if "-" in entry:
                    code, level = entry.split("-", 1)
                else:
                    code, level = entry, None

                languages.append({
                    "code": code.lower(),
                    "level": level
                })

            return {
                "user": username,
                "languages": languages
            }

        except Exception:
            time.sleep(backoff * (2 ** attempt))

    return {"user": username, "error": f"Failed after {max_retries} attempts"}

def add(a,b):
    return a+b
