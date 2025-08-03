import click
import re
from devtoolkit.utils import console

@click.command(help="Converts text to a URL-friendly slug.")
@click.argument('text')
def slugify_cmd(text):
    """Converts text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    console.print(f"[bold green]Slug:[/] {text}")