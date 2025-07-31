import json

import click
from rich.table import Table
from rich.console import Console

from delta.cli.utils import API, Utils

DELTA_TWIN_NAME = "Name"
DELTA_TWIN_DESCRIPTION = "Short Description"
DELTA_TWIN_PUBLICATION_DATE = "Publication Date"
DELTA_TWIN_TOPICS = "Topics"
DELTA_TWIN_LICENSE = "License"
DELTA_TWIN_VISIBILITY = "Visibility"
DELTA_TWIN_OWNER = "Owner"


@click.command('list', short_help='List of the Delta component of the user.')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--format-output',
    '-f',
    type=str,
    default=None,
    help='Format of the output json/text default is text')
@click.option(
    '--visibility',
    '-v',
    type=str,
    default=None,
    help="Set a filter to retrieve DeltaTwins® depending on its visibility."
         " By default 'public'")
@click.option(
    '--owner',
    '-o',
    type=str,
    default=None,
    help='Set a filter to retrieve DeltaTwins® depending on the author')
@click.help_option("--help", "-h")
def list_deltatwins(
        conf,
        format_output,
        visibility,
        owner

):
    """List the DeltaTwins components available to the user.
    The user can view his DeltaTwin® component details, all the
    Delta components from the Starter Kit and those
    created with the public visibility.

    This command will list the DeltaTwins® components of the user.
    Before using this command the user must be logged in.
    """
    if visibility is None:
        dts = API.get_dts(conf, 'private') + API.get_dts(conf, 'public')
    else:
        dts = API.get_dts(conf, visibility)

    if len(dts) == 0:
        click.echo(f"{Utils.log_info} No DeltaTwin found.")

    data = Utils.prepare_dt(dts)

    data = Utils.filter_dts(data, owner)

    if format_output is not None and format_output.lower() == 'json':
        click.echo(json.dumps(data, indent=4))
    else:
        if isinstance(data, list):
            table = Table(show_lines=True)
            table.add_column(DELTA_TWIN_NAME)
            table.add_column(DELTA_TWIN_DESCRIPTION)
            table.add_column(DELTA_TWIN_PUBLICATION_DATE)
            table.add_column(DELTA_TWIN_LICENSE)
            table.add_column(DELTA_TWIN_VISIBILITY)
            table.add_column(DELTA_TWIN_TOPICS)
            table.add_column(DELTA_TWIN_OWNER)

            for dt in data:
                table.add_row(
                    dt['name'],
                    dt['short_description'],
                    dt['publication_date'],
                    dt['license'],
                    dt['visibility'],
                    str(', '.join(dt['topics'])),
                    dt['owner'])

            console = Console()
            console.print(table)
