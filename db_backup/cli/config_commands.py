import typer
import yaml
from rich.console import Console
from rich.prompt import Prompt
from pathlib import Path
from db_backup.connectors.sqlite_connector import SQLiteConnector
from db_backup.connectors.postgres_connector import PostgresConnector
from db_backup.connectors.mysql_connector import MySQLConnector
import os

app = typer.Typer()
console = Console()

CONFIG_DIR = Path("configs")
CONFIG_FILE = CONFIG_DIR / "db_config.yaml"

@app.command()
def init():
    """
    Initialize the database backup utility by creating a configuration file template.
    """
    console.print("[bold blue]Welcome to the Database Backup Utility Init[/bold blue]")

    db_type = Prompt.ask("Choose database type", choices=["sqlite", "postgres", "mysql"], default="sqlite")
    
    if db_type == "sqlite":
        config = {
            "type": "sqlite",
            "database": "db.sqlite"
        }
    elif db_type == "postgres":
        config = {
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "username": "your_pg_user",
            "password": "your_pg_password",
            "database": "your_pg_db",
            "storage":"path"
        }
    elif db_type == "mysql":
        config = {
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "username": "your_mysql_user",
            "password": "your_mysql_password",
            "database": "your_mysql_db",
            "storage":"path"
        }

    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
    
    if CONFIG_FILE.exists():
        overwrite = Prompt.ask(f"{CONFIG_FILE} already exists. Overwrite?", choices=["y", "n"], default="n")
        if overwrite == "n":
            console.print("[yellow]Aborted.[/yellow]")
            return

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, sort_keys=False)
        os.makedirs(".backup", exist_ok=True)
    
    console.print(f"[bold green]Configuration template generated at {CONFIG_FILE}[/bold green]")
    console.print("Please edit the file with your actual database credentials.")
    console.print("Then run [bold]python main.py config check[/bold] to verify the connection.")

@app.command()
def check():
    """
    Verify the database connection using the current configuration.
    """
    if not CONFIG_FILE.exists():
        console.print(f"[bold red]Configuration file {CONFIG_FILE} not found.[/bold red]")
        console.print("Run [bold]init[/bold] command first.")
        raise typer.Exit(code=1)

    try:
        with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        console.print(f"[bold red]Error reading configuration file: {e}[/bold red]")
        raise typer.Exit(code=1)

    db_type = config.get("type")
    
    connector = None
    if db_type == "sqlite":
        connector = SQLiteConnector(config)
    elif db_type == "postgres":
        connector = PostgresConnector(config)
    elif db_type == "mysql":
        connector = MySQLConnector(config)
    else:
        console.print(f"[bold red]Unsupported database type: {db_type}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[yellow]Verifying {db_type} connection...[/yellow]")
    if connector.verify_connection():
        console.print("[green]Connection successful![/green]")
    else:
        console.print("[bold red]Connection failed.[/bold red]")
        raise typer.Exit(code=1)
