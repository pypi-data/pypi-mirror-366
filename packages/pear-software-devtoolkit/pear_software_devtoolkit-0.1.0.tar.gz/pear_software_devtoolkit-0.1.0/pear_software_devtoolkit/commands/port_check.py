import click
import socket
from devtoolkit.utils import console

@click.command(name="port-check", help="Checks if a port is free on localhost.")
@click.argument('port', type=int)
def port_check_cmd(port):
    """Checks if a port is free on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            console.print(f"[bold green]Port {port} is free.[/]")
        except OSError:
            console.print(f"[bold red]Port {port} is already in use.[/]")