#!/usr/bin/env python3
"""yeller

Author:
    Josh Moulder <josh.moulder12@gmail.com>
"""

import click
from version import yeller_version
from hello import hello  # Import the hello command
from install_dev import installdev  # Import the installdev command

# Set context settings for click
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

# Version number
version_num = yeller_version

# Define the main command group
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version_num, prog_name="Yeller", help="Show the version and exit.")
def cli():
    """Yeller is the Yell CLI toolset -- a single command with multiple subcommands for automating repeatable tasks."""
    pass

# Add the hello command to the main command group
cli.add_command(hello)

# Add the installdev command to the main command group
cli.add_command(installdev)

if __name__ == '__main__':
    cli()
