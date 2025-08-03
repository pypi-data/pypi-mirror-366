import click
import platform
import getpass
from devtoolkit.utils import console

@click.command(help="Displays system and user information.")
def whoami_cmd():
    """Displays system and user information."""
    console.print(f"[bold cyan]System Information:[/]")
    console.print(f"  [bold]User:[/] {getpass.getuser()}")
    console.print(f"  [bold]OS:[/] {platform.system()} {platform.release()}")
    console.print(f"  [bold]Architecture:[/] {platform.machine()}")