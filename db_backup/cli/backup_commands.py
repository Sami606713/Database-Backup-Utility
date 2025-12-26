import typer
import yaml
import datetime
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from db_backup.connectors.postgres_connector import PostgresConnector

console = Console()
CONFIG_DIR = Path("configs")
CONFIG_FILE = CONFIG_DIR / "db_config.yaml"

def load_config():
    if not CONFIG_FILE.exists():
        console.print(f"[bold red]Configuration file {CONFIG_FILE} not found.[/bold red]")
        console.print("Run [bold]init[/bold] command first.")
        raise typer.Exit(code=1)

    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[bold red]Error reading configuration file: {e}[/bold red]")
        raise typer.Exit(code=1)

def backup():
    """
    Create a backup of the configured PostgreSQL database.
    """
    config = load_config()
    
    if config.get("type") != "postgres":
        console.print("[bold red]Only PostgreSQL is supported for backup currently.[/bold red]")
        raise typer.Exit(code=1)

    connector = PostgresConnector(config)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    console.print(f"[yellow]Starting backup for database: {config.get('database')}...[/yellow]")
    
    try:
        backup_path = connector.backup_database(timestamp)
        console.print(f"[bold green]Backup created successfully![/bold green]")
        console.print(f"Path: {backup_path}")
    except Exception as e:
        console.print(f"[bold red]Backup failed: {e}[/bold red]")
        raise typer.Exit(code=1)

def restore():
    """
    Restore the PostgreSQL database from a backup file.
    """
    config = load_config()

    if config.get("type") != "postgres":
        console.print("[bold red]Only PostgreSQL is supported for restore currently.[/bold red]")
        raise typer.Exit(code=1)

    connector = PostgresConnector(config)
    
    backups = connector.list_backups()
    if not backups:
        console.print("[yellow]No backups found in .backup/postgres/[/yellow]")
        raise typer.Exit(code=0)

    console.print("[bold blue]Available Backups:[/bold blue]")
    for idx, backup_file in enumerate(backups):
        console.print(f"{idx + 1}. {backup_file}")

    choice = Prompt.ask("Select backup to restore (number)", choices=[str(i+1) for i in range(len(backups))])
    selected_backup = backups[int(choice) - 1]

    confirm = Prompt.ask(f"Are you sure you want to restore [bold]{selected_backup}[/bold]? This will overwrite existing data.", choices=["y", "n"], default="n")
    if confirm == "n":
        console.print("[yellow]Restore aborted.[/yellow]")
        return

    console.print(f"[yellow]Restoring from {selected_backup}...[/yellow]")
    try:
        connector.restore_database(selected_backup)
        console.print(f"[bold green]Database restored successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Restore failed: {e}[/bold red]")
        raise typer.Exit(code=1)
