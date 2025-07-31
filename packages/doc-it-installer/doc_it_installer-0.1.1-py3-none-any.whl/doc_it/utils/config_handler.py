# doc_it/utils/config_handler.py

import json
from pathlib import Path

# --- Path Definitions ---
# Find the project root by looking for a .git folder. This makes the tool
# work correctly even if you run it from a sub-directory.
try:
    PROJECT_ROOT = Path.cwd().joinpath('.git').resolve().parent
except FileNotFoundError:
    # As a fallback, use the current working directory if not in a git repo
    PROJECT_ROOT = Path.cwd()

# All of Doc-It's internal files will be stored in a hidden .docit directory
DOCIT_DIR = PROJECT_ROOT / ".docit"
CONFIG_FILE = DOCIT_DIR / "config.json"
DB_FILE = DOCIT_DIR / "docit.db"


# --- Default Configuration ---
# These are the settings that will be created during the 'init' command.
DEFAULT_CONFIG = {
    "author": "Your Name",
    "ollama_model_name": "llama3:latest",
    "ollama_api_endpoint": "http://localhost:11434/api/generate",
    "files_to_include": ["*.py", "*.js", "*.html", "*.css"],
    "files_to_ignore": ["__pycache__", ".venv", ".docit"]
}


# --- Core Functions ---
def ensure_docit_dir_exists():
    """Creates the .docit directory in the project root if it doesn't already exist."""
    DOCIT_DIR.mkdir(exist_ok=True)

def get_config() -> dict:
    """Loads the configuration from the JSON file. Returns default if not found."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config_data: dict):
    """Saves the given dictionary to the config.json file."""
    ensure_docit_dir_exists()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)
