import click
import uuid
from devtoolkit.utils import console

@click.command(help="Generates a version 4 UUID.")
def uuid_cmd():
    """Generates a version 4 UUID."""
    generated_uuid = uuid.uuid4()
    console.print(f"[bold green]Generated UUID v4:[/] {generated_uuid}")