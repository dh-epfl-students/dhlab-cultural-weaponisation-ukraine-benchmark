# wikipedia/client.py
import requests
import time

class WikipediaClient:
    BASE_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, user_agent, sleep=0.5):
        self.sleep = sleep
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get(self, params, retries=3):
        params["format"] = "json"
        for attempt in range(retries):
            try:
                r = self.session.get(self.BASE_URL, params=params, timeout=10)
                r.raise_for_status()
                return r.json()
            except Exception:
                time.sleep(2 ** attempt)
        raise RuntimeError("Wikipedia API request failed")
