import click
import re
from devtoolkit.utils import console

@click.command(name="regex-tester", help="Tests a regex pattern against a string.")
@click.argument('pattern')
@click.argument('string')
def regex_tester_cmd(pattern, string):
    """Tests a regex pattern against a string."""
    try:
        matches = re.findall(pattern, string)
        if matches:
            console.print(f"[bold green]Matches found:[/] {matches}")
        else:
            console.print("[bold yellow]No matches found.[/]")
    except re.error as e:
        console.print(f"[bold red]Invalid regex pattern:[/] {e}")