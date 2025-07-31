import json
import click

from delta.cli.utils import Utils, API

RUN_STATUS = "Status"
RUN_DATE = "Creation Date"
RUN_ID = "Id"
RUN_AUTHOR = "Author"
RUN_MESSAGE = "Message"


@click.command(
    name='get',
    short_help='Gets detailed information on a DeltaTwin component execution')
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
@click.help_option("--help", "-h")
@click.argument('run_id')
def get_deltatwin_execution(conf, run_id, format_output):
    """Get the details of a run by specifying its ID.

    RUN_ID: the id of the run to retrieve [MANDATORY]

    Example:

    deltatwin run get 5e8f6a4f-3a83-4f41-ae28-99ce831a9861
    """

    run = API.get_run(conf, run_id)
    run['generation_date'] = Utils.format_date(run['generation_date'])
    run['end_at'] = Utils.format_date(run['end_at'])
    if Utils.output_as_json(format_output, run):
        click.echo(json.dumps(run, indent=4))
    else:
        Utils.display_run_detailed(run)
