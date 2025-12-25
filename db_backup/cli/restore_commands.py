"""
Restore commands for Database Backup Utility.
"""
import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Confirm
from pathlib import Path
from datetime import datetime
from typing import Optional
import os
import subprocess
import gzip
import shutil

from db_backup.connectors.sqlite_connector import SQLiteConnector
from db_backup.connectors.postgres_connector import PostgresConnector
from db_backup.connectors.mysql_connector import MySQLConnector
from db_backup.connectors.mongodb_connector import MongoDBConnector

app = typer.Typer()
console = Console()

CONFIG_DIR = Path("configs")
CONFIG_FILE = CONFIG_DIR / "db_config.yaml"
DEFAULT_BACKUP_DIR = Path(".backup")


def get_connector(config: dict):
    """Get the appropriate connector based on database type."""
    db_type = config.get("type")
    
    if db_type == "sqlite":
        return SQLiteConnector(config)
    elif db_type == "postgres":
        return PostgresConnector(config)
    elif db_type == "mysql":
        return MySQLConnector(config)
    elif db_type == "mongodb":
        return MongoDBConnector(config)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def load_config(config_path: Path = None) -> dict:
    """Load configuration from file."""
    config_file = config_path or CONFIG_FILE
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file {config_file} not found. Run 'init' first.")
    
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


@app.command()
def restore(
    backup_file: Path = typer.Argument(
        ...,
        help="Path to the backup file to restore"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="Path to configuration file"
    ),
    target_database: Optional[str] = typer.Option(
        None, "--target-db", "-t",
        help="Target database name (overrides config)"
    ),
    collections: Optional[str] = typer.Option(
        None, "--collections",
        help="Comma-separated list of collections to restore (MongoDB only)"
    ),
    drop: bool = typer.Option(
        False, "--drop",
        help="Drop existing data before restore"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation prompt"
    )
):
    """
    Restore a database from a backup file.
    
    Examples:
        db-backup restore ./backups/mydb_20240115.archive.gz
        db-backup restore backup.sql.gz --target-db restored_db
        db-backup restore backup.archive.gz --collections users,orders --drop
    """
    # Validate backup file exists
    if not backup_file.exists():
        console.print(f"[bold red]❌ Backup file not found: {backup_file}[/bold red]")
        raise typer.Exit(code=1)
    
    try:
        config = load_config(config_path)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)
    
    db_type = config.get("type")
    database = target_database or config.get("database")
    
    console.print(f"\n[bold blue]🔄 Database Restore Utility[/bold blue]")
    console.print(f"   Database Type: {db_type}")
    console.print(f"   Target Database: {database}")
    console.print(f"   Backup File: {backup_file}")
    if drop:
        console.print(f"   [yellow]⚠️  Drop existing data: Yes[/yellow]")
    console.print()
    
    # Confirmation
    if not force:
        if not Confirm.ask(f"[yellow]This will restore data to '{database}'. Continue?[/yellow]"):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit(code=0)
    
    # Override target database if provided
    if target_database:
        config["database"] = target_database
    
    # Get connector
    try:
        connector = get_connector(config)
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)
    
    # Perform restore based on database type
    if db_type == "mongodb":
        _restore_mongodb(connector, backup_file, collections, drop)
    elif db_type == "sqlite":
        _restore_sqlite(config, backup_file)
    elif db_type == "mysql":
        _restore_mysql(config, backup_file)
    elif db_type == "postgres":
        _restore_postgres(config, backup_file)
    else:
        console.print(f"[bold red]Restore not implemented for {db_type}[/bold red]")
        raise typer.Exit(code=1)


def _restore_mongodb(connector: MongoDBConnector, backup_file: Path, collections_str: Optional[str], drop: bool):
    """Perform MongoDB restore using mongorestore."""
    collections_list = None
    if collections_str:
        collections_list = [c.strip() for c in collections_str.split(",")]
        console.print(f"   Collections: {', '.join(collections_list)}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring MongoDB database...", total=None)
        start_time = datetime.now()
        
        try:
            success = connector.restore(
                backup_path=backup_file,
                collections=collections_list,
                drop=drop
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                progress.update(task, description=f"[green]✅ Restore completed successfully[/green]")
            else:
                progress.update(task, description=f"[red]❌ Restore failed[/red]")
                raise typer.Exit(code=1)
            
        except RuntimeError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ Restore failed: {e}[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_restore_summary(backup_file, duration)


def _restore_sqlite(config: dict, backup_file: Path):
    """Restore SQLite database from backup."""
    target_db = Path(config.get("database"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring SQLite database...", total=None)
        start_time = datetime.now()
        
        try:
            # Handle compressed backup
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(target_db, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_file, target_db)
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task, description=f"[green]✅ Restore completed successfully[/green]")
            
        except Exception as e:
            progress.stop()
            console.print(f"\n[bold red]❌ Restore failed: {e}[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_restore_summary(backup_file, duration)


def _restore_mysql(config: dict, backup_file: Path):
    """Restore MySQL database from backup."""
    database = config.get("database")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring MySQL database...", total=None)
        start_time = datetime.now()
        
        cmd = [
            "mysql",
            "-h", config.get("host", "localhost"),
            "-P", str(config.get("port", 3306)),
            "-u", config.get("username"),
            f"-p{config.get('password')}",
            database
        ]
        
        try:
            # Handle compressed backup
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, 'rt') as f:
                    sql_content = f.read()
            else:
                with open(backup_file, 'r') as f:
                    sql_content = f.read()
            
            result = subprocess.run(
                cmd,
                input=sql_content,
                capture_output=True,
                text=True,
                check=True
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task, description=f"[green]✅ Restore completed successfully[/green]")
            
        except subprocess.CalledProcessError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ mysql restore failed: {e.stderr}[/bold red]")
            raise typer.Exit(code=1)
        except FileNotFoundError:
            progress.stop()
            console.print("\n[bold red]❌ mysql not found. Install MySQL client tools.[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_restore_summary(backup_file, duration)


def _restore_postgres(config: dict, backup_file: Path):
    """Restore PostgreSQL database from backup."""
    database = config.get("database")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env["PGPASSWORD"] = config.get("password", "")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Restoring PostgreSQL database...", total=None)
        start_time = datetime.now()
        
        cmd = [
            "psql",
            "-h", config.get("host", "localhost"),
            "-p", str(config.get("port", 5432)),
            "-U", config.get("username"),
            "-d", database
        ]
        
        try:
            # Handle compressed backup
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, 'rt') as f:
                    sql_content = f.read()
            else:
                with open(backup_file, 'r') as f:
                    sql_content = f.read()
            
            result = subprocess.run(
                cmd,
                input=sql_content,
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task, description=f"[green]✅ Restore completed successfully[/green]")
            
        except subprocess.CalledProcessError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ psql restore failed: {e.stderr}[/bold red]")
            raise typer.Exit(code=1)
        except FileNotFoundError:
            progress.stop()
            console.print("\n[bold red]❌ psql not found. Install PostgreSQL client tools.[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_restore_summary(backup_file, duration)


def _print_restore_summary(backup_file: Path, duration: float):
    """Print restore summary table."""
    table = Table(title="🔄 Restore Summary", show_header=False, border_style="green")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Source File", str(backup_file))
    
    if backup_file.exists():
        size_bytes = backup_file.stat().st_size
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes > 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes} bytes"
        table.add_row("Backup Size", size_str)
    
    table.add_row("Duration", f"{duration:.2f} seconds")
    table.add_row("Completed At", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    console.print(table)
    console.print("\n[bold green]✅ Restore completed successfully![/bold green]")
