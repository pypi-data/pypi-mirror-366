import click

from delta.cli.utils import Utils


@click.command(
    'add',
    short_help='Add a dependency to the working DeltaTwin component'
)
@click.option("--version", "-v", type=str, default=None,
              help="Give a specific version of DeltaTwin component")
@click.argument('name', required=False)
def add_dependency(name, version=None):
    """This command allows to add a dependency to an existing DeltaTwin
    component. If no version is specified the last version will be used.

    NAME: the name of the dependency [MANDATORY]

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(
        f'{Utils.log_info} deltatwin drive dependency add not yet implemented.'
    )
