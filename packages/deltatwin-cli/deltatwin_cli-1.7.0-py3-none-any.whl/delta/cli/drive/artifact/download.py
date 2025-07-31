import re

import click

from delta.cli.utils import API, Utils

DEFAULT_LIMIT = 15


@click.command(
    name='download',
    short_help='download an artifact')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--file',
    '-F',
    type=str,
    default=None,
    help='Path of the file to save the artifact, by default '
         'it is the basename of the artifact in current directory')
@click.argument('artifact_id')
@click.help_option("--help", "-h")
def download_artifact(
        conf, artifact_id,
        file: str) -> None:
    """Download an artifact and store it in a file.

    ARTIFACT_ID: Id of the Artifact [MANDATORY]

    Example:

    deltatwin drive artifact download b8810ff1-16c7-4269-b784-0c5ce392ff25
    --file my_art.jpg
    """

    resp = API.download_artifact(conf, artifact_id)

    if file is None:
        d = resp.headers['content-disposition']
        file = re.findall("filename=\"(.+)\"", d)[0]

    with open(file, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            # If you have chunk encoded response uncomment if
            # and set chunk_size parameter to None.
            # if chunk:
            f.write(chunk)

    click.echo(f"{Utils.log_info} Artifact \"{artifact_id}\" successfully "
               f"downloaded in \"{file}\"")
