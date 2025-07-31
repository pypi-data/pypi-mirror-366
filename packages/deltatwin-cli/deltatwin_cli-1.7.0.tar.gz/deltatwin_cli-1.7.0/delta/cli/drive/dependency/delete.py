import click

from delta.cli.utils import Utils


@click.command(
    'delete',
    short_help='Remove a dependency to the working DeltaTwin'
)
@click.argument('name', required=True)
def delete_dependency(name):
    """This command allows to remove a dependency to the working DeltaTwin.

    NAME: the name of the Dependency [MANDATORY]

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(
        f'{Utils.log_info} deltatwin drive dependency '
        f'delete not yet implemented.'
    )
