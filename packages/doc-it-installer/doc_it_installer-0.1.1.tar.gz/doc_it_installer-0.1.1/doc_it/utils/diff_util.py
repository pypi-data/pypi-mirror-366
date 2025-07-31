# doc_it/utils/diff_util.py

import difflib
import json
import time
from pathlib import Path
from rich.console import Console

from .config_handler import PROJECT_ROOT, DOCIT_DIR, get_config

console = Console()

SNAPSHOTS_DIR = DOCIT_DIR / "snapshots"

def take_snapshot() -> Path | None:
    """
    Scans the current codebase, creates a snapshot of file contents,
    and saves it to a timestamped JSON file.

    Returns:
        The path to the newly created snapshot file, or None on error.
    """
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    config = get_config()
    files_to_include = config.get("files_to_include", [])
    files_to_ignore = config.get("files_to_ignore", [])
    
    snapshot_data = {}
    
    for pattern in files_to_include:
        for filepath in PROJECT_ROOT.rglob(pattern):
            if any(part in files_to_ignore for part in filepath.parts):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    snapshot_data[str(filepath.relative_to(PROJECT_ROOT))] = content
            except Exception:
                pass

    if not snapshot_data:
        return None

    timestamp = int(time.time())
    snapshot_path = SNAPSHOTS_DIR / f"snapshot_{timestamp}.json"
    
    with open(snapshot_path, 'w') as f:
        json.dump(snapshot_data, f, indent=2)
        
    return snapshot_path


def get_latest_snapshot_path() -> Path | None:
    """Finds the most recent snapshot file in the snapshots directory."""
    if not SNAPSHOTS_DIR.exists():
        return None
    
    snapshots = list(SNAPSHOTS_DIR.glob("snapshot_*.json"))
    if not snapshots:
        return None
        
    return max(snapshots, key=lambda p: p.stat().st_mtime)


def compare_snapshots(old_snapshot_path: Path, new_snapshot_path: Path) -> dict:
    """
    Compares two snapshots and identifies added, modified, and deleted files.
    """
    with open(old_snapshot_path, 'r') as f:
        old_data = json.load(f)
    with open(new_snapshot_path, 'r') as f:
        new_data = json.load(f)

    old_files = set(old_data.keys())
    new_files = set(new_data.keys())

    return {
        "added": list(new_files - old_files),
        "deleted": list(old_files - new_files),
        "modified": [
            f for f in old_files & new_files if old_data[f] != new_data[f]
        ],
    }

def get_code_diff(old_content: str, new_content: str) -> str:
    """
    Generates a unified diff string between two versions of a file's content.
    """
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='old',
        tofile='new',
    )
    return "".join(diff)
