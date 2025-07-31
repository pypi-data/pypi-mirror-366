import click

from delta.cli.drive.dependency.add import add_dependency
from delta.cli.drive.dependency.delete import delete_dependency
from delta.cli.drive.dependency.list import list_dependency


@click.group(help='DeltaTwins are composable so that users'
                  'can easily reuse existing'
                  'DeltaTwin® component and combine them to build'
                  'more complex DeltaTwin® components. '
                  'These command allow the user to list,'
                  'all the dependencies from the working Delta component. '
                  'To add a new dependency to the working DeltaT component. '
                  'And to remove a dependency.',
             short_help='DeltaTwin® drive dependency is dedicated '
                        'to manage all the dependencies of a Delta component.'
             )
def dependency():
    pass


dependency.add_command(add_dependency)
dependency.add_command(delete_dependency)
dependency.add_command(list_dependency)
