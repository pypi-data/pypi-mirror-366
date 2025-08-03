import click
import requests
from devtoolkit.utils import console

@click.command(name="git-ignore", help="Generates a .gitignore file.")
@click.argument('technologies', nargs=-1)
def git_ignore_cmd(technologies):
    """Generates a .gitignore file from gitignore.io."""
    if not technologies:
        console.print("[bold red]Error:[/] Please specify at least one technology.")
        return

    try:
        url = f"https://www.toptal.com/developers/gitignore/api/{','.join(technologies)}"
        response = requests.get(url)
        response.raise_for_status()
        
        with open('.gitignore', 'w') as f:
            f.write(response.text)
        
        console.print("[bold green].gitignore file created successfully.[/]")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error fetching .gitignore:[/] {e}")