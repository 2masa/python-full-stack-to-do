from pathlib import Path
from app.cli.service import run_command
from pydantic import Field
from rich.console import Console
from pydantic_settings import BaseSettings, SettingsConfigDict

console = Console()

class Settings(BaseSettings):
    # EdgeDB
    geldb_host: str = Field(alias="GEL_HOST")
    geldb_port: int = Field(alias="GEL_SERVER_PORT")
    geldb_user: str = Field(alias="GEL_SERVER_USER")
    # 'database' is the instance name
    geldb_instance_name: str = Field(alias="GEL_SERVER_INSTANCE_NAME") 
    
    # 'branch' is the branch name
    geldb_branch_name: str = Field(alias="GEL_SERVER_DEFAULT_BRANCH")
    geldb_tls_security: str = "strict"
    geldb_tls_ca_data: str = Field(alias="GEL_SERVER_TLS_CERT")
    geldb_tls_mode: str = Field(alias="GEL_SERVER_TLS_CERT_MODE")    
    geldb_password: str = Field(alias="GEL_SERVER_PASSWORD")    
    geldb_private_key: str = Field(alias="GEL_SERVER_TLS_KEY")    

    # Flask
    flask_port:str = Field(alias="FLASK_PORT")
    flask_host:str = Field(alias="FLASK_HOST")
    # Build Version
    model_config = SettingsConfigDict(env_file="envs/cli.env", extra="ignore")

env_path = Path("envs/cli.env")

if not env_path.exists():
    console.print("[bold cyan]Missing envs/cli.env file. Run: `cli env create` first.[/bold cyan]")
    if not run_command(["uv", "run", "cli", "env", "create"], "Failed to create .env files"):
        console.print("[bold red]Env file creation failed. Please check the error above.[/bold red]")
    console.print("[green]✓ Environment files created.[/green]")

else:
    settings =  Settings()