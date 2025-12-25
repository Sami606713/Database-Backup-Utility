"""
Backup commands for Database Backup Utility.
"""
import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import os

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
def backup(
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", 
        help="Path to configuration file"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output directory for backup"
    ),
    compress: bool = typer.Option(
        True, "--compress/--no-compress",
        help="Enable/disable compression"
    ),
    collections: Optional[str] = typer.Option(
        None, "--collections",
        help="Comma-separated list of collections to backup (MongoDB only)"
    )
):
    """
    Create a database backup.
    
    Examples:
        db-backup backup
        db-backup backup --output ./my-backups
        db-backup backup --config custom-config.yaml
        db-backup backup --collections users,orders (MongoDB)
    """
    try:
        config = load_config(config_path)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)
    
    db_type = config.get("type")
    database = config.get("database")
    output_dir = output or Path(config.get("storage", DEFAULT_BACKUP_DIR))
    
    console.print(f"\n[bold blue]🗄️  Database Backup Utility[/bold blue]")
    console.print(f"   Database Type: {db_type}")
    console.print(f"   Database: {database}")
    console.print(f"   Output: {output_dir}")
    console.print()
    
    # Get connector
    try:
        connector = get_connector(config)
    except ValueError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        raise typer.Exit(code=1)
    
    # Verify connection first
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Verifying database connection...", total=None)
        
        if not connector.verify_connection():
            progress.stop()
            console.print("[bold red]❌ Connection failed. Check your configuration.[/bold red]")
            raise typer.Exit(code=1)
        
        progress.update(task, description="[green]✅ Connection verified[/green]")
    
    # Perform backup based on database type
    console.print()
    
    if db_type == "mongodb":
        _backup_mongodb(connector, output_dir, compress, collections)
    elif db_type == "sqlite":
        _backup_sqlite(connector, config, output_dir, compress)
    elif db_type == "mysql":
        _backup_mysql(connector, config, output_dir, compress)
    elif db_type == "postgres":
        _backup_postgres(connector, config, output_dir, compress)
    else:
        console.print(f"[bold red]Backup not implemented for {db_type}[/bold red]")
        raise typer.Exit(code=1)


