from .load_app import app
import typer
import sys
from honeydb_mcp_client.configuration import config
from honeydb_mcp_client.llm_client import chat
from importlib.metadata import version

def version_callback(value: bool = False):
    if value:
        typer.echo(f"delo-mcp-client version: {version("delo_mcp_client")}")
        raise typer.Exit()

@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."),
):
    pass

def main():
    app()