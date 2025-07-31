import click

from delta.cli.utils import Utils, API


@click.command(
    name='delete',
    short_help='Delete a run execution using his ID')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.help_option("--help", "-h")
@click.argument('run_id')
def delete_deltatwin_execution(conf, run_id):
    """Delete the run whose id is given as input argument.

    RUN_ID: the id of the run to retrieve

    Example:

    deltatwin run delete 5e8f6a4f-3a83-4f41-ae28-99ce831a9861

    """
    API.delete_run(conf, run_id)

    click.echo(f"{Utils.log_info} Run \"{run_id}\""
               f" successfully deleted")
