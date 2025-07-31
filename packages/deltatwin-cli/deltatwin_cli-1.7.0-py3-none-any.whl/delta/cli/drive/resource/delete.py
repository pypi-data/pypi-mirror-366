import click

from delta.cli.utils import API, Utils


@click.command(
    name="delete", short_help="Delete a resource from user remote storage"
)
@click.option(
    "--conf", "-c", type=str, default=None, help="Path to the conf file"
)
@click.argument("resource_id")
@click.help_option("--help", "-h")
def delete_resource(conf: str | None, resource_id: str) -> None:
    """
    This command deletes a resource from the user DeltaTwin® drive storage
    by specifying its ID.

    Only the user who has published the resource or the administrator can
    perform the deletion.

    RESOURCE_ID: Id of the resource [MANDATORY]
    """

    API.delete_resource(conf, resource_id)

    click.echo(
        f'{Utils.log_info} Resource "{resource_id}"' f" successfully deleted"
    )
