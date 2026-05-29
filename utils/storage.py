import os
from pathlib import Path

# Where persistent files (pickle caches) live.
# On Railway, attach a Volume and set DATA_DIR to its mount path
# (e.g. /data) so caches survive restarts and redeploys. Locally this
# defaults to the project directory, preserving the original behavior.
DATA_DIR = Path(os.getenv('DATA_DIR', '.'))
DATA_DIR.mkdir(parents=True, exist_ok=True)


def data_path(filename):
    """Return the absolute path for a persistent data file."""
    return str(DATA_DIR / filename)
