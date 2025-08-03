import click
from devtoolkit.utils import console

# A simple conversion map. A more robust solution would use a library.
CONVERSIONS = {
    'length': {
        'm_to_ft': 3.28084,
        'ft_to_m': 0.3048,
    },
    'temp': {
        'c_to_f': lambda c: (c * 9/5) + 32,
        'f_to_c': lambda f: (f - 32) * 5/9,
    }
}

@click.command(name="unit-convert", help="Converts units.")
@click.argument('value', type=float)
@click.argument('from_unit')
@click.argument('to_unit')
def unit_convert_cmd(value, from_unit, to_unit):
    """Converts units (e.g., 10 m ft)."""
    conversion_key = f"{from_unit}_to_{to_unit}"
    
    for category in CONVERSIONS.values():
        if conversion_key in category:
            conversion = category[conversion_key]
            if callable(conversion):
                result = conversion(value)
            else:
                result = value * conversion
            console.print(f"[bold green]Result:[/] {value} {from_unit} = {result:.4f} {to_unit}")
            return

    console.print(f"[bold red]Error:[/] Conversion from '{from_unit}' to '{to_unit}' is not supported.")