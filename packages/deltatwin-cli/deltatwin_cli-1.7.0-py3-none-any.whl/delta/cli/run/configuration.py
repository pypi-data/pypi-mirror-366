import sys

import click

from delta.cli import Utils, ReturnCode


@click.command(
    'configuration',
    short_help='Manage run configuration',
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ))
def configuration():
    """Manage run configuration

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(
        f'{Utils.log_info} delta run configuration not yet implemented.'
    )
