import click

from delta.cli.drive.artifact.delete import delete_artifact
from delta.cli.drive.artifact.download import download_artifact
from delta.cli.drive.artifact.list import list_artifact
from delta.cli.drive.artifact.get import get_artifact
from delta.cli.drive.artifact.add import add_artifact
from delta.cli.drive.update import update


@click.group(
    help="""DeltaTwin® drive artifact stores generated output data in the
     user's DeltaTwin® drive storage"""
)
def artifact():
    pass


artifact.add_command(list_artifact)
artifact.add_command(get_artifact)
artifact.add_command(add_artifact)
artifact.add_command(delete_artifact)
artifact.add_command(download_artifact)
artifact.add_command(update)
