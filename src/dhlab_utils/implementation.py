import json
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_json_key(value, key):
    """Safely extract a key from a JSON string or return '' if missing."""
    try:
        data = json.loads(value)
        return str(data.get(key, ""))  # return the value as string
    except (TypeError, json.JSONDecodeError):
        return ""  # if NaN or invalid JSON

def check_global(ngrams, dfs):

    matches = []

    print(80*'-')
    
    for i, df in enumerate(dfs):
        if "changed_version" in df.columns:
            for ng in ngrams:
                found_rows = df[df["changed_version"].astype(str).str.contains(ng, case=False, na=False, regex=False)]
                if not found_rows.empty:
                    matches.append((i, ng, found_rows.index.tolist()))

    if matches:
        for df_index, ng, rows in matches:
            print(f"Found n-gram '{ng}' in DataFrame {df_index}, rows {rows}")
    else:
        print("No matches found in any DataFrame")

def check_local(chunk, dfs_name):

    for name, df in dfs_name.items():
        if "changed_version" in df.columns:
            found_rows = df[df["changed_version"].astype(str).str.contains(chunk, case=False, na=False, regex=False)]
            if not found_rows.empty:
                print(f"Match found in article '{name}', rows {found_rows.index.tolist()}")

def generate_ngrams(text, n=4):
    words = text.split()
    return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

def extract_after(value):
    """Extract the 'after' field from a JSON-like string, ignoring ``` and other wrappers."""
    try:
        if not isinstance(value, str):
            return np.nan  # non-string entries -> NaN
        
        # Remove Markdown code fences and leading/trailing whitespace
        cleaned = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", value.strip())
        
        # Try loading JSON
        data = json.loads(cleaned)
        
        # Extract value
        after_value = data["detected_changes"][0].get("after", "").strip()
        
        # If empty string -> treat as NaN (ignore later)
        if after_value == "":
            return np.nan
        
        return after_value
    
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return np.nan

def find_best_match(text, df, threshold=0.9):
    texts = df['changed_version'].astype(str).tolist() + df['initial_version'].astype(str).tolist()
    users = df['user'].tolist() * 2  # because we concatenated 2 columns
    
    vectorizer = TfidfVectorizer().fit([text] + texts)
    vectors = vectorizer.transform([text] + texts)
    sims = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    best_idx = np.argmax(sims)
    
    if sims[best_idx] >= threshold:
        return users[best_idx], sims[best_idx]
    return None, None