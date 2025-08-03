import click
import time
from devtoolkit.utils import console

@click.command(help="Starts a timer from the terminal.")
@click.argument('duration', type=int)
def timer_cmd(duration):
    """Starts a timer from the terminal."""
    console.print(f"Starting timer for {duration} seconds...")
    with console.status("[bold green]Running...") as status:
        for i in range(duration):
            time.sleep(1)
            status.update(f"[bold green]Running... {duration - i - 1}s left[/]")
    console.print("[bold green]Time's up![/]")