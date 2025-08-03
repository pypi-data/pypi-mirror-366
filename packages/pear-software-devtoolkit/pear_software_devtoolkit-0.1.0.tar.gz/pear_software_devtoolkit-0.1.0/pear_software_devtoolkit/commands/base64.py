import click
import base64
from devtoolkit.utils import console

@click.command(help="Encodes or decodes a string using base64.")
@click.argument('string_to_process')
@click.option('--decode', is_flag=True, help='Decode the string instead of encoding.')
def base64_cmd(string_to_process, decode):
    """Encodes or decodes a string using base64."""
    try:
        if decode:
            decoded_bytes = base64.b64decode(string_to_process)
            console.print(f"[bold green]Decoded string:[/] {decoded_bytes.decode('utf-8')}")
        else:
            encoded_bytes = base64.b64encode(string_to_process.encode('utf-8'))
            console.print(f"[bold green]Encoded string:[/] {encoded_bytes.decode('utf-8')}")
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")