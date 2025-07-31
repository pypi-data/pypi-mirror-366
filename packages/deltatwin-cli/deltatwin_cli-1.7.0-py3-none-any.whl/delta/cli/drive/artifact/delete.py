import click

from delta.cli.utils import API, Utils


@click.command(
    name='delete',
    short_help='Delete an artifact from user remote storage')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.help_option("--help", "-h")
@click.argument('artifact_id')
def delete_artifact(conf, artifact_id) -> None:
    """
    Delete an artifact from user remote storage using its ID.


    ARTIFACT_ID: Id of the artifact [MANDATORY]
    """

    API.delete_artifact(conf, artifact_id)

    click.echo(f"{Utils.log_info} Artifact \"{artifact_id}\""
               f" successfully deleted")
