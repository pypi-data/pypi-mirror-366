import click
from delta.core import DeltaCore


@click.command(
    'sync',
    short_help='Reload the manifest file')
def sync():
    """
    Reload the manifest file content to refresh project resources section
    """
    with DeltaCore() as core:
        core.drive_sync()
