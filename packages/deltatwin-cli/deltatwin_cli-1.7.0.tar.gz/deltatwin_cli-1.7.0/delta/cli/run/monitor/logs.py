import json
import click

from delta.cli.utils import Utils, API

RUN_STATUS = "Status"
RUN_DATE = "Creation Date"
RUN_ID = "Id"
RUN_AUTHOR = "Author"
RUN_MESSAGE = "Message"


@click.command(
    name='logs',
    short_help='Gets available logs of a node of a running '
               'DeltaTwin® component.')
@click.option(
    '--conf',
    '-c',
    type=str,
    default=None,
    help='Path to the conf file')
@click.help_option("--help", "-h")
@click.argument('run_id')
@click.argument('node_id')
def get_deltatwin_execution_logs(conf, run_id, node_id):
    """Get available logs of a node of a running DeltaTwin® component.

    To get the list of all runs and their associated IDs, use the command:
    'deltatwin run list'. Then, use the RUN_ID of interest as input of the
    command 'deltatwin run monitor status <RUN_ID>' to get the list of each
    node of the workflow execution and retrieve their associated STEP_ID.

    Then, this command allows to get the available logs for the specific
    STEP_ID.
    Note that only nodes of type model have logs available.


    RUN_ID: the id of the run to retrieve [MANDATORY]

    NODE_ID: the id of the node to retrieve logs [MANDATORY]

    Example:

    deltatwin run monitor logs c71f0e8d-d014f35102d9 b03cf13f-59c631fe2991
    """
    click.echo(json.dumps({
        'stdout': API.get_run_nodes_logs(conf, run_id, node_id).decode(),
        'stderr': API.get_run_nodes_logs(
            conf, run_id,
            node_id, True
        ).decode()
    }, indent=4))
