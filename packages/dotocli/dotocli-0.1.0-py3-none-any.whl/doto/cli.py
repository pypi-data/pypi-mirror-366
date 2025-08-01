"""Typer CLI for Doto package management tool."""

import typer

import doto.package_manager.manager as package_manager
from doto import doto

app = typer.Typer(name="doto", no_args_is_help=False, help="doto - A package management tool")

app.add_typer(package_manager.app, name="package")
app.add_typer(doto.app_host, name="host")


@app.command()
def version() -> None:
    """Show the version of doto."""
    print("doto version 1.0.0")


@app.command()
def init() -> None:
    """Initialize a new manifest file."""
    d = doto.Doto()
    if d.init():
        print("Doto initialized successfully.")
    else:
        print("Failed to initialize Doto.")


if __name__ == "__main__":
    app()
