import json

import click
from humanize import naturalsize
from rich.console import Console
from rich.table import Table

from delta.cli.utils import API, Utils


@click.command(
    "list",
    short_help=(
        "List the resources available on the user's DeltaTwin® Drive storage"
    ),
)
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
@click.option(
    "--visibility",
    "-v",
    type=str,
    default=None,
    help="Set a filter to retrieve Resource depending on its visibility",
)
@click.help_option("--help", "-h")
def list_resource(conf, format_output: str, visibility: str | None) -> None:
    """This command lists all the resources published by the user and all
    publicly available resources within the service.

    **Example:** deltatwin drive resource list
    """
    if visibility is None:
        resources = API.list_resource(
            conf,
            "private",
        ) + API.list_resource(conf, "public")
    else:
        resources = API.list_resource(
            conf,
            visibility,
        )

    data = []

    for resource in resources:
        data.append(
            {
                "resource_id": resource["resource_id"],
                "name": resource["name"],
                "size": resource["size"],
                "visibility": resource["visibility"],
                "description": resource["description"],
                "owner": resource["owner"],
                'topics': resource['topics']
            }
        )

    if format_output is not None and format_output.lower() == 'json':
        click.echo(json.dumps(data, indent=4))
        return

    if isinstance(data, list):
        if len(data) == 0:
            click.echo(f"{Utils.log_info} No resource found")

        table = Table(show_lines=True)
        table.add_column("Id", no_wrap=True)
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("Visibility")
        table.add_column("Description")
        table.add_column("Owner")
        table.add_column('Topics')

        for resource in data:
            rows = (
                resource["resource_id"],
                resource["name"],
                naturalsize(resource["size"]),
                str(resource["visibility"]),
                str(resource["description"]),
                str(resource["owner"]),
                str(", ".join(resource['topics'])),
            )

            table.add_row(*rows)
        console = Console()
        console.print(table)
