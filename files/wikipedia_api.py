"""
Wikipedia API Module

This module provides a comprehensive set of functions for interacting with the Wikipedia API.
All functions handle pagination, retries, and rate limiting automatically.
"""

import re
import requests
import time
from typing import Optional, Dict, List, Any


# ============================================================================
# CONFIGURATION
# ============================================================================

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)"
}

# Default settings
DEFAULT_SLEEP = 0.5  # Polite delay between requests
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF = 1.0


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_ip(user: str) -> bool:
    """Detect if username looks like an IP address."""
    return bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", user))


def request_api(params: Dict[str, Any], max_retries: int = DEFAULT_MAX_RETRIES, 
                backoff: float = DEFAULT_BACKOFF, timeout: int = 10) -> Dict[str, Any]:
    """
    Send a request to the Wikipedia API with retry logic and user-agent.
    
    Args:
        params: API parameters dictionary
        max_retries: Maximum number of retry attempts
        backoff: Base backoff time for exponential backoff
        timeout: Request timeout in seconds
        
    Returns:
        JSON response as dictionary
        
    Raises:
        Exception: If all retries fail
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for attempt in range(max_retries):
        try:
            response = session.get(URL, params=params, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff * (2 ** attempt))
    
    raise Exception(f"Failed after {max_retries} attempts")


# ============================================================================
# USER-RELATED FUNCTIONS
# ============================================================================

def get_user_metadata(username: str, max_retries: int = DEFAULT_MAX_RETRIES, 
                     backoff: float = DEFAULT_BACKOFF) -> Dict[str, Any]:
    """
    Retrieve user metadata including blockinfo, groups, editcount, registration, etc.
    
    Args:
        username: Wikipedia username
        max_retries: Maximum number of retry attempts
        backoff: Base backoff time for exponential backoff
        
    Returns:
        Dictionary with user metadata or error information
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
        "action": "query",
        "list": "users",
        "ususers": username,
        "usprop": "blockinfo|groups|editcount|registration|emailable|gender",
        "format": "json"
    }

    for attempt in range(max_retries):
        try:
            response = session.get(url=URL, params=params, timeout=10)

            if response.status_code != 200:
                return {"user": username, "error": f"HTTP {response.status_code}"}

            try:
                data = response.json()
            except ValueError:
                return {"user": username, "error": "Invalid JSON response"}

            if "query" in data and "users" in data["query"]:
                return data["query"]["users"][0]
            else:
                return {"user": username, "error": "Missing 'users' in response"}

        except Exception as e:
            time.sleep(backoff * (2 ** attempt))  # exponential backoff

    return {"user": username, "error": f"Failed after {max_retries} attempts"}


