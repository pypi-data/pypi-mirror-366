import click

from delta.cli.utils import Utils


@click.command(
    'list',
    short_help='list all dependencies of the working DeltaTwin'
)
def list_dependency():
    """This command show all the dependencies of the working DeltaTwin.

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(
        f'{Utils.log_info} deltatwin drive dependency'
        f' list not yet implemented.'
    )
