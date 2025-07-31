# doc_it/commands/generate.py

import typer
from rich.console import Console

# Import all our generator functions
from doc_it.utils.doc_generator import generate_markdown, generate_docx, generate_latex

console = Console()
app = typer.Typer()

@app.callback(invoke_without_command=True)
def generate_command(
    output_format: str = typer.Option(
        "md", 
        "--format", 
        "-f", 
        help="Output format: md, docx, or tex"
    )
):
    """
    Generates the final documentation file from all saved explanations.
    """
    console.print(f"\n[cyan]Generating documentation in {output_format.upper()} format...[/cyan]")
    
    output_path = None
    if output_format.lower() == 'md':
        output_path = generate_markdown()
    elif output_format.lower() == 'docx':
        output_path = generate_docx()
    elif output_format.lower() == 'tex':
        output_path = generate_latex()
    else:
        console.print(f"[bold red]Error: Invalid format '{output_format}'. Please use 'md', 'docx', or 'tex'.[/bold red]")
        raise typer.Exit(code=1)

    if output_path:
        console.print(f"\n[bold green]Documentation generated successfully![/bold green]")
        console.print(f"File saved at: {output_path}")
    else:
        console.print("\n[bold yellow]Could not generate documentation. No data found.[/bold yellow]")

