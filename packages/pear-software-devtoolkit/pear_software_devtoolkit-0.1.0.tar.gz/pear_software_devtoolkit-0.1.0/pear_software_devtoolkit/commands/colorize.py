import click
from devtoolkit.utils import console

@click.command(help="Colorizes text in the terminal.")
@click.argument('text')
@click.option('--color', default='white', help='Color to use.')
def colorize_cmd(text, color):
    """Colorizes text in the terminal."""
    try:
        console.print(f"[{color}]{text}[/]")
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")