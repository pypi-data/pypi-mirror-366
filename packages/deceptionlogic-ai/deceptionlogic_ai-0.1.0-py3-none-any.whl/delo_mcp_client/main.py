from .load_app import app
import typer
from delo_mcp_client import *
from importlib.metadata import version


def version_callback(value: bool = False):
    if value:
        typer.echo(f"deceptionlogic-ai version: {version("deceptionlogic-ai")}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    else:
        pass


def main():
    app()