def get_user_revisions(username: str, max_edits: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all contributions for a user via Wikipedia API pagination.
    Optionally limit total retrieved edits with max_edits.
    
    Args:
        username: Wikipedia username
        max_edits: Optional limit on number of edits to retrieve
        
    Returns:
        List of edit dictionaries, each containing ids, title, timestamp, comment, size, flags
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
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
            params["uccontinue"] = uccontinue

        response = session.get(URL, params=params)
        response.raise_for_status()
        data = response.json()

        contribs = data.get("query", {}).get("usercontribs", [])
        for c in contribs:
            c["username"] = username
        all_edits.extend(contribs)

        uccontinue = data.get("continue", {}).get("uccontinue")
        cont = bool(uccontinue)

        # optional stopping condition
        if max_edits and len(all_edits) >= max_edits:
            all_edits = all_edits[:max_edits]
            break

        time.sleep(DEFAULT_SLEEP)  # polite delay

    return all_edits


def get_user_languages_from_wikitext(username: str, max_retries: int = DEFAULT_MAX_RETRIES, 
                                    backoff: float = DEFAULT_BACKOFF) -> Dict[str, Any]:
    """
    Extract language codes from a user's User page wikitext.
    Looks for {{User xx}} and {{User xx-N}} templates.
    
    Args:
        username: Wikipedia username
        max_retries: Maximum number of retry attempts
        backoff: Base backoff time for exponential backoff
        
    Returns:
        Dictionary with 'user' and 'languages' (list) or 'error'
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
        "action": "parse",
        "page": f"User:{username}",
        "prop": "wikitext",
        "format": "json"
    }

    for attempt in range(max_retries):
        try:
            r = session.get(URL, params=params, timeout=10)
            if r.status_code != 200:
                return {"user": username, "error": f"HTTP {r.status_code}"}

            data = r.json()
            if "parse" not in data or "wikitext" not in data["parse"]:
                return {"user": username, "languages": []}

            text = data["parse"]["wikitext"]["*"]

            # extract {{User xx}} and {{User xx-N}}
            langs = re.findall(r"\{\{User\s+([a-z\-]+)", text, re.IGNORECASE)

            return {
                "user": username,
                "languages": sorted(set(langs))
            }

        except Exception:
            time.sleep(backoff * (2 ** attempt))

    return {"user": username, "error": "Failed after retries"}


def get_all_bots() -> List[str]:
    """
    Retrieve list of all bot usernames from Wikipedia.
    
    Returns:
        List of bot usernames
    """
    session = requests.Session()
    session.headers.update(HEADERS)
    
    bots = []
    params = {
        "action": "query",
        "list": "allusers",
        "augroup": "bot",
        "aulimit": "max", 
        "format": "json"
    }

    while True:
        response = session.get(URL, params=params)
        data = response.json()

        # Extract bot usernames
        users = data.get("query", {}).get("allusers", [])
        bots.extend([u["name"] for u in users])

        # If there is no "continue", we reached the end
        if "continue" not in data:
            break

        # Update params for the next request
        params.update(data["continue"])
        time.sleep(DEFAULT_SLEEP)

    return bots


# ============================================================================
# ARTICLE-RELATED FUNCTIONS
# ============================================================================

def get_article_creation_date(title: str) -> Optional[Dict[str, Any]]:
    """
    Get the creation date and first revision information for an article.
    
    Args:
        title: Article title
        
    Returns:
        Dictionary with timestamp, user, and comment of first revision, or None if article missing
    """
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 1,
        "rvprop": "timestamp|user|comment",
        "rvdir": "newer"    # first revision = creation
    }

    r = requests.get(URL, params=params, headers=HEADERS)
    data = r.json()

    page = next(iter(data["query"]["pages"].values()))

    if "missing" in page:
        return None

    rev = page["revisions"][0]
    return {
        "timestamp": rev["timestamp"],
        "user": rev.get("user"),
        "comment": rev.get("comment")
    }


def mw_normalize_and_redirects(title: str) -> set:
    """
    Return canonical title + any redirects (all with underscores).
    
    Args:
        title: Article title
        
    Returns:
        Set of normalized titles (canonical + redirects)
    """
    params = {
        "action": "query",
        "titles": title,
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    r = requests.get(URL, params=params, headers=HEADERS).json()
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


def parse_page_html(title: str) -> Optional[str]:
    """
    Fetch parsed HTML for a wiki page title.
    
    Args:
        title: Article title
        
    Returns:
        HTML content as string, or None if page doesn't exist
    """
    params = {"action": "parse", "page": title, "prop": "text", "format": "json"}
    r = requests.get(URL, params=params, headers=HEADERS).json()
    if "error" in r:
        return None
    return r["parse"]["text"]["*"]


# ============================================================================
# REVISION-RELATED FUNCTIONS
# ============================================================================

def fetch_all_revisions(title: str, rvprop: str = "user|timestamp|ids|comment") -> List[Dict[str, Any]]:
    """
    Fetch all revision metadata (user, timestamp, comment...) for a given Wikipedia article title.
    
    Args:
        title: Article title
        rvprop: Properties to retrieve (default: "user|timestamp|ids|comment")
        
    Returns:
        List of revision dictionaries
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": title,
        "rvprop": rvprop,
        "rvlimit": "500",            # Max per request
        "formatversion": "2",
        "rvslots": "main"
    }

    all_revs = []
    cont = {}

    while True:
        if cont:
            params.update(cont)
        resp = session.get(URL, params=params, timeout=30)
        resp.raise_for_status()

        # --- Defensive JSON decoding ---
        try:
            data = resp.json()
        except Exception as e:
            print(f"⚠️ JSON decode error for {title}: {e}")
            print(resp.text[:300])
            break

        pages = data.get("query", {}).get("pages", [])
        if not pages:
            break

        page = pages[0]
        if "missing" in page:
            break

        revs = page.get("revisions", [])
        for rev in revs:
            rev["title"] = title
        all_revs.extend(revs)

        # Check for continuation
        if "continue" in data:
            cont = data["continue"]
        else:
            break

        time.sleep(DEFAULT_SLEEP)

    return all_revs


