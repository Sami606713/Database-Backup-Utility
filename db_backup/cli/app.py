"""
Database Backup Utility - Main CLI Application.

A production-ready CLI tool for backing up and restoring databases.
Supports: SQLite, MySQL, PostgreSQL, MongoDB
"""
import typer
from rich.console import Console

from db_backup.cli import config_commands
from db_backup.cli import backup_commands
from db_backup.cli import restore_commands

app = typer.Typer(
    name="db-backup",
    help="🗄️  Database Backup Utility - Backup and restore any database",
    add_completion=False
)
console = Console()

# Register command groups
app.add_typer(config_commands.app, name="config", help="Configuration management commands")
app.add_typer(backup_commands.app, name="backup", help="Backup operations")
app.add_typer(restore_commands.app, name="restore", help="Restore operations")

# Register top-level shortcuts for better UX
app.command(name="init")(config_commands.init)
app.command(name="check")(config_commands.check)


@app.command()
def version():
    """Show version information."""
    console.print("[bold blue]Database Backup Utility[/bold blue]")
    console.print("Version: 0.1.0")
    console.print("\nSupported Databases:")
    console.print("  • SQLite")
    console.print("  • MySQL")
    console.print("  • PostgreSQL")
    console.print("  • MongoDB")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    🗄️  Database Backup Utility
    
    A CLI tool for backing up and restoring databases.
    """
    if ctx.invoked_subcommand is None:
        console.print("\n[bold blue]🗄️  Database Backup Utility[/bold blue]")
        console.print("\nQuick Start:")
        console.print("  1. Run [cyan]db-backup init[/cyan] to create config")
        console.print("  2. Run [cyan]db-backup check[/cyan] to verify connection")
        console.print("  3. Run [cyan]db-backup backup backup[/cyan] to create backup")
        console.print("  4. Run [cyan]db-backup restore restore <file>[/cyan] to restore")
        console.print("\nUse [cyan]--help[/cyan] for more information.\n")


if __name__ == "__main__":
    app()
