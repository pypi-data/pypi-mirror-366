import json

import click
from humanize import naturalsize
from rich.console import Console
from rich.table import Table

from delta.cli.utils import API, Utils

DEFAULT_LIMIT = 15


@click.command(
    name='get',
    short_help='Retrieve an artifact')
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
@click.argument('artifact_id')
@click.help_option("--help", "-h")
def get_artifact(conf, artifact_id, format_output) -> None:
    """This command displays the details of a artifact referenced by its ID.

    ARTIFACT_ID: Id of the Artifact [MANDATORY]

    Example:

    deltatwin® drive artifact get b8810ff1-16c7-4269-b784-0c5ce392ff25
    """
    resp = API.get_artifact(conf, artifact_id)

    data = {
        'artifact_id': resp['artifact_id'],
        'name': resp['name'],
        'twin_name': f"{resp['twin_name']}:{resp['twin_version']}",
        'size': resp['size'],
        'visibility': resp['visibility'],
        'description': resp['description'],
        'owner': resp['owner'],
        'topics': resp['topics']

    }

    if format_output is not None and format_output.lower() == 'json':
        click.echo(json.dumps(data, indent=4))
    else:
        table = Table()
        table.add_column("Artifact ID", no_wrap=True)
        table.add_column("Artifact Name")
        table.add_column("DeltaTwin Name")
        table.add_column("Size")
        table.add_column("Visibility")
        table.add_column("Description")
        table.add_column("Owner")
        table.add_column("Topics")

        table.add_row(str(data['artifact_id']),
                      data['name'],
                      data['twin_name'],
                      naturalsize(data['size'], True),
                      data['visibility'],
                      data['description'],
                      data['owner'],
                      ", ".join(data['topics']))

        console = Console()
        console.print(table)
