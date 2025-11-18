import re
import requests
import time

URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {
    "User-Agent": "DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)"
}

def get_user_metadata(username, max_retries=3, backoff=1.0):
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