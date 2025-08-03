import click
import urllib.parse
from devtoolkit.utils import console

@click.command(name="url-encode", help="URL-encodes a string.")
@click.argument('string_to_encode')
def url_encode_cmd(string_to_encode):
    """URL-encodes a string."""
    encoded_string = urllib.parse.quote(string_to_encode)
    console.print(f"[bold green]URL-encoded string:[/] {encoded_string}")