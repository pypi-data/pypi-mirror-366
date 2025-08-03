import click
import os
from devtoolkit.utils import console

@click.command(help="Creates a basic project structure.")
@click.argument('project_name')
@click.option('--type', 'project_type', default='generic', help='Project type (e.g., python, web).')
def mkproject_cmd(project_name, project_type):
    """Creates a basic project structure."""
    try:
        os.makedirs(project_name, exist_ok=True)
        console.print(f"[bold green]Project '{project_name}' created.[/]")

        if project_type == 'python':
            os.makedirs(os.path.join(project_name, project_name), exist_ok=True)
            with open(os.path.join(project_name, project_name, '__init__.py'), 'w') as f:
                pass
            with open(os.path.join(project_name, 'README.md'), 'w') as f:
                f.write(f"# {project_name}\n")
            console.print("  [bold]Python structure created.[/]")

    except Exception as e:
        console.print(f"[bold red]An error occurred:[/] {e}")