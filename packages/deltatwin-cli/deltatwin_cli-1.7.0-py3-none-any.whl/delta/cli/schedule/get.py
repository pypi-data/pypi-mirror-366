import json

import click

from delta.cli.schedule.utils import display_schedule_detailed, format_schedule

from delta.cli.utils import Utils, API

DEFAULT_LIMIT = 15


@click.command(
    name='get',
    short_help='get a scheduled DeltaTwin component execution')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.option(
    '--format-output',
    '-f',
    type=str,
    default=None,
    help='Format of the output (json/text). Default is text')
@click.argument('schedule_id')
@click.help_option("--help", "-h")
def get_deltatwin_schedule(conf, schedule_id, format_output: str):
    """
    Get all information on a specific DeltaTwin® schedule depending
    on the DeltaTwin® component schedule ID.
    """
    schedules = API.get_scheduled_run(conf, schedule_id)
    schedules = format_schedule(schedules)
    if Utils.output_as_json(format_output, schedules):
        click.echo(json.dumps(schedules, indent=4))
    else:
        display_schedule_detailed(schedules)
