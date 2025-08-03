import click
from devtoolkit.utils import console

@click.command(help="Creates a .env file from user input.")
def envgen_cmd():
    """Creates a .env file from user input."""
    variables = {}
    console.print("Enter environment variables (KEY=VALUE). Type 'done' when finished.")
    while True:
        entry = click.prompt("Variable", default="", show_default=False)
        if entry.lower() == 'done':
            break
        if '=' in entry:
            key, value = entry.split('=', 1)
            variables[key.strip()] = value.strip()
        else:
            console.print("[bold yellow]Invalid format.[/] Please use KEY=VALUE.")

    with open('.env', 'w') as f:
        for key, value in variables.items():
            f.write(f"{key}={value}\n")
    
    console.print("[bold green].env file created successfully.[/]")