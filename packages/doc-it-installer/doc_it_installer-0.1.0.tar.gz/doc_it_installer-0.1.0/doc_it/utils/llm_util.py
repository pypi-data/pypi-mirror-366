# doc_it/utils/llm_util.py

import json
import requests
from rich.console import Console
from rich.spinner import Spinner

from .config_handler import get_config

console = Console()

def send_to_ollama(prompt: str, model_name: str, api_endpoint: str) -> str | None:
    """
    Sends a prompt to the specified Ollama API endpoint and streams the response.

    Args:
        prompt: The full prompt to send to the LLM.
        model_name: The name of the Ollama model to use (e.g., 'llama3:latest').
        api_endpoint: The URL of the Ollama generate API.

    Returns:
        The complete generated response as a string, or None if an error occurs.
    """
    try:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False  # We'll get the full response at once
        }

        with console.status(f"[bold cyan]Asking '{model_name}' for insights...[/bold cyan]", spinner="dots") as status:
            response = requests.post(api_endpoint, json=payload)
            response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            return response_data.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Error: Could not connect to Ollama API at '{api_endpoint}'.[/bold red]")
        console.print("Please ensure Ollama is running and accessible.")
        return None
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]An error occurred while communicating with Ollama: {e}[/bold red]")
        return None


def generate_codebase_summary(codebase_content: str) -> str | None:
    """
    Asks the LLM to generate a high-level summary of the entire codebase.

    Args:
        codebase_content: A single string containing the content of all relevant files.

    Returns:
        The AI-generated summary as a string.
    """
    config = get_config()
    model_name = config.get("ollama_model_name")
    api_endpoint = config.get("ollama_api_endpoint")

    prompt = (
        "You are an expert software architect. Below is the content of an entire codebase. "
        "Your task is to provide a high-level summary of the project.\n"
        "Describe its main purpose, the technologies used, and the overall structure. "
        "Keep the summary concise and to the point.\n\n"
        "--- CODEBASE ---\n"
        f"{codebase_content}\n"
        "--- END CODEBASE ---\n\n"
        "Summary:"
    )
    
    console.print("\n[cyan]Generating codebase summary...[/cyan]")
    return send_to_ollama(prompt, model_name, api_endpoint)


def generate_change_explanation(filepath: str, old_code: str, new_code: str, codebase_summary: str) -> str | None:
    """
    Asks the LLM to explain the changes made to a single file.

    Args:
        filepath: The path to the file that was changed.
        old_code: The content of the file before the change.
        new_code: The content of the file after the change.
        codebase_summary: The high-level summary of the project for context.

    Returns:
        The AI-generated explanation as a string.
    """
    config = get_config()
    model_name = config.get("ollama_model_name")
    api_endpoint = config.get("ollama_api_endpoint")

    prompt = (
        f"You are an expert code reviewer. The project you are reviewing has the following purpose: '{codebase_summary}'.\n\n"
        f"A change was made to the file '{filepath}'.\n\n"
        "--- OLD CODE ---\n"
        f"{old_code}\n"
        "--- END OLD CODE ---\n\n"
        "--- NEW CODE ---\n"
        f"{new_code}\n"
        "--- END NEW CODE ---\n\n"
        "Please explain this change. What was the purpose, and what was the impact? "
        "Provide a clear, concise explanation suitable for documentation."
    )

    console.print(f"\n[cyan]Generating explanation for '{filepath}'...[/cyan]")
    return send_to_ollama(prompt, model_name, api_endpoint)

