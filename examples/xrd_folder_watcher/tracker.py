"""
tracker.py

Tracks which files have already been uploaded to avoid duplicate processing.

Uses a local JSON file (processed.json) to store the MD5 hash, status, and
timestamp for each file seen. If a file's content changes (different MD5 hash),
it will be re-processed automatically.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime


def _load(log_path: str) -> dict:
    """Load the processed log from disk, or return an empty dict if it doesn't exist."""
    p = Path(log_path)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def _save(log_path: str, log: dict) -> None:
    """Write the processed log to disk."""
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)


def _md5(file_path) -> str:
    """Compute the MD5 hash of a file's contents."""
    return hashlib.md5(Path(file_path).read_bytes()).hexdigest()


def needs_processing(filename: str, file_path, log_path: str) -> bool:
    """Return True if the file is new or its content has changed since last upload."""
    log = _load(log_path)
    current_hash = _md5(file_path)
    entry = log.get(filename)
    if entry is None:
        return True  # file has never been seen before
    return entry.get("hash") != current_hash  # same name, but content has changed


def record(filename: str, file_path, status: str, log_path: str) -> None:
    """Save the processing outcome for a file.

    status: 'uploaded', 'skipped', or 'failed'
    """
    log = _load(log_path)
    log[filename] = {
        "status": status,
        "hash": _md5(file_path),
        "timestamp": datetime.now().isoformat(),
    }
    _save(log_path, log)
