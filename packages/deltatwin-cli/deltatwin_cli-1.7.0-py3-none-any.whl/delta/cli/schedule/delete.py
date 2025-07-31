from sys import flags

import click

from delta.cli.utils import API


@click.command(
    name='delete',
    short_help='Delete a scheduled DeltaTwin component execution')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option('--yes', '-y',
              type=bool,
              required=False,
              is_flag=True,
              default=False,
              help="Don't ask for confirmation of deletion")
@click.argument('schedule_id')
@click.help_option("--help", "-h")
def delete_deltatwin_schedule(conf, schedule_id, yes):
    """
    Delete the scheduled execution plan on a DeltaTwin® component.

    SCHEDULE_ID : Id of the schedule execution to be deleted [MANDATORY]
    """
    msg = (f'Are you sure you want to delete the '
           f'DeltaTwin® component execution schedule {schedule_id} ?')
    if yes or click.confirm(msg, default=False):
        API.delete_scheduled_run(conf, schedule_id)
