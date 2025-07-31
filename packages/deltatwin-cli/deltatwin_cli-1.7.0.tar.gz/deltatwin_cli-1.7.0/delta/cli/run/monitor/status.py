import json
import click

from delta.cli.utils import Utils, API

RUN_STATUS = "Status"
RUN_DATE = "Creation Date"
RUN_ID = "Id"
RUN_AUTHOR = "Author"
RUN_MESSAGE = "Message"


@click.command(
    name='status',
    short_help='Gets detailed information on a '
               'DeltaTwin® component execution status.')
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
def get_deltatwin_execution_status(conf, run_id, format_output):
    """Get the details of each step execution of a run by specifying its ID.

    To get the list of all runs and their associated IDs, use the command:
    'deltatwin run list'. Then, use the RUN_ID of interest as input for
    this command.
    This will return the status of each node in the workflow and their STEP_ID.
    To get the log of a specific node, use the command:
    'deltatwin run monitor logs <RUN_ID> <STEP_ID>'.

    RUN_ID: the id of the run to retrieve [MANDATORY]

    Example:

    deltatwin run monitor status 5e8f6a4f-3a83-4f41-ae28-99ce831a9861
    """

    run = [
        {
            'node_id': item['id'],
            'name': item['name'],
            'status': item['status'],
            'type': item['type'],
            'node_number': item['workflow_node_id']
        }
        for item in API.get_run_nodes(conf, run_id)

    ]
    if Utils.output_as_json(format_output, run):
        click.echo(json.dumps(run, indent=4))
    else:
        Utils.display_run_node_status(run)
