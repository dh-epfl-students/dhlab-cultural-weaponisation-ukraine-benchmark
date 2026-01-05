# Wikipedia API Module

This module provides a comprehensive set of functions for interacting with the Wikipedia API. All functions handle pagination, retries, and rate limiting automatically.

## Installation

Make sure you have the required dependencies:

```bash
pip install requests
```

## Usage

### Import Functions

You can import functions in two ways:

**Option 1: Import from the `files` module**
```python
from files import get_user_metadata, get_user_revisions, fetch_all_revisions
```

**Option 2: Import from the specific module**
```python
from files.wikipedia_api import get_user_metadata, get_user_revisions
```

### Examples

#### Get User Metadata
```python
from files import get_user_metadata

# Get metadata for a user
user_info = get_user_metadata("ExampleUser")
print(user_info)
```

#### Get User Revisions
```python
from files import get_user_revisions

# Get all edits by a user
edits = get_user_revisions("ExampleUser")

# Or limit to first 1000 edits
edits = get_user_revisions("ExampleUser", max_edits=1000)
```

#### Get Article Revisions
```python
from files import fetch_all_revisions

# Get all revisions for an article
revisions = fetch_all_revisions("Ukraine")
```

#### Get Article Protection Status
```python
from files import get_article_protection_status

# Check if an article is protected
status = get_article_protection_status("Ukraine")
print(status["status"])  # e.g., "semi-protected", "fully protected", "unprotected"
```

#### Get Talk Page Content
```python
from files import get_talk_wikitext

# Get the wikitext of a talk page
talk_content = get_talk_wikitext("Ukraine")
```

## Available Functions

### User Functions
- `get_user_metadata(username)` - Get user metadata (groups, editcount, registration, etc.)
- `get_user_revisions(username, max_edits=None)` - Get all edits by a user
- `get_user_languages_from_wikitext(username)` - Extract language codes from user page
- `get_all_bots()` - Get list of all bot usernames

### Article Functions
- `get_article_creation_date(title)` - Get article creation date and first revision
- `mw_normalize_and_redirects(title)` - Get canonical title and redirects
- `parse_page_html(title)` - Fetch parsed HTML for a page

### Revision Functions
- `fetch_all_revisions(title, rvprop="user|timestamp|ids|comment")` - Get all revisions for an article

### Talk Page Functions
- `get_talk_wikitext(title)` - Get raw wikitext of talk page
- `fetch_talk_revisions(article_title)` - Get all revisions of talk page

### Protection Functions
- `get_article_protection_status(article_title)` - Get current protection status
- `get_article_protection_history(article_title)` - Get full protection history

### Utility Functions
- `is_ip(user)` - Check if username is an IP address
- `request_api(params)` - Generic API request with retry logic

## Configuration

The module uses the following default configuration:

- **API URL**: `https://en.wikipedia.org/w/api.php`
- **User-Agent**: `DH_Project/1.0 (https://www.epfl.ch/labs/dhlab/; maxime.garambois@epfl.ch)`
- **Default sleep**: 0.5 seconds between requests
- **Default max retries**: 3
- **Default backoff**: 1.0 second

## Notes

- All functions automatically handle pagination
- Functions include retry logic with exponential backoff
- Rate limiting is built-in (0.5 second delay between requests)
- All functions respect Wikipedia's API usage guidelines

