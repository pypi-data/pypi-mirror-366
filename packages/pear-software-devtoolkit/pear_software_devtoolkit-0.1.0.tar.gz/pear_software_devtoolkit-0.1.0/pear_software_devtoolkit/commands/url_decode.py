import click
import urllib.parse
from devtoolkit.utils import console

@click.command(name="url-decode", help="URL-decodes a string.")
@click.argument('string_to_decode')
def url_decode_cmd(string_to_decode):
    """URL-decodes a string."""
    decoded_string = urllib.parse.unquote(string_to_decode)
    console.print(f"[bold green]URL-decoded string:[/] {decoded_string}")