# ============================================================================
# TALK PAGE FUNCTIONS
# ============================================================================

def get_talk_wikitext(title: str) -> Optional[str]:
    """
    Retrieve raw wikitext of the Talk page.
    
    Args:
        title: Article title (without "Talk:" prefix)
        
    Returns:
        Wikitext content as string, or None if talk page doesn't exist
    """
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


def fetch_talk_revisions(article_title: str) -> List[Dict[str, Any]]:
    """
    Fetch all wikitext revisions of the Talk:Article page.
    
    Args:
        article_title: Article title (without "Talk:" prefix)
        
    Returns:
        List of dicts: {rev_id, timestamp, content}
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
    cont = {}

    while True:
        if cont:
            params.update(cont)
        data = request_api(params)

        pages = data["query"]["pages"]
        page = next(iter(pages.values()))

        if "revisions" in page:
            for rev in page["revisions"]:
                revisions.append({
                    "rev_id": rev["revid"],
                    "timestamp": rev["timestamp"],
                    "content": rev.get("slots", {}).get("main", {}).get("*", "")
                })

        # Check for continuation
        if "continue" in data:
            cont = data["continue"]
        else:
            break

        time.sleep(DEFAULT_SLEEP)

    return revisions


# ============================================================================
# PROTECTION-RELATED FUNCTIONS
# ============================================================================

def get_article_protection_status(article_title: str) -> Dict[str, Any]:
    """
    Get the protection status of an article.
    The status can be:
    - fully protected 
    - semi-protected
    - extended-protected
    - template protected
    - move-protected
    - unprotected
    
    Args:
        article_title: Article title
        
    Returns:
        Dictionary with 'status' and 'protections' list
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    params = {
        "action": "query",
        "titles": article_title,
        "prop": "info",
        "inprop": "protection",
        "format": "json"
    }

    response = requests.get(url=URL, params=params, headers=HEADERS)
    data = response.json()

    # Extract page object (the pageid is unknown => key is not fixed)
    page = next(iter(data["query"]["pages"].values()))

    if "missing" in page:
        return {"status": "missing", "protections": []}

    protections = page.get("protection", [])

    # If no protection entries → page is fully open
    if not protections:
        return {"status": "unprotected", "protections": []} 

    # Convert the protection status to understand better
    status = "custom protection"
    for prot in protections:
        action = prot.get("type")
        level = prot.get("level")

        if action == "edit":
            if level == "autoconfirmed":
                status = "semi-protected"
            elif level == "extendedconfirmed":
                status = "extended-protected"
            elif level == "sysop":
                status = "fully protected"
        elif action == "move" and level == "sysop":
            status = "move-protected"

    return {
        "status": status,
        "protections": protections  # raw list for further analysis
    }


def get_article_protection_history(article_title: str) -> List[Dict[str, Any]]:
    """
    Retrieve the full protection history of an article using MediaWiki logevents.
    
    Args:
        article_title: Article title
        
    Returns:
        Sorted list of protection events including timestamp, action,
        protection levels, expiry, and comments.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    events = []
    cont = {}

    while True:
        params = {
            "action": "query",
            "list": "logevents",
            "letype": "protect",
            "letitle": article_title,
            "lelimit": "max",
            "format": "json",
            **cont
        }

        response = session.get(URL, params=params)
        data = response.json()

        for ev in data["query"]["logevents"]:
            event = {
                "timestamp": ev.get("timestamp"),
                "user": ev.get("user"),
                "action": ev.get("action"),        # protect / modify / unprotect / move_prot
                "comment": ev.get("comment"),

                # details with levels and expiry (may be missing)
                "protection": ev.get("params", {}).get("details", []),
            }
            events.append(event)

        # Continue if there's more data
        if "continue" in data:
            cont = data["continue"]
        else:
            break

        time.sleep(DEFAULT_SLEEP)

    # Sort chronologically
    events.sort(key=lambda x: x["timestamp"])

    return events

