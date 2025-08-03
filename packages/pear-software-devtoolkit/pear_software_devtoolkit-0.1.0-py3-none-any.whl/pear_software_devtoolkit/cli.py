import click
from .utils import console

# Import command functions
from .commands.uuid import uuid_cmd
from .commands.hash import hash_cmd
from .commands.jsonfmt import jsonfmt_cmd
from .commands.envgen import envgen_cmd
from .commands.port_check import port_check_cmd
from .commands.regex_tester import regex_tester_cmd
from .commands.cheats import cheats_cmd
from .commands.lorem import lorem_cmd
from .commands.base64 import base64_cmd
from .commands.timer import timer_cmd
from .commands.timestamp import timestamp_cmd
from .commands.gen_password import gen_password_cmd
from .commands.slugify import slugify_cmd
from .commands.file_stats import file_stats_cmd
from .commands.colorize import colorize_cmd
from .commands.mkproject import mkproject_cmd
from .commands.git_ignore import git_ignore_cmd
from .commands.url_encode import url_encode_cmd
from .commands.url_decode import url_decode_cmd
from .commands.unit_convert import unit_convert_cmd
from .commands.whoami import whoami_cmd
from .commands.ipinfo import ipinfo_cmd



@click.group()
def cli():
    """A versatile command-line toolkit for developers."""
    pass

# Add commands to the CLI group
cli.add_command(uuid_cmd, name='uuid')
cli.add_command(hash_cmd, name='hash')
cli.add_command(jsonfmt_cmd, name='jsonfmt')
cli.add_command(envgen_cmd, name='envgen')
cli.add_command(port_check_cmd, name='port-check')
cli.add_command(regex_tester_cmd, name='regex-tester')
cli.add_command(cheats_cmd, name='cheats')
cli.add_command(lorem_cmd, name='lorem')
cli.add_command(base64_cmd, name='base64')
cli.add_command(timer_cmd, name='timer')
cli.add_command(timestamp_cmd, name='timestamp')
cli.add_command(gen_password_cmd, name='gen-password')
cli.add_command(slugify_cmd, name='slugify')
cli.add_command(file_stats_cmd, name='file-stats')
cli.add_command(colorize_cmd, name='colorize')
cli.add_command(mkproject_cmd, name='mkproject')
cli.add_command(git_ignore_cmd, name='git-ignore')
cli.add_command(url_encode_cmd, name='url-encode')
cli.add_command(url_decode_cmd, name='url-decode')
cli.add_command(unit_convert_cmd, name='unit-convert')
cli.add_command(whoami_cmd, name='whoami')
cli.add_command(ipinfo_cmd, name='ipinfo')

if __name__ == "__main__":
    cli()