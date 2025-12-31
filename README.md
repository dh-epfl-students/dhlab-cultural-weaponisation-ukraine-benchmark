# Cultural Weaponisation Ukraine Benchmark

## How to use

### Wikipedia API Functions

All Wikipedia API functions have been consolidated into the `files/` module for easy reuse across notebooks.

**Import and use in notebooks:**

```python
# Add project root to path (if needed)
import sys
sys.path.append("/path/to/dhlab-cultural-weaponisation-ukraine-benchmark")

# Import Wikipedia API functions
from files import get_user_metadata, get_user_revisions, fetch_all_revisions

# Use the functions
user_info = get_user_metadata("ExampleUser")
edits = get_user_revisions("ExampleUser", max_edits=1000)
revisions = fetch_all_revisions("Ukraine")
```

See `files/README.md` for complete documentation of all available functions.
