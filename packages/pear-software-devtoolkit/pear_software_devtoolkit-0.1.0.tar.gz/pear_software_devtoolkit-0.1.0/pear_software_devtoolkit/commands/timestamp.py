import click
import datetime
from devtoolkit.utils import console

@click.command(help="Converts timestamps and dates.")
@click.argument('value', required=False)
def timestamp_cmd(value):
    """Converts timestamps and dates."""
    if value is None:
        now = datetime.datetime.now()
        console.print(f"[bold green]Current Timestamp:[/] {int(now.timestamp())}")
        console.print(f"[bold green]Current Datetime (UTC):[/] {now.isoformat()}")
        return

    try:
        # Try to convert from timestamp
        ts = int(value)
        dt_object = datetime.datetime.fromtimestamp(ts)
        console.print(f"[bold green]Datetime from timestamp {ts}:[/] {dt_object.isoformat()}")
    except ValueError:
        # Try to convert from ISO date string
        try:
            dt_object = datetime.datetime.fromisoformat(value)
            console.print(f"[bold green]Timestamp from date {value}:[/] {int(dt_object.timestamp())}")
        except ValueError:
            console.print("[bold red]Error:[/] Invalid timestamp or date format. Use integer timestamp or ISO 8601 format.")