import click

from delta.cli.schedule.delete import delete_deltatwin_schedule
from delta.cli.schedule.get import get_deltatwin_schedule
from delta.cli.schedule.list import list_deltatwin_schedule
from delta.cli.schedule.pause import pause_deltatwin_schedule
from delta.cli.schedule.resume import resume_deltatwin_schedule
from delta.cli.schedule.add import add_deltatwin_schedule


@click.group(
    help='The DeltaTwin® schedule command group allows '
         'users to trigger executions on specific dates '
         'or on a periodic basis, as well as to interrupt, '
         'delete or view scheduled plans.'
)
def schedule():
    pass


# Manage schedule
schedule.add_command(add_deltatwin_schedule)
schedule.add_command(list_deltatwin_schedule)
schedule.add_command(delete_deltatwin_schedule)
schedule.add_command(get_deltatwin_schedule)
schedule.add_command(resume_deltatwin_schedule)
schedule.add_command(pause_deltatwin_schedule)
