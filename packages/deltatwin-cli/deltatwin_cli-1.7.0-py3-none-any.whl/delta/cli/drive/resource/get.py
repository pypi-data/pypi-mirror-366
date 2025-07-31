import json

import click
from humanize import naturalsize
from rich.console import Console
from rich.table import Table

from delta.cli.utils import API

DEFAULT_LIMIT = 15


@click.command(name="get", short_help="Retrieve a resource")
@click.option(
    "--conf", "-c", type=str, default=None, help="Path to the conf file"
)
@click.option(
    "--format-output",
    "-f",
    type=str,
    default=None,
    help="Format of the output json/text default is text",
)
@click.argument("resource_id")
@click.help_option("--help", "-h")
def get_resource(
    conf, resource_id, format_output
) -> None:
    """This commands returns the details of a resource referred to by its ID.

    RESOURCE_ID: Id of the resource [MANDATORY]

    """
    resp = API.get_resource(conf, resource_id)

    data = {
        "resource_id": resp["resource_id"],
        "name": resp["name"],
        "size": resp["size"],
        "visibility": resp["visibility"],
        "description": resp["description"],
        "owner": resp["owner"],
        'topics': resp['topics']
    }

    if format_output is not None and format_output.lower() == "json":
        click.echo(json.dumps(data, indent=4))
    else:
        table = Table()
        table.add_column("Resource ID", no_wrap=True)
        table.add_column("Resource Name")
        table.add_column("Size")
        table.add_column("Visibility")
        table.add_column("Description")
        table.add_column("Owner")
        table.add_column('Topics')

        table.add_row(
            str(data["resource_id"]),
            data["name"],
            naturalsize(data["size"]),
            data["visibility"],
            data["description"],
            data["owner"],
            str(", ".join(data['topics'])),
        )

        console = Console()
        console.print(table)
