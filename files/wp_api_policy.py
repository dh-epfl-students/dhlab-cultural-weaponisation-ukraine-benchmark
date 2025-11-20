import re
import requests
import time

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)"
}

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



    