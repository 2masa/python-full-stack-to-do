import subprocess
import time
from app.controller import run_command
import rich_click as click
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
# Import the getter function for settings

# Import the sync client to check the DB
from app.db import get_sync_client

console = Console()

# --- NEW HELPER FUNCTION ---
def check_db_connection() -> bool:
    """
    Polls the database to see if it's ready to accept connections.
    """
    console.print("\n[cyan]Step 4: Waiting for the database to initialize...[/cyan]")
    with Status("Attempting to connect to the database...", spinner="clock") as status:
        for i in range(15): # Try for 30 seconds (15 * 2s)
            try:
                # get_sync_client will lazy-load settings
                with get_sync_client() as client:
                    client.query_single("SELECT 1")
                
                console.print("[green]✓ Database connection successful![/green]")
                return True
            except Exception as e:
                status.update(f"Attempt {i+1}/15 failed. Retrying in 2s... (Error: {e})")
                time.sleep(2)
                
    console.print("[bold red]Error: Could not connect to the database after 30 seconds.[/bold red]")
    console.print("Please check the 'todo_db' container logs: 'docker compose logs todo_db'")
    return False

# --- SERVICE COMMANDS ---

@click.group(name="service")
def service() -> None:
    """Manage application services using Docker Compose."""
    pass

@service.command(name="start")
def start_services() -> None:
    """Start all services in detached mode."""
    console.print("[cyan]Starting all services...[/cyan]")
    # UPDATED: using 'docker', 'compose'
    run_command(
        ["docker", "compose", "-f", "docker-compose.yml", "up", "-d", "--build"],
        "Failed to start services."
    )
    console.print("[bold green]Services started successfully.[/bold green]")

@service.command(name="stop")
def stop_services() -> None:
    """Stop all running services."""
    console.print("[cyan]Stopping all services...[/cyan]")
    # UPDATED: using 'docker', 'compose'
    run_command(
        ["docker", "compose", "-f", "docker-compose.yml", "stop"],
        "Failed to stop services."
    )
    console.print("[bold green]Services stopped.[/bold green]")

@service.command(name="down")
def down_services() -> None:
    """Stop and remove all services (keeps volumes)."""
    console.print("[cyan]Stopping and removing service containers...[/cyan]")
    # UPDATED: using 'docker', 'compose'
    run_command(
        ["docker", "compose", "-f", "docker-compose.yml", "down"],
        "Failed to bring services down."
    )
    console.print("[bold green]Services are down.[/bold green]")

@service.command(name="purge")
def purge_services() -> None:
    """Stop/remove services AND delete volumes (all data)."""
    console.print("[bold red]WARNING: This will stop all services and permanently delete all data (database, etc).[/bold red]")
    if click.confirm("Are you sure you want to continue?", abort=True):
        console.print("[cyan]Purging services and volumes...[/cyan]")
        # UPDATED: using 'docker', 'compose'
        run_command(
            ["docker", "compose", "-f", "docker-compose.yml", "down", "-v"],
            "Failed to purge services and volumes."
        )
        console.print("[bold green]Services and volumes purged.[/bold green]")

# --- YOUR CORRECTED FUNCTION ---

@service.command(name="start-dev")
def start_beginner() -> None:
    """Guided first-time setup for developers."""
    console.rule("[bold magenta]Developer First-Time Setup[/bold magenta]", style="magenta")
    
    # --- Step 1: Purge old setup ---
    console.print("[cyan]Step 1: Purging any existing setup (containers & data)...[/cyan]")
    if not run_command(["uv", "run", "cli", "service", "purge"], "Failed to purge services"):
        console.print("[bold red]Purge failed. Please check Docker and try again.[/bold red]")
        return
    console.print("[green]✓ Environment purged.[/green]")

    # --- Step 2: Create .env files ---
    console.print("\n[cyan]Step 2: Creating new .env files...[/cyan]")
    if not run_command(["uv", "run", "cli", "env", "create"], "Failed to create .env files"):
        console.print("[bold red]Env file creation failed. Please check the error above.[/bold red]")
        return
    console.print("[green]✓ Environment files created.[/green]")
    
    # --- Step 3: Start services ---
    console.print("\n[cyan]Step 3: Starting all Docker services...[/cyan]")
    with Status("Running 'docker compose up -d --build'...", spinner="dots"):
        # UPDATED: using 'docker', 'compose'
        if not run_command(["docker", "compose", "-f", "docker-compose.yml", "up", "-d", "--build"], "Failed to start services"):
            return
    console.print("[green]✓ Services started.[/green]")

    # --- Step 4: Check DB Connection ---
    # This calls the new helper function
    if not check_db_connection():
        return    # stop the script

    # --- Step 5: Create root user ---
    console.print("\n[cyan]Step 5: Creating root user...[/cyan]")
    console.print("This will now run the 'user create-root' command.")
    
    if not run_command(["uv", "run", "cli", "user", "create-root"], "Failed to create root user"):
         console.print("[bold red]Root user creation failed. See error above.[/bold red]")
         return
    console.print("[green]✓ Root user check/creation complete.[/green]")

    # --- Step 6: Create user ---
    console.print("\n[cyan]Step 6: creating End user...[/cyan]")
    if not run_command(["uv", "run", "cli", "user", "create"], "Failed to create End user"):
         console.print("[bold red]End User creation failed. See error above.[/bold red]")
         return
    console.print("[green]✓ End User check/creation complete.[/green]")
    
    # --- Step 7: Show link ---
    console.print("\n[bold green]🎉 Setup Complete! 🎉[/bold green]")
    from app.config import settings
    host = "localhost" if settings.flask_host == "0.0.0.0" else settings.flask_host
    url = f"http://{host}:{settings.flask_port}"
    console.print(Panel(
        f"You can now access the web UI at:\n\n[link={url}]{url}[/link]",
        title="Application Ready",
        border_style="green"
    ))