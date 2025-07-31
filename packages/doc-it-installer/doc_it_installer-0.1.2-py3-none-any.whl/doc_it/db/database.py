# doc_it/db/database.py

import sqlite3
from rich.console import Console
from doc_it.utils.config_handler import DB_FILE # Import the DB_FILE path

console = Console()

def get_connection():
    """Establishes a connection to the SQLite database."""
    try:
        # Using check_same_thread=False is generally safe for CLI tools
        # where operations are sequential.
        con = sqlite3.connect(DB_FILE, check_same_thread=False)
        return con
    except sqlite3.Error as e:
        console.print(f"[bold red]Database connection error: {e}[/bold red]")
        return None

def initialize():
    """
    Initializes the database and creates the three required tables if they don't exist.
    This function is safe to run multiple times.
    """
    con = get_connection()
    if con is None:
        return False
        
    try:
        with con:
            cur = con.cursor()
            # Table 1: For storing the high-level summary of the entire codebase
            cur.execute("""
                CREATE TABLE IF NOT EXISTS codebase_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table 2: For storing explanations of changes to specific files
            cur.execute("""
                CREATE TABLE IF NOT EXISTS explanations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table 3: For logging detailed file changes (can be used later)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    old_code TEXT,
                    new_code TEXT,
                    explanation_id INTEGER,
                    user_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (explanation_id) REFERENCES explanations (id)
                )
            """)
        return True
    except sqlite3.Error as e:
        console.print(f"[bold red]Error initializing database tables: {e}[/bold red]")
        return False
    finally:
        if con:
            con.close()

def save_codebase_summary(summary: str):
    """Saves the given codebase summary to the database."""
    con = get_connection()
    if con is None: return
    try:
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO codebase_summary (summary) VALUES (?)", (summary,))
    except sqlite3.Error as e:
        console.print(f"[bold red]Error saving codebase summary: {e}[/bold red]")
    finally:
        if con: con.close()

def get_codebase_summary() -> str | None:
    """Retrieves the most recent codebase summary from the database."""
    con = get_connection()
    if con is None: return None
    try:
        with con:
            cur = con.cursor()
            # Get the most recent summary, as it's the most relevant one
            cur.execute("SELECT summary FROM codebase_summary ORDER BY timestamp DESC LIMIT 1")
            result = cur.fetchone()
            return result[0] if result else None
    except sqlite3.Error as e:
        console.print(f"[bold red]Error retrieving codebase summary: {e}[/bold red]")
        return None
    finally:
        if con: con.close()

def save_explanation(filepath: str, explanation: str) -> int | None:
    """Saves a file change explanation and returns its unique ID."""
    con = get_connection()
    if con is None: return None
    try:
        with con:
            cur = con.cursor()
            cur.execute("INSERT INTO explanations (filepath, explanation) VALUES (?, ?)", (filepath, explanation))
            return cur.lastrowid
    except sqlite3.Error as e:
        console.print(f"[bold red]Error saving explanation: {e}[/bold red]")
        return None
    finally:
        if con: con.close()

def get_explanations() -> list[dict]:
    """Retrieves all stored explanations, returning them as a list of dictionaries."""
    con = get_connection()
    if con is None: return []
    try:
        with con:
            con.row_factory = sqlite3.Row # This allows accessing columns by name
            cur = con.cursor()
            cur.execute("SELECT filepath, explanation, timestamp FROM explanations ORDER BY timestamp ASC")
            rows = cur.fetchall()
            # Convert the sqlite3.Row objects to standard Python dictionaries
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        console.print(f"[bold red]Error retrieving explanations: {e}[/bold red]")
        return []
    finally:
        if con: con.close()
