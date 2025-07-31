import click
from delta.cli.utils import API, Utils

DEFAULT_LIMIT = 15


@click.command(
    name='add',
    short_help='Convert an output of a run into artifact')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--artifact-name',
    '-a',
    type=str,
    required=True,
    help='Name of the artifact')
@click.option(
    '--description',
    '-d',
    type=str,
    required=True,
    help='Description of the artifact')
@click.option(
    '--visibility',
    '-v',
    type=str,
    default='private',
    help='Visibility of the resource within the service. '
         'The public visibility requires to contact the DESP service support')
@click.option(
    '--topic',
    '-t',
    type=str,
    required=True,
    multiple=True,
    help='Define each topic of the artifact '
         '(multiple topics can be defined)')
@click.argument('run_id')
@click.argument('output_name')
@click.help_option("--help", "-h")
def add_artifact(conf, run_id, output_name: str, artifact_name: str,
                 description: str = None, visibility: str = 'private',
                 topic: list = None) -> None:
    """
    Create an artifact from an output of a DeltaTwin® component execution.

    RUN_ID: Id of the run Execution [MANDATORY]

    OUTPUT_NAME: Name of the output [MANDATORY]

    Example:
    deltatwin drive artifact add b8810ff1-16c7-4269-b784-0c5ce392ff25 out
    --artifact-name artifact_1 --description description
    --topic topic1 --topic topic2

    """
    topics = ",".join(topic)

    if artifact_name is None:
        artifact_name = output_name

    code = API.create_artifact(conf, run_id, output_name,
                               artifact_name, description, visibility, topics)

    if code == 202:
        click.echo(f"{Utils.log_info} Artifact \"{artifact_name}\" "
                   f"is being created and will be available shortly.")

    else:
        click.echo(f"{Utils.log_info} Artifact \"{artifact_name}\" "
                   f"successfully created")
