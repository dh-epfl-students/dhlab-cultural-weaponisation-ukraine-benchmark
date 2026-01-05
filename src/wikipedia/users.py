from .client import WikipediaClient

client = WikipediaClient(
    user_agent="DH_Project/1.0 (maxime.garambois@epfl.ch)"
)

def get_all_bots():
    bots = []
    params = {
        "action": "query",
        "list": "allusers",
        "augroup": "bot",
        "aulimit": "max",
    }

    while True:
        data = client.get(params)
        users = data.get("query", {}).get("allusers", [])
        bots.extend(u["name"] for u in users)

        if "continue" not in data:
            break
        params.update(data["continue"])

    return bots

def get_user_metadata(username):
    params = {
        "action": "query",
        "list": "users",
        "ususers": username,
        "usprop": "blockinfo|groups|editcount|registration|emailable|gender",
    }
    data = client.get(params)
    return data["query"]["users"][0]
    

def get_user_revisions(username, max_edits=None):
    params = {
        "action": "query",
        "list": "usercontribs",
        "ucuser": username,
        "ucprop": "ids|title|timestamp|comment|size|flags",
        "uclimit": 500,
    }

    edits = []

    while True:
        data = client.get(params)
        contribs = data.get("query", {}).get("usercontribs", [])
        for c in contribs:
            c["username"] = username
        edits.extend(contribs)

        if max_edits and len(edits) >= max_edits:
            return edits[:max_edits]

        if "continue" not in data:
            break
        params.update(data["continue"])

    return edits

