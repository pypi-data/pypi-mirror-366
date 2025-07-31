# doc_it/commands/commit.py

import json
import typer
from rich.console import Console

# Import all the necessary utility and database functions
from doc_it.utils.diff_util import (
    take_snapshot,
    get_latest_snapshot_path,
    compare_snapshots,
)
from doc_it.utils.llm_util import generate_change_explanation
from doc_it.db.database import get_codebase_summary, save_explanation

console = Console()
app = typer.Typer()

@app.callback(invoke_without_command=True)
def commit_command(
    message: str = typer.Option(..., "-m", "--message", help="A message describing the changes made.")
):
    """
    Analyzes code changes since the last snapshot, generates AI explanations,
    and saves them to the database.
    """
    console.print(f"\n[bold cyan]Analyzing changes for commit: '{message}'[/bold cyan]")

    # 1. Find the most recent snapshot to compare against.
    old_snapshot_path = get_latest_snapshot_path()
    if not old_snapshot_path:
        console.print("[bold red]Error: No previous snapshot found. Please run 'doc-it init' first.[/bold red]")
        raise typer.Exit(code=1)

    # 2. Take a new snapshot of the project's current state.
    console.print("Taking new snapshot of codebase...")
    new_snapshot_path = take_snapshot()
    if not new_snapshot_path:
        console.print("[yellow]No code files found to snapshot. Nothing to commit.[/yellow]")
        raise typer.Exit()

    # 3. Compare the two snapshots to find what has changed.
    console.print("Comparing snapshots to find changes...")
    with open(old_snapshot_path, 'r') as f:
        old_data = json.load(f)
    with open(new_snapshot_path, 'r') as f:
        new_data = json.load(f)

    changes = compare_snapshots(old_snapshot_path, new_snapshot_path)
    modified_files = changes.get("modified", [])
    added_files = changes.get("added", [])
    # We can also track deleted files if needed in the future
    # deleted_files = changes.get("deleted", [])

    if not modified_files and not added_files:
        console.print("\n[green]No changes detected. Everything is up-to-date.[/green]")
        raise typer.Exit()

    # 4. Get the codebase summary to give the AI context.
    codebase_summary = get_codebase_summary()
    if not codebase_summary:
        console.print("[yellow]Warning: Could not retrieve codebase summary for context.[/yellow]")
        codebase_summary = "A software project." # Fallback summary

    # 5. Iterate over each changed file and generate an explanation.
    all_changes = (("modified", modified_files, "Analyzing modified file"), 
                   (("added", added_files, "Analyzing added file")))

    for change_type, file_list, message_text in all_changes:
        for filepath in file_list:
            console.print(f"-> {message_text}: [cyan]{filepath}[/cyan]")
            old_code = old_data.get(filepath, "") if change_type == "modified" else ""
            new_code = new_data.get(filepath, "")
            
            explanation = generate_change_explanation(filepath, old_code, new_code, codebase_summary)
            if explanation:
                save_explanation(filepath, explanation)
                console.print(f"   [green]✓ Explanation saved.[/green]")
            else:
                console.print(f"   [red]✗ Failed to generate explanation.[/red]")

    console.print("\n[bold green]Change analysis complete![/bold green]")

