import click
from devtoolkit.utils import console

CHEAT_SHEETS = {
    "git": "... (Git cheat sheet content) ...",
    "docker": "... (Docker cheat sheet content) ...",
}

@click.command(help="Displays cheat sheets for various tools.")
@click.argument('topic', type=click.Choice(CHEAT_SHEETS.keys()))
def cheats_cmd(topic):
    """Displays cheat sheets for various tools."""
    console.print(f"[bold cyan]Cheat Sheet: {topic.capitalize()}[/]")
    console.print(CHEAT_SHEETS[topic])