import click
import os
import datetime
from devtoolkit.utils import console

@click.command(name="file-stats", help="Displays statistics for a file.")
@click.argument('file_path', type=click.Path(exists=True))
def file_stats_cmd(file_path):
    """Displays statistics for a file."""
    try:
        stats = os.stat(file_path)
        console.print(f"[bold cyan]Stats for {file_path}:[/]")
        console.print(f"  [bold]Size:[/] {stats.st_size} bytes")
        console.print(f"  [bold]Last modified:[/] {datetime.datetime.fromtimestamp(stats.st_mtime)}")
        console.print(f"  [bold]Created:[/] {datetime.datetime.fromtimestamp(stats.st_ctime)}")
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")