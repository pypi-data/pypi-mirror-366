import warnings

import typer

from .commands.cortex import cortex_app
from .commands.init import init_synapso
from .commands.query import cmd_query

warnings.filterwarnings("ignore", category=FutureWarning)

app = typer.Typer()
app.add_typer(cortex_app, name="cortex")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output including debug logs"
    ),
):
    """Synapso CLI - Local-first AI knowledge management."""
    if verbose:
        set_verbose_logging()


@app.command()
def init():
    init_synapso()


@app.command()
def query(
    query_text: str = typer.Option(..., help="The query to execute", metavar="QUERY"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output including debug logs"
    ),
):
    """Query a cortex with a natural language query."""
    if verbose:
        set_verbose_logging()

    result = cmd_query(query_text)
    typer.echo(result)


def set_verbose_logging(): ...


if __name__ == "__main__":
    app()
