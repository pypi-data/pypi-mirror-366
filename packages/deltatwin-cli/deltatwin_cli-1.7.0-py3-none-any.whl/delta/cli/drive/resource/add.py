import click

from delta.cli.utils import API


@click.command(
    "add", short_help="Add a resource to the user's DeltaTwin® Drive storage"
)
@click.option(
    "--conf", "-c", type=str, default=None, help="Path to the conf file"
)
@click.option(
    "--description",
    "-d",
    type=str,
    required=True,
    default=None,
    help="Description of the resource",
)
@click.option(
    "--visibility",
    "-v",
    type=click.Choice(["public", "private"]),
    default="private",
    help='Visibility of the resource within the service. '
         'The public visibility requires to contact the DESP service support',
)
@click.option(
    "--topic",
    "-t",
    type=str,
    multiple=True,
    required=True,
    help="Define each topic of the resource "
         "(multiple topics can be defined)",
)
@click.argument("path")
@click.argument("filename")
@click.help_option("--help", "-h")
def add_resource(
        conf: str | None,
        description: str | None,
        visibility: str,
        topic: list[str],
        path: str,
        filename: str,
):
    """Add a resource to the user's DeltaTwin® Drive storage by specifying
    its name, description, topics that will be associated to this data.

    It returns the id which then can be used to reference your data within
    the service.

    To publish with the public visibility, please contact DESP service support.


    PATH: fullpath or url of the resources. [MANDATORY]

    FILENAME: by which the resource is referenced in your drive. [MANDATORY]
    """
    topics = ",".join(topic)
    if description is None:
        description = ""
    resource_id = API.create_resource(
        conf, path, filename, description, visibility, topics
    )
    click.echo(f"Resource added to Drive. Resource id: {resource_id}")
