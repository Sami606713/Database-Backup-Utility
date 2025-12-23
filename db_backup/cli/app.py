import typer
from db_backup.cli import config_commands

app = typer.Typer()

app.add_typer(config_commands.app, name="config", help="Configuration commands")
# We can also register init directly at the top level for better UX
app.command(name="init")(config_commands.init)

if __name__ == "__main__":
    app()
