import typer
from db_backup.cli import config_commands
from db_backup.cli import backup_commands

app = typer.Typer()

app.add_typer(config_commands.app, name="config", help="Configuration commands")
# We can also register init directly at the top level for better UX
app.command(name="init")(config_commands.init)

app.command(name="backup")(backup_commands.backup)
app.command(name="restore")(backup_commands.restore)

if __name__ == "__main__":
    app()
