import click
import json
from devtoolkit.utils import console

@click.command(help="Formats and validates a JSON file.")
@click.argument('file_path', type=click.Path(exists=True))
def jsonfmt_cmd(file_path):
    """Formats and validates a JSON file."""
    try:
        with open(file_path, 'r+') as f:
            data = json.load(f)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        console.print(f"[bold green]JSON file '{file_path}' has been formatted and validated.[/]")
    except json.JSONDecodeError:
        console.print(f"[bold red]Error:[/] Invalid JSON format in '{file_path}'.")
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")