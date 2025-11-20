import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import requests
import time

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)"
}

# -------------------------
# API FOR PROTECTION STATUS
# -------------------------

def get_article_protection_status(article_title):
    """
    Get the protection staturs of an article
    The status can be :
    - fully protected 
    - semi-protected
    - template protected
    - ...
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

def get_article_protection_history(article_title):
    """
    Retrieve the full protection history of an article using MediaWiki logevents.
    Returns a sorted list of protection events including timestamp, action,
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

    # Sort chronologically
    events.sort(key=lambda x: x["timestamp"])

    return events

# -----------------------------
# METHODS FOR PROTECTION STATUS 
# -----------------------------

def parse_old_protection(comment):
    """
    Extracts old-style MediaWiki protection settings from a log comment.
    Example: "edit war [edit=sysop:move=sysop]"
    Returns dict: {"edit": "sysop", "move": "sysop"}
    """
    match = re.search(r"\[(.*?)\]", comment)
    if not match:
        return {}

    content = match.group(1)
    rules = content.split(":")

    prot = {}
    for rule in rules:
        if "=" in rule:
            key, value = rule.split("=", 1)
            prot[key.strip()] = value.strip()

    return prot


def resolve_status(prot_dict):
    """
    Convert a dict of edit/move protection settings to a unified status string.
    Used for new-style AND old-style protections.
    """
    edit = prot_dict.get("edit")
    move = prot_dict.get("move")

    if edit == "sysop":
        return "fully protected"
    if edit == "extendedconfirmed":
        return "extended-protected"
    if edit == "autoconfirmed":
        return "semi-protected"
    if move == "sysop":
        return "move-protected"

    return "unprotected"


def build_protection_timeline(article_title):
    """
    Build chronological protection timeline with both:
      - new-style MW protection data (post-2010)
      - old-style comment-embedded protection info (pre-2010)
    """

    events = get_article_protection_history(article_title)

    if not events:
        return [{
            "start": None,
            "end": None,
            "status": "unprotected"
        }]

    timeline = []
    current_status = "unprotected"
    current_start = None

    for ev in events:
        timestamp = datetime.fromisoformat(ev["timestamp"].replace("Z", "+00:00"))
        action = ev.get("action")
        protections = ev.get("protection", [])
        comment = ev.get("comment", "")

        new_status = "unprotected"

        # CASE A — Explicit unprotection
        if action == "unprotect":
            new_status = "unprotected"

        # CASE B — New-style protection ("protect", "modify")
        elif action in ("protect", "modify", "move_prot", "move_protect"):

            prot_dict = {}

            # (1) Try new-style protection entries from API
            for prot in protections:
                ptype = prot.get("type")
                level = prot.get("level")
                if ptype and level:
                    prot_dict[ptype] = level

            # (2) If nothing found → try old-style [edit=sysop:move=sysop]
            if not prot_dict:
                old = parse_old_protection(comment)
                prot_dict.update(old)

            # (3) Resolve final status
            new_status = resolve_status(prot_dict)

        # CASE C — Nothing explicit found → keep unprotected

        # SEE IF WE KEEP THIS BECAUSE CAN BE MISLEADING
        else:
            new_status = "unprotected"
 
        # STEP 2 — If status changed, close previous interval
        if new_status != current_status:
            if current_start is not None:
                timeline.append({
                    "start": current_start,
                    "end": timestamp,
                    "status": current_status
                })

            current_start = timestamp
            current_status = new_status

    
    # STEP 3 — Close last interval (ends now)
    timeline.append({
        "start": current_start,
        "end": datetime.utcnow(),
        "status": current_status
    })

    return timeline

PROTECTION_COLORS = {
    "unprotected": "#C0C0C0",
    "semi-protected": "#1f77b4",
    "extended-protected": "#ff7f0e",
    "fully protected": "#d62728",
    "move-protected": "#9467bd",
}

def plot_protection_timelines(timelines):
    """
    Gantt-style plot for multiple articles.
    timelines: dict => {article_name: [intervals]}
    """

    
    
    articles = sorted(timelines.keys())  # alphabetical order
    fig, ax = plt.subplots(figsize=(14, len(articles) * 0.4))

    y_pos = 0
    height = 0.8

    for article in articles:
        intervals = timelines[article]

        for interval in intervals:
            start = interval["start"]
            end = interval["end"]
            status = interval["status"]

            if start is None or end is None:
                continue

            ax.broken_barh(
                [(mdates.date2num(start), mdates.date2num(end) - mdates.date2num(start))],
                (y_pos, height),
                facecolors=PROTECTION_COLORS.get(status, "black"),
                edgecolor="none"
            )

        ax.text(mdates.date2num(intervals[0]["start"]) - 50, 
                y_pos + height/2,
                article, va="center", ha="right")

        y_pos += 1

    ax.set_yticks([])
    ax.set_xlabel("Year")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.title("Wikipedia Protection Evolution Timeline", fontsize=14)
    plt.tight_layout()
    plt.show()
