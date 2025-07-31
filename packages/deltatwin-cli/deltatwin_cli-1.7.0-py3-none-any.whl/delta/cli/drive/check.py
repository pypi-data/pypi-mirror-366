import click

from delta.cli.utils import Utils


@click.command(
    'check',
    short_help='Check that related references are accessible')
@click.option('--all', '-a', is_flag=True)
@click.option('--dependencies', '-d', is_flag=True,
              help='If flag present check all the dependencies')
@click.option('--resources', '-r', is_flag=True,
              help='If flag present check all the resources')
@click.argument('url', required=True, default='None')
def check(url, all, dependencies, resources):
    """Check that related references are accessible.

    URL: Url where the DeltaTwin is accessible [MANDATORY]

    **Note:** THIS COMMAND WILL BE AVAILABLE SOON
    """
    click.echo(f'{Utils.log_info} delta drive check not yet implemented.')
