# doc_it/commands/init.py

import os
from pathlib import Path
import typer
from rich.console import Console

# Import our utility and database functions
from doc_it.utils.config_handler import (
    PROJECT_ROOT,
    DEFAULT_CONFIG,
    ensure_docit_dir_exists,
    save_config,
    get_config,
)
from doc_it.db.database import initialize, save_codebase_summary
from doc_it.utils.llm_util import generate_codebase_summary
from doc_it.utils.diff_util import take_snapshot # NEW: Import take_snapshot

console = Console()
app = typer.Typer()

def collect_codebase_content() -> str:
    """
    Scans the project directory and collects the content of all files
    specified in the configuration.
    """
    console.print("[cyan]Scanning project files...[/cyan]")
    config = get_config()
    files_to_include = config.get("files_to_include", [])
    files_to_ignore = config.get("files_to_ignore", [])
    
    all_content = []
    
    for pattern in files_to_include:
        for filepath in PROJECT_ROOT.rglob(pattern):
            if any(part in files_to_ignore for part in filepath.parts):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    all_content.append(f"--- File: {filepath.relative_to(PROJECT_ROOT)} ---\n{content}\n")
            except Exception as e:
                console.print(f"[yellow]Could not read file {filepath}: {e}[/yellow]")

    return "\n".join(all_content)

@app.callback(invoke_without_command=True)
def init_command():
    """
    Initializes a new project for Doc-It.
    - Creates the .docit directory and config file.
    - Initializes the database.
    - Scans the codebase and generates an initial AI summary.
    - Takes the initial snapshot.
    """
    console.print("[bold green]Initializing Doc-It for this project...[/bold green]")

    ensure_docit_dir_exists()
    save_config(DEFAULT_CONFIG)
    console.print("✅ Created .docit directory and config file.")

    if initialize():
        console.print("✅ Database initialized successfully.")
    else:
        console.print("[bold red]Error: Failed to initialize the database.[/bold red]")
        raise typer.Exit(code=1)

    codebase_content = collect_codebase_content()
    if not codebase_content:
        console.print("[yellow]Warning: No source code files found to summarize.[/yellow]")
        return

    summary = generate_codebase_summary(codebase_content)
    if not summary:
        console.print("[bold red]Error: Could not generate codebase summary.[/bold red]")
        raise typer.Exit(code=1)

    save_codebase_summary(summary)
    console.print("✅ AI-generated codebase summary has been created and saved.")
    
    # --- THIS IS THE FIX ---
    # Take the initial snapshot of the codebase after setup.
    console.print("Taking initial snapshot...")
    if take_snapshot():
        console.print("✅ Initial snapshot created.")
    else:
        console.print("[yellow]Warning: Could not create initial snapshot.[/yellow]")

    console.print("\n[bold green]Doc-It initialization complete![/bold green]")
