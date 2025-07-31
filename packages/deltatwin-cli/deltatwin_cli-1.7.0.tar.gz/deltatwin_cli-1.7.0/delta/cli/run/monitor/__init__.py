import click

from delta.cli.run.delete import delete_deltatwin_execution
from delta.cli.run.download import download_deltatwin_execution
from delta.cli.run.monitor.logs import get_deltatwin_execution_logs
from delta.cli.run.monitor.status import get_deltatwin_execution_status
from delta.cli.run.start import start
from delta.cli.run.stop import stop
from delta.cli.run.resume import resume
from delta.cli.run.list import list_deltatwin_executions
from delta.cli.run.get import get_deltatwin_execution
from delta.cli.run.local import run_local


@click.group(
    help='DeltaTwin® run monitor aims to check the status of a running '
         'DeltaTwin®. It provides the information on the status of each step '
         'of the workflow and allows to retrieve the available logs '
         'for each node of type model.'
)
def monitor():
    pass


# Manage run
monitor.add_command(get_deltatwin_execution_status)
monitor.add_command(get_deltatwin_execution_logs)