def _backup_mongodb(connector: MongoDBConnector, output_dir: Path, compress: bool, collections_str: Optional[str]):
    """Perform MongoDB backup using mongodump."""
    collections_list = None
    if collections_str:
        collections_list = [c.strip() for c in collections_str.split(",")]
        console.print(f"   Collections: {', '.join(collections_list)}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Get stats first
        task = progress.add_task("Getting database statistics...", total=None)
        try:
            connector.connect()
            stats = connector.get_stats()
            progress.update(task, description=f"[green]📊 Database: {stats['collections']} collections, {stats['documents']} documents[/green]")
        except Exception as e:
            progress.update(task, description=f"[yellow]⚠️ Could not get stats: {e}[/yellow]")
            stats = {}
        finally:
            connector.disconnect()
        
        # Perform backup
        task2 = progress.add_task("Creating backup with mongodump...", total=None)
        start_time = datetime.now()
        
        try:
            backup_path = connector.backup(
                output_path=output_dir,
                collections=collections_list,
                compress=compress
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task2, description=f"[green]✅ Backup created successfully[/green]")
            
        except RuntimeError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ Backup failed: {e}[/bold red]")
            raise typer.Exit(code=1)
    
    # Summary
    console.print()
    _print_backup_summary(backup_path, duration, stats)


def _backup_sqlite(connector: SQLiteConnector, config: dict, output_dir: Path, compress: bool):
    """Perform SQLite backup by copying the database file."""
    import shutil
    import gzip
    
    db_path = Path(config.get("database"))
    if not db_path.exists():
        console.print(f"[bold red]❌ Database file not found: {db_path}[/bold red]")
        raise typer.Exit(code=1)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating SQLite backup...", total=None)
        start_time = datetime.now()
        
        if compress:
            backup_name = f"{db_path.stem}_{timestamp}.db.gz"
            backup_path = output_dir / backup_name
            
            with open(db_path, 'rb') as f_in:
                with gzip.open(backup_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            backup_name = f"{db_path.stem}_{timestamp}.db"
            backup_path = output_dir / backup_name
            shutil.copy2(db_path, backup_path)
        
        duration = (datetime.now() - start_time).total_seconds()
        progress.update(task, description=f"[green]✅ Backup created successfully[/green]")
    
    console.print()
    _print_backup_summary(backup_path, duration, {})


def _backup_mysql(connector: MySQLConnector, config: dict, output_dir: Path, compress: bool):
    """Perform MySQL backup using mysqldump."""
    import subprocess
    import gzip
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    database = config.get("database")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating MySQL backup with mysqldump...", total=None)
        start_time = datetime.now()
        
        # Build mysqldump command
        cmd = [
            "mysqldump",
            "-h", config.get("host", "localhost"),
            "-P", str(config.get("port", 3306)),
            "-u", config.get("username"),
            f"-p{config.get('password')}",
            database
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if compress:
                backup_name = f"{database}_{timestamp}.sql.gz"
                backup_path = output_dir / backup_name
                with gzip.open(backup_path, 'wt') as f:
                    f.write(result.stdout)
            else:
                backup_name = f"{database}_{timestamp}.sql"
                backup_path = output_dir / backup_name
                with open(backup_path, 'w') as f:
                    f.write(result.stdout)
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task, description=f"[green]✅ Backup created successfully[/green]")
            
        except subprocess.CalledProcessError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ mysqldump failed: {e.stderr}[/bold red]")
            raise typer.Exit(code=1)
        except FileNotFoundError:
            progress.stop()
            console.print("\n[bold red]❌ mysqldump not found. Install MySQL client tools.[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_backup_summary(backup_path, duration, {})


def _backup_postgres(connector: PostgresConnector, config: dict, output_dir: Path, compress: bool):
    """Perform PostgreSQL backup using pg_dump."""
    import subprocess
    import gzip
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    database = config.get("database")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env["PGPASSWORD"] = config.get("password", "")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating PostgreSQL backup with pg_dump...", total=None)
        start_time = datetime.now()
        
        cmd = [
            "pg_dump",
            "-h", config.get("host", "localhost"),
            "-p", str(config.get("port", 5432)),
            "-U", config.get("username"),
            database
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
            
            if compress:
                backup_name = f"{database}_{timestamp}.sql.gz"
                backup_path = output_dir / backup_name
                with gzip.open(backup_path, 'wt') as f:
                    f.write(result.stdout)
            else:
                backup_name = f"{database}_{timestamp}.sql"
                backup_path = output_dir / backup_name
                with open(backup_path, 'w') as f:
                    f.write(result.stdout)
            
            duration = (datetime.now() - start_time).total_seconds()
            progress.update(task, description=f"[green]✅ Backup created successfully[/green]")
            
        except subprocess.CalledProcessError as e:
            progress.stop()
            console.print(f"\n[bold red]❌ pg_dump failed: {e.stderr}[/bold red]")
            raise typer.Exit(code=1)
        except FileNotFoundError:
            progress.stop()
            console.print("\n[bold red]❌ pg_dump not found. Install PostgreSQL client tools.[/bold red]")
            raise typer.Exit(code=1)
    
    console.print()
    _print_backup_summary(backup_path, duration, {})


def _print_backup_summary(backup_path: Path, duration: float, stats: dict):
    """Print backup summary table."""
    table = Table(title="📦 Backup Summary", show_header=False, border_style="green")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("File", str(backup_path))
    
    if backup_path.exists():
        size_bytes = backup_path.stat().st_size
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes > 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        else:
            size_str = f"{size_bytes} bytes"
        table.add_row("Size", size_str)
    
    table.add_row("Duration", f"{duration:.2f} seconds")
    table.add_row("Timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    if stats:
        if "collections" in stats:
            table.add_row("Collections", str(stats["collections"]))
        if "documents" in stats:
            table.add_row("Documents", str(stats["documents"]))
    
    console.print(table)
    console.print("\n[bold green]✅ Backup completed successfully![/bold green]")


@app.command()
def list_backups(
    directory: Path = typer.Option(
        DEFAULT_BACKUP_DIR, "--dir", "-d",
        help="Directory to list backups from"
    )
):
    """
    List all available backups in the backup directory.
    """
    if not directory.exists():
        console.print(f"[yellow]No backups found. Directory does not exist: {directory}[/yellow]")
        return
    
    backups = list(directory.glob("*"))
    backups = [b for b in backups if b.is_file()]
    
    if not backups:
        console.print(f"[yellow]No backup files found in {directory}[/yellow]")
        return
    
    table = Table(title="📋 Available Backups")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Modified", style="yellow")
    
    for backup in sorted(backups, key=lambda x: x.stat().st_mtime, reverse=True):
        size = backup.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / (1024 * 1024):.2f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size} bytes"
        
        mtime = datetime.fromtimestamp(backup.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        table.add_row(backup.name, size_str, mtime)
    
    console.print(table)
