"""
Legacy module for backward compatibility.

This module now imports from wikipedia_api. 
For new code, use: from files import get_user_metadata, get_user_revisions
"""

# Import from the consolidated wikipedia_api module
from .wikipedia_api import (
    URL,
    HEADERS,
    get_user_metadata,
    get_user_revisions,
)

# Re-export for backward compatibility
__all__ = ["URL", "HEADERS", "get_user_metadata", "get_user_revisions"]