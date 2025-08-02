import typer

from .commands.cortex import cortex_app
from .commands.init import init_synapso
from .commands.query import cmd_query

app = typer.Typer()
app.add_typer(cortex_app, name="cortex")


@app.command()
def init():
    init_synapso()


@app.command()
def query(
    query_text: str = typer.Option(..., help="The query to execute", metavar="QUERY"),
):
    """Query a cortex with a natural language query."""
    result = cmd_query(query_text)
    typer.echo(result)


if __name__ == "__main__":
    app()
