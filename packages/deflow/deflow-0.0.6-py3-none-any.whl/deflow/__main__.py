import typer

main = typer.Typer()


@main.command()
def hello(name: str):
    typer.echo(f"Hello {name}, this is DeFlow package.")


@main.command()
def version():
    """Return the version of the current installed DeFlow package."""
    from deflow.__about__ import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    main()
