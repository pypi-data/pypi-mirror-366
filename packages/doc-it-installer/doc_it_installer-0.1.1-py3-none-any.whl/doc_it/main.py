# doc_it/main.py

import typer

# Import the Typer app objects from the command files
from .commands.init import app as init_app
from .commands.commit import app as commit_app
from .commands.generate import app as generate_app # NEW: Import the generate app

# Create the main Typer application
app = typer.Typer(
    name="doc-it",
    help="A modular CLI tool to automatically generate documentation for code changes using a local Ollama LLM.",
    add_completion=False
)

# Register the command modules
app.add_typer(init_app, name="init")
app.add_typer(commit_app, name="commit")
app.add_typer(generate_app, name="generate") # NEW: Register the generate command


# This is the entry point that Typer calls when you run 'doc-it'
if __name__ == "__main__":
    app()
