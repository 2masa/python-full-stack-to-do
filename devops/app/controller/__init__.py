import subprocess

from rich.console import Console

console = Console()

def run_command(cmd_list, error_msg, capture_output=False, check=True):
    """Helper to run shell commands and handle errors."""
    try:
        # Note: We run commands from the 'devops' dir, so docker-compose path is relative
        result = subprocess.run(
            cmd_list, 
            check=check, 
            capture_output=capture_output, 
            text=True,
            encoding='utf-8', # Explicitly set encoding
            cwd="." # Run from the devops directory
        )
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Error: {error_msg}[/bold red]")
        if e.stderr:
            console.print(f"Details: {e.stderr}")
        return False
    except FileNotFoundError:
        console.print(f"[bold red]Error: Command not found.[/bold red]")
        console.print(f"Please ensure '{cmd_list[0]}' is installed and in your PATH.")
        return False