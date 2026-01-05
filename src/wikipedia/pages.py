# wikipedia/pages.py
import mwparserfromhell
from .client import WikipediaClient

client = WikipediaClient(
    user_agent="DH_Project/1.0 (maxime.garambois@epfl.ch)"
)

def fetch_wikitext(title):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "formatversion": "2",
    }

    pages = client.get(params)["query"]["pages"]
    if not pages or "missing" in pages[0]:
        return None

    revs = pages[0].get("revisions", [])
    return revs[0]["slots"]["main"]["content"] if revs else None


def fetch_parsed_html(title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
    }
    data = client.get(params)
    return data["parse"]["text"]["*"] if "parse" in data else None
