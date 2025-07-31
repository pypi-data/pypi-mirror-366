import json

import click

from delta.cli.schedule.utils import display_list_detailed, format_schedules

from delta.cli.utils import Utils, API

DEFAULT_LIMIT = 15


@click.command(
    name='list',
    short_help='List scheduled DeltaTwin component execution')
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
@click.option(
    '--twin-name',
    '-t',
    type=str,
    default=None,
    help='List all the scheduled execution plans on this DeltaTwin component')
@click.option(
    '--author',
    '-a',
    type=str,
    default=None,
    help='List all the scheduled execution '
         'plan made by the user [RESERVED FOR ADMIN]')
@click.help_option("--help", "-h")
def list_deltatwin_schedule(conf, twin_name, author, format_output: str):
    """
    List all the scheduled execution plans on a DeltaTwin service.
    """
    schedules = API.list_scheduled_run(conf, twin_name, author)

    schedules = format_schedules(schedules)

    if Utils.output_as_json(format_output, schedules):
        click.echo(json.dumps(schedules, indent=4))
    else:
        display_list_detailed(schedules)
