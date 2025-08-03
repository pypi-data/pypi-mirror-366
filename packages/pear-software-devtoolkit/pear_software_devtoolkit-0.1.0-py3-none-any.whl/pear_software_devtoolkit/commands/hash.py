import click
import hashlib
from devtoolkit.utils import console

@click.command(help="Hashes a string using a specified algorithm.")
@click.argument('string_to_hash')
@click.option('--algorithm', default='sha256', help='Hash algorithm (md5, sha1, sha256, sha512)', type=click.Choice(['md5', 'sha1', 'sha256', 'sha512']))
def hash_cmd(string_to_hash, algorithm):
    """Hashes a string using a specified algorithm."""
    try:
        hasher = hashlib.new(algorithm)
        hasher.update(string_to_hash.encode('utf-8'))
        hashed_string = hasher.hexdigest()
        console.print(f"[bold green]Hashed string ({algorithm}):[/] {hashed_string}")
    except ValueError:
        console.print(f"[bold red]Error:[/] Invalid algorithm specified.")