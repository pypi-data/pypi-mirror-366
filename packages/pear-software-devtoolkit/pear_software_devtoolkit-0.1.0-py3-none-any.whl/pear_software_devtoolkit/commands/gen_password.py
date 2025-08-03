import click
import secrets
import string
from devtoolkit.utils import console

@click.command(name="gen-password", help="Generates a secure password.")
@click.option('--length', default=16, help='Length of the password.')
@click.option('--no-symbols', is_flag=True, help='Exclude symbols from the password.')
def gen_password_cmd(length, no_symbols):
    """Generates a secure password."""
    alphabet = string.ascii_letters + string.digits
    if not no_symbols:
        alphabet += string.punctuation
    
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    console.print(f"[bold green]Generated Password:[/] {password}")