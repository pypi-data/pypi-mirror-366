import click
import socket
import requests
from devtoolkit.utils import console

@click.command(help="Displays public and local IP addresses.")
def ipinfo_cmd():
    """Displays public and local IP addresses."""
    try:
        # Local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        console.print(f"[bold green]Local IP:[/] {local_ip}")

        # Public IP
        public_ip = requests.get('https://api.ipify.org').text
        console.print(f"[bold green]Public IP:[/] {public_ip}")

    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")