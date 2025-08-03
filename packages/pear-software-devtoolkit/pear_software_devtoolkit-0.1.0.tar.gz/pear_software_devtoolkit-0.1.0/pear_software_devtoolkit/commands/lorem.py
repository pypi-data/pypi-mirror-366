import click
from devtoolkit.utils import console

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

@click.command(help="Generates lorem ipsum text.")
@click.option('--paragraphs', default=1, help='Number of paragraphs to generate.')
@click.option('--words', help='Number of words to generate.')
def lorem_cmd(paragraphs, words):
    """Generates lorem ipsum text."""
    if words:
        word_list = LOREM_IPSUM.split()
        output = " ".join(word_list[:int(words)])
    else:
        output = "\n\n".join([LOREM_IPSUM] * paragraphs)
    
    console.print(output)