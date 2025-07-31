import click

from delta.cli.drive.check import check
from delta.cli.drive.resource import resource
from delta.cli.drive.dependency import dependency
from delta.cli.drive.artifact import artifact


@click.help_option("--help", "-h")
@click.group(help="""
             DeltaTwin® drive is dedicated to handle
             DeltaTwin® project repository.
             It stores all the configuration,
             resources, models and sources
             to run a DeltaTwin® and retrieve data,
             the DeltaTwin® drive commands can also be used to manage
             the resources, artifacts and dependencies of the user DeltaTwin®.
             """,
             short_help="""
             DeltaTwin® drive is dedicated to manage
              DeltaTwin® project repository.
             """)
def drive():
    pass


drive.add_command(resource)
drive.add_command(artifact)
