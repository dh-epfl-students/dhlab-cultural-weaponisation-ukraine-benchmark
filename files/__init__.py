"""
Files module for Wikipedia API utilities.

This module provides functions for interacting with the Wikipedia API.
Import functions directly from this module or from files.wikipedia_api.
"""

from .wikipedia_api import (
    # Configuration
    URL,
    HEADERS,
    DEFAULT_SLEEP,
    DEFAULT_MAX_RETRIES,
    DEFAULT_BACKOFF,
    
    # Utility functions
    is_ip,
    request_api,
    
    # User-related functions
    get_user_metadata,
    get_user_revisions,
    get_user_languages_from_wikitext,
    get_all_bots,
    
    # Article-related functions
    get_article_creation_date,
    mw_normalize_and_redirects,
    parse_page_html,
    
    # Revision-related functions
    fetch_all_revisions,
    
    # Talk page functions
    get_talk_wikitext,
    fetch_talk_revisions,
    
    # Protection-related functions
    get_article_protection_status,
    get_article_protection_history,
)

__all__ = [
    # Configuration
    "URL",
    "HEADERS",
    "DEFAULT_SLEEP",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_BACKOFF",
    
    # Utility functions
    "is_ip",
    "request_api",
    
    # User-related functions
    "get_user_metadata",
    "get_user_revisions",
    "get_user_languages_from_wikitext",
    "get_all_bots",
    
    # Article-related functions
    "get_article_creation_date",
    "mw_normalize_and_redirects",
    "parse_page_html",
    
    # Revision-related functions
    "fetch_all_revisions",
    
    # Talk page functions
    "get_talk_wikitext",
    "fetch_talk_revisions",
    
    # Protection-related functions
    "get_article_protection_status",
    "get_article_protection_history",
]

