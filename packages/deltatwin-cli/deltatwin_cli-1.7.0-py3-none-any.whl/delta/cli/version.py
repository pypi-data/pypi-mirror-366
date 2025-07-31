import click

from delta.cli.utils import Utils
from delta.cli._version import __version__ as cli_version
from delta.core._version import __version__ as core_version


@click.command('version', short_help='Get version info.')
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="If present this option will also "
         "show the version of the delta-core.")
@click.help_option("--help", "-h")
def version(all):
    """
    Prints the DeltaTwin® command line version currently used.
    """
    click.echo(f"{Utils.log_info} DeltaTwin® CLI version : {cli_version}")
    if all:
        click.echo(f"{Utils.log_info} DeltaTwin® CORE version : {core_version}"
                   )
